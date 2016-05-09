# A105
list([1])
# A105
list((1,))
# A105
tuple([1])
# A105
tuple((1,))
# A105
set([1])
# A105
set((1,))
# A105
dict([])
# A105
dict([[1, 1]])
# A105
dict([(1, 1)])
# A105
dict(())
# A105
dict(((1, 1),))
# A105
dict(([1, 1],))

# A105
list([x for x in range(10)])
# A105
list(x for x in range(10))
# A105
set([x for x in range(10)])
# A105
set(x for x in range(10))
# A105
dict([(x, x) for x in range(10)])
# A105
dict([[x, x] for x in range(10)])
# A105
dict((x, x) for x in range(10))
# A105
dict([x, x] for x in range(10))


def make_dict(x):
    dict(x)
    dict([x])
    dict((x,))
    dict([pair for pair in x])
    dict(pair for pair in x)


def make_unique(x):
    tuple({y for y in x})
    list({y for y in x})


tuple([x for x in range(10)])
tuple(x for x in range(10))
tuple({x for x in range(10)})
