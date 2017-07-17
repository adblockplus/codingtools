# update-copyright

This script will attempt to update the eyeo copyright information on each
page of each repo listed on a Mercurial index page.
By default, running the script will scrape [https://hg.adblockplus.org/](https://hg.adblockplus.org/),
and then for each repo, it will:
* make a local copy of the repo
* update the copyright information on each file to the current year
* attempt to push the updates to `ssh://hg@hg.adblockplus.org/`

If a user doesn't have permission to push to a repo, the script will make a
local `repo-name.patch` file to submit later. 

You are free to use this for other projects but please keep in mind that we
make no stability guarantees whatsoever and might change functionality any
time.

## How to use

To update the copyright on all the repos indexed at [https://hg.adblockplus.org/](https://hg.adblockplus.org/),
simply run the script, e.g.:

    ./update_copyright.py

To run the script elsewhere, you must specify the URL for a Mercurial index
site to scrape, and the location of the base URL to push to, e.g.:

    ./update_copyright.py -u https://hg.example.com/ -p ssh://user@hg.example.com/

## Testing

Testing can be run via [tox](http://tox.readthedocs.org/).
