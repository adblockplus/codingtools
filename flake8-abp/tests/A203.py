def noop():
    pass


def foo():
    """This is a doc string"""
    # A203
    'this string is unused'
    noop()


def bar():
    # A203
    42
    # A203
    noop() is None
