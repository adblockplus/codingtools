# A201
global a
a = 1


class Foo:
    global a
    # A201
    global a, b
    a = 2
    b = 3

    def foo(self):
        # A201
        global b, c
        b = 4


math = None
Class = None
func = None


def lazy_import():
    global math
    if math is None:
        import math
    return math


def lacy_class():
    global Class
    if Class is None:
        class Class:
            pass
    return Class


def lazy_function():
    global func
    if func is None:
        def func():
            pass
    return func
