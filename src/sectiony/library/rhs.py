import math
from ..geometry import Shape, Geometry
from ..section import Section
from .utils import arc

def rhs(b: float, h: float, t: float, r: float, n: int = 4) -> Section:
    """
    Rectangular Hollow Section
    
    Args:
        b: Width (z-direction)
        h: Height (y-direction)
        t: Wall thickness
        r: Outer corner radius
        n: Number of segments for corner radius
    """
    if t >= b/2 or t >= h/2:
         raise ValueError("Thickness too large for dimensions")
         
    # Coordinate system: (y, z)
    # Centers of outer corners
    # Quadrant 1: Top-Right (+y, +z)
    cy = h/2 - r
    cz = b/2 - r
    
    # Outer Points (CCW)
    outer_points = []
    
    # Top-Right Corner (0 to 90 deg)
    # Start at Right edge (0 deg), go to Top edge (90 deg)
    outer_points.extend(arc(cy, cz, r, 0, math.pi/2, n))
    
    # Top-Left Corner (90 to 180)
    # Center: (+y, -z)
    outer_points.extend(arc(cy, -cz, r, math.pi/2, math.pi, n))
    
    # Bottom-Left Corner (180 to 270)
    # Center: (-y, -z)
    outer_points.extend(arc(-cy, -cz, r, math.pi, 3*math.pi/2, n))
    
    # Bottom-Right Corner (270 to 360)
    # Center: (-y, +z)
    outer_points.extend(arc(-cy, cz, r, 3*math.pi/2, 2*math.pi, n))
    
    # Inner Points
    r_inner = max(0.0, r - t)
    cy_in = h/2 - t - r_inner
    cz_in = b/2 - t - r_inner
    
    inner_points = []
    inner_points.extend(arc(cy_in, cz_in, r_inner, 0, math.pi/2, n))
    inner_points.extend(arc(cy_in, -cz_in, r_inner, math.pi/2, math.pi, n))
    inner_points.extend(arc(-cy_in, -cz_in, r_inner, math.pi, 3*math.pi/2, n))
    inner_points.extend(arc(-cy_in, cz_in, r_inner, 3*math.pi/2, 2*math.pi, n))

    geom = Geometry(shapes=[
        Shape(points=outer_points, hollow=False),
        Shape(points=inner_points, hollow=True)
    ])
    
    return Section(name=f"RHS {b}x{h}x{t}", geometry=geom)
