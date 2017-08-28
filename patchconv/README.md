# Convert Rietveld patches to apply them locally

The `patchconv` module and `patchconv` script convert SVN-style patches that
are downloaded from [Rietveld](https://github.com/rietveld-codereview/rietveld)
code reviews to Git-style patches that can be used as input for `hg import` or
`git apply`.

In many cases the patches from the review can be applied directly with
`patch -p1`. However, if the changes contain copies or renames or include
binary files, `patch` will not apply them correctly. Git and Mercurial commands
will also not work because when the changes are uploaded to the review, they
are converted to SVN-like format that Rietveld normally works with. `patchconv`
undoes this conversion and returns the patch to the state where it can be
applied using Git or Mercurial.

## Installation

Install directly from Mercurial repository using pip:

    $ pip install 'hg+https://hg.adblockplus.org/codingtools#egg=patchconv&subdirectory=patchconv'

## Usage

The script in the package will be available immediately after the installation.
Its interface is simple: it reads from stdin and writes to stdout.

    $ patchconv <patch-from-rietveld.diff >git-patch.diff

For additional convenience you can use the provided `rapply.sh` script that
downloads, converts and applies patches from Rietveld reviews to your local
working copy. In order to use it, open a review, copy the URL of a `[raw]`
download link in the top right corner of a patch set overview and then paste it
into the console:

    $ rapply.sh https://codereview.adblockplus.org/download/issue3322_4433.diff

or, if you've already downloaded the diff to a local file:

    $ rapply.sh issue3322_4433.diff

In both cases you need to be in the directory containing the repository to
which you are applying the diff.

## Testing

The tests can be run via [Tox](http://tox.readthedocs.org/)
