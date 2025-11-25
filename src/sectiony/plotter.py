from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import numpy as np

if TYPE_CHECKING:
    from .section import Section
    from .geometry import Contour, Segment, Line, Arc, CubicBezier


def _contour_to_path(contour: 'Contour') -> Path:
    """
    Convert a Contour to a matplotlib Path with native curve commands.
    Uses CURVE4 for beziers and arcs (converted to beziers).
    """
    from .geometry import Line, Arc, CubicBezier
    
    if not contour.segments:
        return None
    
    vertices = []
    codes = []
    
    # Start with MOVETO to first point
    first_segment = contour.segments[0]
    if isinstance(first_segment, Line):
        start_point = first_segment.start
    elif isinstance(first_segment, Arc):
        cy, cz = first_segment.center
        import math
        y = cy + first_segment.radius * math.sin(first_segment.start_angle)
        z = cz + first_segment.radius * math.cos(first_segment.start_angle)
        start_point = (y, z)
    elif isinstance(first_segment, CubicBezier):
        start_point = first_segment.p0
    else:
        start_point = (0, 0)
    
    # Convert (y, z) to plot coords (z, y) - z horizontal, y vertical
    vertices.append((start_point[1], start_point[0]))
    codes.append(Path.MOVETO)
    
    for segment in contour.segments:
        if isinstance(segment, Line):
            # Line: just LINETO to end point
            vertices.append((segment.end[1], segment.end[0]))
            codes.append(Path.LINETO)
            
        elif isinstance(segment, Arc):
            # Convert arc to bezier curves for native rendering
            beziers = segment.to_beziers()
            for bez in beziers:
                # CURVE4 needs 3 vertices: control1, control2, end
                vertices.append((bez.p1[1], bez.p1[0]))
                codes.append(Path.CURVE4)
                vertices.append((bez.p2[1], bez.p2[0]))
                codes.append(Path.CURVE4)
                vertices.append((bez.p3[1], bez.p3[0]))
                codes.append(Path.CURVE4)
                
        elif isinstance(segment, CubicBezier):
            # Native cubic bezier
            vertices.append((segment.p1[1], segment.p1[0]))
            codes.append(Path.CURVE4)
            vertices.append((segment.p2[1], segment.p2[0]))
            codes.append(Path.CURVE4)
            vertices.append((segment.p3[1], segment.p3[0]))
            codes.append(Path.CURVE4)
    
    # Close the path
    codes.append(Path.CLOSEPOLY)
    vertices.append(vertices[0])  # Close back to start
    
    return Path(vertices, codes)


def _shape_to_path(shape) -> Path:
    """
    Convert a Shape to a matplotlib Path.
    Uses native curves if contour available, otherwise falls back to polygon.
    """
    # Try to use contour for native curves
    if hasattr(shape, '_contour') and shape._contour and shape._contour.segments:
        return _contour_to_path(shape._contour)
    
    # Fallback: use points as polygon
    if not shape.points or len(shape.points) < 3:
        return None
    
    vertices = [(p[1], p[0]) for p in shape.points]  # Convert (y,z) to (z,y)
    vertices.append(vertices[0])  # Close
    codes = [Path.MOVETO] + [Path.LINETO] * (len(shape.points) - 1) + [Path.CLOSEPOLY]
    
    return Path(vertices, codes)


def plot_section(section: 'Section', ax: Optional[plt.Axes] = None, show: bool = True) -> Optional[plt.Axes]:
    """
    Plot the cross-section geometry with native curve rendering.
    
    Args:
        section: The section to plot
        ax: Optional matplotlib axes to plot on. If None, creates a new figure.
        show: Whether to call plt.show() at the end.
    
    Returns:
        The axes object used for plotting.
    """
    if not section.geometry or not section.geometry.shapes:
        print("No geometry defined for this section.")
        return None

    if ax is None:
        fig, ax = plt.subplots()
    
    solids = [s for s in section.geometry.shapes if not s.hollow]
    hollows = [s for s in section.geometry.shapes if s.hollow]
    
    all_z = []
    all_y = []
    
    # Plot solids
    for s in solids:
        path = _shape_to_path(s)
        if path is None:
            continue
            
        # Collect bounds from points
        for p in s.points:
            all_y.append(p[0])
            all_z.append(p[1])
        
        patch = PathPatch(path, facecolor='silver', edgecolor='black', 
                         alpha=0.8, linewidth=1.0)
        ax.add_patch(patch)
        
    # Plot hollows
    for h in hollows:
        path = _shape_to_path(h)
        if path is None:
            continue
            
        for p in h.points:
            all_y.append(p[0])
            all_z.append(p[1])
        
        patch = PathPatch(path, facecolor='white', edgecolor='black',
                         linestyle='--', alpha=1.0, linewidth=1.0)
        ax.add_patch(patch)
        
    # Set limits and aspect
    if all_z and all_y:
        z_min, z_max = min(all_z), max(all_z)
        y_min, y_max = min(all_y), max(all_y)
        
        dz = z_max - z_min
        dy = y_max - y_min
        
        if dz == 0: dz = 1.0
        if dy == 0: dy = 1.0
        
        padding_z = dz * 0.1
        padding_y = dy * 0.1
        
        ax.set_xlim(z_min - padding_z, z_max + padding_z)
        ax.set_ylim(y_min - padding_y, y_max + padding_y)
        ax.set_aspect('equal')
    
    ax.set_xlabel('z (Horizontal)')
    ax.set_ylabel('y (Vertical)')
    ax.set_title(f"Section: {section.name}")
    ax.grid(True, linestyle=':', alpha=0.6)

    if show:
        plt.show()
        
    return ax
