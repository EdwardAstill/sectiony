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
        N: Axial force along +z (positive = tension).
        Vx: Shear force in x direction (horizontal).
        Vy: Shear force in y direction (vertical).
        Mx: Bending moment about x axis.
        My: Bending moment about y axis.
        Mz: Torsional moment about z axis (longitudinal torsion).
    """
    section: Section
    N: float = 0.0
    Vx: float = 0.0
    Vy: float = 0.0
    Mx: float = 0.0
    My: float = 0.0
    Mz: float = 0.0

    def sigma_axial(self, x: float, y: float) -> float:
        """Normal stress due to axial force: σ = N/A."""
        if not self.section.A:
            return 0.0
        return self.N / self.section.A

    def sigma_bending(self, x: float, y: float) -> float:
        """
        Normal stress due to bending moments.
        
        Formula (principal axes, no coupling): σ = -(Mx * y) / Ix - (My * x) / Iy

        Sign convention:
        - Positive Mx compresses +y fibers (top).
        - Positive My compresses +x fibers (right).
        """
        sigma = 0.0
        if self.section.Ix:
            sigma -= (self.Mx * y) / self.section.Ix
        if self.section.Iy:
            sigma -= (self.My * x) / self.section.Iy
        return sigma

    def sigma(self, x: float, y: float) -> float:
        """Total normal stress: σ_axial + σ_bending."""
        return self.sigma_axial(x, y) + self.sigma_bending(x, y)

    def tau_shear(self, x: float, y: float) -> float:
        """
        Shear stress due to transverse shear forces (Vx, Vy).
        
        NOTE: Approximate average shear stress (V/A).
        Accurate distribution requires shear flow analysis.
        """
        if not self.section.A:
            return 0.0
        tau_x = self.Vx / self.section.A
        tau_y = self.Vy / self.section.A
        return np.sqrt(tau_x**2 + tau_y**2)

    def tau_torsion(self, x: float, y: float) -> float:
        """
        Shear stress due to torsion (Mz).
        
        NOTE: Approximate using τ = Mz * r / J.
        Accurate distribution requires solving Poisson's equation.
        """
        if not self.section.J:
            return 0.0
        cx = self.section.Cx if self.section.Cx is not None else 0.0
        cy = self.section.Cy if self.section.Cy is not None else 0.0
        r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        return abs(self.Mz * r / self.section.J)

    def tau(self, x: float, y: float) -> float:
        """Total shear stress magnitude (conservative sum)."""
        return self.tau_shear(x, y) + self.tau_torsion(x, y)

    def von_mises(self, x: float, y: float) -> float:
        """Von Mises equivalent stress: √(σ² + 3τ²)."""
        s = self.sigma(x, y)
        t = self.tau(x, y)
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
        return max(func(x, y) for x, y in points)

    def min(self, stress_type: StressType = "von_mises") -> float:
        """Minimum stress value over geometry vertices."""
        points = self._get_all_points()
        if not points:
            return 0.0
        func = self.get_stress_func(stress_type)
        return min(func(x, y) for x, y in points)

    def at(self, x: float, y: float, stress_type: StressType = "von_mises") -> float:
        """Calculate stress at a specific point."""
        return self.get_stress_func(stress_type)(x, y)

    def _compute_bounds(self) -> Tuple[float, float, float, float]:
        """Compute bounding box of geometry."""
        all_xs: List[float] = []
        all_ys: List[float] = []
        for contour in self.section.geometry.contours:
            for x, y in contour.discretize():
                all_xs.append(x)
                all_ys.append(y)
        return min(all_xs), max(all_xs), min(all_ys), max(all_ys)

    def _create_mask(self, X: np.ndarray, Y: np.ndarray) -> np.ndarray:
        """
        Create mask for points inside solid regions but outside hollow regions.
        Uses Path.contains_points which is accurate for arbitrary polygons.
        """
        points_flat = np.column_stack((X.flatten(), Y.flatten()))
        
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
        
        return (is_in_solid & ~is_in_hollow).reshape(X.shape)

    def _draw_outlines(self, ax: plt.Axes, rotate: bool = False) -> None:
        """
        Draw contour outlines on the plot using high-quality paths.
        Uses shared path conversion from plotter module.
        Hollows are clipped to only show the parts that intersect with solids.
        
        Args:
            ax: Matplotlib axes to draw on.
            rotate: If True, transform paths for rotated view.
        """
        from .plotter import contour_to_path, points_to_path, _clip_hollow_to_solids
        from matplotlib.path import Path
        
        solids = [c for c in self.section.geometry.contours if not c.hollow]
        hollows = [c for c in self.section.geometry.contours if c.hollow]
        
        # Helper function to transform path if rotating
        def transform_path(path: Path) -> Path:
            """Transform all vertices in a path: (x, y) -> (-y, x)"""
            if not rotate:
                return path
            transformed_vertices = [(-v[1], v[0]) for v in path.vertices]
            return Path(transformed_vertices, path.codes)
        
        # Draw solids
        for contour in solids:
            path = contour_to_path(contour)
            if path is None:
                continue
            path = transform_path(path)
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
                # Transform points if rotating
                if rotate:
                    transformed_points = [(-p[1], p[0]) for p in clipped_points]
                else:
                    transformed_points = clipped_points
                path = points_to_path(transformed_points)
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
        rotate: bool = False,
    ) -> Optional[plt.Axes]:
        """
        Generate a contour plot of stress distribution.
        
        Args:
            stress_type: Type of stress to plot.
            ax: Matplotlib axes (creates new if None).
            show: Whether to display the plot.
            cmap: Colormap name.
            rotate: If True, rotate the plot so x becomes vertical and y points left.
                    The scale remains on the right side.
            
        Returns:
            The axes object, or None if no geometry.
        """
        if not self.section.geometry:
            return None

        if ax is None:
            _, ax = plt.subplots()

        func = self.get_stress_func(stress_type)
        
        # Compute grid bounds
        min_x, max_x, min_y, max_y = self._compute_bounds()
        
        # Add a small buffer to ensure we cover the edges
        dx = max_x - min_x
        dy = max_y - min_y
        padding = max(dx, dy) * _PLOT_PADDING_FACTOR
        if padding == 0:
            padding = 1.0
        
        # Create evaluation grid with higher resolution
        x_grid = np.linspace(min_x - padding, max_x + padding, _PLOT_RESOLUTION)
        y_grid = np.linspace(min_y - padding, max_y + padding, _PLOT_RESOLUTION)
        X, Y = np.meshgrid(x_grid, y_grid)

        # Transform coordinates if rotating: (x, y) -> (-y, x)
        if rotate:
            X_plot = -Y
            Y_plot = X
            # For stress calculation, we need original coordinates
            # So we compute stress at (X, Y) but plot at (X_plot, Y_plot)
        else:
            X_plot = X
            Y_plot = Y

        # Compute stress values (using original coordinates)
        S = np.vectorize(func)(X, Y)

        # Mask points outside geometry (using original coordinates)
        mask = self._create_mask(X, Y)
        S_masked = np.where(mask, S, np.nan)

        # Plot contours
        contour_plot = ax.contourf(X_plot, Y_plot, S_masked, cmap=cmap, levels=_CONTOUR_LEVELS)
        display_name = _STRESS_DISPLAY_NAMES[stress_type] if stress_type in _STRESS_DISPLAY_NAMES else stress_type
        colorbar = plt.colorbar(contour_plot, ax=ax, label=display_name, format='%.4g')

        # Draw outlines on top to hide jagged edges
        self._draw_outlines(ax, rotate=rotate)
        
        # Set appropriate limits
        if rotate:
            # Transform bounds: (x, y) -> (-y, x)
            plot_min_x = -max_y
            plot_max_x = -min_y
            plot_min_y = min_x
            plot_max_y = max_x
            ax.set_xlim(plot_max_x + padding/2, plot_min_x - padding/2)  # Inverted
            ax.set_ylim(plot_min_y - padding/2, plot_max_y + padding/2)
            ax.set_xlabel('y (pointing left)')
            ax.set_ylabel('x (vertical)')
        else:
            ax.set_xlim(min_x - padding/2, max_x + padding/2)
            ax.set_ylim(min_y - padding/2, max_y + padding/2)
        
        ax.set_aspect('equal')

        if show:
            plt.show()

        return ax
