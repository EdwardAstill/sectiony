from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Any, Optional
import numpy as np
import math

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

def calculate_exact_properties(shapes: List[Any]) -> SectionProperties:
    """
    Calculate exact geometric properties (Area, Centroids, Inertia) using Green's Theorem.
    """
    A_total = 0.0
    Qz_total = 0.0 # Integral y dA
    Qy_total = 0.0 # Integral z dA
    Izz_total = 0.0 # Integral y^2 dA
    Iyy_total = 0.0 # Integral z^2 dA
    Iyz_total = 0.0 # Integral yz dA
    
    valid_shapes = False

    for shape in shapes:
        pts = shape.points
        if not pts or len(pts) < 3:
            continue
        
        valid_shapes = True
        
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
            
        sign = -1.0 if shape.hollow else 1.0
        
        A_total += sign * A_poly
        Qz_total += sign * Qz_poly
        Qy_total += sign * Qy_poly
        Izz_total += sign * Izz_poly
        Iyy_total += sign * Iyy_poly
        Iyz_total += sign * Iyz_poly

    if not valid_shapes or abs(A_total) < 1e-9:
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
    
    for shape in shapes:
        # Check all points, even for hollow shapes, to find bounds
        for yi, zi in shape.points:
            dy = abs(yi - Cy)
            dz = abs(zi - Cz)
            if dy > y_max: y_max = dy
            if dz > z_max: z_max = dz
            
    # Section Moduli
    Sy = Iy_c / z_max if z_max > 1e-9 else 0.0
    Sz = Iz_c / y_max if y_max > 1e-9 else 0.0
    
    return SectionProperties(
        A=A_total, Cy=Cy, Cz=Cz,
        Iy=Iy_c, Iz=Iz_c, Iyz=Iyz_c,
        Sy=Sy, Sz=Sz, ry=ry, rz=rz,
        y_max=y_max, z_max=z_max
    )

def calculate_grid_properties(props: SectionProperties, shapes: List[Any], resolution: int = 100):
    """
    Calculate properties requiring grid discretization (J, Zpl).
    Updates the passed SectionProperties object.
    """
    from matplotlib.path import Path

    all_points = []
    for s in shapes:
        all_points.extend(s.points)
    
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
    if padding == 0: padding = 1.0
    
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
    for s in shapes:
        if s.hollow or len(s.points) < 3: continue
        path = Path(s.points)
        is_solid |= path.contains_points(pts_flat)
        
    is_hole = np.zeros(len(pts_flat), dtype=bool)
    for s in shapes:
        if not s.hollow or len(s.points) < 3: continue
        path = Path(s.points)
        is_hole |= path.contains_points(pts_flat)
        
    final_mask_flat = is_solid & (~is_hole)
    mask = final_mask_flat.reshape((ny, nz))
    
    dA = h * h
    
    # --- Torsion Constant J ---
    # Solve Poisson equation: del^2 phi = -2 inside, phi = 0 on boundary
    # Simple iterative solver
    phi = np.zeros((ny, nz))
    max_iter = 5000
    tol = 1e-6
    source = 2.0 * h * h
    
    # Indices for interior points
    # (Excluding grid boundaries which are definitely 0 as they are padded)
    
    for _ in range(max_iter):
        phi_old = phi.copy()
        
        # Vectorized Jacobi update
        neighbors = np.zeros_like(phi)
        neighbors[1:-1, 1:-1] = (phi[0:-2, 1:-1] + phi[2:, 1:-1] + 
                                 phi[1:-1, 0:-2] + phi[1:-1, 2:])
        
        phi_new = 0.25 * (neighbors + source)
        
        # Enforce boundary conditions (phi = 0 outside section)
        phi_new[~mask] = 0.0
        
        # Relaxation / Update
        phi = phi_new
        
        if np.max(np.abs(phi - phi_old)) < tol:
            break
            
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
