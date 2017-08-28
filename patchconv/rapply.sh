#!/bin/sh
#
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

set -eu

if [ $# -lt 1 ]; then
    echo "usage: rapply.sh PATCH"
    exit 1
fi

if git st >/dev/null 2>&1; then
    IMPORT="git apply"
elif hg st >/dev/null 2>&1; then
    IMPORT="hg import --no-commit -"
else
    echo "No repository found in `pwd`"
    exit 2
fi

BASEDIR=$(dirname "$0")
if [ -f "$BASEDIR/patchconv.py" ]; then
    alias patchconv="$BASEDIR/patchconv.py"
fi

if [ -f "$1" ]; then
    patchconv < "$1" | $IMPORT
else
    curl "$1" | patchconv | $IMPORT
fi
