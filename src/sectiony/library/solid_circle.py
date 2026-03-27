import math
from ..geometry import Geometry, Contour, Arc
from ..section import Section


def solid_circle(d: float) -> Section:
    """
    Solid circular section centered at origin.

    Args:
        d: Diameter
    """
    R = d / 2.0
    contour = Contour(
        segments=[Arc(center=(0, 0), radius=R, start_angle=0.0, end_angle=2 * math.pi)],
        hollow=False,
    )
    geom = Geometry(contours=[contour])
    return Section(
        name=f"Circle d={d}",
        geometry=geom,
        dimensions={"d": d},
    )
