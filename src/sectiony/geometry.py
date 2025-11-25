from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Union
import math

# Type alias for points
Point = Tuple[float, float]


@dataclass
class Line:
    """A straight line segment from start to end."""
    start: Point
    end: Point

    def discretize(self, resolution: int = 32) -> List[Point]:
        """Return start and end points (lines don't need intermediate points)."""
        return [self.start, self.end]

    def end_point(self) -> Point:
        return self.end


@dataclass
class Arc:
    """
    A circular arc defined by center, radius, and angles.
    Angles in radians: 0 is +z (Right), pi/2 is +y (Up).
    """
    center: Point
    radius: float
    start_angle: float
    end_angle: float

    def discretize(self, resolution: int = 32) -> List[Point]:
        """Convert arc to points."""
        if self.radius <= 1e-9:
            return [self.center]
        
        # Determine number of points based on arc span
        angle_span = abs(self.end_angle - self.start_angle)
        n = max(2, int(resolution * angle_span / (2 * math.pi)))
        
        points = []
        cy, cz = self.center
        for i in range(n + 1):
            theta = self.start_angle + (self.end_angle - self.start_angle) * i / n
            y = cy + self.radius * math.sin(theta)
            z = cz + self.radius * math.cos(theta)
            points.append((y, z))
        return points

    def end_point(self) -> Point:
        cy, cz = self.center
        y = cy + self.radius * math.sin(self.end_angle)
        z = cz + self.radius * math.cos(self.end_angle)
        return (y, z)

    def to_beziers(self) -> List['CubicBezier']:
        """
        Convert arc to cubic Bezier curves for native rendering.
        Uses the standard approximation: split arc into segments <= 90 degrees.
        """
        beziers = []
        angle_span = self.end_angle - self.start_angle
        
        # Split into segments of at most 90 degrees (pi/2)
        num_segments = max(1, int(math.ceil(abs(angle_span) / (math.pi / 2))))
        segment_angle = angle_span / num_segments
        
        cy, cz = self.center
        r = self.radius
        
        for i in range(num_segments):
            a1 = self.start_angle + i * segment_angle
            a2 = a1 + segment_angle
            
            # Bezier control point factor for circular arc
            # k = (4/3) * tan(angle/4)
            k = (4.0 / 3.0) * math.tan(abs(segment_angle) / 4.0)
            if segment_angle < 0:
                k = -k
            
            # Start and end points on arc
            # y = r*sin(theta), z = r*cos(theta) relative to center
            p0_y = cy + r * math.sin(a1)
            p0_z = cz + r * math.cos(a1)
            p3_y = cy + r * math.sin(a2)
            p3_z = cz + r * math.cos(a2)
            
            # Tangent directions (perpendicular to radius)
            # At angle theta: tangent direction is (cos(theta), -sin(theta)) for CCW
            # For our coord system where y=sin, z=cos:
            # dy/dtheta = r*cos(theta), dz/dtheta = -r*sin(theta)
            t1_y = r * math.cos(a1)
            t1_z = -r * math.sin(a1)
            t2_y = r * math.cos(a2)
            t2_z = -r * math.sin(a2)
            
            # Control points
            p1_y = p0_y + k * t1_y
            p1_z = p0_z + k * t1_z
            p2_y = p3_y - k * t2_y
            p2_z = p3_z - k * t2_z
            
            beziers.append(CubicBezier(
                p0=(p0_y, p0_z),
                p1=(p1_y, p1_z),
                p2=(p2_y, p2_z),
                p3=(p3_y, p3_z)
            ))
        
        return beziers


@dataclass
class CubicBezier:
    """
    A cubic Bezier curve with 4 control points.
    p0: start point
    p1: first control point
    p2: second control point  
    p3: end point
    """
    p0: Point
    p1: Point
    p2: Point
    p3: Point

    def discretize(self, resolution: int = 32) -> List[Point]:
        """Convert bezier to points using de Casteljau's algorithm."""
        points = []
        for i in range(resolution + 1):
            t = i / resolution
            point = self._evaluate(t)
            points.append(point)
        return points

    def _evaluate(self, t: float) -> Point:
        """Evaluate bezier at parameter t using de Casteljau."""
        u = 1 - t
        y = (u**3 * self.p0[0] + 
             3 * u**2 * t * self.p1[0] + 
             3 * u * t**2 * self.p2[0] + 
             t**3 * self.p3[0])
        z = (u**3 * self.p0[1] + 
             3 * u**2 * t * self.p1[1] + 
             3 * u * t**2 * self.p2[1] + 
             t**3 * self.p3[1])
        return (y, z)

    def end_point(self) -> Point:
        return self.p3


# Union type for all segment types
Segment = Union[Line, Arc, CubicBezier]


@dataclass
class Contour:
    """
    A closed contour made up of connected curve segments.
    Segments should form a closed loop (end of last connects to start of first).
    """
    segments: List[Segment] = field(default_factory=list)
    hollow: bool = False

    def discretize(self, resolution: int = 32) -> List[Point]:
        """Convert all segments to a single list of points."""
        if not self.segments:
            return []
        
        points = []
        for i, segment in enumerate(self.segments):
            seg_points = segment.discretize(resolution)
            if i == 0:
                points.extend(seg_points)
            else:
                # Skip first point of subsequent segments (it's the same as last point)
                points.extend(seg_points[1:])
        
        # Remove last point if it duplicates first (closed contour)
        if len(points) > 1 and self._points_equal(points[0], points[-1]):
            points = points[:-1]
        
        return points

    def _points_equal(self, p1: Point, p2: Point, tol: float = 1e-9) -> bool:
        return abs(p1[0] - p2[0]) < tol and abs(p1[1] - p2[1]) < tol


# Legacy Shape class - now wraps a Contour for backward compatibility during transition
@dataclass
class Shape:
    """
    Legacy shape class that wraps points.
    Prefer using Contour for new code.
    """
    points: List[Point] = field(default_factory=list)
    hollow: bool = False
    _contour: Contour = field(default=None, repr=False)

    def __post_init__(self):
        # If points provided but no contour, create contour from points
        if self.points and self._contour is None:
            self._contour = self._points_to_contour()

    def _points_to_contour(self) -> Contour:
        """Convert point list to a contour of line segments."""
        if len(self.points) < 2:
            return Contour(segments=[], hollow=self.hollow)
        
        segments = []
        for i in range(len(self.points)):
            start = self.points[i]
            end = self.points[(i + 1) % len(self.points)]
            segments.append(Line(start=start, end=end))
        
        return Contour(segments=segments, hollow=self.hollow)

    @classmethod
    def from_contour(cls, contour: Contour) -> 'Shape':
        """Create a Shape from a Contour."""
        points = contour.discretize()
        shape = cls(points=points, hollow=contour.hollow)
        shape._contour = contour
        return shape


@dataclass
class Geometry:
    """Collection of shapes/contours that define a cross-section."""
    shapes: List[Shape] = field(default_factory=list)
    contours: List[Contour] = field(default_factory=list)

    def __post_init__(self):
        # If contours provided but shapes not, create shapes from contours
        if self.contours and not self.shapes:
            self.shapes = [Shape.from_contour(c) for c in self.contours]
        # If shapes provided but contours not, create contours from shapes
        elif self.shapes and not self.contours:
            self.contours = [s._contour if s._contour else s._points_to_contour() 
                           for s in self.shapes]

    def reduce_hollows(self) -> List[Shape]:
        """Clip polygons to handle holes."""
        return _reduce_hollows_impl(self.shapes)

    def calculate_properties(self):
        """Calculate section properties."""
        from .properties import calculate_exact_properties, calculate_grid_properties, SectionProperties
        
        reduced_shapes = self.reduce_hollows()
        props = calculate_exact_properties(reduced_shapes)
        calculate_grid_properties(props, reduced_shapes)
        
        return props


# -----------------------------------------------------------------------------
# Geometry Utils (Clipping)
# -----------------------------------------------------------------------------

def _reduce_hollows_impl(shapes: List[Shape]) -> List[Shape]:
    solids = [s for s in shapes if not s.hollow]
    hollows = [s for s in shapes if s.hollow]
    
    if not hollows:
        return solids
        
    reduced_shapes = list(solids)
    for h in hollows:
        for s in solids:
            clipped_points = _clip_polygon(h.points, s.points)
            if len(clipped_points) >= 3 and abs(_polygon_area_signed(clipped_points)) > 1e-9:
                reduced_shapes.append(Shape(points=clipped_points, hollow=True))
    return reduced_shapes


def _polygon_area_signed(points: List[Point]) -> float:
    area = 0.0
    for i in range(len(points)):
        j = (i + 1) % len(points)
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]
    return 0.5 * area


def _clip_polygon(subject: List[Point], clipper: List[Point]) -> List[Point]:
    """Sutherland-Hodgman clipping."""
    def inside(p, cp1, cp2):
        return (cp2[0]-cp1[0])*(p[1]-cp1[1]) - (cp2[1]-cp1[1])*(p[0]-cp1[0]) >= 0
    
    def compute_intersection(cp1, cp2, s, e):
        dc = [cp1[0] - cp2[0], cp1[1] - cp2[1]]
        dp = [s[0] - e[0], s[1] - e[1]]
        n1 = cp1[0] * cp2[1] - cp1[1] * cp2[0]
        n2 = s[0] * e[1] - s[1] * e[0]
        det = dc[0] * dp[1] - dc[1] * dp[0]
        if abs(det) < 1e-9: 
            return e
        n3 = 1.0 / det
        return ((n1 * dp[0] - n2 * dc[0]) * n3, (n1 * dp[1] - n2 * dc[1]) * n3)
    
    output = list(subject)
    if _polygon_area_signed(clipper) < 0:
        clipper_oriented = list(reversed(clipper))
    else:
        clipper_oriented = list(clipper)
        
    cp1 = clipper_oriented[-1]
    for cp2 in clipper_oriented:
        input_list = output
        output = []
        if not input_list:
            break
        s = input_list[-1]
        for e in input_list:
            if inside(e, cp1, cp2):
                if not inside(s, cp1, cp2):
                    output.append(compute_intersection(cp1, cp2, s, e))
                output.append(e)
            elif inside(s, cp1, cp2):
                output.append(compute_intersection(cp1, cp2, s, e))
            s = e
        cp1 = cp2
    return output
