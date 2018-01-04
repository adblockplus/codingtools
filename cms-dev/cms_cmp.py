#!/bin/env python
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

"""Test CMS by comparing the output of its different revisions."""

from __future__ import print_function, unicode_literals

import argparse
import difflib
import filecmp
import io
import os
import shutil
import subprocess
import sys

# Path to static generation script.
GENERATE_PATH = 'cms/bin/generate_static_pages.py'

# Fake revision that indicates "use current working copy".
WORKING_COPY = '[working-copy]'


def run_cmd(*cmd, **kw):
    """Run a command, print and return its output."""
    silent = kw.get('silent', False)
    if 'silent' in kw:
        del kw['silent']
    if not silent:
        print('$', *cmd)
    try:
        output = subprocess.check_output(cmd, **kw).decode('utf-8')
    except subprocess.CalledProcessError:
        sys.exit('Command invocation failed: {}'.format(' '.join(cmd)))
    if not silent:
        for line in output.splitlines():
            print('>', line)
    return output


def hg(*args, **kw):
    """Run Mercurial and return its output."""
    cmd = ['hg']
    if 'repo' in kw:
        cmd += ['-R', kw['repo']]
        del kw['repo']
    # Disable default options from local user config.
    cmd += ['--config', 'defaults.{}='.format(args[0])]
    return run_cmd(*(cmd + list(args)), **kw)


def get_current_rev(repo):
    """Get the revision ids of the working copy in repository."""
    return hg('id', repo=repo, silent=True).split()


def read_file(path):
    """Read file, return list of strings."""
    with io.open(path, encoding='utf-8') as f:
        return f.read().splitlines()


def print_diff(one, two):
    """Print unified diff between two files."""
    for line in difflib.unified_diff(read_file(one), read_file(two),
                                     fromfile=one, tofile=two):
        print(line)


def compare_dirs(one, two, ignore=[]):
    """Compare two directories, return True if same, False if not."""
    def recursive_compare(c):
        if c.left_only:
            print('The following file(s)/dir(s) are only in base', c.left)
            for f in c.left_only:
                print('-', f)
            return False
        if c.right_only:
            print('The following file(s)/dir(s) are only in test', c.right)
            for f in c.right_only:
                print('-', f)
            return False
        if c.diff_files:
            print('The following file(s) are different between', c.left,
                  'and', c.right)
            for f in c.diff_files:
                print('-', f)
                base = os.path.join(c.left, f)
                test = os.path.join(c.right, f)
                print_diff(base, test)
            return False
        return all(recursive_compare(sub) for sub in c.subdirs.values())

    print('Comparing', one, 'and', two)
    comparator = filecmp.dircmp(one, two, ignore=ignore)
    return recursive_compare(comparator)


class Tester(object):
    """Test runner.

    Generates one or more websites with two different versions of CMS and
    compares the results.
    """

    def __init__(self, website_paths, cms_repo, dest, ignore=[],
                 python=sys.executable, remove_old=False,
                 base_rev='master', test_rev=WORKING_COPY):
        """Create test runner.

        Parameters
        ----------
        website_paths : list of strings
            Paths of the website source folders that are used for comparisons.
        cms_repo : str
            Path to CMS repository.
        dest : str
            Directory into which CMS outputs will be placed.
        ignore : list of strings
            List of file names to ignore in output comparision.
        python : str
            Path to the python interpeter.
        remove_old : bool
            Remove results of earlier runs of this script? Setting this to
            `True` will make things slower but will ensure correctness.
        base_rev : str
            Revision of CMS to use as a baseline.
        test_rev : str
            Revision of CMS to use for testing.

        """
        self.website_paths = website_paths
        self.cms_repo = cms_repo
        self.dest = dest
        self.ignore = ignore
        self.python = python
        self.remove_old = remove_old
        self.base_rev = base_rev
        self.test_rev = test_rev

    def clone_cms(self):
        """Clone CMS repository for to use for tests."""
        self.cms_clone = os.path.join(self.dest, 'cms-cmp.cms-clone')
        print('Cloning CMS to', self.cms_clone)
        if os.path.exists(self.cms_clone):
            shutil.rmtree(self.cms_clone)
        hg('clone', self.cms_repo, self.cms_clone)

    def cms_checkout(self, rev):
        """Checkout specified revision of CMS.

        Returns revision hash (or working copy marker) and path to where it is.
        """
        if rev is WORKING_COPY:
            print('Using CMS working copy')
            return WORKING_COPY, self.cms_repo
        print('Switching CMS to revision:', rev)
        hg('co', rev, repo=self.cms_clone)
        return get_current_rev(self.cms_clone)[0], self.cms_clone

    def generate(self, cms_rev, website_path):
        """Generate the website using specified revision of CMS."""
        name = os.path.basename(website_path)
        website_rev = get_current_rev(website_path)[0]
        cms_rev, cms_path = self.cms_checkout(cms_rev)
        print('Generating', website_path, 'with CMS revision:', cms_rev)
        unique_id = '{}-rev-{}-cms-{}'.format(name, website_rev, cms_rev)
        dst = os.path.join(self.dest, unique_id)
        if os.path.exists(dst):
            if self.remove_old or cms_rev == WORKING_COPY:
                shutil.rmtree(dst)
            else:
                print(dst, 'exists, assuming it was generated earlier')
                return dst
        env = dict(os.environ)
        env['PYTHONPATH'] = cms_path
        generate = os.path.join(cms_path, GENERATE_PATH)
        run_cmd(self.python, generate, website_path, dst, env=env)
        return dst

    def run(self):
        """Run the comparison."""
        if not os.path.exists(os.path.join(self.cms_repo, GENERATE_PATH)):
            sys.exit('No cms source found in ' + self.cms_repo)
        print('Using CMS repository at', self.cms_repo)
        self.clone_cms()
        for website_path in self.website_paths:
            base = self.generate(self.base_rev, website_path)
            test = self.generate(self.test_rev, website_path)
            if not compare_dirs(base, test, ignore=self.ignore):
                print('Differences found for', website_path)
                sys.exit(1)


def configure():
    """Configure the script from arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('website_paths', metavar='WEBSITE', nargs='+',
                        help='path of website source to use for comparison')
    parser.add_argument('-b', '--base-rev', metavar='REVISION',
                        default='master',
                        help='base revision of CMS to use as baseline')
    parser.add_argument('-c', '--cms-repo', metavar='CMS_REPO',
                        default=os.getcwd(),
                        help='Location of CMS repository')
    parser.add_argument('-d', '--dest', metavar='OUT_DIR',
                        default=os.environ.get('TMPDIR', '/tmp'),
                        help='directory for storing CMS output')
    parser.add_argument('-i', '--ignore', metavar='FILENAME', action='append',
                        default=[],
                        help='file names to ignore in output comparison')
    parser.add_argument('-p', '--python', metavar='PYTHON_EXE',
                        default=sys.executable,
                        help='python interpreter to run CMS')
    parser.add_argument('-r', '--remove-old', action='store_true',
                        help='remove previously generated CMS outputs instead'
                             'of reusing them')
    parser.add_argument('-t', '--test-rev', metavar='REVISION',
                        default=WORKING_COPY,
                        help='revision of CMS to use for testing (by default '
                             'currently checked out working copy including '
                             'uncommited changes will be used)')
    return parser.parse_args()


def main():
    """Parse command line arguments and run the tests.

    Main entry point for the script.
    """
    config = configure()
    tester = Tester(**config.__dict__)
    tester.run()


if __name__ == '__main__':
    main()
