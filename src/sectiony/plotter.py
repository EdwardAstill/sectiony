from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Tuple
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import math

if TYPE_CHECKING:
    from .section import Section
    from .geometry import Contour, Line, Arc, CubicBezier

# Type alias for points
Point = Tuple[float, float]


def contour_to_path(contour: 'Contour') -> Optional[Path]:
    """
    Convert a Contour to a matplotlib Path with native curve commands.
    Uses CURVE4 for beziers and arcs (converted to beziers).
    
    This is a shared utility used by both plotter and stress modules.
    
    Args:
        contour: The Contour to convert
        
    Returns:
        A matplotlib Path, or None if contour has no segments
    """
    from .geometry import Line, Arc, CubicBezier
    
    if not contour.segments:
        return None
    
    vertices: List[tuple[float, float]] = []
    codes: List[int] = []
    
    # Start with MOVETO to first point
    first_segment = contour.segments[0]
    if isinstance(first_segment, Line):
        start_point = first_segment.start
    elif isinstance(first_segment, Arc):
        cx, cy = first_segment.center
        x = cx + first_segment.radius * math.cos(first_segment.start_angle)
        y = cy + first_segment.radius * math.sin(first_segment.start_angle)
        start_point = (x, y)
    elif isinstance(first_segment, CubicBezier):
        start_point = first_segment.p0
    else:
        start_point = (0, 0)
    
    # Plot coords are the section coords (x horizontal, y vertical)
    vertices.append((start_point[0], start_point[1]))
    codes.append(Path.MOVETO)
    
    for segment in contour.segments:
        if isinstance(segment, Line):
            # Line: just LINETO to end point
            vertices.append((segment.end[0], segment.end[1]))
            codes.append(Path.LINETO)
            
        elif isinstance(segment, Arc):
            # Convert arc to bezier curves for native rendering
            beziers = segment.to_beziers()
            for bez in beziers:
                # CURVE4 needs 3 vertices: control1, control2, end
                vertices.append((bez.p1[0], bez.p1[1]))
                codes.append(Path.CURVE4)
                vertices.append((bez.p2[0], bez.p2[1]))
                codes.append(Path.CURVE4)
                vertices.append((bez.p3[0], bez.p3[1]))
                codes.append(Path.CURVE4)
                
        elif isinstance(segment, CubicBezier):
            # Native cubic bezier
            vertices.append((segment.p1[0], segment.p1[1]))
            codes.append(Path.CURVE4)
            vertices.append((segment.p2[0], segment.p2[1]))
            codes.append(Path.CURVE4)
            vertices.append((segment.p3[0], segment.p3[1]))
            codes.append(Path.CURVE4)
    
    # Close the path
    codes.append(Path.CLOSEPOLY)
    vertices.append(vertices[0])  # Close back to start
    
    return Path(vertices, codes)


def points_to_path(points: List[Point]) -> Optional[Path]:
    """
    Convert a list of points to a matplotlib Path (polygon).
    
    Args:
        points: List of (y, z) points
        
    Returns:
        A matplotlib Path, or None if fewer than 3 points
    """
    if not points or len(points) < 3:
        return None
    
    # Plot coords are the section coords (x horizontal, y vertical)
    vertices = [(p[0], p[1]) for p in points]
    vertices.append(vertices[0])  # Close
    codes = [Path.MOVETO] + [Path.LINETO] * (len(points) - 1) + [Path.CLOSEPOLY]
    
    return Path(vertices, codes)


def _clip_hollow_to_solids(
    hollow_points: List[Point], 
    solid_contours: List['Contour']
) -> List[List[Point]]:
    """
    Clip a hollow contour to only the parts that intersect with solid regions.
    
    Args:
        hollow_points: Discretized points of the hollow contour
        solid_contours: List of solid contours to clip against
        
    Returns:
        List of clipped point lists (one for each solid intersection)
    """
    # Import clipping functions from geometry module
    from .geometry import _clip_polygon, _polygon_area_signed
    
    clipped_regions = []
    
    for solid in solid_contours:
        solid_points = solid.discretize()
        if len(solid_points) < 3:
            continue
            
        # Clip hollow to this solid
        clipped = _clip_polygon(hollow_points, solid_points)
        
        # Only keep if it has area (actual intersection)
        if len(clipped) >= 3 and abs(_polygon_area_signed(clipped)) > 1e-9:
            clipped_regions.append(clipped)
    
    return clipped_regions


def plot_section(
    section: 'Section', 
    ax: Optional[plt.Axes] = None, 
    show: bool = True,
) -> Optional[plt.Axes]:
    """
    Plot the cross-section geometry with native curve rendering.
    
    Hollow regions are clipped to only show the parts that actually 
    intersect with solid regions (matching the property calculation).
    
    Args:
        section: The section to plot
        ax: Optional matplotlib axes to plot on. If None, creates a new figure.
        show: Whether to call plt.show() at the end.
    
    Returns:
        The axes object used for plotting.
    """
    if not section.geometry or not section.geometry.contours:
        print("No geometry defined for this section.")
        return None

    if ax is None:
        fig, ax = plt.subplots()
    
    solids = [c for c in section.geometry.contours if not c.hollow]
    hollows = [c for c in section.geometry.contours if c.hollow]
    
    all_x: List[float] = []
    all_y: List[float] = []
    
    # Plot solids
    for contour in solids:
        path = contour_to_path(contour)
        if path is None:
            continue
        
        # Collect bounds from discretized points
        points = contour.discretize()
        for p in points:
            all_x.append(p[0])
            all_y.append(p[1])
        
        patch = PathPatch(path, facecolor='silver', edgecolor='black', 
                         alpha=0.8, linewidth=1.0)
        ax.add_patch(patch)
    
    # Plot hollows - clipped to solid regions
    for contour in hollows:
        hollow_points = contour.discretize()
        if len(hollow_points) < 3:
            continue
        
        # Clip hollow to solid regions
        clipped_regions = _clip_hollow_to_solids(hollow_points, solids)
        
        for clipped_points in clipped_regions:
            # Collect bounds from clipped points
            for p in clipped_points:
                all_x.append(p[0])
                all_y.append(p[1])
            
            # Create path from clipped polygon
            path = points_to_path(clipped_points)
            if path is None:
                continue
            
            patch = PathPatch(path, facecolor='white', edgecolor='black',
                             linestyle='--', alpha=1.0, linewidth=1.0)
            ax.add_patch(patch)
        
    # Set limits and aspect
    if all_x and all_y:
        x_min, x_max = min(all_x), max(all_x)
        y_min, y_max = min(all_y), max(all_y)
        
        dx = x_max - x_min
        dy = y_max - y_min
        
        if dx == 0:
            dx = 1.0
        if dy == 0:
            dy = 1.0
        
        padding_x = dx * 0.1
        padding_y = dy * 0.1
        
        ax.set_xlim(x_min - padding_x, x_max + padding_x)
        ax.set_ylim(y_min - padding_y, y_max + padding_y)
        ax.set_aspect('equal')
    
    if show:
        plt.show()
        
    return ax
