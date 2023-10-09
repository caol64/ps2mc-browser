import codecs


def zero_terminate(s):
    """Truncate a string at the first NUL ('\0') character, if any."""

    i = s.find(b'\0')
    if i == -1:
        return s
    return s[:i]


def decode_name(byte_array):
    return byte_array.decode('ascii')


def decode_sjis(s):
    try:
        return codecs.decode(s, 'shift-jis', 'replace').replace(u'\u3000', ' ')
    except Exception as ex:
        print(ex)
        return u'\uFFFD' * 3
