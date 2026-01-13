import math
from ..geometry import Geometry, Contour, Line, Arc
from ..section import Section


def u(b: float, h: float, tw: float, tf: float, r: float) -> Section:
    """
    U (Channel) Section with native curve geometry.
    Web at Left (x = -b/2 + tw/2 centered), flanges point Right.
    
    Args:
        b: Width (x-direction)
        h: Height (y-direction)
        tw: Web thickness
        tf: Flange thickness
        r: Outside corner radius
    """
    segments = []
    
    # Key coordinates
    half_h = h / 2
    half_b = b / 2
    
    use_outer_fillet = r > 1e-9
    ri = max(0.0, r - tw)  # Inner radius (based on web thickness)
    use_inner_fillet = ri > 1e-9
    
    # CCW trace starting from Top-Right outer tip
    
    # 1. Top flange outer: Top-Right to near Top-Left corner
    if use_outer_fillet:
        segments.append(Line(start=(half_b, half_h), end=(-half_b + r, half_h)))
        
        # 2. Top-Left outer corner arc
        cy = half_h - r
        cz = -half_b + r
        segments.append(Arc(center=(cz, cy), radius=r, start_angle=math.pi/2, end_angle=math.pi))
        
        # 3. Left web outer edge (going down) 
        segments.append(Line(start=(-half_b, half_h - r), end=(-half_b, -half_h + r)))
        
        # 4. Bottom-Left outer corner arc
        cy = -half_h + r
        cz = -half_b + r
        segments.append(Arc(center=(cz, cy), radius=r, start_angle=math.pi, end_angle=3*math.pi/2))
        
        # 5. Bottom flange outer: to Bottom-Right
        segments.append(Line(start=(-half_b + r, -half_h), end=(half_b, -half_h)))
    else:
        # Sharp corners
        segments.append(Line(start=(half_b, half_h), end=(-half_b, half_h)))
        segments.append(Line(start=(-half_b, half_h), end=(-half_b, -half_h)))
        segments.append(Line(start=(-half_b, -half_h), end=(half_b, -half_h)))
    
    # 6. Bottom-Right tip: outer to inner (going up inside the flange)
    segments.append(Line(start=(half_b, -half_h), end=(half_b, -half_h + tf)))
    
    # Inner profile (going back up)
    if use_inner_fillet:
        # 7. Bottom flange inner: to near corner
        segments.append(Line(start=(half_b, -half_h + tf), end=(-half_b + r, -half_h + tf)))
        
        # 8. Bottom-Left inner corner arc (concave, going CW in local sense)
        cy = -half_h + r
        cz = -half_b + r
        segments.append(Arc(center=(cz, cy), radius=ri, start_angle=3*math.pi/2, end_angle=math.pi))
        
        # 9. Left web inner edge (going up)
        segments.append(Line(start=(-half_b + tw, -half_h + r), end=(-half_b + tw, half_h - r)))
        
        # 10. Top-Left inner corner arc
        cy = half_h - r
        cz = -half_b + r
        segments.append(Arc(center=(cz, cy), radius=ri, start_angle=math.pi, end_angle=math.pi/2))
        
        # 11. Top flange inner: from corner to tip
        segments.append(Line(start=(-half_b + r, half_h - tf), end=(half_b, half_h - tf)))
    else:
        # Sharp inner corners
        segments.append(Line(start=(half_b, -half_h + tf), end=(-half_b + tw, -half_h + tf)))
        segments.append(Line(start=(-half_b + tw, -half_h + tf), end=(-half_b + tw, half_h - tf)))
        segments.append(Line(start=(-half_b + tw, half_h - tf), end=(half_b, half_h - tf)))
    
    # 12. Top-Right tip: inner to outer (closing)
    segments.append(Line(start=(half_b, half_h - tf), end=(half_b, half_h)))
    
    contour = Contour(segments=segments, hollow=False)
    geom = Geometry(contours=[contour])
    
    return Section(
        name=f"U {b}x{h}x{tw}x{tf}", 
        geometry=geom,
        dimensions={"b": b, "h": h, "tw": tw, "tf": tf, "r": r}
    )

