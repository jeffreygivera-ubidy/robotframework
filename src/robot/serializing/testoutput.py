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


import time

from robot import utils
from robot.errors import DataError
from robot.common import Statistics
from robot.conf import get_title
from robot.output import process_outputs, process_output

import templates
from templating import Namespace, Template
from serializer import OutputSerializer, SummaryStatisticsSerializer, \
    ReportStatisticsSerializer, ReportSuiteSerializer, ReportTagStatSerializer, \
    LogStatisticsSerializer, LogSyslogSerializer, LogSuiteSerializer, \
    SplitLogSuiteSerializer, SplitLogStatisticsSerializer, SplitReportSuiteSerializer


class RobotTestOutput:

    def __init__(self, testsuite, testsyslog, settings=None):
        self.suite = testsuite
        self.syslog = testsyslog
        if settings is not None:
            params = (settings['SuiteStatLevel'], settings['TagStatInclude'],
                      settings['TagStatExclude'], settings['TagStatCombine'],
                      settings['TagDoc'], settings['TagStatLink'])
        else:
            params = ()
        self.statistics = Statistics(testsuite, *params)
        self._generator = 'Robot'

    def serialize(self, settings, syslog=None, generator='Robot'):
        self._generator = generator
        self.serialize_output(settings['Output'], settings['SplitOutputs'], syslog)
        self.serialize_summary(settings['Summary'], settings['SummaryTitle'], syslog)
        self.serialize_report(settings['Report'], settings['ReportTitle'],
                              settings['Log'], settings['SplitOutputs'], syslog)
        self.serialize_log(settings['Log'], settings['LogTitle'], 
                           settings['SplitOutputs'], syslog)
        
    def serialize_output(self, path, split=-1, syslog=None):
        if path == 'NONE':
            return
        serializer = OutputSerializer(path, split)
        self.suite.serialize(serializer)
        self.statistics.serialize(serializer)
        self.syslog.serialize(serializer)
        serializer.close()
        if syslog is not None:
            syslog.output_file('Output', path)
        
    def serialize_summary(self, path, title=None, syslog=None):
        outfile = self._get_outfile(path, 'summary', syslog)
        if outfile is None:
            return
        if title is None:
            title = get_title('Summary', self.suite.name)
        self._use_template(outfile, templates.REPORT, title)
        self.statistics.serialize(SummaryStatisticsSerializer(outfile))
        outfile.write('</body>\n</html>\n')
        outfile.close()
        if syslog is not None:
            syslog.output_file('Summary', path)
        
    def serialize_report(self, path, title=None, logpath=None, split=-1,
                         syslog=None):
        outfile = self._get_outfile(path, 'report', syslog)
        if outfile is None:
            return
        if title is None:
            title = get_title('Report', self.suite.name)
        if logpath == 'NONE':
            logpath = None
        self._use_template(outfile, templates.REPORT, title)
        self.statistics.serialize(ReportStatisticsSerializer(outfile))
        if split > 0 and logpath is not None:
            self.suite.serialize(SplitReportSuiteSerializer(outfile, logpath, split))
        else:
            self.suite.serialize(ReportSuiteSerializer(outfile, logpath))
        self.statistics.tags.serialize(ReportTagStatSerializer(outfile))
        outfile.write('</body>\n</html>\n')
        outfile.close()
        if syslog is not None:
            syslog.output_file('Report', path)
        
    def serialize_log(self, path, title=None, split=-1, syslog=None):
        outfile = self._get_outfile(path, 'log', syslog)
        if outfile is None:
            return
        if title is None:
            title = get_title('Log', self.suite.name)
        self._use_template(outfile, templates.LOG, title)
        if split > 0:
            self._serialize_split_log(outfile, split)
        else:
            self._serialize_log(outfile)
        outfile.write('</body>\n</html>\n')
        outfile.close()
        if syslog is not None:
            syslog.output_file('Log', path)
            
    def _serialize_log(self, outfile):
        self.statistics.serialize(LogStatisticsSerializer(outfile))
        self.syslog.serialize(LogSyslogSerializer(outfile))            
        self.suite.serialize(LogSuiteSerializer(outfile))
            
    def _serialize_split_log(self, outfile, level):
        self.statistics.serialize(SplitLogStatisticsSerializer(outfile, level))
        self.syslog.serialize(LogSyslogSerializer(outfile))
        self.suite.serialize(SplitLogSuiteSerializer(outfile, level))
        self._create_split_sub_logs(self.suite, level)
        
    def _create_split_sub_logs(self, suite, level):
        # Overridden by RebotTestOutput
        pass
        
    def _use_template(self, outfile, template, title):
        ttuple = time.localtime()
        str_time = '%s %s' % (utils.format_time(ttuple, daytimesep='&nbsp;'),
                              utils.get_diff_to_gmt())
        int_time = long(time.mktime(ttuple))
        namespace = Namespace(gentime_str=str_time, gentime_int=int_time, 
                              version=utils.get_full_version(self._generator), 
                              suite=self.suite, title=title)
        tmpl = Template(template=template)
        tmpl.generate(namespace, outfile)

    def _get_outfile(self, outpath, outtype, syslog=None):
        if outpath == 'NONE':
            return None
        try:
            return open(outpath, 'wb')
        except:
            msg = ("Opening %s file '%s' for writing failed: %s" 
                   % (outtype, outpath, utils.get_error_message()))
            if syslog is None:
                raise DataError(msg)
            syslog.error(msg)
            return None
        

class RebotTestOutput(RobotTestOutput):
    
    def __init__(self, datasources, settings, syslog):
        testsuite, testsyslog = process_outputs(datasources, settings, syslog)
        testsuite.set_options(settings)
        RobotTestOutput.__init__(self, testsuite, testsyslog, settings)
        self._namegen = utils.FileNameGenerator(settings['Log'])
        self._syslog = syslog
        
    def _create_split_sub_logs(self, suite, split_level, suite_level=0):
        if suite_level < split_level:
            for sub in suite.suites:
                self._create_split_sub_logs(sub, split_level, suite_level+1)
        elif suite_level == split_level:
            self._create_split_sub_log(suite)
            
    def _create_split_sub_log(self, suite):
        suite.set_names()
        outfile = self._get_outfile(self._namegen.get_name(), 'log', self._syslog)
        if outfile is None:
            return
        self._use_template(outfile, templates.LOG, get_title('Log', suite.name))
        Statistics(suite).serialize(LogStatisticsSerializer(outfile))
        suite.serialize(LogSuiteSerializer(outfile))
        outfile.write('</body>\n</html>\n')
        outfile.close()

        
class SplitSubTestOutput(RobotTestOutput):
    
    def __init__(self, path):
        testsuite, testsyslog = process_output(path)
        testsuite.set_names()
        RobotTestOutput.__init__(self, testsuite, testsyslog)


class SplitIndexTestOutput(RobotTestOutput):
    
    def __init__(self, runsuite, path, settings):
        # 'runsuite' is the one got when running tests and 'outsuite' is read
        # from xml. The former contains information (incl. stats) about all 
        # tests but no messages. The latter contains messages but no info
        # about tests in splitted outputs. 
        outsuite, outsyslog = process_output(path, settings['SplitOutputs'])
        outsuite.set_names()
        self._update_stats(outsuite, runsuite)
        RobotTestOutput.__init__(self, runsuite, outsyslog, settings)
        self.outsuite = outsuite
        
    def _update_stats(self, outsuite, runsuite):
        outsuite.critical_stats = runsuite.critical_stats
        outsuite.all_stats = runsuite.all_stats
        outsuite.status = runsuite.status
        for outsub, runsub in zip(outsuite.suites, runsuite.suites):
            self._update_stats(outsub, runsub)

    def _serialize_split_log(self, outfile, level):
        self.statistics.serialize(SplitLogStatisticsSerializer(outfile, level))
        self.syslog.serialize(LogSyslogSerializer(outfile))
        self.outsuite.serialize(SplitLogSuiteSerializer(outfile, level))
