# A109
'this doc string should use three double quotes'


class Foo:
    # A109
    "this doc string should use three quotes"

    def single(self):
        # A109
        '''this doc string should use double quotes'''

    def correct(self):
        """this doc string uses the right quotes"""
