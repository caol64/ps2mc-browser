import codecs
import numpy as np


CANVAS_WIDTH = 640
CANVAS_HEIGHT = 480
CIRCLE_SEGMENTS_NUM = 10
CIRCLE_RADIUS = 0.02


def zero_terminate(s):
    """Truncate a string at the first NUL ('\0') character, if any."""

    i = s.find(b"\0")
    if i == -1:
        return s
    return s[:i]


def decode_name(byte_array):
    return byte_array.decode("ascii")


def decode_sjis(s):
    try:
        return codecs.decode(s, "shift-jis", "replace").replace("\u3000", " ")
    except Exception as ex:
        print(ex)
        return "\uFFFD" * 3


def distance(x1, y1, x2, y2):
    """
    Calculating the distance between two points using the Pythagorean Theorem.
    """
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def circle_centers(n):
    """
    Create a specified number of circle centers and return their coordinates.
    Ignore if the quantity is 1.
    """
    if n == 1:
        return []
    return ((0.7, 0.85), (0.8, 0.85)) if n == 2 else ((0.6, 0.85), (0.7, 0.85), (0.8, 0.85))


def circle_data(circle_center):
    """
    Construct vertex data that forms a circle based on the center coordinates and radius of the circle.
    """
    vertices = []
    for i in range(CIRCLE_SEGMENTS_NUM + 1):
        angle = i * 2.0 * np.pi / CIRCLE_SEGMENTS_NUM
        x = CIRCLE_RADIUS * np.cos(angle) + circle_center[0]
        y = CIRCLE_RADIUS * np.sin(angle) + circle_center[1]
        vertices.extend([x, y])
    return np.array(vertices, dtype='f4')


def coord_convert(screen_x, screen_y):
    """
    Convert screen coordinates to normalized device coordinates.
    """
    ndc_x = (2.0 * screen_x / CANVAS_WIDTH) - 1.0
    ndc_y = 1.0 - (2.0 * screen_y / CANVAS_HEIGHT)
    return (ndc_x, ndc_y)


def determine_circle_index(screen_x, screen_y, circle_centers):
    """
    Determine whether the given coordinates are within the radius coverage of a circle.
    If so, return the index of the circle.
    """
    if not circle_centers:
        return None
    ndc_x, ndc_y = coord_convert(screen_x, screen_y)
    for index, circle_center in enumerate(circle_centers):
        if distance(ndc_x, ndc_y, circle_center[0], circle_center[1]) <= CIRCLE_RADIUS:
            return index
    return None
