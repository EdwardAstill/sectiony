from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict
from .geometry import Geometry
from .properties import SectionProperties

@dataclass
class Section:
    """
    Cross-section properties in local coordinates.
    Can be initialized with properties directly or with a geometry object.
    """
    name: str
    A: Optional[float] = None
    Cx: Optional[float] = None
    Cy: Optional[float] = None
    Ix: Optional[float] = None
    Iy: Optional[float] = None
    Ixy: Optional[float] = None
    J: Optional[float] = None
    Sx: Optional[float] = None
    Sy: Optional[float] = None
    rx: Optional[float] = None
    ry: Optional[float] = None
    x_max: Optional[float] = None
    y_max: Optional[float] = None
    Zpl_x: Optional[float] = None
    Zpl_y: Optional[float] = None
    Cw: Optional[float] = None  # Warping constant
    SCx: Optional[float] = None  # Shear center x-coordinate
    SCy: Optional[float] = None  # Shear center y-coordinate
    geometry: Optional[Geometry] = None
    dimensions: Optional[Dict[str, float]] = field(default_factory=lambda: None)  # Original dimensions for library shapes

    def plot(self, ax=None, show: bool = True, rotate: bool = False,
             show_centroid: bool = False, show_shear_center: bool = False):
        """Plot the section geometry.

        Args:
            ax: Optional matplotlib axes to plot on. If None, creates a new figure.
            show: Whether to call plt.show() at the end.
            rotate: If True, rotate the plot so x becomes vertical and y points left.
            show_centroid: If True, plot a marker at the centroid.
            show_shear_center: If True, plot a marker at the shear centre.
        """
        from .plotter import plot_section
        return plot_section(self, ax=ax, show=show, rotate=rotate,
                            show_centroid=show_centroid,
                            show_shear_center=show_shear_center)

    def calculate_stress(self, N: float = 0.0, Vx: float = 0.0, Vy: float = 0.0, Mx: float = 0.0, My: float = 0.0, Mz: float = 0.0):
        """
        Create a Stress object for this section with the specified internal forces.
        """
        from .stress import Stress
        return Stress(self, N=N, Vx=Vx, Vy=Vy, Mx=Mx, My=My, Mz=Mz)

    def discretize_uniform(self, count: int = 100) -> List[Tuple[List[Tuple[float, float]], bool]]:
        """
        Get uniformly discretized points for the section geometry.
        
        Args:
            count: Number of points per contour.
            
        Returns:
            List of (points, hollow) tuples.
        """
        if self.geometry is None:
            return []
        return self.geometry.discretize_uniform(count)

    def __post_init__(self):
        if self.geometry:
            # Validate that geometry consists of closed contours
            if not self.geometry.is_closed:
                raise ValueError(
                    "Section geometry must consist of closed contours. "
                    "Geometry objects can contain open contours for manipulation, "
                    "but a Section requires closed loops to calculate properties."
                )
            
            if self.A is None:
                self._apply_properties_from_geometry()
        
        if self.A is None:
            raise ValueError("Section properties must be provided if geometry is not.")

    def _apply_properties_from_geometry(self):
        props: SectionProperties = self.geometry.calculate_properties()
        self.A = props.A
        self.Cx = props.Cx
        self.Cy = props.Cy
        self.Ix = props.Ix
        self.Iy = props.Iy
        self.Ixy = props.Ixy
        self.J = props.J
        self.Sx = props.Sx
        self.Sy = props.Sy
        self.rx = props.rx
        self.ry = props.ry
        self.x_max = props.x_max
        self.y_max = props.y_max
        self.Zpl_x = props.Zpl_x
        self.Zpl_y = props.Zpl_y
        self.Cw = props.Cw
        self.SCx = props.SCx
        self.SCy = props.SCy

    def rotate(self, angle: float) -> 'Section':
        """
        Return a new Section with geometry rotated CCW by angle (radians).
        Properties are recalculated from the rotated geometry.
        """
        if self.geometry is None:
            raise ValueError("Cannot rotate a Section without geometry.")
        new_geom = self.geometry.rotate(angle)
        deg = math.degrees(angle)
        return Section(name=f"{self.name} (rot {deg:.1f}°)", geometry=new_geom)

    def __add__(self, other: 'Section') -> 'Section':
        """
        Combine two sections into one by merging their geometries.
        Useful for built-up sections. Properties are recalculated.
        """
        if self.geometry is None or other.geometry is None:
            raise ValueError("Both sections must have geometry to combine.")
        combined_contours = self.geometry.contours + other.geometry.contours
        new_geom = Geometry(contours=combined_contours)
        return Section(name=f"{self.name} + {other.name}", geometry=new_geom)

    @property
    def shape_factor_x(self) -> Optional[float]:
        """Plastic/elastic modulus ratio about x-axis (shape factor)."""
        if self.Zpl_x is None or self.Sx is None or self.Sx == 0:
            return None
        return self.Zpl_x / self.Sx

    @property
    def shape_factor_y(self) -> Optional[float]:
        """Plastic/elastic modulus ratio about y-axis (shape factor)."""
        if self.Zpl_y is None or self.Sy is None or self.Sy == 0:
            return None
        return self.Zpl_y / self.Sy

    @property
    def I1(self) -> Optional[float]:
        """Maximum (major) principal second moment of area."""
        if None in (self.Ix, self.Iy, self.Ixy):
            return None
        avg = (self.Ix + self.Iy) / 2
        diff = (self.Ix - self.Iy) / 2
        return avg + math.sqrt(diff**2 + self.Ixy**2)

    @property
    def I2(self) -> Optional[float]:
        """Minimum (minor) principal second moment of area."""
        if None in (self.Ix, self.Iy, self.Ixy):
            return None
        avg = (self.Ix + self.Iy) / 2
        diff = (self.Ix - self.Iy) / 2
        return avg - math.sqrt(diff**2 + self.Ixy**2)

    @property
    def principal_angle(self) -> Optional[float]:
        """Angle (radians) from x-axis to major principal axis (I1)."""
        if None in (self.Ix, self.Iy, self.Ixy):
            return None
        return 0.5 * math.atan2(-2 * self.Ixy, self.Ix - self.Iy)

    def __str__(self) -> str:
        rows = [
            ("A",              self.A,              "Area"),
            ("Cx",             self.Cx,             "Centroid x"),
            ("Cy",             self.Cy,             "Centroid y"),
            ("Ix",             self.Ix,             "2nd moment about x (centroidal)"),
            ("Iy",             self.Iy,             "2nd moment about y (centroidal)"),
            ("Ixy",            self.Ixy,            "Product of inertia"),
            ("I1",             self.I1,             "Major principal 2nd moment"),
            ("I2",             self.I2,             "Minor principal 2nd moment"),
            ("principal_angle (deg)", math.degrees(self.principal_angle) if self.principal_angle is not None else None, "Angle of major principal axis"),
            ("rx",             self.rx,             "Radius of gyration x"),
            ("ry",             self.ry,             "Radius of gyration y"),
            ("Sx",             self.Sx,             "Elastic section modulus x"),
            ("Sy",             self.Sy,             "Elastic section modulus y"),
            ("Zpl_x",          self.Zpl_x,          "Plastic section modulus x"),
            ("Zpl_y",          self.Zpl_y,          "Plastic section modulus y"),
            ("shape_factor_x", self.shape_factor_x, "Zpl_x / Sx"),
            ("shape_factor_y", self.shape_factor_y, "Zpl_y / Sy"),
            ("J",              self.J,              "Torsion constant"),
            ("Cw",             self.Cw,             "Warping constant"),
            ("SCx",            self.SCx,            "Shear centre x"),
            ("SCy",            self.SCy,            "Shear centre y"),
        ]
        lines = [f"Section: {self.name}", "-" * 55]
        for label, val, desc in rows:
            if val is not None:
                lines.append(f"  {label:<25} = {val:>14.6g}   {desc}")
        return "\n".join(lines)
