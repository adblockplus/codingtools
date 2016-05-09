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
