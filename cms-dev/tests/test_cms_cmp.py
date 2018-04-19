# This file is part of Adblock Plus <https://adblockplus.org/>,
# Copyright (C) 2017-present eyeo GmbH
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

import glob
import os
import subprocess
import sys

import pytest

CMSCMP = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cms_cmp.py')


def run_cms_cmp(*args, **kw):
    return subprocess.check_call([sys.executable, CMSCMP] + list(args), **kw)


def hg(*args, **kw):
    cmd = ['hg']
    if 'repo' in kw:
        cmd += ['-R', kw['repo']]
        del kw['repo']
    # Disable default options from local user config.
    cmd += ['--config', 'defaults.{}='.format(args[0])]
    return subprocess.check_call(cmd + list(args), **kw)


@pytest.fixture(scope='session')
def website(tmpdir_factory):
    root = tmpdir_factory.mktemp('website')
    root.join('foo').write('foo')
    hg('init', str(root))
    hg('commit', '-A', '-m', 'x', repo=str(root))
    return root


@pytest.fixture(scope='session')
def cms(tmpdir_factory):
    root = tmpdir_factory.mktemp('cms')
    generate = root.mkdir('cms').mkdir('bin').join('generate_static_pages.py')
    generate.write('\n'.join([
        'import sys, shutil',
        'shutil.copytree(sys.argv[1], sys.argv[2])',
    ]))
    hg('init', str(root))
    hg('commit', '-A', '-m', 'x', repo=str(root))
    root.join('foo').write('bar')
    hg('commit', '-A', '-m', 'y', repo=str(root))
    generate.write(
        generate.read() +
        '\nshutil.copy(sys.argv[2] + "/foo", sys.argv[2] + "/bar")',
    )
    hg('commit', '-m', 'z', repo=str(root))
    hg('bookmark', '-r', '0', 'master', repo=str(root))
    hg('bookmark', '-r', '1', 'yoda', repo=str(root))
    hg('bookmark', '-r', '2', 'other', repo=str(root))
    return root


def test_same_revision(website, cms, tmpdir):
    run_cms_cmp('-d', str(tmpdir), '-c', str(cms),
                '-b', 'master', '-t', 'yoda',
                str(website))


def test_different_revision(website, cms, tmpdir):
    with pytest.raises(subprocess.CalledProcessError):
        # Here the websites will be different, so the comparison will fail...
        run_cms_cmp('-d', str(tmpdir), '-c', str(cms),
                    '-b', 'master', '-t', 'other',
                    str(website))
    # ...but it will succeed if we ignore 'bar'.
    run_cms_cmp('-d', str(tmpdir), '-c', str(cms),
                '-b', 'master', '-t', 'other',
                '-i', 'bar',
                str(website))


def test_bad_python(website, cms, tmpdir):
    with pytest.raises(subprocess.CalledProcessError):
        # The run should fail with a broken python...
        run_cms_cmp('-d', str(tmpdir), '-c', str(cms),
                    '-t', 'yoda', '-p', 'foobar',
                    str(website))
    # ...but succeed with a good one.
    run_cms_cmp('-d', str(tmpdir), '-c', str(cms),
                '-t', 'yoda', '-p', sys.executable,
                str(website))


def test_remove_old(website, cms, tmpdir):
    run_cms_cmp('-d', str(tmpdir), '-c', str(cms), '-t', 'yoda',
                str(website))
    # Let's add a file to one of the output directories:
    d = glob.glob(os.path.join(str(tmpdir), 'website*'))[0]
    with open(os.path.join(d, 'baz'), 'w') as f:
        f.write('here')
    # Now the comparison will fail...
    with pytest.raises(subprocess.CalledProcessError):
        run_cms_cmp('-d', str(tmpdir), '-c', str(cms), '-t', 'yoda',
                    str(website))
    # ...but it will succeed if we tell it to delete old outputs.
    run_cms_cmp('-d', str(tmpdir), '-c', str(cms), '-t', 'yoda', '-r',
                str(website))


def test_working_copy(website, cms, tmpdir):
    with pytest.raises(subprocess.CalledProcessError):
        # This will fail because current version is 'other'.
        run_cms_cmp('-d', str(tmpdir), '-c', str(cms), str(website))
    generate = cms.join('cms').join('bin').join('generate_static_pages.py')
    # Remove last line that breaks stuff.
    generate.write('\n'.join(generate.read().splitlines()[:-1]))
    # Now it should be better.
    run_cms_cmp('-d', str(tmpdir), '-c', str(cms), str(website))
