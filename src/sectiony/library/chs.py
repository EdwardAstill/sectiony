import math
from ..geometry import Shape, Geometry
from ..section import Section

def chs(d: float, t: float, n: int = 64) -> Section:
    """
    Circular Hollow Section
    
    Args:
        d: Outer diameter
        t: Wall thickness
        n: Number of points for the circle
    """
    R = d / 2.0
    r_inner = R - t
    
    if r_inner < 0:
        raise ValueError("Thickness cannot be greater than radius")

    # Coordinates: (y, z)
    # y = Up, z = Right
    outer_points = []
    inner_points = []
    
    for i in range(n):
        theta = 2 * math.pi * i / n
        # y = R sin, z = R cos
        outer_points.append((R * math.sin(theta), R * math.cos(theta)))
        inner_points.append((r_inner * math.sin(theta), r_inner * math.cos(theta)))
        
    geom = Geometry(shapes=[
        Shape(points=outer_points, hollow=False),
        Shape(points=inner_points, hollow=True)
    ])
    
    return Section(name=f"CHS {d}x{t}", geometry=geom)
