import codecs


def zero_terminate(s: str) -> str:
    """
    Truncate a string at the first NUL ('\0') character, if any.
    """
    i = s.find(b"\0")
    if i == -1:
        return s
    return s[:i]


def decode_name(byte_array: bytes) -> str:
    """Decode bytes to a string."""
    return byte_array.decode("ascii")


def decode_sjis(s: bytes) -> str:
    """Decode bytes to a string using the Shift-JIS encoding."""
    try:
        return codecs.decode(s, "shift-jis", "replace").replace("\u3000", " ")
    except Exception as ex:
        print(ex)
        return "\uFFFD" * 3

def zeros(shape: tuple):
    if len(shape) == 1:
        return [0.0 for _ in range(shape[0])]
    return [zeros(shape[1:]) for _ in range(shape[0])]
