from __future__ import annotations

import math
from dataclasses import dataclass

from .geometry import Arc, CubicBezier, Line, Point, Segment


@dataclass(frozen=True)
class LineElement:
    """Weighted open-line segment for welds, seams, and other line groups."""

    segment: Segment
    weight: float = 1.0
    name: str = ""

    def __post_init__(self) -> None:
        if self.weight <= 0.0:
            raise ValueError("LineElement weight must be positive")
        if self.segment.length <= 0.0:
            raise ValueError("LineElement segment length must be positive")


@dataclass(frozen=True)
class LineGroupProperties:
    """Centroidal properties of weighted open-line geometry."""

    length: float
    weighted_area: float
    Cx: float
    Cy: float
    Ix: float
    Iy: float
    Ixy: float
    J: float


@dataclass(frozen=True)
class _LineIntegral:
    length: float
    area: float
    first_x: float
    first_y: float
    second_x: float
    second_y: float
    product_xy: float


@dataclass(frozen=True)
class LineGroup:
    """A group of weighted open-line elements.

    The weight is a generic effective width. For a weld group this is normally
    the effective throat, so ``weighted_area`` has area units.
    """

    elements: tuple[LineElement, ...]
    curve_resolution: int = 64

    def __post_init__(self) -> None:
        if not self.elements:
            raise ValueError("LineGroup requires at least one LineElement")
        if self.curve_resolution < 1:
            raise ValueError("LineGroup curve_resolution must be positive")

    @property
    def properties(self) -> LineGroupProperties:
        """Return centroidal properties for the weighted line group."""
        integrals = tuple(
            _integrate_element(element, self.curve_resolution)
            for element in self.elements
        )
        total_length = sum(integral.length for integral in integrals)
        area = sum(integral.area for integral in integrals)
        if area <= 0.0:
            raise ValueError("LineGroup weighted area must be positive")

        cx = sum(integral.first_x for integral in integrals) / area
        cy = sum(integral.first_y for integral in integrals) / area
        ix_origin = sum(integral.second_y for integral in integrals)
        iy_origin = sum(integral.second_x for integral in integrals)
        ixy_origin = sum(integral.product_xy for integral in integrals)

        ix = ix_origin - area * cy**2
        iy = iy_origin - area * cx**2
        ixy = ixy_origin - area * cx * cy
        return LineGroupProperties(
            length=total_length,
            weighted_area=area,
            Cx=cx,
            Cy=cy,
            Ix=_zero_near(ix),
            Iy=_zero_near(iy),
            Ixy=_zero_near(ixy),
            J=_zero_near(ix + iy),
        )

    def sample_points(self, resolution: int | None = None) -> tuple[Point, ...]:
        """Return points on every element suitable for stress sampling."""
        sample_resolution = resolution or self.curve_resolution
        points: list[Point] = []
        for element in self.elements:
            points.extend(_segment_points(element.segment, sample_resolution))
        return tuple(points)

    def elastic_stress(
        self,
        *,
        force_x: float = 0.0,
        force_y: float = 0.0,
        moment_z: float = 0.0,
    ):
        """Return an elastic in-plane line-group stress evaluator."""
        from .line_stress import ElasticLineGroupStress

        return ElasticLineGroupStress(
            group=self,
            force_x=force_x,
            force_y=force_y,
            moment_z=moment_z,
        )


def _integrate_element(element: LineElement, curve_resolution: int) -> _LineIntegral:
    points = _segment_points(element.segment, curve_resolution)
    total = _LineIntegral(
        length=0.0,
        area=0.0,
        first_x=0.0,
        first_y=0.0,
        second_x=0.0,
        second_y=0.0,
        product_xy=0.0,
    )
    for start, end in zip(points, points[1:]):
        total = _sum_integrals(
            total,
            _integrate_straight_chord(start, end, element.weight),
        )
    return total


def _segment_points(segment: Segment, resolution: int) -> tuple[Point, ...]:
    if isinstance(segment, Line):
        return (segment.start, segment.end)
    if isinstance(segment, (Arc, CubicBezier)):
        return tuple(segment.discretize(resolution))
    return tuple(segment.discretize(resolution))


def _integrate_straight_chord(start: Point, end: Point, weight: float) -> _LineIntegral:
    x1, y1 = start
    x2, y2 = end
    length = math.hypot(x2 - x1, y2 - y1)
    if length <= 0.0:
        return _LineIntegral(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    area = weight * length
    first_x = area * (x1 + x2) / 2.0
    first_y = area * (y1 + y2) / 2.0
    second_x = weight * length * (x1**2 + x1 * x2 + x2**2) / 3.0
    second_y = weight * length * (y1**2 + y1 * y2 + y2**2) / 3.0

    dx = x2 - x1
    dy = y2 - y1
    product_xy = weight * length * (
        x1 * y1 + (x1 * dy + y1 * dx) / 2.0 + dx * dy / 3.0
    )
    return _LineIntegral(
        length=length,
        area=area,
        first_x=first_x,
        first_y=first_y,
        second_x=second_x,
        second_y=second_y,
        product_xy=product_xy,
    )


def _sum_integrals(a: _LineIntegral, b: _LineIntegral) -> _LineIntegral:
    return _LineIntegral(
        length=a.length + b.length,
        area=a.area + b.area,
        first_x=a.first_x + b.first_x,
        first_y=a.first_y + b.first_y,
        second_x=a.second_x + b.second_x,
        second_y=a.second_y + b.second_y,
        product_xy=a.product_xy + b.product_xy,
    )


def _zero_near(value: float, tolerance: float = 1e-15) -> float:
    return 0.0 if abs(value) < tolerance else value
