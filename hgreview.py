import BaseHTTPServer
import os
import re
import socket
import sys
import urllib

from mercurial import cmdutil, error

SERVER = 'https://codereview.adblockplus.org'
UPLOADTOOL_URL = SERVER + '/static/upload.py'

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
             ('', 'no_mail', None, 'Don\'t send an email after uploading.'),
         ], '[options] [path...]')
def review(ui, repo, *paths, **opts):
    '''
      Uploads a review to https://codereview.adblockplus.org/ or updates an
      existing review request. This will always send mails for new reviews, when
      updating a review mails will only be sent if a message is given.
    '''
    args = ['--oauth2', '--server', SERVER]
    if ui.debugflag:
        args.append('--noisy')
    elif ui.verbose:
        args.append('--verbose')
    elif ui.quiet:
        args.append('--quiet')

    if (not opts.get('no_mail') and
        (not opts.get('issue') or opts.get('message'))):
        args.append('--send_mail')

    if opts.get('revision') and opts.get('change'):
        raise error.Abort('Ambiguous revision range, only one of --revision and --change can be specified.')
    if opts.get('change'):
        rev = repo[opts['change']]
        args.extend(['--rev', '{}:{}'.format(rev.parents()[0], rev)])
    elif opts.get('revision'):
        args.extend(['--rev', opts['revision']])
    else:
        raise error.Abort('What should be reviewed? Either --revision or --change is required.')

    if not opts.get('issue'):
        # New issue, make sure title and message are set
        fulltitle = None

        if not opts.get('title') and not opts.get('change'):
            opts['title'] = ui.prompt('New review title: ', '')
        elif not opts.get('title'):
            fulltitle = repo[opts['change']].description()
            opts['title'] = fulltitle.rstrip().split('\n')[0]

        if not opts['title'].strip():
            raise error.Abort('No review title given.')

        if not opts.get('message'):
            opts['message'] = fulltitle or opts['title']

        path = (ui.config('paths', 'default-push')
                or ui.config('paths', 'default')
                or '')
        match = re.search(r'^(?:https://|ssh://hg@)(.*)', path)
        if match:
            opts['base_url'] = 'https://' + match.group(1)

        # Make sure there is at least one reviewer
        if not opts.get('reviewers'):
            if opts.get('no_mail'):
                ui.status('No reviewers specified, edit the review to add '
                          'some.\n')
            else:
                opts['reviewers'] = ui.prompt('Reviewers (comma-separated): ',
                                              '')
                if not opts['reviewers'].strip():
                    raise error.Abort('No reviewers given.')

    for opt in ('reviewers', 'cc'):
        if opts.get(opt):
            users = [u if '@' in u else u + '@adblockplus.org'
                     for u in re.split(r'\s*,\s*', opts[opt])]
            opts[opt] = ','.join(users)

    for opt in ('issue', 'title', 'message', 'reviewers', 'cc', 'base_url'):
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
        ui.status('Downloading {0} to {1}.\n'.format(UPLOADTOOL_URL, upload_path))
        urllib.urlretrieve(UPLOADTOOL_URL, upload_path)

    # Find an available port for our local server
    issue = None

    class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/javascript')
            self.end_headers()
            self.wfile.write('location.href = "{0}";'.format(SERVER + '/' + issue))

        def log_message(*args, **kwargs):
            pass
    for port in range(54770, 54780):
        try:
            server = BaseHTTPServer.HTTPServer(('localhost', port), RequestHandler)
            break
        except socket.error:
            pass

    # Modify upload tool's auth response in order to redirect to the issue
    scope = {}
    execfile(upload_path, scope)
    if server:
        scope['AUTH_HANDLER_RESPONSE'] = '''\
<html>
  <head>
    <title>Authentication Status</title>
    <script>
    window.onload = function()
    {
      setInterval(function()
      {
        var script = document.createElement("script");
        script.src = "http://localhost:%s/?" + (new Date().getTime());
        document.body.appendChild(script);
      }, 1000)
    }
    </script>
  </head>
  <body>
    <p>
      The authentication flow has completed. This page will redirect to your
      review shortly.
    </p>
  </body>
</html>
''' % port

    # Run the upload tool
    issue, patchset = scope['RealMain']([upload_path] + args)

    # Wait for the page to check in and retrieve issue URL
    if server:
        server.handle_request()
