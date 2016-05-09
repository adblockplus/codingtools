#         * A101
for i in (0, 1):
    pass

#        * A101
for i in {0, 1}:
    pass


def make_list():
    #                   * A101
    return [i for i in (0, 1)]


def make_generator():
    #                  * A101
    return (i for i in {0, 1})
