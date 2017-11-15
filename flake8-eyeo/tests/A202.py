def noop():
    pass


def dead_code_after_return():
    return
    # A202
    noop()


def dead_code_after_raise():
    raise Exception()
    # A202
    noop()


def dead_code_after_return_in_try():
    try:
        return
        # A202
        noop()
    except Exception:
        return
        # A202
        noop()
    finally:
        return
        # A202
        noop()


for i in range(10):
    if i == 0:
        continue
        # A202
        noop()

    if i == 1:
        break
        # A202
        noop()
