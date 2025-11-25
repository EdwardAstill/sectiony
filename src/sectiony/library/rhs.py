import math
from ..geometry import Shape, Geometry, Contour, Line, Arc
from ..section import Section


def rhs(b: float, h: float, t: float, r: float) -> Section:
    """
    Rectangular Hollow Section with native curve geometry.
    
    Args:
        b: Width (z-direction)
        h: Height (y-direction)
        t: Wall thickness
        r: Outer corner radius
    """
    if t >= b/2 or t >= h/2:
        raise ValueError("Thickness too large for dimensions")
    
    # Outer contour
    outer_segments = _rounded_rect_segments(h, b, r)
    outer_contour = Contour(segments=outer_segments, hollow=False)
    
    # Inner contour
    r_inner = max(0.0, r - t)
    h_inner = h - 2*t
    b_inner = b - 2*t
    inner_segments = _rounded_rect_segments(h_inner, b_inner, r_inner)
    inner_contour = Contour(segments=inner_segments, hollow=True)
    
    geom = Geometry(contours=[outer_contour, inner_contour])
    
    return Section(name=f"RHS {b}x{h}x{t}", geometry=geom)


def _rounded_rect_segments(h: float, b: float, r: float):
    """Create segments for a rounded rectangle centered at origin."""
    segments = []
    
    use_corners = r > 1e-9
    
    # Half dimensions
    half_h = h / 2
    half_b = b / 2
    
    if use_corners:
        # Corner centers (distance from origin to corner arc center)
        cy = half_h - r  # y-distance
        cz = half_b - r  # z-distance
        
        # Start at right side of top-right corner, go CCW
        # Top-Right Corner arc (0 to 90 deg)
        segments.append(Arc(center=(cy, cz), radius=r, start_angle=0, end_angle=math.pi/2))
        
        # Top edge
        segments.append(Line(start=(half_h, cz), end=(half_h, -cz)))
        
        # Top-Left Corner arc (90 to 180 deg)
        segments.append(Arc(center=(cy, -cz), radius=r, start_angle=math.pi/2, end_angle=math.pi))
        
        # Left edge
        segments.append(Line(start=(cy, -half_b), end=(-cy, -half_b)))
        
        # Bottom-Left Corner arc (180 to 270 deg)
        segments.append(Arc(center=(-cy, -cz), radius=r, start_angle=math.pi, end_angle=3*math.pi/2))
        
        # Bottom edge
        segments.append(Line(start=(-half_h, -cz), end=(-half_h, cz)))
        
        # Bottom-Right Corner arc (270 to 360 deg)
        segments.append(Arc(center=(-cy, cz), radius=r, start_angle=3*math.pi/2, end_angle=2*math.pi))
        
        # Right edge (back to start)
        segments.append(Line(start=(-cy, half_b), end=(cy, half_b)))
    else:
        # Sharp corners - simple rectangle
        segments.append(Line(start=(half_h, half_b), end=(half_h, -half_b)))
        segments.append(Line(start=(half_h, -half_b), end=(-half_h, -half_b)))
        segments.append(Line(start=(-half_h, -half_b), end=(-half_h, half_b)))
        segments.append(Line(start=(-half_h, half_b), end=(half_h, half_b)))
    
    return segments
