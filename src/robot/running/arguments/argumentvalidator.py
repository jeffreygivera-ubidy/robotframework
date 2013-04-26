#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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

from robot.errors import DataError
from robot.utils import plural_or_not
from robot.variables import is_list_var


class ArgumentValidator(object):

    def __init__(self, argspec):
        self._argspec = argspec

    def validate_arguments(self, positional, named):
        self._validate_no_mandatory_missing(positional, named, self._argspec)
        self._validate_no_arg_given_twice(positional, named, self._argspec)
        self._validate_limits(positional, named, self._argspec)

    def _validate_no_mandatory_missing(self, positional, named, spec):
        for name in spec.positional[len(positional):spec.minargs]:
            if name not in named:
                raise DataError("%s '%s' missing value for argument '%s'."
                                % (spec.type, spec.name, name))

    def _validate_no_arg_given_twice(self, positional, named, spec):
        for name in spec.positional[:len(positional)]:
            if name in named:
                raise DataError("Error in %s '%s'. Value for argument '%s' was given twice."
                                % (spec.type.lower(), spec.name, name))

    def validate_limits(self, positional, named=None, dry_run=False):
        if not (dry_run and any(is_list_var(arg) for arg in positional)):
            self._validate_limits(positional, named or {}, self._argspec)

    def _validate_limits(self, positional, named, spec):
        count = len(positional) + len(named)
        if not spec.minargs <= count <= spec.maxargs:
            self._raise_wrong_count(count, spec)

    def _raise_wrong_count(self, count, spec):
        minend = plural_or_not(spec.minargs)
        if spec.minargs == spec.maxargs:
            expected = '%d argument%s' % (spec.minargs, minend)
        elif not (spec.varargs or spec.kwargs):
            expected = '%d to %d arguments' % (spec.minargs, spec.maxargs)
        else:
            expected = 'at least %d argument%s' % (spec.minargs, minend)
        raise DataError("%s '%s' expected %s, got %d."
                        % (spec.type, spec.name, expected, count))
