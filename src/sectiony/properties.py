from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
import math

# Type alias for points
Point = Tuple[float, float]


@dataclass
class SectionProperties:
    """
    Data class for storing section properties.
    """
    A: float = 0.0
    Cx: float = 0.0
    Cy: float = 0.0
    Ix: float = 0.0
    Iy: float = 0.0
    Ixy: float = 0.0
    J: float = 0.0
    Sx: float = 0.0
    Sy: float = 0.0
    rx: float = 0.0
    ry: float = 0.0
    x_max: float = 0.0
    y_max: float = 0.0
    Zpl_x: float = 0.0
    Zpl_y: float = 0.0
    Cw: float = 0.0  # Warping constant
    SCx: float = 0.0  # Shear center x-coordinate
    SCy: float = 0.0  # Shear center y-coordinate


def calculate_exact_properties(contours: List[Tuple[List[Point], bool]]) -> SectionProperties:
    """
    Calculate exact geometric properties (Area, Centroids, Inertia) using Green's Theorem.
    
    Args:
        contours: List of (points, hollow) tuples
        
    Returns:
        SectionProperties with exact values calculated
    """
    A_total = 0.0
    Qx_total = 0.0  # Integral x dA
    Qy_total = 0.0  # Integral y dA
    Ixx_total = 0.0  # Integral y^2 dA
    Iyy_total = 0.0  # Integral x^2 dA
    Ixy_total = 0.0  # Integral x*y dA
    
    valid_contours = False

    for pts, hollow in contours:
        if not pts or len(pts) < 3:
            continue
        
        valid_contours = True
        
        # Ensure closed polygon
        pts_closed = list(pts)
        if pts[0] != pts[-1]:
            pts_closed.append(pts[0])
            
        A_poly = 0.0
        Qx_poly = 0.0
        Qy_poly = 0.0
        Ixx_poly = 0.0
        Iyy_poly = 0.0
        Ixy_poly = 0.0
        
        for i in range(len(pts_closed) - 1):
            xi, yi = pts_closed[i]
            xj, yj = pts_closed[i + 1]
            
            det = xi * yj - yi * xj
            
            A_poly += det
            Qx_poly += (xi + xj) * det
            Qy_poly += (yi + yj) * det
            Ixx_poly += (yi**2 + yi*yj + yj**2) * det
            Iyy_poly += (xi**2 + xi*xj + xj**2) * det
            Ixy_poly += (xi*yj + 2*xi*yi + 2*xj*yj + xj*yi) * det

        A_poly *= 0.5
        Qx_poly /= 6.0
        Qy_poly /= 6.0
        Ixx_poly /= 12.0
        Iyy_poly /= 12.0
        Ixy_poly /= 24.0
        
        # Enforce positive area for calculation logic, then apply sign based on hollow flag
        if A_poly < 0:
            A_poly = -A_poly
            Qx_poly = -Qx_poly
            Qy_poly = -Qy_poly
            Ixx_poly = -Ixx_poly
            Iyy_poly = -Iyy_poly
            Ixy_poly = -Ixy_poly
            
        sign = -1.0 if hollow else 1.0
        
        A_total += sign * A_poly
        Qx_total += sign * Qx_poly
        Qy_total += sign * Qy_poly
        Ixx_total += sign * Ixx_poly
        Iyy_total += sign * Iyy_poly
        Ixy_total += sign * Ixy_poly

    if not valid_contours or abs(A_total) < 1e-9:
        return SectionProperties()

    # Centroid
    Cx = Qx_total / A_total
    Cy = Qy_total / A_total
    
    # Shift Inertia to Centroid (Parallel Axis Theorem)
    Ix_c = Ixx_total - A_total * Cy**2
    Iy_c = Iyy_total - A_total * Cx**2
    Ixy_c = Ixy_total - A_total * Cx * Cy
    
    # Radii of Gyration
    rx = math.sqrt(Ix_c / A_total) if A_total > 0 and Ix_c > 0 else 0.0
    ry = math.sqrt(Iy_c / A_total) if A_total > 0 and Iy_c > 0 else 0.0
    
    # Extreme fibers (relative to Centroid)
    x_max = 0.0
    y_max = 0.0
    
    for pts, _ in contours:
        # Check all points, even for hollow contours, to find bounds
        for xi, yi in pts:
            dx = abs(xi - Cx)
            dy = abs(yi - Cy)
            if dx > x_max:
                x_max = dx
            if dy > y_max:
                y_max = dy
            
    # Section Moduli
    Sx = Ix_c / y_max if y_max > 1e-9 else 0.0
    Sy = Iy_c / x_max if x_max > 1e-9 else 0.0
    
    return SectionProperties(
        A=A_total, Cx=Cx, Cy=Cy,
        Ix=Ix_c, Iy=Iy_c, Ixy=Ixy_c,
        Sx=Sx, Sy=Sy, rx=rx, ry=ry,
        x_max=x_max, y_max=y_max
    )


def calculate_grid_properties(
    props: SectionProperties, 
    contours: List[Tuple[List[Point], bool]], 
    resolution: int = 100
) -> None:
    """
    Calculate properties requiring grid discretization (J, Zpl, Shear Center).
    Updates the passed SectionProperties object.
    
    Args:
        props: SectionProperties object to update
        contours: List of (points, hollow) tuples
        resolution: Grid resolution
    """
    from matplotlib.path import Path

    all_points: List[Point] = []
    for pts, _ in contours:
        all_points.extend(pts)
    
    if not all_points:
        return

    xs = [p[0] for p in all_points]
    ys = [p[1] for p in all_points]
    x_min, x_max_coord = min(xs), max(xs)
    y_min, y_max_coord = min(ys), max(ys)
    
    height = y_max_coord - y_min
    width = x_max_coord - x_min
    
    # Add padding
    padding = max(height, width) * 0.1
    if padding == 0:
        padding = 1.0
    
    # Grid limits
    y0 = y_min - padding
    x0 = x_min - padding
    
    # Determine step size h
    max_dim = max(height, width) + 2*padding
    h = max_dim / resolution
    
    ny = int((height + 2 * padding) / h)
    nx = int((width + 2 * padding) / h)
    
    # Create meshgrid coordinates
    y_vals = np.linspace(y0, y0 + (ny - 1) * h, ny)
    x_vals = np.linspace(x0, x0 + (nx - 1) * h, nx)
    
    Y, X = np.meshgrid(y_vals, x_vals, indexing='ij')
    pts_flat = np.column_stack((X.ravel(), Y.ravel()))
    
    # Create mask using matplotlib Path
    is_solid = np.zeros(len(pts_flat), dtype=bool)
    for pts, hollow in contours:
        if hollow or len(pts) < 3:
            continue
        path = Path(pts)
        is_solid |= path.contains_points(pts_flat)
        
    is_hole = np.zeros(len(pts_flat), dtype=bool)
    for pts, hollow in contours:
        if not hollow or len(pts) < 3:
            continue
        path = Path(pts)
        is_hole |= path.contains_points(pts_flat)
        
    final_mask_flat = is_solid & (~is_hole)
    mask = final_mask_flat.reshape((ny, nx))
    
    dA = h * h
    
    # --- Torsion Constant J ---
    # Solve Poisson equation: del^2 phi = -2 inside, phi = 0 on boundary
    from .utils import solve_poisson_jacobi
    
    phi = solve_poisson_jacobi(mask, h)
    
    # J = 2 * Volume under phi
    props.J = 2.0 * np.sum(phi) * dA
    
    # --- Plastic Section Modulus Zpl ---
    # Zpl = Integral |u - PNA| dA
    # PNA divides area in half
    
    rows, cols = np.where(mask)
    if len(rows) == 0:
        return
        
    y_coords = y_vals[rows]
    x_coords = x_vals[cols]
    
    # Zpl_x (Bending about x-axis -> PNA is y = const)
    sorted_y = np.sort(y_coords)
    mid_idx = len(sorted_y) // 2
    pna_y = sorted_y[mid_idx]
    props.Zpl_x = np.sum(np.abs(y_coords - pna_y)) * dA
    
    # Zpl_y (Bending about y-axis -> PNA is x = const)
    sorted_x = np.sort(x_coords)
    mid_idx = len(sorted_x) // 2
    pna_x = sorted_x[mid_idx]
    props.Zpl_y = np.sum(np.abs(x_coords - pna_x)) * dA
    
    # --- Shear Center ---
    _calculate_shear_center(props, contours)
    
    # --- Warping Constant Cw ---
    from .utils import solve_warping_jacobi
    
    # Solve Laplace for omega
    omega = solve_warping_jacobi(mask, h, props.Cx, props.Cy, x_vals, y_vals)
    
    # Extract omega values inside the section
    w = omega[mask]
    
    if len(w) > 0:
        # Normalize omega (Condition 1: Mean = 0)
        w_mean = np.mean(w)
        w0 = w - w_mean
        
        # Calculate warping moments
        # The coordinates x, y are already available for mask points in x_coords, y_coords
        # Relative to centroid
        x_c = x_coords - props.Cx
        y_c = y_coords - props.Cy
        
        _ = np.sum(w0 * x_c) * dA  # Integral w0 * x dA (unused)
        _ = np.sum(w0 * y_c) * dA  # Integral w0 * y dA (unused)
        
        # Calculate shear center coordinates (from warping definition)
        # Note: We already calculated SCy, SCz using a different method. 
        # Ideally they should match.
        
        # Normalized warping function (standard form in x,y):
        # wn = w0 - SCx*y + SCy*x  (coords relative to centroid)
        wn = w0 - props.SCx * y_c + props.SCy * x_c
        
        # Warping constant Cw = Integral wn^2 dA
        props.Cw = np.sum(wn**2) * dA


def _calculate_shear_center(
    props: SectionProperties, 
    contours: List[Tuple[List[Point], bool]]
) -> None:
    """
    Calculate shear center using numerical methods.
    
    The shear center is the point where transverse loads can be applied
    without causing torsion. For doubly symmetric sections it coincides
    with the centroid; for asymmetric sections it's offset.
    
    Method:
    - Detect symmetry using moments (most common case for structural sections)
    - For symmetric sections: SC lies on axis of symmetry or at centroid
    - For asymmetric sections: use sectorial coordinate approximation
    """
    Cx, Cy = props.Cx, props.Cy
    Ix, Iy, Ixy = props.Ix, props.Iy, props.Ixy
    A = props.A
    
    # Collect all boundary points for symmetry analysis
    all_points: List[Point] = []
    for pts, hollow in contours:
        if not hollow and len(pts) >= 3:
            all_points.extend(pts)
    
    if not all_points:
        props.SCx = Cx
        props.SCy = Cy
        return
    
    # Compute third moments (skewness) relative to centroid.
    # These indicate asymmetry about each axis.
    
    # Use boundary points to estimate third moments
    n = len(all_points)
    S_yyy = 0.0  # Third moment in y
    S_xxx = 0.0  # Third moment in x
    S_yyx = 0.0  # Mixed third moment
    S_yxx = 0.0  # Mixed third moment
    
    # Use Green's theorem-like approach for third moments
    for i in range(n):
        j = (i + 1) % n
        xi, yi = all_points[i]
        xj, yj = all_points[j]
        
        # Relative to centroid
        xi_c, yi_c = xi - Cx, yi - Cy
        xj_c, yj_c = xj - Cx, yj - Cy
        
        # Cross product (for area element direction)
        det = xi_c * yj_c - xj_c * yi_c
        
        # Third moment contributions (approximate using polygon vertices)
        S_yyy += (yi_c**3 + yi_c**2*yj_c + yi_c*yj_c**2 + yj_c**3) * det
        S_xxx += (xi_c**3 + xi_c**2*xj_c + xi_c*xj_c**2 + xj_c**3) * det
        S_yyx += (yi_c**2 + yi_c*yj_c + yj_c**2) * (xi_c + xj_c) * det
        S_yxx += (xi_c**2 + xi_c*xj_c + xj_c**2) * (yi_c + yj_c) * det
    
    S_yyy /= 20.0
    S_xxx /= 20.0
    S_yyx /= 24.0
    S_yxx /= 24.0
    
    # Characteristic length for symmetry tolerance
    char_length = math.sqrt(A) if A > 0 else 1.0
    tol = 1e-4 * char_length**3  # Relative tolerance for third moments
    
    # Check for symmetry (only odd moments need to be ~0).
    # Symmetric about x-axis (horizontal axis): odd powers of y should be ~0.
    # Symmetric about y-axis (vertical axis): odd powers of x should be ~0.
    x_symmetric = abs(S_yyy) < tol
    y_symmetric = abs(S_xxx) < tol
    
    if x_symmetric and y_symmetric:
        # Doubly symmetric - shear center at centroid
        props.SCx = Cx
        props.SCy = Cy
        return
    
    if x_symmetric:
        # Symmetric about x-axis (horizontal) - SC_y = Cy
        props.SCy = Cy
        # Need to compute SC_x offset using sectorial method
        e_x = _compute_shear_center_offset_x(all_points, Cx, Cy, Ix, Iy, Ixy)
        props.SCx = Cx + e_x
        return
    
    if y_symmetric:
        # Symmetric about y-axis (vertical) - SC_x = Cx
        props.SCx = Cx
        # Need to compute SC_y offset using sectorial method
        e_y = _compute_shear_center_offset_y(all_points, Cx, Cy, Ix, Iy, Ixy)
        props.SCy = Cy + e_y
        return
    
    # Asymmetric section - use full sectorial calculation
    e_y, e_x = _compute_shear_center_offsets(all_points, Cx, Cy, Ix, Iy, Ixy)
    props.SCy = Cy + e_y
    props.SCx = Cx + e_x


def _compute_shear_center_offsets(
    points: List[Point], 
    Cx: float, Cy: float,
    Ix: float, Iy: float, Ixy: float
) -> Tuple[float, float]:
    """
    Compute shear center offsets using sectorial coordinate method.
    Returns (e_y, e_x) offsets from centroid.
    """
    n = len(points)
    if n < 3:
        return 0.0, 0.0
    
    # Compute sectorial coordinates and segment lengths
    omega = [0.0] * n
    ds_list: List[float] = []
    
    for i in range(n):
        j = (i + 1) % n
        xi, yi = points[i]
        xj, yj = points[j]
        
        ds = math.sqrt((xj - xi)**2 + (yj - yi)**2)
        ds_list.append(ds)
        
        ri_x, ri_y = xi - Cx, yi - Cy
        rj_x, rj_y = xj - Cx, yj - Cy
        
        d_omega = ri_x * rj_y - ri_y * rj_x
        if j > 0:
            omega[j] = omega[i] + d_omega
    
    # Normalize sectorial coordinates
    total_perimeter = sum(ds_list)
    if total_perimeter > 1e-9:
        omega_ds_sum = sum(0.5 * (omega[i] + omega[(i+1) % n]) * ds_list[i] for i in range(n))
        omega_mean = omega_ds_sum / total_perimeter
        omega = [w - omega_mean for w in omega]
    
    # Compute sectorial products
    I_omega_y = 0.0
    I_omega_x = 0.0
    
    for i in range(n):
        j = (i + 1) % n
        xi, yi = points[i]
        xj, yj = points[j]
        
        omega_avg = 0.5 * (omega[i] + omega[j])
        y_avg = 0.5 * (yi + yj) - Cy
        x_avg = 0.5 * (xi + xj) - Cx
        ds = ds_list[i]
        
        I_omega_y += omega_avg * y_avg * ds
        I_omega_x += omega_avg * x_avg * ds
    
    # Compute offsets
    det = Ix * Iy - Ixy * Ixy
    
    if abs(det) > 1e-12:
        e_y = (-Iy * I_omega_x + Ixy * I_omega_y) / det
        e_x = (Ix * I_omega_y - Ixy * I_omega_x) / det
    else:
        e_y = -I_omega_x / Iy if abs(Iy) > 1e-12 else 0.0
        e_x = I_omega_y / Ix if abs(Ix) > 1e-12 else 0.0
    
    return e_y, e_x


def _compute_shear_center_offset_y(
    points: List[Point],
    Cx: float, Cy: float,
    Ix: float, Iy: float, Ixy: float
) -> float:
    """Compute y-offset of shear center for section symmetric about y-axis."""
    e_y, _ = _compute_shear_center_offsets(points, Cx, Cy, Ix, Iy, Ixy)
    return e_y


def _compute_shear_center_offset_x(
    points: List[Point],
    Cx: float, Cy: float,  
    Ix: float, Iy: float, Ixy: float
) -> float:
    """Compute x-offset of shear center for section symmetric about x-axis."""
    _, e_x = _compute_shear_center_offsets(points, Cx, Cy, Ix, Iy, Ixy)
    return e_x
