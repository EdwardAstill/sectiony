from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
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
    Cy: Optional[float] = None
    Cz: Optional[float] = None
    Iy: Optional[float] = None
    Iz: Optional[float] = None
    Iyz: Optional[float] = None
    J: Optional[float] = None
    Sy: Optional[float] = None
    Sz: Optional[float] = None
    ry: Optional[float] = None
    rz: Optional[float] = None
    y_max: Optional[float] = None
    z_max: Optional[float] = None
    Zpl_y: Optional[float] = None
    Zpl_z: Optional[float] = None
    geometry: Optional[Geometry] = None

    def plot(self, ax=None, show=True):
        """Plot the section geometry."""
        from .plotter import plot_section
        return plot_section(self, ax=ax, show=show)

    def calculate_stress(self, N=0.0, Vy=0.0, Vz=0.0, Mx=0.0, My=0.0, Mz=0.0):
        """
        Create a Stress object for this section with the specified internal forces.
        """
        from .stress import Stress
        return Stress(self, N=N, Vy=Vy, Vz=Vz, Mx=Mx, My=My, Mz=Mz)

    def __post_init__(self):
        if self.geometry and self.A is None:
            self._apply_properties_from_geometry()
        
        if self.A is None:
            raise ValueError("Section properties must be provided if geometry is not.")

    def _apply_properties_from_geometry(self):
        props: SectionProperties = self.geometry.calculate_properties()
        self.A = props.A
        self.Cy = props.Cy
        self.Cz = props.Cz
        self.Iy = props.Iy
        self.Iz = props.Iz
        self.Iyz = props.Iyz
        self.J = props.J
        self.Sy = props.Sy
        self.Sz = props.Sz
        self.ry = props.ry
        self.rz = props.rz
        self.y_max = props.y_max
        self.z_max = props.z_max
        self.Zpl_y = props.Zpl_y
        self.Zpl_z = props.Zpl_z
