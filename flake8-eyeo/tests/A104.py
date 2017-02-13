import itertools
from itertools import imap, ifilter

# A104
map(lambda x: x, range(10))
# A104
filter(lambda x: x, range(10))
# A104
imap(lambda x: x, range(10))
# A104
ifilter(lambda x: x, range(10))
# A104
itertools.imap(lambda x: x, range(10))
# A104
itertools.ifilter(lambda x: x, range(10))

map(lambda a, b: a or b, [0, 1], [2, 3])
