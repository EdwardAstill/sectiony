import math
from ..geometry import Geometry, Contour, Line, Arc
from ..section import Section


def rhs(b: float, h: float, t: float, r: float) -> Section:
    """
    Rectangular Hollow Section with native curve geometry.
    
    Args:
        b: Width (x-direction)
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
    
    return Section(
        name=f"RHS {b}x{h}x{t}", 
        geometry=geom,
        dimensions={"b": b, "h": h, "t": t, "r": r}
    )


def _rounded_rect_segments(h: float, b: float, r: float):
    """Create segments for a rounded rectangle centered at origin."""
    segments = []
    
    use_corners = r > 1e-9
    
    # Half dimensions
    half_y = h / 2
    half_x = b / 2
    
    if use_corners:
        # Corner centers (distance from origin to corner arc center)
        cx = half_x - r  # x-distance
        cy = half_y - r  # y-distance
        
        # Start at right side of top-right corner, go CCW
        # Top-Right Corner arc (0 to 90 deg): right -> top
        segments.append(Arc(center=(cx, cy), radius=r, start_angle=0.0, end_angle=math.pi / 2))
        
        # Top edge: from top-right arc end -> top-left arc start
        segments.append(Line(start=(cx, half_y), end=(-cx, half_y)))
        
        # Top-Left Corner arc (90 to 180 deg): top -> left
        segments.append(Arc(center=(-cx, cy), radius=r, start_angle=math.pi / 2, end_angle=math.pi))
        
        # Left edge: from top-left arc end -> bottom-left arc start
        segments.append(Line(start=(-half_x, cy), end=(-half_x, -cy)))
        
        # Bottom-Left Corner arc (180 to 270 deg): left -> bottom
        segments.append(Arc(center=(-cx, -cy), radius=r, start_angle=math.pi, end_angle=3 * math.pi / 2))
        
        # Bottom edge: from bottom-left arc end -> bottom-right arc start
        segments.append(Line(start=(-cx, -half_y), end=(cx, -half_y)))
        
        # Bottom-Right Corner arc (270 to 360 deg): bottom -> right
        segments.append(Arc(center=(cx, -cy), radius=r, start_angle=3 * math.pi / 2, end_angle=2 * math.pi))
        
        # Right edge: from bottom-right arc end -> top-right arc start
        segments.append(Line(start=(half_x, -cy), end=(half_x, cy)))
    else:
        # Sharp corners - simple rectangle
        segments.append(Line(start=(half_x, half_y), end=(-half_x, half_y)))
        segments.append(Line(start=(-half_x, half_y), end=(-half_x, -half_y)))
        segments.append(Line(start=(-half_x, -half_y), end=(half_x, -half_y)))
        segments.append(Line(start=(half_x, -half_y), end=(half_x, half_y)))
    
    return segments
