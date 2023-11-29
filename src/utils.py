import codecs
from typing import Tuple
import numpy as np


CANVAS_WIDTH = 640
CANVAS_HEIGHT = 480
CIRCLE_SEGMENTS_NUM = 10
CIRCLE_RADIUS = 0.02


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


def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calculating the distance between two points using the Pythagorean Theorem.

    Parameters:
    - x1 (float): The x-coordinate of the first point.
    - y1 (float): The y-coordinate of the first point.
    - x2 (float): The x-coordinate of the second point.
    - y2 (float): The y-coordinate of the second point.

    Returns:
        float: The distance between two points.
    """
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def circle_centers(n: int) -> Tuple[float, float]:
    """
    Create a specified number of action buttons and return their coordinates.
    Ignore if the quantity is 1.

    Parameters:
    - n (int): The number of action button to create.

    Returns:
        Tuple[float, float]: The coordinate of the circle center of the action button.
    """
    if n == 1:
        return ()
    return ((0.7, 0.85), (0.8, 0.85)) if n == 2 else ((0.6, 0.85), (0.7, 0.85), (0.8, 0.85))


def circle_data(circle_center: Tuple[float, float]) -> np.ndarray:
    """
    Construct vertex data for an action button, typically in the form of a solid circle.

    Parameters:
    - circle_center (Tuple[float, float]): The coordinate of the circle center of the action button.

    Returns:
        np.ndarray: The vertex data.
    """
    vertices = []
    for i in range(CIRCLE_SEGMENTS_NUM + 1):
        angle = i * 2.0 * np.pi / CIRCLE_SEGMENTS_NUM
        x = CIRCLE_RADIUS * np.cos(angle) + circle_center[0]
        y = CIRCLE_RADIUS * np.sin(angle) + circle_center[1]
        vertices.extend([x, y])
    return np.array(vertices, dtype='f4')


def coord_convert(screen_x: float, screen_y: float) -> Tuple[float, float]:
    """
    Convert screen coordinates to normalized device coordinates.

    Parameters:
    - screen_x (float): The x-coordinate of the screen coordinates.
    - screen_y (float): The y-coordinate of the screen coordinates.

    Returns:
        Tuple[float, float]: The normalized device coordinates.
    """
    ndc_x = (2.0 * screen_x / CANVAS_WIDTH) - 1.0
    ndc_y = 1.0 - (2.0 * screen_y / CANVAS_HEIGHT)
    return (ndc_x, ndc_y)


def determine_circle_index(screen_x: float, screen_y: float, circle_centers: Tuple[float, float]) -> int:
    """
    Determine whether the given coordinates are within the action button.
    If so, return the index of the action button.

    Parameters:
    - screen_x (float): The x-coordinate of the screen coordinates.
    - screen_y (float): The y-coordinate of the screen coordinates.
    - circle_centers (Tuple[float, float]): The coordinates of the circle centers of the action buttons.

    Returns:
        int: The index of the action button.
    """
    if not circle_centers:
        return None
    ndc_x, ndc_y = coord_convert(screen_x, screen_y)
    for index, circle_center in enumerate(circle_centers):
        if distance(ndc_x, ndc_y, circle_center[0], circle_center[1]) <= CIRCLE_RADIUS:
            return index
    return None
