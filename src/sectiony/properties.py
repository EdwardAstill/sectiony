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
    Cy: float = 0.0
    Cz: float = 0.0
    Iy: float = 0.0
    Iz: float = 0.0
    Iyz: float = 0.0
    J: float = 0.0
    Sy: float = 0.0
    Sz: float = 0.0
    ry: float = 0.0
    rz: float = 0.0
    y_max: float = 0.0
    z_max: float = 0.0
    Zpl_y: float = 0.0
    Zpl_z: float = 0.0
    Cw: float = 0.0  # Warping constant
    SCy: float = 0.0  # Shear center y-coordinate
    SCz: float = 0.0  # Shear center z-coordinate


def calculate_exact_properties(contours: List[Tuple[List[Point], bool]]) -> SectionProperties:
    """
    Calculate exact geometric properties (Area, Centroids, Inertia) using Green's Theorem.
    
    Args:
        contours: List of (points, hollow) tuples
        
    Returns:
        SectionProperties with exact values calculated
    """
    A_total = 0.0
    Qz_total = 0.0  # Integral y dA
    Qy_total = 0.0  # Integral z dA
    Izz_total = 0.0  # Integral y^2 dA
    Iyy_total = 0.0  # Integral z^2 dA
    Iyz_total = 0.0  # Integral yz dA
    
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
        Qz_poly = 0.0
        Qy_poly = 0.0
        Izz_poly = 0.0
        Iyy_poly = 0.0
        Iyz_poly = 0.0
        
        for i in range(len(pts_closed) - 1):
            yi, zi = pts_closed[i]
            yj, zj = pts_closed[i+1]
            
            det = yi * zj - zi * yj
            
            A_poly += det
            Qz_poly += (yi + yj) * det
            Qy_poly += (zi + zj) * det
            Izz_poly += (yi**2 + yi*yj + yj**2) * det
            Iyy_poly += (zi**2 + zi*zj + zj**2) * det
            Iyz_poly += (yi*zj + 2*yi*zi + 2*yj*zj + yj*zi) * det

        A_poly *= 0.5
        Qz_poly /= 6.0
        Qy_poly /= 6.0
        Izz_poly /= 12.0
        Iyy_poly /= 12.0
        Iyz_poly /= 24.0
        
        # Enforce positive area for calculation logic, then apply sign based on hollow flag
        if A_poly < 0:
            A_poly = -A_poly
            Qz_poly = -Qz_poly
            Qy_poly = -Qy_poly
            Izz_poly = -Izz_poly
            Iyy_poly = -Iyy_poly
            Iyz_poly = -Iyz_poly
            
        sign = -1.0 if hollow else 1.0
        
        A_total += sign * A_poly
        Qz_total += sign * Qz_poly
        Qy_total += sign * Qy_poly
        Izz_total += sign * Izz_poly
        Iyy_total += sign * Iyy_poly
        Iyz_total += sign * Iyz_poly

    if not valid_contours or abs(A_total) < 1e-9:
        return SectionProperties()

    # Centroid
    Cy = Qz_total / A_total
    Cz = Qy_total / A_total
    
    # Shift Inertia to Centroid (Parallel Axis Theorem)
    Iy_c = Iyy_total - A_total * Cz**2
    Iz_c = Izz_total - A_total * Cy**2
    Iyz_c = Iyz_total - A_total * Cy * Cz
    
    # Radii of Gyration
    ry = math.sqrt(Iy_c / A_total) if A_total > 0 and Iy_c > 0 else 0.0
    rz = math.sqrt(Iz_c / A_total) if A_total > 0 and Iz_c > 0 else 0.0
    
    # Extreme fibers (relative to Centroid)
    y_max = 0.0
    z_max = 0.0
    
    for pts, _ in contours:
        # Check all points, even for hollow contours, to find bounds
        for yi, zi in pts:
            dy = abs(yi - Cy)
            dz = abs(zi - Cz)
            if dy > y_max:
                y_max = dy
            if dz > z_max:
                z_max = dz
            
    # Section Moduli
    Sy = Iy_c / z_max if z_max > 1e-9 else 0.0
    Sz = Iz_c / y_max if y_max > 1e-9 else 0.0
    
    return SectionProperties(
        A=A_total, Cy=Cy, Cz=Cz,
        Iy=Iy_c, Iz=Iz_c, Iyz=Iyz_c,
        Sy=Sy, Sz=Sz, ry=ry, rz=rz,
        y_max=y_max, z_max=z_max
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

    ys = [p[0] for p in all_points]
    zs = [p[1] for p in all_points]
    y_min, y_max_coord = min(ys), max(ys)
    z_min, z_max_coord = min(zs), max(zs)
    
    height = y_max_coord - y_min
    width = z_max_coord - z_min
    
    # Add padding
    padding = max(height, width) * 0.1
    if padding == 0:
        padding = 1.0
    
    # Grid limits
    y0 = y_min - padding
    z0 = z_min - padding
    
    # Determine step size h
    max_dim = max(height, width) + 2*padding
    h = max_dim / resolution
    
    ny = int((height + 2*padding) / h)
    nz = int((width + 2*padding) / h)
    
    # Create meshgrid coordinates
    y_vals = np.linspace(y0, y0 + (ny-1)*h, ny)
    z_vals = np.linspace(z0, z0 + (nz-1)*h, nz)
    
    Y, Z = np.meshgrid(y_vals, z_vals, indexing='ij')
    pts_flat = np.column_stack((Y.ravel(), Z.ravel()))
    
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
    mask = final_mask_flat.reshape((ny, nz))
    
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
    z_coords = z_vals[cols]
    
    # Zpl_z (Bending about z-axis / vertical bending -> PNA is y = const)
    sorted_y = np.sort(y_coords)
    mid_idx = len(sorted_y) // 2
    pna_y = sorted_y[mid_idx]
    props.Zpl_z = np.sum(np.abs(y_coords - pna_y)) * dA
    
    # Zpl_y (Bending about y-axis / horizontal bending -> PNA is z = const)
    sorted_z = np.sort(z_coords)
    mid_idx = len(sorted_z) // 2
    pna_z = sorted_z[mid_idx]
    props.Zpl_y = np.sum(np.abs(z_coords - pna_z)) * dA
    
    # --- Shear Center ---
    _calculate_shear_center(props, contours)
    
    # --- Warping Constant Cw ---
    from .utils import solve_warping_jacobi
    
    # Solve Laplace for omega
    omega = solve_warping_jacobi(mask, h, props.Cy, props.Cz, y_vals, z_vals)
    
    # Extract omega values inside the section
    w = omega[mask]
    
    if len(w) > 0:
        # Normalize omega (Condition 1: Mean = 0)
        w_mean = np.mean(w)
        w0 = w - w_mean
        
        # Calculate warping moments
        # The coordinates y, z are already available for mask points in y_coords, z_coords
        # Relative to centroid
        y_c = y_coords - props.Cy
        z_c = z_coords - props.Cz
        
        Iw_z = np.sum(w0 * z_c) * dA  # Integral w0 * z dA
        Iw_y = np.sum(w0 * y_c) * dA  # Integral w0 * y dA
        
        # Calculate shear center coordinates (from warping definition)
        # Note: We already calculated SCy, SCz using a different method. 
        # Ideally they should match.
        
        # Normalized warping function: wn = w0 - SCz * y + SCy * z
        # (Note: Using SC from properties)
        # Check signs: 
        # Standard: wn = w0 - x_s * y + y_s * x (using x,y)
        # Here (y,z): wn = w0 - z_s * y + y_s * z ?
        # Let's verify with dimensions: w ~ L^2. z_s * y ~ L^2. Correct.
        
        wn = w0 - props.SCz * y_c + props.SCy * z_c
        
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
    Cy, Cz = props.Cy, props.Cz
    Iy, Iz, Iyz = props.Iy, props.Iz, props.Iyz
    A = props.A
    
    # Collect all boundary points for symmetry analysis
    all_points: List[Point] = []
    for pts, hollow in contours:
        if not hollow and len(pts) >= 3:
            all_points.extend(pts)
    
    if not all_points:
        props.SCy = Cy
        props.SCz = Cz
        return
    
    # Compute third moments (skewness) relative to centroid
    # These indicate asymmetry about each axis
    # S_yyy = ∫y³dA indicates asymmetry about z-axis (affects SC_y)
    # S_zzz = ∫z³dA indicates asymmetry about y-axis (affects SC_z)
    
    # Use boundary points to estimate third moments
    n = len(all_points)
    S_yyy = 0.0  # Third moment in y
    S_zzz = 0.0  # Third moment in z
    S_yyz = 0.0  # Mixed third moment
    S_yzz = 0.0  # Mixed third moment
    
    # Use Green's theorem-like approach for third moments
    for i in range(n):
        j = (i + 1) % n
        yi, zi = all_points[i]
        yj, zj = all_points[j]
        
        # Relative to centroid
        yi_c, zi_c = yi - Cy, zi - Cz
        yj_c, zj_c = yj - Cy, zj - Cz
        
        # Cross product (for area element direction)
        det = yi_c * zj_c - yj_c * zi_c
        
        # Third moment contributions (approximate using polygon vertices)
        S_yyy += (yi_c**3 + yi_c**2*yj_c + yi_c*yj_c**2 + yj_c**3) * det
        S_zzz += (zi_c**3 + zi_c**2*zj_c + zi_c*zj_c**2 + zj_c**3) * det
        S_yyz += (yi_c**2 + yi_c*yj_c + yj_c**2) * (zi_c + zj_c) * det
        S_yzz += (zi_c**2 + zi_c*zj_c + zj_c**2) * (yi_c + yj_c) * det
    
    S_yyy /= 20.0
    S_zzz /= 20.0
    S_yyz /= 24.0
    S_yzz /= 24.0
    
    # Characteristic length for symmetry tolerance
    char_length = math.sqrt(A) if A > 0 else 1.0
    tol = 1e-4 * char_length**3  # Relative tolerance for third moments
    
    # Check for symmetry (only odd moments need to be zero)
    # z-symmetry (symmetric about horizontal axis y=Cy): odd powers of y should be ~0
    # y-symmetry (symmetric about vertical axis z=Cz): odd powers of z should be ~0
    z_symmetric = abs(S_yyy) < tol  # Symmetric about z-axis (horizontal line through centroid)
    y_symmetric = abs(S_zzz) < tol  # Symmetric about y-axis (vertical line through centroid)
    
    if z_symmetric and y_symmetric:
        # Doubly symmetric - shear center at centroid
        props.SCy = Cy
        props.SCz = Cz
        return
    
    if z_symmetric:
        # Symmetric about z-axis (horizontal) - SC_y = Cy
        props.SCy = Cy
        # Need to compute SC_z offset using sectorial method
        e_z = _compute_shear_center_offset_z(all_points, Cy, Cz, Iy, Iz, Iyz)
        props.SCz = Cz + e_z
        return
    
    if y_symmetric:
        # Symmetric about y-axis (vertical) - SC_z = Cz  
        props.SCz = Cz
        # Need to compute SC_y offset using sectorial method
        e_y = _compute_shear_center_offset_y(all_points, Cy, Cz, Iy, Iz, Iyz)
        props.SCy = Cy + e_y
        return
    
    # Asymmetric section - use full sectorial calculation
    e_y, e_z = _compute_shear_center_offsets(all_points, Cy, Cz, Iy, Iz, Iyz)
    props.SCy = Cy + e_y
    props.SCz = Cz + e_z


def _compute_shear_center_offsets(
    points: List[Point], 
    Cy: float, Cz: float,
    Iy: float, Iz: float, Iyz: float
) -> Tuple[float, float]:
    """
    Compute shear center offsets using sectorial coordinate method.
    Returns (e_y, e_z) offsets from centroid.
    """
    n = len(points)
    if n < 3:
        return 0.0, 0.0
    
    # Compute sectorial coordinates and segment lengths
    omega = [0.0] * n
    ds_list: List[float] = []
    
    for i in range(n):
        j = (i + 1) % n
        yi, zi = points[i]
        yj, zj = points[j]
        
        ds = math.sqrt((yj - yi)**2 + (zj - zi)**2)
        ds_list.append(ds)
        
        ri_y, ri_z = yi - Cy, zi - Cz
        rj_y, rj_z = yj - Cy, zj - Cz
        
        d_omega = ri_y * rj_z - ri_z * rj_y
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
    I_omega_z = 0.0
    
    for i in range(n):
        j = (i + 1) % n
        yi, zi = points[i]
        yj, zj = points[j]
        
        omega_avg = 0.5 * (omega[i] + omega[j])
        y_avg = 0.5 * (yi + yj) - Cy
        z_avg = 0.5 * (zi + zj) - Cz
        ds = ds_list[i]
        
        I_omega_y += omega_avg * y_avg * ds
        I_omega_z += omega_avg * z_avg * ds
    
    # Compute offsets
    det = Iy * Iz - Iyz * Iyz
    
    if abs(det) > 1e-12:
        e_y = (-Iy * I_omega_z + Iyz * I_omega_y) / det
        e_z = (Iz * I_omega_y - Iyz * I_omega_z) / det
    else:
        e_y = -I_omega_z / Iz if abs(Iz) > 1e-12 else 0.0
        e_z = I_omega_y / Iy if abs(Iy) > 1e-12 else 0.0
    
    return e_y, e_z


def _compute_shear_center_offset_y(
    points: List[Point],
    Cy: float, Cz: float,
    Iy: float, Iz: float, Iyz: float
) -> float:
    """Compute y-offset of shear center for section symmetric about y-axis."""
    e_y, _ = _compute_shear_center_offsets(points, Cy, Cz, Iy, Iz, Iyz)
    return e_y


def _compute_shear_center_offset_z(
    points: List[Point],
    Cy: float, Cz: float,  
    Iy: float, Iz: float, Iyz: float
) -> float:
    """Compute z-offset of shear center for section symmetric about z-axis."""
    _, e_z = _compute_shear_center_offsets(points, Cy, Cz, Iy, Iz, Iyz)
    return e_z
