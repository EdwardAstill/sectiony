import math
from ..geometry import Shape, Geometry
from ..section import Section
from .utils import arc

def i_section(d: float, b: float, tf: float, tw: float, r: float, n: int = 4) -> Section:
    """
    I Section
    
    Args:
        d: Depth (Height, y-direction)
        b: Width (Base, z-direction)
        tf: Flange thickness
        tw: Web thickness
        r: Root radius (fillet between web and flange)
        n: Segments for radius
    """
    points = []
    
    # CCW trace
    
    # 1. Top-Right Corner (y=d/2, z=b/2)
    points.append((d/2, b/2))
    
    # 2. Top-Left Corner (y=d/2, z=-b/2)
    points.append((d/2, -b/2))
    
    # 3. Top-Left Flange Bottom (y=d/2-tf, z=-b/2)
    points.append((d/2 - tf, -b/2))
    
    # 4. Top-Left Fillet (Concave)
    # Connects Flange Bottom to Web Left
    # Center: y = d/2 - tf - r, z = -tw/2 - r
    cy = d/2 - tf - r
    cz = -tw/2 - r
    # Start: Flange Bottom. y = Cy + r, z = Cz. (Theta = 90)
    # End: Web Left. y = Cy, z = Cz + r. (Theta = 0)
    # CCW trace of the solid -> Right Turn (Concave)
    # 90 -> 0 (Clockwise arc in param space, but points added to list)
    points.extend(arc(cy, cz, r, math.pi/2, 0, n))
    
    # 5. Bottom-Left Fillet (Concave)
    # Center: y = -d/2 + tf + r, z = -tw/2 - r
    cy = -d/2 + tf + r
    cz = -tw/2 - r
    # Start: Web Left. y = Cy, z = Cz + r (Theta = 0).
    # End: Flange Top. y = Cy - r, z = Cz. (Theta = 270/-90).
    # 0 -> -pi/2
    points.extend(arc(cy, cz, r, 0, -math.pi/2, n))
    
    # 6. Bottom-Left Flange Top (y=-d/2+tf, z=-b/2)
    points.append((-d/2 + tf, -b/2))
    
    # 7. Bottom-Left Flange Bottom (y=-d/2, z=-b/2)
    points.append((-d/2, -b/2))
    
    # 8. Bottom-Right Flange Bottom (y=-d/2, z=b/2)
    points.append((-d/2, b/2))
    
    # 9. Bottom-Right Flange Top (y=-d/2+tf, z=b/2)
    points.append((-d/2 + tf, b/2))
    
    # 10. Bottom-Right Fillet (Concave)
    # Center: y = -d/2 + tf + r, z = tw/2 + r
    cy = -d/2 + tf + r
    cz = tw/2 + r
    # Start: Flange Top. y = Cy - r, z = Cz. (Theta = 270).
    # End: Web Right. y = Cy, z = Cz - r. (Theta = 180).
    # 270 -> 180
    points.extend(arc(cy, cz, r, 3*math.pi/2, math.pi, n))
    
    # 11. Top-Right Fillet (Concave)
    # Center: y = d/2 - tf - r, z = tw/2 + r
    cy = d/2 - tf - r
    cz = tw/2 + r
    # Start: Web Right. y = Cy, z = Cz - r. (Theta = 180).
    # End: Flange Bottom. y = Cy + r, z = Cz. (Theta = 90).
    # 180 -> 90
    points.extend(arc(cy, cz, r, math.pi, math.pi/2, n))
    
    # 12. Top-Right Flange Bottom (y=d/2-tf, z=b/2)
    points.append((d/2 - tf, b/2))
    
    geom = Geometry(shapes=[Shape(points=points, hollow=False)])
    return Section(name=f"I {d}x{b}", geometry=geom)
