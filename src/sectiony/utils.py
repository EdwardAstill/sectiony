# utils.py
from __future__ import annotations
import numpy as np

def heaviside(x: float) -> float:
    """Simple Heaviside step (0 for x<0, 1 for x>=0)."""
    return 0.0 if x < 0.0 else 1.0

def clip_to_span(x: float, L: float) -> float:
    """Clamp x to [0, L] for safety."""
    return max(0.0, min(L, x))


def solve_poisson_jacobi(mask: np.ndarray, h: float, max_iter: int = 5000, tol: float = 1e-6) -> np.ndarray:
    """
    Solve Poisson equation del^2(phi) = -2 for torsion using optimized Jacobi.
    
    Optimizations over naive implementation:
    - Pre-allocated buffers (no allocations in loop)
    - Convergence checked via relative change in sum (cheaper than max diff)
    - Early exit based on solution stability
    
    Args:
        mask: Boolean array, True where phi is solved, False where phi=0 (boundary)
        h: Grid spacing
        max_iter: Maximum iterations
        tol: Convergence tolerance
        
    Returns:
        phi: Solution array
    """
    ny, nz = mask.shape
    source = 2.0 * h * h
    
    # Pre-allocate both buffers once
    phi = np.zeros((ny, nz), dtype=np.float64)
    phi_new = np.zeros((ny, nz), dtype=np.float64)
    
    prev_sum = 0.0
    
    for iteration in range(max_iter):
        # Vectorized Jacobi update (in-place into phi_new)
        # Only update inside the mask
        # Note: We rely on phi being 0 outside mask, so boundary neighbors are handled implicitly as 0
        
        # Standard 5-point stencil
        phi_new[1:-1, 1:-1] = 0.25 * (
            phi[:-2, 1:-1] + phi[2:, 1:-1] + 
            phi[1:-1, :-2] + phi[1:-1, 2:] + source
        )
        
        # Apply boundary (phi = 0 outside section)
        phi_new[~mask] = 0.0
        
        # Swap buffers (no copy!)
        phi, phi_new = phi_new, phi
        
        # Check convergence every 10 iterations (cheaper)
        if iteration % 10 == 9:
            curr_sum = np.sum(phi)
            # Avoid division by zero
            denom = max(abs(curr_sum), 1.0)
            if abs(curr_sum - prev_sum) < tol * denom:
                break
            prev_sum = curr_sum
    
    return phi


def solve_warping_jacobi(
    mask: np.ndarray, 
    h: float, 
    cy: float, 
    cz: float, 
    y_vals: np.ndarray, 
    z_vals: np.ndarray,
    max_iter: int = 5000, 
    tol: float = 1e-6
) -> np.ndarray:
    """
    Solve Laplace equation del^2(omega) = 0 with Neumann BCs for warping function.
    
    BC: d(omega)/dn = y*nz - z*ny
    (Using coordinates relative to centroid)
    
    Args:
        mask: Boolean array (True inside section)
        h: Grid spacing
        cy, cz: Centroid coordinates
        y_vals: Array of y coordinates for rows
        z_vals: Array of z coordinates for cols
        
    Returns:
        omega: Solution array
    """
    ny, nz = mask.shape
    omega = np.zeros((ny, nz), dtype=np.float64)
    omega_new = np.zeros((ny, nz), dtype=np.float64)
    
    # Pre-calculate coordinates relative to centroid
    # Y varies along rows (axis 0), Z varies along cols (axis 1)
    # y_vals corresponds to axis 0 indices
    # z_vals corresponds to axis 1 indices
    Y, Z = np.meshgrid(y_vals, z_vals, indexing='ij')
    Yc = Y - cy
    Zc = Z - cz
    
    # Pre-compute boundary fluxes for each direction
    # Flux q = y*nz - z*ny
    # Top neighbor (y-h): n=(-1, 0) -> q = y(0) - z(-1) = z
    # Bottom neighbor (y+h): n=(1, 0) -> q = y(0) - z(1) = -z
    # Left neighbor (z-h): n=(0, -1) -> q = y(-1) - z(0) = -y
    # Right neighbor (z+h): n=(0, 1) -> q = y(1) - z(0) = y
    
    # Flux * h terms to add to center value
    # If neighbor is missing, we use ghost point: omega_neighbor = omega_self + h*q
    # So we add h*q to the sum in the update rule
    
    flux_top = Zc * h
    flux_bottom = -Zc * h
    flux_left = -Yc * h
    flux_right = Yc * h
    
    # Identify interior and boundary cells
    # We only update cells within the mask
    # For each cell in mask, we check neighbors
    
    # Shifted masks for neighbors (True if neighbor is IN mask)
    mask_top = np.zeros_like(mask)
    mask_top[1:, :] = mask[:-1, :]
    
    mask_bottom = np.zeros_like(mask)
    mask_bottom[:-1, :] = mask[1:, :]
    
    mask_left = np.zeros_like(mask)
    mask_left[:, 1:] = mask[:, :-1]
    
    mask_right = np.zeros_like(mask)
    mask_right[:, :-1] = mask[:, 1:]
    
    # For vectorized operations, we only care about pixels in the mask
    # To optimize, we can use simple iteration with boolean indexing or just iterate whole array
    # Iterating whole array is cleaner code, masked at end
    
    prev_sum = 0.0
    
    for iteration in range(max_iter):
        # We construct the sum of neighbors
        # Start with 0
        neighbor_sum = np.zeros_like(omega)
        
        # Add Top Neighbor
        # If top is in mask, take value. Else take self + flux
        # Actually easier: Take top value (masked 0) + (if top not in mask: self + flux)
        # But self is from previous step? Yes. Jacobi uses previous step.
        
        # Optimization:
        # 4*new = (val_top + val_bottom + val_left + val_right)
        # val_top = omega[y-1] if inside else (omega[y] + flux_top)
        
        # Since this logic is complex to vectorize efficiently without heavy memory use,
        # let's do it in steps.
        
        # Get shifted arrays (padded with 0)
        # These represent omega[y-1], omega[y+1], etc.
        o_top = np.zeros_like(omega); o_top[1:, :] = omega[:-1, :]
        o_bot = np.zeros_like(omega); o_bot[:-1, :] = omega[1:, :]
        o_lft = np.zeros_like(omega); o_lft[:, 1:] = omega[:, :-1]
        o_rgt = np.zeros_like(omega); o_rgt[:, :-1] = omega[:, 1:]
        
        # Add contributions
        # If neighbor exists (mask_top True), use o_top. 
        # Else use omega (self) + flux_top
        
        # Term 1: Top
        term = np.where(mask_top, o_top, omega + flux_top)
        neighbor_sum += term
        
        # Term 2: Bottom
        term = np.where(mask_bottom, o_bot, omega + flux_bottom)
        neighbor_sum += term
        
        # Term 3: Left
        term = np.where(mask_left, o_lft, omega + flux_left)
        neighbor_sum += term
        
        # Term 4: Right
        term = np.where(mask_right, o_rgt, omega + flux_right)
        neighbor_sum += term
        
        # Update
        omega_new = 0.25 * neighbor_sum
        
        # Enforce mask (outside is 0, though it doesn't matter for next step's inside calc)
        omega_new[~mask] = 0.0
        
        # Swap
        omega, omega_new = omega_new, omega
        
        # Convergence check
        if iteration % 20 == 0:
            # Normalize to avoid drift (Neumann problem has arbitrary constant)
            # Fix mean to 0 every few steps to keep values in reasonable range
            if np.any(mask):
                mean_val = np.mean(omega[mask])
                omega[mask] -= mean_val
                
            curr_sum = np.sum(np.abs(omega)) # Use sum abs for convergence
            denom = max(curr_sum, 1.0)
            if abs(curr_sum - prev_sum) < tol * denom:
                break
            prev_sum = curr_sum
            
    return omega
