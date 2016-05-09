# A109
'this doc string should use three double quotes'


class Foo:
    # A109
    "this doc string should use three quotes"

    def single(self):
        # A109
        '''this doc string should use double quotes'''

    def unicode(self):
        # A109
        u"""this doc string must not be marked as unicode string"""

    def raw(self):
        # A109
        r"""this doc string must not be marked as raw string"""

    def correct(self):
        """this doc string uses the right quotes"""
