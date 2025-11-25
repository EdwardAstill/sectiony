from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Optional
from .properties import calculate_exact_properties, calculate_grid_properties, SectionProperties

# Re-export Shape for compatibility if needed, or import from properties?
# Actually Shape is defined in geometry.py in the previous plan.
# Let's keep Shape in geometry.py as the data structure definition.

@dataclass
class Shape:
    points: List[Tuple[float, float]]
    hollow: bool = False

@dataclass
class Geometry:
    shapes: List[Shape]

    def reduce_hollows(self) -> List[Shape]:
        # Clip polygons to handle holes
        # ... (Same clipping logic as before) ...
        # For brevity, let's copy the helper functions or move them to a utils file?
        # Since I replaced geometry.py entirely, I need to restore the clipping logic here.
        return _reduce_hollows_impl(self.shapes)

    def calculate_properties(self) -> SectionProperties:
        # 1. Exact properties
        reduced_shapes = self.reduce_hollows()
        props = calculate_exact_properties(reduced_shapes)
        
        # 2. Grid properties
        # Pass the original shapes or reduced? 
        # Discretization works better with reduced shapes? 
        # Or just original shapes + logic?
        # The discretizer in properties.py handles shapes with .hollow flags using mask logic.
        # It expects a list of Shape objects.
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

def _polygon_area_signed(points: List[Tuple[float, float]]) -> float:
    area = 0.0
    for i in range(len(points)):
        j = (i + 1) % len(points)
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]
    return 0.5 * area

def _clip_polygon(subject: List[Tuple[float, float]], clipper: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    # Sutherland-Hodgman clipping
    def inside(p, cp1, cp2):
        return (cp2[0]-cp1[0])*(p[1]-cp1[1]) - (cp2[1]-cp1[1])*(p[0]-cp1[0]) >= 0
    
    def compute_intersection(cp1, cp2, s, e):
        dc = [cp1[0] - cp2[0], cp1[1] - cp2[1]]
        dp = [s[0] - e[0], s[1] - e[1]]
        n1 = cp1[0] * cp2[1] - cp1[1] * cp2[0]
        n2 = s[0] * e[1] - s[1] * e[0]
        det = dc[0] * dp[1] - dc[1] * dp[0]
        if abs(det) < 1e-9: return e
        n3 = 1.0 / det
        return ((n1 * dp[0] - n2 * dc[0]) * n3, (n1 * dp[1] - n2 * dc[1]) * n3)
    
    output = list(subject)
    # Check winding order of clipper
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
