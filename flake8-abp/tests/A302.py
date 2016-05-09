#       * A302
def foo(type):
    # A302
    from io import open
    file = open(__file__)

    # A302
    id = 0

    return (file, id)


try:
    unichr
except NameError:
    unichr = chr


class Foo:
    id = 0

    def type(self):
        pass
