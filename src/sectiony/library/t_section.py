import math
from ..geometry import Geometry, Contour, Line, Arc
from ..section import Section


def t_section(b: float, d: float, tf: float, tw: float, r: float = 0.0) -> Section:
    """
    T-section centered at origin (flange at top).

    Args:
        b: Flange width (x-direction)
        d: Total depth (y-direction)
        tf: Flange thickness
        tw: Web thickness
        r: Fillet radius at flange/web junction
    """
    if tf >= d or tw >= b:
        raise ValueError("Dimensions invalid: tf >= d or tw >= b")

    half_b = b / 2
    half_d = d / 2
    half_tw = tw / 2
    use_fillet = r > 1e-9

    segments = []
    # CCW trace from top-right corner
    # 1. Top flange: right → left
    segments.append(Line(start=(half_b, half_d), end=(-half_b, half_d)))
    # 2. Left flange edge: down
    segments.append(Line(start=(-half_b, half_d), end=(-half_b, half_d - tf)))

    if use_fillet:
        # 3. Flange bottom going right to fillet tangent
        segments.append(Line(start=(-half_b, half_d - tf), end=(-half_tw - r, half_d - tf)))
        # 4. Left fillet: CW from π/2 → 0
        #    Center: (-half_tw - r, half_d - tf - r)
        segments.append(Arc(
            center=(-half_tw - r, half_d - tf - r),
            radius=r,
            start_angle=math.pi / 2,
            end_angle=0,
        ))
        # 5. Left web edge: down
        segments.append(Line(start=(-half_tw, half_d - tf - r), end=(-half_tw, -half_d)))
    else:
        segments.append(Line(start=(-half_b, half_d - tf), end=(-half_tw, half_d - tf)))
        segments.append(Line(start=(-half_tw, half_d - tf), end=(-half_tw, -half_d)))

    # 6. Bottom of web: left → right
    segments.append(Line(start=(-half_tw, -half_d), end=(half_tw, -half_d)))

    if use_fillet:
        # 7. Right web edge: up to fillet tangent
        segments.append(Line(start=(half_tw, -half_d), end=(half_tw, half_d - tf - r)))
        # 8. Right fillet: CW from π → π/2
        #    Center: (half_tw + r, half_d - tf - r)
        segments.append(Arc(
            center=(half_tw + r, half_d - tf - r),
            radius=r,
            start_angle=math.pi,
            end_angle=math.pi / 2,
        ))
        # 9. Flange bottom: right from fillet to flange edge
        segments.append(Line(start=(half_tw + r, half_d - tf), end=(half_b, half_d - tf)))
    else:
        segments.append(Line(start=(half_tw, -half_d), end=(half_tw, half_d - tf)))
        segments.append(Line(start=(half_tw, half_d - tf), end=(half_b, half_d - tf)))

    # 10. Right flange edge: up (closing)
    segments.append(Line(start=(half_b, half_d - tf), end=(half_b, half_d)))

    contour = Contour(segments=segments, hollow=False)
    geom = Geometry(contours=[contour])
    return Section(
        name=f"T {b}x{d}",
        geometry=geom,
        dimensions={"b": b, "d": d, "tf": tf, "tw": tw, "r": r},
    )
