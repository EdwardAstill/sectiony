from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Union, Dict, Any, TYPE_CHECKING
import math
import json
import warnings

# Schema version for JSON serialization
_SCHEMA_VERSION = 1

# Type alias for points
Point = Tuple[float, float]


@dataclass
class Line:
    """A straight line segment from start to end."""
    start: Point
    end: Point

    def discretize(self, resolution: int = 32) -> List[Point]:
        """
        Return discretized points along the line.
        
        Args:
            resolution: Number of segments to split the line into.
        """
        if resolution < 1:
            resolution = 1
            
        points = []
        for i in range(resolution + 1):
            t = i / resolution
            points.append(self.point_at(t))
        return points

    def point_at(self, t: float) -> Point:
        """Get point at parameter t (0.0 to 1.0)."""
        return (
            self.start[0] + (self.end[0] - self.start[0]) * t,
            self.start[1] + (self.end[1] - self.start[1]) * t
        )

    @property
    def length(self) -> float:
        """Length of the line segment."""
        return math.hypot(self.end[0] - self.start[0], self.end[1] - self.start[1])

    def start_point(self) -> Point:
        return self.start

    def end_point(self) -> Point:
        return self.end

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "line",
            "start": self.start,
            "end": self.end
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Line':
        """Create Line from dictionary. Validates required fields."""
        required = ["start", "end"]
        missing = [k for k in required if k not in data]
        if missing:
            raise ValueError(f"Line missing required fields: {missing}")
        return Line(
            start=tuple(data["start"]),
            end=tuple(data["end"])
        )


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
        # Ensure at least 'resolution' points for a full circle, scaled by span
        # But if resolution is treated as 'segments per curve', we might want to just use it.
        # Existing logic scaled it. Let's keep the scaling but ensure minimum density.
        n = max(2, int(resolution * angle_span / (2 * math.pi)))
        # If the user specifically asks for high resolution, we should probably honor it more directly
        # effectively resolution here acts as "points per full circle"
        
        # Let's trust the user passed resolution as "number of segments" if they called it directly?
        # The Weld class calls it with 'discretization' (default 100).
        # If we use the old formula, for a small arc, n is small.
        # If we want "split up into many small lines", we might want to use resolution as count.
        
        # New logic: Use resolution as the number of segments for this arc directly, 
        # unless it's huge relative to the angle.
        # But for backward compatibility with 'resolution' meaning 'density', let's stick to a safe max.
        n = max(n, resolution) 

        points = []
        cy, cz = self.center
        for i in range(n + 1):
            theta = self.start_angle + (self.end_angle - self.start_angle) * i / n
            y = cy + self.radius * math.sin(theta)
            z = cz + self.radius * math.cos(theta)
            points.append((y, z))
        return points

    def point_at(self, t: float) -> Point:
        """Get point at parameter t (0.0 to 1.0)."""
        theta = self.start_angle + (self.end_angle - self.start_angle) * t
        cy, cz = self.center
        y = cy + self.radius * math.sin(theta)
        z = cz + self.radius * math.cos(theta)
        return (y, z)

    @property
    def length(self) -> float:
        """Length of the arc."""
        return self.radius * abs(self.end_angle - self.start_angle)

    def start_point(self) -> Point:
        cy, cz = self.center
        y = cy + self.radius * math.sin(self.start_angle)
        z = cz + self.radius * math.cos(self.start_angle)
        return (y, z)

    def end_point(self) -> Point:
        cy, cz = self.center
        y = cy + self.radius * math.sin(self.end_angle)
        z = cz + self.radius * math.cos(self.end_angle)
        return (y, z)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "arc",
            "center": self.center,
            "radius": self.radius,
            "start_angle": self.start_angle,
            "end_angle": self.end_angle
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Arc':
        """Create Arc from dictionary. Validates required fields."""
        required = ["center", "radius", "start_angle", "end_angle"]
        missing = [k for k in required if k not in data]
        if missing:
            raise ValueError(f"Arc missing required fields: {missing}")
        return Arc(
            center=tuple(data["center"]),
            radius=data["radius"],
            start_angle=data["start_angle"],
            end_angle=data["end_angle"]
        )

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

    def point_at(self, t: float) -> Point:
        """Get point at parameter t (0.0 to 1.0)."""
        return self._evaluate(t)

    @property
    def length(self) -> float:
        """Approximate length of the Bezier curve."""
        # Use discretization to approximate length
        # A resolution of 32 is usually sufficient for a good approximation
        points = self.discretize(32)
        length = 0.0
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i+1]
            length += math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        return length

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

    def start_point(self) -> Point:
        return self.p0

    def end_point(self) -> Point:
        return self.p3

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "bezier",
            "p0": self.p0,
            "p1": self.p1,
            "p2": self.p2,
            "p3": self.p3
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'CubicBezier':
        """Create CubicBezier from dictionary. Validates required fields."""
        required = ["p0", "p1", "p2", "p3"]
        missing = [k for k in required if k not in data]
        if missing:
            raise ValueError(f"CubicBezier missing required fields: {missing}")
        return CubicBezier(
            p0=tuple(data["p0"]),
            p1=tuple(data["p1"]),
            p2=tuple(data["p2"]),
            p3=tuple(data["p3"])
        )


# Union type for all segment types
Segment = Union[Line, Arc, CubicBezier]


@dataclass
class Contour:
    """
    A contour made up of connected curve segments.
    Can be open or closed.
    """
    segments: List[Segment] = field(default_factory=list)
    hollow: bool = False

    @property
    def is_closed(self) -> bool:
        """Check if the contour forms a closed loop."""
        if not self.segments:
            return False
            
        start = self.segments[0].start_point()
        end = self.segments[-1].end_point()
        
        return self._points_equal(start, end)
    
    @property
    def length(self) -> float:
        """Total length of the contour."""
        return sum(s.length for s in self.segments)

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
    
    def discretize_uniform(self, count: int = 100) -> List[Point]:
        """
        Discretize the contour into a fixed number of equally spaced points.
        
        Args:
            count: Number of points to generate.
            
        Returns:
            List of points equally spaced along the contour.
        """
        if not self.segments:
            return []
            
        total_length = self.length
        if total_length < 1e-9:
            return [self.segments[0].start_point()] * count
            
        points: List[Point] = []
        
        # We want 'count' points.
        # If closed, we might want the last point to match the first, 
        # but typically 'discretize' implies unique points for closed loops 
        # or inclusive of end for open.
        # If it's a closed loop, we usually want N points representing N segments.
        # If open, N points represent N-1 segments.
        # Let's assume inclusive of start and end for open, 
        # and start==end for closed (so returned list has duplicate start/end).
        
        step = total_length / max(1, count - 1) if not self.is_closed else total_length / count
        
        current_dist = 0.0
        accumulated_len = 0.0
        
        current_seg_idx = 0
        
        # Start with the first point
        points.append(self.segments[0].start_point())
        
        for i in range(1, count):
            target_dist = i * step
            
            # Find which segment contains the target distance
            while current_seg_idx < len(self.segments):
                seg = self.segments[current_seg_idx]
                seg_len = seg.length
                
                if accumulated_len + seg_len >= target_dist - 1e-9:
                    # Point is in this segment
                    local_dist = target_dist - accumulated_len
                    t = local_dist / seg_len if seg_len > 1e-9 else 0.0
                    points.append(seg.point_at(max(0.0, min(1.0, t))))
                    break
                else:
                    accumulated_len += seg_len
                    current_seg_idx += 1
            else:
                # If we ran past the end (floating point errors), assume last point
                points.append(self.segments[-1].end_point())
                
        return points

    def _points_equal(self, p1: Point, p2: Point, tol: float = 1e-4) -> bool:
        return abs(p1[0] - p2[0]) < tol and abs(p1[1] - p2[1]) < tol

    def to_dict(self) -> Dict[str, Any]:
        return {
            "segments": [s.to_dict() for s in self.segments],
            "hollow": self.hollow
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Contour':
        """Create Contour from dictionary. Validates required fields."""
        if "segments" not in data:
            raise ValueError("Contour missing required field: segments")
        
        segments = []
        for seg_data in data["segments"]:
            if "type" not in seg_data:
                raise ValueError("Segment missing required field: type")
            
            type_ = seg_data["type"]
            if type_ == "line":
                segments.append(Line.from_dict(seg_data))
            elif type_ == "arc":
                segments.append(Arc.from_dict(seg_data))
            elif type_ == "bezier":
                segments.append(CubicBezier.from_dict(seg_data))
            else:
                raise ValueError(f"Unknown segment type: {type_}")
        
        hollow = data["hollow"] if "hollow" in data else False
        return cls(segments=segments, hollow=hollow)

    @classmethod
    def from_points(cls, points: List[Point], hollow: bool = False) -> 'Contour':
        """
        Create a Contour from a list of points (polygon).
        Convenience method for creating simple polygonal contours.
        """
        if len(points) < 2:
            return cls(segments=[], hollow=hollow)
        
        segments = []
        for i in range(len(points)):
            start = points[i]
            end = points[(i + 1) % len(points)]
            segments.append(Line(start=start, end=end))
        
        return cls(segments=segments, hollow=hollow)


@dataclass
class Geometry:
    """Collection of contours that define a cross-section."""
    contours: List[Contour] = field(default_factory=list)

    @property
    def is_closed(self) -> bool:
        """Check if all contours are closed."""
        if not self.contours:
            return False
        return all(c.is_closed for c in self.contours)

    def get_discretized_contours(self, resolution: int = 32) -> List[Tuple[List[Point], bool]]:
        """
        Get discretized points for each contour.
        
        Returns:
            List of (points, hollow) tuples for each contour.
        """
        return [(c.discretize(resolution), c.hollow) for c in self.contours]
    
    def discretize_uniform(self, count: int = 100) -> List[Tuple[List[Point], bool]]:
        """
        Get uniformly discretized points for each contour.
        
        Args:
            count: Number of points per contour.
            
        Returns:
            List of (points, hollow) tuples.
        """
        return [(c.discretize_uniform(count), c.hollow) for c in self.contours]

    def reduce_hollows(self) -> List[Tuple[List[Point], bool]]:
        """
        Clip polygons to handle holes. Returns discretized points with hollow flags.
        """
        discretized = self.get_discretized_contours()
        return _reduce_hollows_impl(discretized)

    def calculate_properties(self) -> 'SectionProperties':
        """Calculate section properties."""
        from .properties import calculate_exact_properties, calculate_grid_properties, SectionProperties
        
        reduced = self.reduce_hollows()
        props = calculate_exact_properties(reduced)
        calculate_grid_properties(props, reduced)
        
        return props

    def to_dict(self) -> Dict[str, Any]:
        """Convert geometry to dictionary with schema version."""
        return {
            "version": _SCHEMA_VERSION,
            "contours": [c.to_dict() for c in self.contours]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Geometry':
        """Create geometry from dictionary. Validates structure."""
        # Handle versioning
        version = data["version"] if "version" in data else 1
        if version > _SCHEMA_VERSION:
            warnings.warn(
                f"JSON schema version {version} is newer than supported version {_SCHEMA_VERSION}. "
                "Some features may not load correctly.",
                UserWarning
            )
        
        if "contours" not in data:
            raise ValueError("Geometry missing required field: contours")
        
        contours = [Contour.from_dict(c) for c in data["contours"]]
        return cls(contours=contours)

    def to_json(self, file_path: str) -> None:
        """Save geometry to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def from_json(cls, file_path: str) -> 'Geometry':
        """Load geometry from a JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

    @classmethod
    def from_dxf(cls, file_path: str) -> 'Geometry':
        """Load geometry from a DXF file."""
        from .dxf_utils import read_dxf_robust
        contours = read_dxf_robust(file_path)
        return cls(contours=contours)

    def to_dxf(self, file_path: str) -> None:
        """Save geometry to a DXF file."""
        from .dxf_utils import write_dxf
        write_dxf(file_path, self.contours)


# -----------------------------------------------------------------------------
# Geometry Utils (Clipping)
# -----------------------------------------------------------------------------

def _reduce_hollows_impl(discretized: List[Tuple[List[Point], bool]]) -> List[Tuple[List[Point], bool]]:
    """
    Clip polygons to handle holes.
    
    Args:
        discretized: List of (points, hollow) tuples
        
    Returns:
        List of (points, hollow) tuples with holes clipped to solids
    """
    solids = [(pts, h) for pts, h in discretized if not h]
    hollows = [(pts, h) for pts, h in discretized if h]
    
    if not hollows:
        return solids
        
    reduced = list(solids)
    for h_pts, _ in hollows:
        for s_pts, _ in solids:
            clipped_points = _clip_polygon(h_pts, s_pts)
            if len(clipped_points) >= 3 and abs(_polygon_area_signed(clipped_points)) > 1e-9:
                reduced.append((clipped_points, True))
    return reduced


def _polygon_area_signed(points: List[Point]) -> float:
    """Calculate signed area of polygon using shoelace formula."""
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
