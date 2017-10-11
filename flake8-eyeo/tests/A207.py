x = object()


def make_dict():
    return {
        'foo': None,
        'bar': None,
        0: None,
        1: None,
        x: None,

        # A207
        'foo': None,
        # A207
        ['bar' + ' '][0].strip(): None,
        # A207
        0.0: None,
        # A207
        True: None,
        # A207
        x: None,
        # A207
        str('foo'): None,
    }


def make_set():
    return {
        'foo',
        'bar',
        0,
        1,
        x,

        # A207
        'foo',
        # A207
        ['bar' + ' '][0].strip(),
        # A207
        0.0,
        # A207
        True,
        # A207
        x,
        # A207
        str('foo'),
    }
