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
            if abs(curr_sum - prev_sum) < tol * max(abs(curr_sum), 1.0):
                break
            prev_sum = curr_sum
    
    return phi


#need something to handle coordinates, by default it should be (horizontal,vertical for the points) - implement this later
