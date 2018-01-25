def redundant_parenthesis(x, y, z):
    #     * A111
    while (x):
        #  * A111
        if ((x or y) and z):
            pass
        #    * A111
        elif (x == max(y, z)):
            pass
        else:
            return

    #   * A111
    for (a, b, c) in y:
        #        * A111
        result = (a + b + c)
        #                * A111
        return result or ('foo')

    # A111
    (a, b, c) = x
    del a, b, c


def mandatory_parenthesis(x, y, z):
    if ():
        return
    if (x, y, z):
        return

    if (x or y) and z:
        return
    if x and (y or z):
        return

    if (x or
            y):
        return


def acceptable_parenthesis(x, y, z):
    a = (x == y)
    b = (x or y == z)
    c = (x + y) / z
    d = (x and y) or z
    return (a, b, c, d)
