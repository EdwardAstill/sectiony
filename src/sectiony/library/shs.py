from ..section import Section
from .rhs import rhs as _rhs


def shs(d: float, t: float, r: float = 0.0) -> Section:
    """
    Square Hollow Section (SHS) — equal-sided RHS.

    Args:
        d: Side length (both width and height)
        t: Wall thickness
        r: Outer corner radius
    """
    sec = _rhs(d, d, t, r)
    sec.name = f"SHS {d}x{t}"
    return sec
