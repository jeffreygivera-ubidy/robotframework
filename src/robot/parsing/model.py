#  Copyright 2008 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


import os

from robot import utils
from robot.errors import DataError
from robot.common import BaseTestSuite, BaseTestCase

from rawdata import RawData
from metadata import TestSuiteMetadata, TestCaseMetadata
from keywords import KeywordList
from userkeyword import UserHandlerList

_IGNORED_PREFIXES = ['_','.']
_IGNORED_DIRS = ['CVS']
_PROCESSED_EXTS = ['.html','.xhtml','.htm','.tsv']


def TestSuiteData(datasources, settings, syslog, process_curdir=True):
    datasources = [ utils.normpath(path) for path in datasources ]
    if len(datasources) == 0:
        raise DataError("No Robot data sources given.")
    elif len(datasources) > 1:
        return MultiSourceSuite(datasources, settings['SuiteNames'], syslog, process_curdir)
    elif os.path.isdir(datasources[0]):
        return DirectorySuite(datasources[0], settings['SuiteNames'], syslog, process_curdir)
    else:
        return FileSuite(datasources[0], syslog, process_curdir)


class _BaseSuite(BaseTestSuite):

    def __init__(self, rawdata):
        name, source = self._get_name_and_source(rawdata.source)
        BaseTestSuite.__init__(self, name, source)
        metadata = TestSuiteMetadata(rawdata)   
        self.doc = metadata['Documentation']
        self.suite_setup = metadata['SuiteSetup']
        self.suite_teardown = metadata['SuiteTeardown']
        self.test_setup = metadata['TestSetup']
        self.test_teardown = metadata['TestTeardown']
        self.default_tags = metadata['DefaultTags']
        self.force_tags = metadata['ForceTags']
        self.test_timeout = metadata['TestTimeout']
        self.metadata = metadata.user_metadata 
        self.imports = metadata.imports
        self.variables = rawdata.variables
        self.user_keywords = UserHandlerList(rawdata.keywords)

    def _get_name_and_source(self, path):
        source = self._get_source(path)
        return self._get_name(source), source
        
    def _get_name(self, source):
        return utils.printable_name_from_path(source)

        
class FileSuite(_BaseSuite):
    
    def __init__(self, path, syslog, process_curdir):
        syslog.info("Parsing test case file '%s'" % path)
        rawdata = self._get_rawdata(path, syslog, process_curdir)
        _BaseSuite.__init__(self, rawdata)
        self.tests = self._process_testcases(rawdata, syslog)

    def _get_source(self, path):
        return path
        
    def _get_rawdata(self, path, syslog, process_curdir):
        rawdata = RawData(path, syslog, process_curdir=process_curdir)
        if rawdata.get_type() == rawdata.TESTCASE:
            return rawdata
        raise DataError("Test case file '%s' contains no test cases."  % path)

    def _process_testcases(self, rawdata, syslog):
        names = []
        tests = []
        for rawtest in rawdata.testcases:
            try:
                test = TestCase(rawtest)
            except:
                rawtest.report_invalid_syntax()
                continue
            tests.append(test)
            name = utils.normalize(test.name)
            if name in names:
                msg = "Multiple test cases with name '%s' in test suite '%s'"
                syslog.warn(msg % (test.name, self.name))
            else:
                names.append(name)
        return tests

            
class DirectorySuite(_BaseSuite):
    
    def __init__(self, path, suitenames, syslog, process_curdir):
        syslog.info("Parsing test suite directory '%s'" % path)
        # If we are included also all our children are
        if self._is_in_incl_suites(os.path.basename(os.path.normpath(path)),
                                   suitenames):
            suitenames = []  
        subitems, initfile = self._get_suite_items(path, suitenames, syslog)
        rawdata = self._get_rawdata(path, initfile, syslog, process_curdir)
        _BaseSuite.__init__(self, rawdata)
        self._process_subsuites(subitems, suitenames, syslog, process_curdir)
        if self.get_test_count() == 0 and len(suitenames) == 0:
            raise DataError("Test suite directory '%s' contains no test cases." 
                            % path)
        
    def _get_source(self, path):
        # 'path' points either to directory or __init__ file inside it
        return utils.get_directory(path)
        
    def _get_suite_items(self, dirpath, suitenames, syslog):
        names = os.listdir(dirpath)
        names.sort(lambda x,y: cmp(x.lower(), y.lower()))
        files = []
        initfile = None
        for name in names:
            path = os.path.join(dirpath, name)
            if self._is_suite_init_file(name, path):
                if initfile is None:
                    initfile = path
                else:
                    syslog.error("Ignoring second test suite init file '%s'" % path)
            elif self._is_ignored(name, path, suitenames):
                syslog.info("Ignoring file or directory '%s'" % name)
            else:             
                files.append(path)
        return files, initfile

    def _get_rawdata(self, path, initfile, syslog, process_curdir):
        if initfile is None:
            syslog.info("No test suite directory init file")
            return RawData(path, syslog, process_curdir=process_curdir)
        syslog.info("Parsing test suite directory init file '%s'" % initfile)
        rawdata = RawData(initfile, syslog, process_curdir=process_curdir)
        if rawdata.get_type() == rawdata.INITFILE:
            return rawdata
        err = "Test suite directory initialization file '%s' contains " % initfile
        if rawdata.get_type() == rawdata.TESTCASE:
            syslog.error(err + 'test cases and is ignored.')
        elif rawdata.get_type() == rawdata.EMPTY:
            syslog.warn(err + 'no test data.')
        return RawData(path, syslog, process_curdir=process_curdir)
            
    def _process_subsuites(self, paths, suitenames, syslog, process_curdir):
        for path in paths:
            try:
                if os.path.isdir(path):
                    suite = DirectorySuite(path, suitenames, syslog, process_curdir)
                else:
                    suite = FileSuite(path, syslog, process_curdir)
            except:
                msg = "Parsing data source '%s' failed: %s"
                syslog.info(msg % (path, utils.get_error_message()))
            else:
                self.suites.append(suite)

    def _is_ignored(self, name, path, incl_suites):
        if name[0] in _IGNORED_PREFIXES:
            return True
        if os.path.isdir(path):
            return name in _IGNORED_DIRS
        root, ext = os.path.splitext(name.lower())
        if ext not in _PROCESSED_EXTS:
            return True
        return not self._is_in_incl_suites(root, incl_suites)

    def _is_in_incl_suites(self, name, incl_suites):
        if incl_suites == []:
            return True
        # Match only to the last part of name given like '--suite parent.child'
        incl_suites = [ incl.split('.')[-1] for incl in incl_suites ]
        return utils.matches_any(name, incl_suites, ignore=['_'])

    def _is_suite_init_file(self, name, path):
        if not os.path.isfile(path):
            return False
        root, ext = os.path.splitext(name.lower())
        return root == '__init__' and ext in _PROCESSED_EXTS
    

class MultiSourceSuite(_BaseSuite):
    
    def __init__(self, paths, suitenames, syslog, process_curdir):
        syslog.info("Parsing multiple data sources %s" % utils.seq2str(paths))
        _BaseSuite.__init__(self, RawData(None, syslog))
        for path in paths:
            try:
                if os.path.isdir(path):
                    suite = DirectorySuite(path, suitenames, syslog, process_curdir)
                else:
                    suite = FileSuite(path, syslog, process_curdir)
            except DataError, err:
                syslog.error("Parsing data source '%s' failed: %s" % (path, err))
            else:
                self.suites.append(suite)
        if self.get_test_count() == 0 and len(suitenames) == 0:
            # The latter check is to get a more informative exception in 
            # suite.filter_by_names later if --suite option was used.
            raise DataError('Data sources %s contain no test cases.' % 
                            (utils.seq2str(paths)))

    def _get_name_and_source(self, path):
        return '', None
        
    def set_names(self, name):
        if name is None:
            name = ' & '.join([suite.name for suite in self.suites])
        return BaseTestSuite.set_names(self, name)

    
class TestCase(BaseTestCase):
    
    def __init__(self, rawdata):
        BaseTestCase.__init__(self, utils.printable_name(rawdata.name))
        metadata = TestCaseMetadata(rawdata.metadata)
        self.doc = metadata['Documentation']
        self.tags = metadata['Tags']
        self.setup = metadata['Setup']
        self.teardown = metadata['Teardown']
        self.timeout = metadata['Timeout'] 
        self.keywords = KeywordList(rawdata.keywords)
