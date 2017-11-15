def noop():
    pass


def superfluos_pass():
    noop()
    # A204
    pass


def multiple_pass():
    pass
    # A204
    pass


class SuperfluosPass:
    noop()
    # A204
    pass


class MultiplePass:
    pass
    # A204
    pass


if True:
    noop()
    # A204
    pass
else:
    noop()
    # A204
    pass

for i in range(10):
    noop()
    # A204
    pass
else:
    noop()
    # A204
    pass

while True:
    noop()
    # A204
    pass
else:
    noop()
    # A204
    pass

try:
    noop()
    # A204
    pass
except Exception:
    noop()
    # A204
    pass
finally:
    noop()
    # A204
    pass
