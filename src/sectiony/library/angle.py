import math
from ..geometry import Geometry, Contour, Line, Arc
from ..section import Section


def angle(b: float, h: float, t: float, r: float = 0.0) -> Section:
    """
    Angle (L-section) centered at origin.

    Args:
        b: Horizontal leg width (x-direction)
        h: Vertical leg height (y-direction)
        t: Leg thickness (applies to both legs)
        r: Root radius at inner corner
    """
    if t >= b or t >= h:
        raise ValueError("Thickness too large for dimensions")

    half_b = b / 2
    half_h = h / 2
    use_fillet = r > 1e-9

    segments = []
    # CCW trace from bottom-right
    # Bottom edge: right -> left
    segments.append(Line(start=(half_b, -half_h), end=(-half_b, -half_h)))
    # Left outer edge: up
    segments.append(Line(start=(-half_b, -half_h), end=(-half_b, half_h)))
    # Top of vertical leg: right
    segments.append(Line(start=(-half_b, half_h), end=(-half_b + t, half_h)))

    if use_fillet:
        # Down inner right of vertical leg to fillet tangent point
        segments.append(Line(
            start=(-half_b + t, half_h),
            end=(-half_b + t, -half_h + t + r),
        ))
        # Inner fillet arc: CCW from pi -> 3*pi/2
        # Center at (-half_b + t + r, -half_h + t + r)
        cx_arc = -half_b + t + r
        cy_arc = -half_h + t + r
        segments.append(Arc(
            center=(cx_arc, cy_arc),
            radius=r,
            start_angle=math.pi,
            end_angle=3 * math.pi / 2,
        ))
        # Inner top of horizontal leg: right
        segments.append(Line(
            start=(-half_b + t + r, -half_h + t),
            end=(half_b, -half_h + t),
        ))
    else:
        # Inner right of vertical leg going down (sharp corner)
        segments.append(Line(start=(-half_b + t, half_h), end=(-half_b + t, -half_h + t)))
        # Inner top of horizontal leg: right
        segments.append(Line(start=(-half_b + t, -half_h + t), end=(half_b, -half_h + t)))

    # Right edge: down (closing)
    segments.append(Line(start=(half_b, -half_h + t), end=(half_b, -half_h)))

    contour = Contour(segments=segments, hollow=False)
    geom = Geometry(contours=[contour])
    return Section(
        name=f"Angle {b}x{h}x{t}",
        geometry=geom,
        dimensions={"b": b, "h": h, "t": t, "r": r},
    )
