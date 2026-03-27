from ..geometry import Geometry, Contour
from ..section import Section
from .rhs import _rounded_rect_segments


def solid_rect(b: float, h: float) -> Section:
    """
    Solid rectangular section centered at origin.

    Args:
        b: Width (x-direction)
        h: Height (y-direction)
    """
    segments = _rounded_rect_segments(h, b, 0.0)
    contour = Contour(segments=segments, hollow=False)
    geom = Geometry(contours=[contour])
    return Section(
        name=f"Rect {b}x{h}",
        geometry=geom,
        dimensions={"b": b, "h": h},
    )
