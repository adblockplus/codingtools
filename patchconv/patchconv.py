#!/usr/bin/env python

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

import sys

# States of the conversion state machine.
NORMAL, INDEX, METAINFO = range(3)
# Double line that SVN uses to separate file name from patch content.
SVN_SEPARATOR = '=' * 67
# Template for the line from Git diff which is replaced during SVN
# conversion.
GIT_PART_HEAD = 'diff --git a/{} b/{}\n'


def rietveld_to_git(lines):
    """Convert patch from Rietveld format to Git format.

    Rietveld format looks similar to SVN patch format but it can also
    contain Git extensions if it was produced by `upload.py` run from
    a project managed by Git or Mercurial. The output format is the
    original Git patch as produced by `git diff` or `hg diff --git`.
    It can be applied by `hg import` or `git apply`.

    Arguments:
        lines -- lines of the patch.
    Returns:
        Lines of the converted patch.

    """
    state = NORMAL
    new_name = None

    for line in lines:
        if state is NORMAL:
            if line.startswith('Index: '):
                new_name = line[7:].strip('\n')
                state = INDEX
            else:
                yield line
        elif state is INDEX:
            if line.startswith(SVN_SEPARATOR):
                state = METAINFO
            else:
                yield 'Index: {}\n'.format(new_name)
                yield line
                state = NORMAL
        elif state is METAINFO:
            if line.startswith('rename from '):
                # File renamed.
                old_name = line[12:].strip('\n')
                yield GIT_PART_HEAD.format(old_name, new_name)
            elif line.startswith('copy from '):
                # File copied.
                old_name = line[10:].strip('\n')
                yield GIT_PART_HEAD.format(old_name, new_name)
            else:
                # File added or removed or changed.
                yield GIT_PART_HEAD.format(new_name, new_name)
            yield line
            state = NORMAL


def main():
    for line in rietveld_to_git(sys.stdin):
        sys.stdout.write(line)


if __name__ == '__main__':
    main()
