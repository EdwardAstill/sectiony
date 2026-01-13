import math
from ..geometry import Geometry, Contour, Line, Arc
from ..section import Section


def i(d: float, b: float, tf: float, tw: float, r: float) -> Section:
    """
    I Section with native curve geometry.
    
    Args:
        d: Depth (Height, y-direction)
        b: Width (Base, x-direction)
        tf: Flange thickness
        tw: Web thickness
        r: Root radius (fillet between web and flange)
    """
    segments = []
    
    # Key coordinates
    half_d = d / 2
    half_b = b / 2
    half_tw = tw / 2
    
    # Fillet geometry
    # When r > 0, fillets curve from flange inner face to web outer face
    # When r = 0, sharp corners
    
    use_fillet = r > 1e-9
    
    # CCW trace starting from Top-Right outer corner
    
    # 1. Top edge: Top-Right to Top-Left (outer)
    segments.append(Line(start=(half_b, half_d), end=(-half_b, half_d)))
    
    # 2. Left edge of top flange: Top-Left outer down to flange inner
    segments.append(Line(start=(-half_b, half_d), end=(-half_b, half_d - tf)))
    
    if use_fillet:
        # 3. Horizontal to fillet start
        segments.append(Line(start=(-half_b, half_d - tf), end=(-half_tw - r, half_d - tf)))
        
        # 4. Top-Left Fillet arc
        cy = half_d - tf - r
        cz = -half_tw - r
        segments.append(Arc(center=(cz, cy), radius=r, start_angle=math.pi/2, end_angle=0))
        
        # 5. Left web edge (going down)
        segments.append(Line(start=(-half_tw, half_d - tf - r), end=(-half_tw, -half_d + tf + r)))
        
        # 6. Bottom-Left Fillet arc
        cy = -half_d + tf + r
        cz = -half_tw - r
        segments.append(Arc(center=(cz, cy), radius=r, start_angle=0, end_angle=-math.pi/2))
        
        # 7. Horizontal from fillet to flange edge
        segments.append(Line(start=(-half_tw - r, -half_d + tf), end=(-half_b, -half_d + tf)))
    else:
        # No fillet - sharp corners
        # 3. Horizontal to web
        segments.append(Line(start=(-half_b, half_d - tf), end=(-half_tw, half_d - tf)))
        
        # 4. Left web edge (going down)
        segments.append(Line(start=(-half_tw, half_d - tf), end=(-half_tw, -half_d + tf)))
        
        # 5. Horizontal from web to flange edge
        segments.append(Line(start=(-half_tw, -half_d + tf), end=(-half_b, -half_d + tf)))
    
    # 8. Bottom flange left edge going down
    segments.append(Line(start=(-half_b, -half_d + tf), end=(-half_b, -half_d)))
    
    # 9. Bottom edge: Bottom-Left to Bottom-Right (outer)
    segments.append(Line(start=(-half_b, -half_d), end=(half_b, -half_d)))
    
    # 10. Right edge of bottom flange going up
    segments.append(Line(start=(half_b, -half_d), end=(half_b, -half_d + tf)))
    
    if use_fillet:
        # 11. Horizontal to fillet
        segments.append(Line(start=(half_b, -half_d + tf), end=(half_tw + r, -half_d + tf)))
        
        # 12. Bottom-Right Fillet arc
        cy = -half_d + tf + r
        cz = half_tw + r
        segments.append(Arc(center=(cz, cy), radius=r, start_angle=3*math.pi/2, end_angle=math.pi))
        
        # 13. Right web edge (going up)
        segments.append(Line(start=(half_tw, -half_d + tf + r), end=(half_tw, half_d - tf - r)))
        
        # 14. Top-Right Fillet arc
        cy = half_d - tf - r
        cz = half_tw + r
        segments.append(Arc(center=(cz, cy), radius=r, start_angle=math.pi, end_angle=math.pi/2))
        
        # 15. Horizontal from fillet to flange edge
        segments.append(Line(start=(half_tw + r, half_d - tf), end=(half_b, half_d - tf)))
    else:
        # No fillet - sharp corners
        # 11. Horizontal to web
        segments.append(Line(start=(half_b, -half_d + tf), end=(half_tw, -half_d + tf)))
        
        # 12. Right web edge (going up)
        segments.append(Line(start=(half_tw, -half_d + tf), end=(half_tw, half_d - tf)))
        
        # 13. Horizontal from web to flange edge
        segments.append(Line(start=(half_tw, half_d - tf), end=(half_b, half_d - tf)))
    
    # 16. Top flange right inner edge going up, closing the loop
    segments.append(Line(start=(half_b, half_d - tf), end=(half_b, half_d)))
    
    contour = Contour(segments=segments, hollow=False)
    geom = Geometry(contours=[contour])
    
    return Section(
        name=f"I {d}x{b}", 
        geometry=geom,
        dimensions={"d": d, "b": b, "tf": tf, "tw": tw, "r": r}
    )

