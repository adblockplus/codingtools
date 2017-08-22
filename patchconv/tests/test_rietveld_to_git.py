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

from __future__ import print_function, unicode_literals

import os
import subprocess
try:
    from StringIO import StringIO
except:
    from io import StringIO

import mock
import pytest

import patchconv

TEST_DIR = os.path.dirname(__file__)


def get_test_cases():
    for filename in os.listdir(TEST_DIR):
        if filename.endswith('.txt'):
            yield filename


@pytest.fixture(params=list(get_test_cases()))
def patch_data(request):
    data = {'input': [], 'expect': []}
    current = []
    with open(os.path.join(TEST_DIR, request.param)) as file:
        for line in file:
            print(line, end='')
            if line.startswith('INPUT'):
                current = data['input']
            elif line.startswith('EXPECT'):
                current = data['expect']
            elif not line.startswith('#'):
                if line.startswith('    '):
                    current.append(line[4:])
                else:
                    current.append('')
    return data


def test_convert(patch_data):
    got = list(patchconv.rietveld_to_git(patch_data['input']))
    print('GOT')
    for line in got:
        print('    ' + line, end='')
    assert got == patch_data['expect']


def test_script():
    process = subprocess.Popen(
        ['patchconv'], stdin=subprocess.PIPE, stdout=subprocess.PIPE
    )
    in_patch = '''Index: README.txt
===================================================================
--- a/README.txt
'''
    expect = '''diff --git a/README.txt b/README.txt
--- a/README.txt
'''
    out, err = process.communicate(input=in_patch.encode('ascii'))
    assert out == expect.encode('ascii')

    stdin = StringIO(in_patch)
    stdout = StringIO()
    with mock.patch('sys.stdin', stdin), mock.patch('sys.stdout', stdout):
        patchconv.main()
    assert stdout.getvalue() == expect
