# This file is part of Adblock Plus <https://adblockplus.org/>,
# Copyright (C) 2006-present eyeo GmbH
#
# Adblock Plus is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Adblock Plus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Adblock Plus.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

import os
import glob
import tokenize
import sys
import re
import subprocess

from setuptools import setup, Command


class TestCommand(Command):
    user_options = []

    def _get_expected_errors(self, filename):
        errors = set()

        def tokeneater(kind, token, start, end, line):
            if kind == tokenize.COMMENT:
                match = re.search(r'^#+[*\s]*(A\d+)', token)
                if match:
                    try:
                        offset = token.index('*')
                    except ValueError:
                        offset = 0
                    errors.add((start[0] + 1,
                                start[1] + 1 + offset,
                                match.group(1)))

        with open(filename, 'rb') as file:
            if sys.version_info[0] >= 3:
                for token in tokenize.tokenize(file.readline):
                    tokeneater(*token)
            else:
                tokenize.tokenize(file.readline, tokeneater)

        return errors

    def _get_reported_errors(self, filename):
        output = subprocess.Popen(['flake8', filename],
                                  stdout=subprocess.PIPE).communicate()[0]

        errors = set()
        for line in output.decode('utf-8').splitlines():
            _, lineno, colno, error = line.split(':', 3)
            errors.add((int(lineno), int(colno), error.split()[0]))

        return errors

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        directory = os.path.dirname(__file__)
        filenames = glob.glob(os.path.join(directory, 'tests', '*.py'))
        failed = False

        for filename in sorted(filenames):
            expected = self._get_expected_errors(filename)
            reported = self._get_reported_errors(filename)
            failures = expected ^ reported

            if not failures:
                print(filename + ': OK')
                continue

            for record in sorted(failures):
                lineno, colno, error = record

                print('{}:{}:{}: '.format(filename, lineno, colno), end='')
                if record in expected:
                    print(error + ' expected')
                else:
                    print('unexpected ' + error)

            failed = True

        if failed:
            sys.exit(1)


setup(
    name='flake8-eyeo',
    version='0.1',
    py_modules=['flake8_eyeo'],
    install_requires=['flake8>=3.2.1'],
    entry_points={
        'flake8.extension': [
            'A    = flake8_eyeo:check_ast',
            'A1   = flake8_eyeo:check_quotes',
            'A111 = flake8_eyeo:check_redundant_parenthesis',
            'A303 = flake8_eyeo:check_non_default_encoding',
        ],
    },
    cmdclass={'test': TestCommand}
)
