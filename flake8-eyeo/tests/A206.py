def noop():
    pass


def else_after_return():
    if True:
        return
    else:
        # A206
        noop()


def else_after_raise():
    if True:
        raise Exception()
    else:
        # A206
        noop()


def else_after_return_in_except():
    try:
        noop()
    except Exception:
        return
    else:
        # A206
        noop()


for i in range(10):
    if i == 0:
        continue
    else:
        # A206
        noop()

    if i == 1:
        break
    else:
        # A206
        noop()
