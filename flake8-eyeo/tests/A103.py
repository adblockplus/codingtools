def compare_int_like_yoda(x):
    #      * A103
    return 1 == x


def compare_string_like_yoda(x):
    #      * A103
    return 'foo' == x


def compare_none_like_yoda(x):
    #      * A103
    return None is x


def compare_tuple_like_yoda(x):
    #       * A103
    return (1, 'foo') == x


def compare_literals():
    return (1, 'foo') == (2, 'bar')


def compare_variables(a, b, c, d):
    return (a, b) == (c, d) or a == b


def compare_builtin(x):
    return dir == x
