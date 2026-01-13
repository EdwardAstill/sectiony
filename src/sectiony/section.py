from __future__ import annotations
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

    def plot(self, ax=None, show: bool = True):
        """Plot the section geometry."""
        from .plotter import plot_section
        return plot_section(self, ax=ax, show=show)

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
