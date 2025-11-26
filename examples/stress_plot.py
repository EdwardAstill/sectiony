"""Example: Stress distribution plot for a rectangular section under bending."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sectiony.geometry import Geometry, Shape
from sectiony.section import Section

# Create a 200x100 rectangular section
h, b = 200, 100
points = [(h/2, b/2), (h/2, -b/2), (-h/2, -b/2), (-h/2, b/2)]
section = Section(
    name="Rect 200x100",
    geometry=Geometry(shapes=[Shape(points=points)])
)

# Apply bending moment about Z axis
stress = section.calculate_stress(Mz=50e6)

# Plot the normal stress distribution
stress.plot("sigma", cmap="RdBu_r")

