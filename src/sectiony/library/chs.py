import math
from ..geometry import Shape, Geometry, Contour, Arc
from ..section import Section


def chs(d: float, t: float) -> Section:
    """
    Circular Hollow Section with native curve geometry.
    
    Args:
        d: Outer diameter
        t: Wall thickness
    """
    R = d / 2.0
    r_inner = R - t
    
    if r_inner < 0:
        raise ValueError("Thickness cannot be greater than radius")

    # Outer circle: single arc from 0 to 2*pi
    # Center at origin (0, 0)
    outer_contour = Contour(
        segments=[Arc(center=(0, 0), radius=R, start_angle=0, end_angle=2*math.pi)],
        hollow=False
    )
    
    # Inner circle (hollow)
    inner_contour = Contour(
        segments=[Arc(center=(0, 0), radius=r_inner, start_angle=0, end_angle=2*math.pi)],
        hollow=True
    )
    
    geom = Geometry(contours=[outer_contour, inner_contour])
    
    return Section(name=f"CHS {d}x{t}", geometry=geom)
