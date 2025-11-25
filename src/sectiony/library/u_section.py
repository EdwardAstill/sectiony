import math
from ..geometry import Shape, Geometry
from ..section import Section
from .utils import arc

def u_section(b: float, h: float, t: float, r: float, n: int = 4) -> Section:
    """
    U (Channel) Section
    
    Args:
        b: Width (z-direction)
        h: Height (y-direction)
        t: Thickness
        r: Outside corner radius
        n: Segments
    """
    # Web at Left (z = -b/2).
    # Flanges point Right.
    
    ri = max(0.0, r - t)
    
    points = []
    
    # Top-Right Tip (Outer)
    # y = h/2, z = b/2
    points.append((h/2, b/2))
    
    # Top-Left Corner (Outer, Convex)
    # Center: y = h/2 - r, z = -b/2 + r
    cy = h/2 - r
    cz = -b/2 + r
    # Arc 90 (y+) -> 180 (z-)
    points.extend(arc(cy, cz, r, math.pi/2, math.pi, n))
    
    # Bottom-Left Corner (Outer, Convex)
    # Center: y = -h/2 + r, z = -b/2 + r
    cy = -h/2 + r
    cz = -b/2 + r
    # Arc 180 (z-) -> 270 (y-)
    points.extend(arc(cy, cz, r, math.pi, 3*math.pi/2, n))
    
    # Bottom-Right Tip (Outer)
    # y = -h/2, z = b/2
    points.append((-h/2, b/2))
    
    # Bottom-Right Tip (Inner)
    # y = -h/2 + t, z = b/2
    points.append((-h/2 + t, b/2))
    
    # Bottom-Left Corner (Inner, Concave)
    # Center: y = -h/2 + r, z = -b/2 + r (Same as outer center for concentric)
    # But inner radius ri.
    cy = -h/2 + r
    cz = -b/2 + r
    # Start: Flange Inner Face. y = -h/2 + t.
    # y = Cy - r + t = Cy - ri. (Theta = 270).
    # End: Web Inner Face. z = -b/2 + t.
    # z = Cz - r + t = Cz - ri. (Theta = 180).
    # 270 -> 180.
    points.extend(arc(cy, cz, ri, 3*math.pi/2, math.pi, n))
    
    # Top-Left Corner (Inner, Concave)
    # Center: y = h/2 - r, z = -b/2 + r
    cy = h/2 - r
    cz = -b/2 + r
    # Start: Web Inner. Theta = 180.
    # End: Flange Inner. y = h/2 - t = Cy + r - t = Cy + ri. Theta = 90.
    # 180 -> 90.
    points.extend(arc(cy, cz, ri, math.pi, math.pi/2, n))
    
    # Top-Right Tip (Inner)
    # y = h/2 - t, z = b/2
    points.append((h/2 - t, b/2))
    
    geom = Geometry(shapes=[Shape(points=points, hollow=False)])
    return Section(name=f"U {b}x{h}x{t}", geometry=geom)
