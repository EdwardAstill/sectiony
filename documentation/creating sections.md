# Creating Sections

A `Section` combines geometry with calculated properties (area, inertia, etc.). There are two primary approaches:

## 1. Using the Standard Library

The easiest method for common structural shapes:

```python
from sectiony.library import chs, rhs, i, u

# Circular Hollow Section (diameter, thickness)
my_chs = chs(d=200.0, t=10.0)

# Rectangular Hollow Section (width, height, thickness, corner radius)
my_rhs = rhs(b=100.0, h=200.0, t=10.0, r=15.0)

# I-Section (depth, width, flange thickness, web thickness, radius)
my_beam = i(d=300.0, b=150.0, tf=12.0, tw=8.0, r=10.0)

# U-Channel (width, height, web thickness, flange thickness, corner radius)
my_channel = u(b=100.0, h=200.0, tw=8.0, tf=10.0, r=5.0)
```

## 2. From Custom Geometry

For arbitrary shapes, create a `Geometry` object first, then wrap it in a `Section`:

```python
from sectiony import Section, Geometry, Contour, Line, Arc
import math

# Create geometry (see Creating Geometries guide for details)
segments = [
    Line(start=(50, 25), end=(50, -25)),
    Line(start=(50, -25), end=(-50, -25)),
    Line(start=(-50, -25), end=(-50, 25)),
    Line(start=(-50, 25), end=(50, 25))
]
contour = Contour(segments=segments, hollow=False)
geometry = Geometry(contours=[contour])

# Create section
section = Section(name="Rectangle 100x50", geometry=geometry)

# Properties are automatically calculated
print(f"Area: {section.A:.2f} mm²")
print(f"Ix: {section.Ix:.2e} mm⁴")
print(f"Centroid: ({section.Cx:.2f}, {section.Cy:.2f})")
```

**Shortcut for simple polygons:**

```python
from sectiony import Contour

# Rectangle from points
points = [(50, 25), (50, -25), (-50, -25), (-50, 25)]
geometry = Geometry(contours=[Contour.from_points(points)])
section = Section(name="Rectangle", geometry=geometry)
```

## 3. From DXF Files

Import geometry from CAD drawings:

```python
from sectiony import Section, Geometry

# Load geometry from DXF
geometry = Geometry.from_dxf("section.dxf")
section = Section(name="Imported Section", geometry=geometry)
```

See [Import and Export](import_export.md) for details on DXF coordinate mapping and file formats.

## Validation: Closed Contours Required

`Section` objects **require closed contours**. The start point of the first segment must connect to the end point of the last segment.

```python
# Valid - closed triangle
valid_geom = Geometry(contours=[Contour.from_points([(0,0), (10,0), (0,10)])])
section = Section("Valid", geometry=valid_geom)  # ✓ OK

# Invalid - open contour
open_geom = Geometry(contours=[Contour.from_points([(0,0), (10,0)])])
section = Section("Invalid", geometry=open_geom)  # ✗ Raises ValueError
```

## Working with Sections

### Accessing Properties

All geometric properties are calculated automatically:

```python
section = rhs(b=100, h=200, t=10, r=15)

# Geometric properties
print(section.A)         # Area
print(section.Cx, section.Cy)  # Centroid
print(section.Ix, section.Iy, section.Ixy)  # Second moments of area
print(section.J)         # Torsion constant
print(section.SCx, section.SCy)  # Shear center

# Section moduli
print(section.Sx, section.Sy)          # Elastic section moduli
print(section.Zpl_x, section.Zpl_y)    # Plastic section moduli
```

### Discretization

Convert continuous curves to discrete points:

```python
# Uniform discretization (equal spacing along perimeter)
# Returns: [(points, is_hollow), ...]
uniform_points = section.discretize_uniform(count=100)
```

See [Creating Geometries](creating geometries.md) for detailed discretization options.

### Visualization

```python
import matplotlib.pyplot as plt

# Plot the section
section.plot(show=True)

# Plot with custom axes
fig, ax = plt.subplots()
section.plot(ax=ax, show=False)
ax.set_title(f"{section.name}")
plt.show()
```

### Stress Analysis

```python
# Calculate stress distribution for internal forces
# Units: N, mm → MPa
stress = section.calculate_stress(
    N=50e3,    # 50 kN tension
    Vx=10e3,   # 10 kN shear (x)
    Vy=20e3,   # 20 kN shear (y)
    Mz=5e6,    # 5 kNm torsion (about z)
    Mx=10e6,   # 10 kNm bending (about x)
    My=20e6    # 20 kNm bending (about y)
)

# Visualize stress distributions
stress.plot(stress_type="von_mises", show=True)
stress.plot(stress_type="sigma", show=True)

# Query stress at specific points
vm_stress = stress.at(x=50, y=0, stress_type="von_mises")
```

See [Stress Analysis](stress.md) for details on stress calculations and visualization.

## Coordinate System

- **x-axis**: Horizontal (Positive Right)
- **y-axis**: Vertical (Positive Up)
- **z-axis**: Longitudinal (Positive Out of Plane/Towards Viewer)
- Points: `(x, y)`

## Next Steps

- **[Creating Geometries](creating geometries.md)**: Detailed guide on building custom shapes
- **[Standard Library](library.md)**: Complete reference for built-in sections
- **[Section Properties](section%20properties.md)**: Understanding calculated properties
- **[Import/Export](import_export.md)**: Working with DXF and JSON files
