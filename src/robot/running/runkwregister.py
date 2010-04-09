#  Copyright 2008-2009 Nokia Siemens Networks Oyj
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


from types import MethodType, FunctionType

from robot import utils


class _RunKeywordRegister:

    def __init__(self):
        self._libs = {}

    def register_run_keyword(self, libname, keyword, args_to_process=None):
        if args_to_process is None:
            args_to_process = self._get_args_from_method(keyword)
            keyword =  keyword.__name__
        kwname = utils.printable_name(keyword, code_style=True)
        self._libs.setdefault(libname, {})[kwname] = int(args_to_process)

    def get_args_to_process(self, libname, kwname):
        if libname in self._libs and kwname in self._libs[libname]:
            return self._libs[libname][kwname]
        return -1

    def is_run_keyword(self, libname, kwname):
        return self.get_args_to_process(libname, kwname) >= 0

    def _get_args_from_method(self, method):
        if type(method) is MethodType:
            return method.im_func.func_code.co_argcount -1
        elif type(method) is FunctionType:
            return method.func_code.co_argcount
        raise ValueError("Needs function or method!")


RUN_KW_REGISTER = _RunKeywordRegister()
