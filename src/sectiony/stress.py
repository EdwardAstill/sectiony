from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING, Literal, Callable, List, Tuple

if TYPE_CHECKING:
    from .section import Section
    from .geometry import Contour

# Type alias for stress calculation function
StressFunc = Callable[[float, float], float]

# Type alias for points
Point = Tuple[float, float]

# Supported stress types
StressType = Literal["sigma", "sigma_axial", "sigma_bending", "tau", "tau_shear", "tau_torsion", "von_mises"]

# Plot configuration
_PLOT_RESOLUTION = 200  # Increased resolution
_PLOT_PADDING_FACTOR = 0.1
_CONTOUR_LEVELS = 20

# Display names for stress types
_STRESS_DISPLAY_NAMES: dict[str, str] = {
    "sigma": "σ",
    "sigma_axial": "σ (axial)",
    "sigma_bending": "σ (bending)",
    "tau": "τ",
    "tau_shear": "τ (shear)",
    "tau_torsion": "τ (torsion)",
    "von_mises": "Von Mises",
}


@dataclass
class Stress:
    """
    Calculates and visualizes stress distribution on a cross-section
    for a given set of internal forces.
    
    Attributes:
        section: The Section object containing geometry and properties.
        N: Axial force (positive = tension).
        Vy: Shear force in Y direction (vertical).
        Vz: Shear force in Z direction (horizontal).
        Mx: Torsional moment about X axis.
        My: Bending moment about Y axis (bending in X-Z plane).
        Mz: Bending moment about Z axis (bending in X-Y plane).
    """
    section: Section
    N: float = 0.0
    Vy: float = 0.0
    Vz: float = 0.0
    Mx: float = 0.0
    My: float = 0.0
    Mz: float = 0.0

    def sigma_axial(self, y: float, z: float) -> float:
        """Normal stress due to axial force: σ = N/A."""
        if not self.section.A:
            return 0.0
        return self.N / self.section.A

    def sigma_bending(self, y: float, z: float) -> float:
        """
        Normal stress due to bending moments.
        
        Formula: σ = (My * z) / Iy - (Mz * y) / Iz
        
        Sign convention: positive Mz compresses positive y fibers.
        """
        sigma = 0.0
        if self.section.Iy:
            sigma += (self.My * z) / self.section.Iy
        if self.section.Iz:
            sigma -= (self.Mz * y) / self.section.Iz
        return sigma

    def sigma(self, y: float, z: float) -> float:
        """Total normal stress: σ_axial + σ_bending."""
        return self.sigma_axial(y, z) + self.sigma_bending(y, z)

    def tau_shear(self, y: float, z: float) -> float:
        """
        Shear stress due to transverse shear forces (Vy, Vz).
        
        NOTE: Approximate average shear stress (V/A).
        Accurate distribution requires shear flow analysis.
        """
        if not self.section.A:
            return 0.0
        tau_y = self.Vy / self.section.A
        tau_z = self.Vz / self.section.A
        return np.sqrt(tau_y**2 + tau_z**2)

    def tau_torsion(self, y: float, z: float) -> float:
        """
        Shear stress due to torsion (Mx).
        
        NOTE: Approximate using τ = Mx * r / J.
        Accurate distribution requires solving Poisson's equation.
        """
        if not self.section.J:
            return 0.0
        r = np.sqrt(y**2 + z**2)
        return abs(self.Mx * r / self.section.J)

    def tau(self, y: float, z: float) -> float:
        """Total shear stress magnitude (conservative sum)."""
        return self.tau_shear(y, z) + self.tau_torsion(y, z)

    def von_mises(self, y: float, z: float) -> float:
        """Von Mises equivalent stress: √(σ² + 3τ²)."""
        s = self.sigma(y, z)
        t = self.tau(y, z)
        return np.sqrt(s**2 + 3 * t**2)

    def get_stress_func(self, stress_type: StressType) -> StressFunc:
        """Get the stress calculation function for a given type."""
        funcs: dict[str, StressFunc] = {
            "sigma": self.sigma,
            "sigma_axial": self.sigma_axial,
            "sigma_bending": self.sigma_bending,
            "tau": self.tau,
            "tau_shear": self.tau_shear,
            "tau_torsion": self.tau_torsion,
            "von_mises": self.von_mises,
        }
        if stress_type not in funcs:
            valid = ", ".join(funcs.keys())
            raise ValueError(f"Unknown stress type: {stress_type}. Valid types: {valid}")
        return funcs[stress_type]

    def _get_all_points(self) -> List[Point]:
        """Get all discretized points from geometry for stress calculations."""
        if not self.section.geometry:
            return []
        points: List[Point] = []
        for contour in self.section.geometry.contours:
            points.extend(contour.discretize())
        return points

    def max(self, stress_type: StressType = "von_mises") -> float:
        """Maximum stress value over geometry vertices."""
        points = self._get_all_points()
        if not points:
            return 0.0
        func = self.get_stress_func(stress_type)
        return max(func(y, z) for y, z in points)

    def min(self, stress_type: StressType = "von_mises") -> float:
        """Minimum stress value over geometry vertices."""
        points = self._get_all_points()
        if not points:
            return 0.0
        func = self.get_stress_func(stress_type)
        return min(func(y, z) for y, z in points)

    def at(self, y: float, z: float, stress_type: StressType = "von_mises") -> float:
        """Calculate stress at a specific point."""
        return self.get_stress_func(stress_type)(y, z)

    def _compute_bounds(self) -> Tuple[float, float, float, float]:
        """Compute bounding box of geometry."""
        all_ys: List[float] = []
        all_zs: List[float] = []
        for contour in self.section.geometry.contours:
            for y, z in contour.discretize():
                all_ys.append(y)
                all_zs.append(z)
        return min(all_ys), max(all_ys), min(all_zs), max(all_zs)

    def _create_mask(self, Y: np.ndarray, Z: np.ndarray) -> np.ndarray:
        """
        Create mask for points inside solid regions but outside hollow regions.
        Uses Path.contains_points which is accurate for arbitrary polygons.
        """
        points_flat = np.column_stack((Y.flatten(), Z.flatten()))
        
        solids = [c for c in self.section.geometry.contours if not c.hollow]
        hollows = [c for c in self.section.geometry.contours if c.hollow]
        
        is_in_solid = np.zeros(len(points_flat), dtype=bool)
        for solid in solids:
            # Create Path from discretized points
            pts = solid.discretize()
            if len(pts) >= 3:
                path = Path(pts)
                is_in_solid |= path.contains_points(points_flat)
        
        is_in_hollow = np.zeros(len(points_flat), dtype=bool)
        for hollow in hollows:
            pts = hollow.discretize()
            if len(pts) >= 3:
                path = Path(pts)
                is_in_hollow |= path.contains_points(points_flat)
        
        return (is_in_solid & ~is_in_hollow).reshape(Y.shape)

    def _draw_outlines(self, ax: plt.Axes) -> None:
        """
        Draw contour outlines on the plot using high-quality paths.
        Uses shared path conversion from plotter module.
        Hollows are clipped to only show the parts that intersect with solids.
        """
        from .plotter import contour_to_path, points_to_path, _clip_hollow_to_solids
        
        solids = [c for c in self.section.geometry.contours if not c.hollow]
        hollows = [c for c in self.section.geometry.contours if c.hollow]
        
        # Draw solids
        for contour in solids:
            path = contour_to_path(contour)
            if path is None:
                continue
            patch = PathPatch(path, facecolor='none', edgecolor='black', 
                              linewidth=1.5)
            ax.add_patch(patch)
            
        # Draw hollows - clipped to solid regions
        for contour in hollows:
            hollow_points = contour.discretize()
            if len(hollow_points) < 3:
                continue
            
            # Clip hollow to solid regions
            clipped_regions = _clip_hollow_to_solids(hollow_points, solids)
            
            for clipped_points in clipped_regions:
                path = points_to_path(clipped_points)
                if path is None:
                    continue
                patch = PathPatch(path, facecolor='none', edgecolor='black',
                                 linestyle='--', linewidth=1.0)
                ax.add_patch(patch)

    def plot(
        self,
        stress_type: StressType = "von_mises",
        ax: Optional[plt.Axes] = None,
        show: bool = True,
        cmap: str = "viridis",
    ) -> Optional[plt.Axes]:
        """
        Generate a contour plot of stress distribution.
        
        Args:
            stress_type: Type of stress to plot.
            ax: Matplotlib axes (creates new if None).
            show: Whether to display the plot.
            cmap: Colormap name.
            
        Returns:
            The axes object, or None if no geometry.
        """
        if not self.section.geometry:
            return None

        if ax is None:
            _, ax = plt.subplots()

        func = self.get_stress_func(stress_type)
        
        # Compute grid bounds
        min_y, max_y, min_z, max_z = self._compute_bounds()
        
        # Add a small buffer to ensure we cover the edges
        dz = max_z - min_z
        dy = max_y - min_y
        padding = max(dz, dy) * _PLOT_PADDING_FACTOR
        if padding == 0:
            padding = 1.0
        
        # Create evaluation grid with higher resolution
        z_grid = np.linspace(min_z - padding, max_z + padding, _PLOT_RESOLUTION)
        y_grid = np.linspace(min_y - padding, max_y + padding, _PLOT_RESOLUTION)
        Z, Y = np.meshgrid(z_grid, y_grid)

        # Compute stress values
        S = np.vectorize(func)(Y, Z)

        # Mask points outside geometry
        mask = self._create_mask(Y, Z)
        S_masked = np.where(mask, S, np.nan)

        # Plot contours
        contour_plot = ax.contourf(Z, Y, S_masked, cmap=cmap, levels=_CONTOUR_LEVELS)
        display_name = _STRESS_DISPLAY_NAMES[stress_type] if stress_type in _STRESS_DISPLAY_NAMES else stress_type
        colorbar = plt.colorbar(contour_plot, ax=ax, label=display_name, format='%.4g')

        # Draw outlines on top to hide jagged edges
        self._draw_outlines(ax)
        
        # Set appropriate limits
        ax.set_xlim(min_z - padding/2, max_z + padding/2)
        ax.set_ylim(min_y - padding/2, max_y + padding/2)
        
        ax.set_aspect('equal')
        ax.set_xlabel('z')
        ax.set_ylabel('y')
        ax.set_title(f'{display_name} stress')

        if show:
            plt.show()

        return ax
