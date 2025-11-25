from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as tri
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .section import Section

@dataclass
class Stress:
    """
    Calculates and visualizes stress distribution on a cross-section
    for a given set of internal forces.
    """
    section: Section
    N: float = 0.0   # Axial Force
    Vy: float = 0.0  # Shear Force in Y (Vertical)
    Vz: float = 0.0  # Shear Force in Z (Horizontal)
    Mx: float = 0.0  # Torsional Moment (T)
    My: float = 0.0  # Bending Moment about Y axis (Bending in X-Z plane)
    Mz: float = 0.0  # Bending Moment about Z axis (Bending in X-Y plane)

    def sigma_axial(self, y: float, z: float) -> float:
        """Calculates normal stress due to axial force (N/A)."""
        if self.section.A is None or self.section.A == 0:
            return 0.0
        return self.N / self.section.A

    def sigma_bending(self, y: float, z: float) -> float:
        """
        Calculates normal stress due to bending moments.
        Formula: sigma = (My * z) / Iy - (Mz * y) / Iz
        Assumes local coordinate system where y is vertical, z is horizontal,
        and origin is at the centroid.
        """
        sigma = 0.0
        if self.section.Iy and self.section.Iy != 0:
            sigma += (self.My * z) / self.section.Iy
        if self.section.Iz and self.section.Iz != 0:
            # Standard beam convention: positive Mz compresses positive y (top fibers)
            # Hence the minus sign.
            sigma -= (self.Mz * y) / self.section.Iz
        return sigma

    def sigma(self, y: float, z: float) -> float:
        """Total normal stress: sigma_axial + sigma_bending."""
        return self.sigma_axial(y, z) + self.sigma_bending(y, z)

    def tau_shear(self, y: float, z: float) -> float:
        """
        Calculates shear stress magnitude due to transverse shear forces (Vy, Vz).
        
        NOTE: This is a simplified placeholder. Accurate shear stress distribution
        requires numerical integration (shear flow) or FEA.
        
        Current approximation: Average shear stress (V/A).
        """
        if self.section.A is None or self.section.A == 0:
            return 0.0
        
        # Very rough approximation for now
        tau_y = self.Vy / self.section.A
        tau_z = self.Vz / self.section.A
        return np.sqrt(tau_y**2 + tau_z**2)

    def tau_torsion(self, y: float, z: float) -> float:
        """
        Calculates shear stress due to torsion (Mx).
        
        NOTE: This is a simplified placeholder. Accurate torsional stress
        requires solving Poisson's equation.
        
        Current approximation: Max shear stress on outer boundary for a circular section
        tau = Tr/J, scaled by distance from centroid.
        """
        if self.section.J is None or self.section.J == 0:
            return 0.0
        
        r = np.sqrt(y**2 + z**2)
        # T * r / J
        return abs(self.Mx * r / self.section.J)

    def tau(self, y: float, z: float) -> float:
        """Total shear stress magnitude estimate."""
        # Conservative addition of magnitudes (worst case alignment)
        # In reality, these are vectors and should be added vectorially.
        return self.tau_shear(y, z) + self.tau_torsion(y, z)

    def von_mises(self, y: float, z: float) -> float:
        """Calculates Von Mises yield criterion: sqrt(sigma^2 + 3*tau^2)."""
        s = self.sigma(y, z)
        t = self.tau(y, z)
        return np.sqrt(s**2 + 3 * t**2)

    def _get_stress_func(self, type: str):
        if type == "sigma": return self.sigma
        if type == "sigma_axial": return self.sigma_axial
        if type == "sigma_bending": return self.sigma_bending
        if type == "tau": return self.tau
        if type == "von_mises": return self.von_mises
        raise ValueError(f"Unknown stress type: {type}")

    def max(self, type: str = "von_mises") -> float:
        """Returns the maximum value of the specified stress component over the geometry."""
        # Sampling points on the geometry boundary + mesh
        # For now, let's just sample vertices of the geometry shapes
        if not self.section.geometry:
            return 0.0
            
        func = self._get_stress_func(type)
        max_val = -float('inf')
        
        for shape in self.section.geometry.shapes:
            for y, z in shape.points: # Points are (y, z)
                # Note: inputs to funcs are (y, z), points are (y, z)
                val = func(y, z)
                if val > max_val:
                    max_val = val
        return max_val

    def min(self, type: str = "von_mises") -> float:
        """Returns the minimum value of the specified stress component."""
        if not self.section.geometry:
            return 0.0
            
        func = self._get_stress_func(type)
        min_val = float('inf')
        
        for shape in self.section.geometry.shapes:
            for y, z in shape.points:
                val = func(y, z)
                if val < min_val:
                    min_val = val
        return min_val

    def plot(self, type: str = "von_mises", ax: Optional[plt.Axes] = None, show: bool = True):
        """
        Generates a contour plot of the specified stress component over the section geometry.
        """
        if not self.section.geometry:
            print("No geometry to plot.")
            return

        if ax is None:
            fig, ax = plt.subplots()
        
        func = self._get_stress_func(type)
        
        # Triangulate the polygon for plotting
        # Simple ear clipping or relying on matplotlib's triangulation might be needed
        # For now, we'll create a mesh grid over the bounding box and mask it
        
        # 1. Determine bounding box
        all_ys = []
        all_zs = []
        for s in self.section.geometry.shapes:
            all_ys.extend(p[0] for p in s.points)
            all_zs.extend(p[1] for p in s.points)
            
        if not all_ys: return
        
        min_y, max_y = min(all_ys), max(all_ys)
        min_z, max_z = min(all_zs), max(all_zs)
        
        padding = max(max_y - min_y, max_z - min_z) * 0.1
        if padding == 0: padding = 1.0
        
        # Create grid
        resolution = 100
        z_grid = np.linspace(min_z - padding, max_z + padding, resolution)
        y_grid = np.linspace(min_y - padding, max_y + padding, resolution)
        Z, Y = np.meshgrid(z_grid, y_grid)
        
        # Calculate stress on grid
        # Vectorized calculation would be better, but loop is safer for arbitrary functions
        S = np.zeros_like(Z)
        for i in range(Z.shape[0]):
            for j in range(Z.shape[1]):
                S[i, j] = func(Y[i, j], Z[i, j])
                
        # Mask points outside the polygon
        from matplotlib.path import Path
        
        mask = np.ones_like(Z, dtype=bool)
        
        # Generally we want to include points inside solids and exclude holes
        # Simplistic approach: Check if inside any solid and not inside any hole
        solids = [s for s in self.section.geometry.shapes if not s.hollow]
        hollows = [s for s in self.section.geometry.shapes if s.hollow]
        
        points_flat = np.column_stack((Y.flatten(), Z.flatten()))
        
        # Check solids (union)
        is_in_solid = np.zeros(len(points_flat), dtype=bool)
        for solid in solids:
            # path expects (x, y) -> (z, y) for us? 
            # Wait, Path.contains_points expects points matching the vertices.
            # Our vertices are (y, z). Our points are (y, z).
            path = Path(solid.points) 
            is_in_solid |= path.contains_points(points_flat)
            
        # Check hollows (subtraction)
        is_in_hollow = np.zeros(len(points_flat), dtype=bool)
        for hollow in hollows:
            path = Path(hollow.points)
            is_in_hollow |= path.contains_points(points_flat)
            
        final_mask = is_in_solid & (~is_in_hollow)
        
        # Apply mask (NaN out invalid points)
        S_flat = S.flatten()
        S_flat[~final_mask] = np.nan
        S = S_flat.reshape(S.shape)
        
        # Plot contours
        # Note: Plot (z, y) so z is horizontal x-axis
        contour = ax.contourf(Z, Y, S, cmap='viridis', levels=20)
        plt.colorbar(contour, ax=ax, label=f'{type} Stress')
        
        # Draw outlines
        for s in self.section.geometry.shapes:
            # (y, z) -> plot (z, y)
            zs = [p[1] for p in s.points] + [s.points[0][1]]
            ys = [p[0] for p in s.points] + [s.points[0][0]]
            color = 'white' if s.hollow else 'black'
            linestyle = '--' if s.hollow else '-'
            ax.plot(zs, ys, color=color, linestyle=linestyle, linewidth=1)
            
        ax.set_aspect('equal')
        ax.set_xlabel('z (Horizontal)')
        ax.set_ylabel('y (Vertical)')
        ax.set_title(f'{type} Stress Distribution')
        
        if show:
            plt.show()
            
        return ax
