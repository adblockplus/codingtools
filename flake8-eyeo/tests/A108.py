def prefix(a, b):
    #                * A108
    return 'foo' + a + b


def infix(a, b):
    #                * A108
    return a + 'foo' + b


def suffix(a, b):
    #            * A108
    return a + b + 'foo'


def prefix_with_two_strings(other):
    return 'foo' + other


def suffix_with_two_strings(other):
    return other + 'foo'
