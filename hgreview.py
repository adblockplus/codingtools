import os
import re
import subprocess
import sys
import urllib

from mercurial import cmdutil, error

cmdtable = {}
command = cmdutil.command(cmdtable)

@command('review',
  [
    ('i', 'issue', '', 'If given, adds a patch set to this review, otherwise create a new one.', 'ISSUE'),
    ('r', 'revision', '', 'Revision to diff against or a revision range to upload.', 'REV'),
    ('c', 'change', '', 'A single revision to upload.', 'REV'),
    ('t', 'title', '', 'New review subject or new patch set title.', 'TITLE'),
    ('m', 'message', '', 'New review description or new patch set message.', 'MESSAGE'),
    ('w', 'reviewers', '', 'Add reviewers (comma separated email addresses or @adblockplus.org user names).', 'REVIEWERS'),
    ('', 'cc', '', 'Add CC (comma separated email addresses or @adblockplus.org user names).', 'CC'),
    ('', 'private', None, 'Make the review restricted to reviewers and those CCed.'),
    ('y', 'assume_yes', None, 'Assume that the answer to yes/no questions is \'yes\'.'),
    ('', 'print_diffs', None, 'Print full diffs.'),
  ], '[options] [path...]')
def review(ui, repo, *paths, **opts):
  '''
    Uploads a review to https://codereview.adblockplus.org/ or updates an
    existing review request. This will always send mails for new reviews, when
    updating a review mails will only be sent if a message is given.
  '''
  args = ['--oauth2']
  if ui.debugflag:
    args.append('--noisy')
  elif ui.verbose:
    args.append('--verbose')
  elif ui.quiet:
    args.append('--quiet')

  if opts.get('issue') or opts.get('message'):
    args.append('--send_mail')

  if opts.get('revision') and opts.get('change'):
    raise error.Abort('Ambiguous revision range, only one of --revision and --change can be specified.')
  if opts.get('change'):
    args.extend(['--rev', '{0}^:{0}'.format(opts['change'])])
  elif opts.get('revision'):
    args.extend(['--rev', opts['revision']])
  else:
    raise error.Abort('What should be reviewed? Either --revision or --change is required.')

  if not opts.get('title') and not opts.get('issue') and opts.get('change'):
    opts['title'] = repo[opts['change']].description()

  if not opts.get('issue') and not opts.get('reviewers'):
    raise error.Abort('Please specify --reviewers for your new review.')
  for opt in ('reviewers', 'cc'):
    if opts.get(opt):
      users = [u if '@' in u else u + '@adblockplus.org'
          for u in re.split(r'\s*,\s*', opts[opt])]
      opts[opt] = ','.join(users)

  for opt in ('issue', 'title', 'message', 'reviewers', 'cc'):
    if opts.get(opt, ''):
      args.extend(['--' + opt, opts[opt]])

  for opt in ('private', 'assume_yes', 'print_diffs'):
    if opts.get(opt, False):
      args.append('--' + opt)

  args.extend(paths)

  upload_path = ui.config('review', 'uploadtool_path',
      os.path.join('~', '.hgreview_upload.py'))
  upload_path = os.path.expanduser(upload_path)
  if not os.path.exists(upload_path):
    url = 'https://codereview.adblockplus.org/static/upload.py'
    ui.status('Downloading {0} to {1}.\n'.format(url, upload_path))
    urllib.urlretrieve(url, upload_path)

  subprocess.call([sys.executable, upload_path] + args)
