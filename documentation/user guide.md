# User Guide

Welcome to **sectiony**, a Python library for cross-section analysis and stress calculation. This guide will walk you through defining sections, calculating properties, and analyzing stresses.

## Quick Start

```python
from sectiony.library import i

# Create an I-beam section
beam = i(d=300.0, b=150.0, tf=12.0, tw=8.0, r=10.0)

# View properties
print(f"Area: {beam.A:.2f}")
print(f"Moment of Inertia: {beam.Iz:.2f}")

# Calculate stress
stress = beam.calculate_stress(N=-10000, Mz=5000)
print(f"Max stress: {stress.max('sigma'):.2f}")

# Visualize
beam.plot()
stress.plot("sigma")
```

## 1. Defining a Section

There are three main ways to create a section in **sectiony**:

1. **Using the Standard Library** (easiest for common shapes)
2. **Creating Custom Geometry** (for arbitrary shapes)
3. **Importing from Files** (JSON or DXF)

### 1.1 Using the Standard Library

The easiest way to create common structural sections is using the built-in library functions. These automatically generate geometry and calculate all properties.

```python
from sectiony.library import chs, rhs, i, u

# Circular Hollow Section
my_chs = chs(d=200.0, t=10.0)

# Rectangular Hollow Section
my_rhs = rhs(b=100.0, h=200.0, t=10.0, r=15.0)

# I-Section
my_beam = i(d=300.0, b=150.0, tf=12.0, tw=8.0, r=10.0)

# U-Channel
my_channel = u(b=100.0, h=200.0, t=8.0, r=5.0)
```

All library functions return a `Section` object with automatically calculated properties. See the [Standard Library](library.md) documentation for detailed parameter descriptions.

### 1.2 Creating Custom Geometry

For arbitrary shapes, you define the section by constructing a `Geometry` object. A `Geometry` is a collection of `Contour` objects, which define the boundary of the shape. Contours are made of segments like `Line` and `Arc`.

**Coordinate System:**
- **y-axis**: Vertical (Positive Up)
- **z-axis**: Horizontal (Positive Right)
- Points are defined as tuples `(y, z)`

You can create solid shapes and hollow shapes (holes).

```python
from sectiony import Section, Geometry, Contour, Line

# Define a solid rectangle (10 wide, 20 high)
# Define segments for the outer boundary
outer_segments = [
    Line(start=(10, 5), end=(10, -5)),   # Top edge
    Line(start=(10, -5), end=(-10, -5)), # Left edge
    Line(start=(-10, -5), end=(-10, 5)), # Bottom edge
    Line(start=(-10, 5), end=(10, 5))    # Right edge
]
solid_contour = Contour(segments=outer_segments, hollow=False)

# Define a hole (smaller rectangle)
inner_segments = [
    Line(start=(5, 2.5), end=(5, -2.5)),
    Line(start=(5, -2.5), end=(-5, -2.5)),
    Line(start=(-5, -2.5), end=(-5, 2.5)),
    Line(start=(-5, 2.5), end=(5, 2.5))
]
hole_contour = Contour(segments=inner_segments, hollow=True)

# Create geometry with both contours
geom = Geometry(contours=[solid_contour, hole_contour])

# Create the section
# Properties (Area, Inertia, etc.) are calculated automatically
my_section = Section(name="Hollow Rect", geometry=geom)
```

**Tip:** For simple polygons, you can use `Contour.from_points()` as a shortcut:

```python
from sectiony import Contour, Geometry, Section

# Create a rectangle from points
points = [(10, 5), (10, -5), (-10, -5), (-10, 5)]
contour = Contour.from_points(points, hollow=False)

# Create the section
geom = Geometry(contours=[contour])
my_section = Section(name="Simple Rect", geometry=geom)
```

### 1.3 Importing from Files

You can also import geometry from JSON or DXF files:

```python
from sectiony import Geometry, Section

# Import from JSON
geom = Geometry.from_json("my_section.json")
section = Section(name="Imported", geometry=geom)

# Import from DXF (CAD files)
geom = Geometry.from_dxf("drawing.dxf")
section = Section(name="DXF Section", geometry=geom)
```

See the [Import and Export](import_export.md) guide for more details.

## 2. Accessing Section Properties

Once a `Section` is initialized, its geometric properties are automatically calculated and available as attributes.

### Basic Properties

```python
print(f"Area: {my_section.A}")
print(f"Centroid: ({my_section.Cy}, {my_section.Cz})")
print(f"Max distances: y_max={my_section.y_max}, z_max={my_section.z_max}")
```

### Inertia Properties

```python
print(f"Iy (about y-axis): {my_section.Iy}")
print(f"Iz (about z-axis): {my_section.Iz}")
print(f"Product of Inertia: {my_section.Iyz}")
print(f"Torsional Constant: {my_section.J}")
```

### Strength Properties

```python
print(f"Elastic Modulus (y): {my_section.Sy}")
print(f"Elastic Modulus (z): {my_section.Sz}")
print(f"Plastic Modulus (y): {my_section.Zpl_y}")
print(f"Plastic Modulus (z): {my_section.Zpl_z}")
```

### Stability Properties

```python
print(f"Radius of Gyration (y): {my_section.ry}")
print(f"Radius of Gyration (z): {my_section.rz}")
```

### Shear Center

```python
print(f"Shear Center: ({my_section.SCy}, {my_section.SCz})")
```

**Property Reference:**

| Property | Description |
|----------|-------------|
| **A** | Cross-sectional area |
| **Cy, Cz** | Centroid coordinates |
| **Iy, Iz** | Second moment of area (bending stiffness) |
| **Iyz** | Product of inertia (asymmetry measure) |
| **J** | Torsional constant |
| **Sy, Sz** | Elastic section modulus |
| **Zpl_y, Zpl_z** | Plastic section modulus |
| **ry, rz** | Radius of gyration (for buckling) |
| **SCy, SCz** | Shear center coordinates |
| **y_max, z_max** | Maximum distances from centroid |

For detailed explanations, see the [Section Properties](section properties.md) documentation.

## 3. Visualizing the Section

You can plot the cross-section geometry easily. The plot shows the exact curve definitions (including arcs) and automatically handles holes.

```python
# Plot in a new window
my_section.plot()

# Plot to existing axes
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
my_section.plot(ax=ax, show=False)
plt.savefig("section.svg")
plt.close()
```

**Note:** Holes are automatically clipped to only show where they intersect with solid material, matching the property calculation behavior.

## 4. Stress Analysis

You can calculate and visualize stresses resulting from internal forces (Normal force, Shear, Bending Moments, Torsion).

### Defining Loads

You can define a stress state by applying loads to your section using the `calculate_stress()` method:

*   **N**: Axial Force (positive = tension)
*   **Vy, Vz**: Shear Forces (vertical and horizontal)
*   **Mx**: Torsional Moment
*   **My**: Bending Moment about Y-axis (bending horizontally)
*   **Mz**: Bending Moment about Z-axis (bending vertically)

```python
# Apply 10kN compression and 5kNm bending moment
stress = my_section.calculate_stress(N=-10000, Mz=5000)

# Or create Stress object directly
from sectiony import Stress
stress = Stress(
    section=my_section,
    N=-10000,      # Compression
    Vy=0.0,
    Vz=0.0,
    Mx=0.0,        # No torsion
    My=0.0,
    Mz=5000        # Bending moment
)
```

### Available Stress Types

The following stress types can be calculated:

*   **`"sigma"`**: Total normal stress (axial + bending)
*   **`"sigma_axial"`**: Normal stress from axial force only
*   **`"sigma_bending"`**: Normal stress from bending only
*   **`"tau"`**: Total shear stress magnitude
*   **`"tau_shear"`**: Shear stress from transverse forces
*   **`"tau_torsion"`**: Shear stress from torsion
*   **`"von_mises"`**: Von Mises equivalent stress

### Calculating Stress Values

You can get specific stress values at any $(y, z)$ coordinate or find maximums/minimums.

```python
# Get stress at a specific point
sigma = stress.sigma(y=10.0, z=0.0)
vm = stress.von_mises(y=10.0, z=0.0)

# Or use the generic 'at' method
sigma = stress.at(y=10.0, z=0.0, stress_type="sigma")

# Find maximum and minimum values
max_tension = stress.max("sigma")
max_compression = stress.min("sigma")
max_vm = stress.max("von_mises")
```

### Visualizing Stress

Plot contour maps of the stress distribution.

```python
# Plot Normal Stress (Sigma)
stress.plot("sigma")

# Plot Von Mises Stress
stress.plot("von_mises")

# Plot with custom options
stress.plot(
    stress_type="sigma",
    cmap="RdBu_r",  # Colormap
    show=True       # Display immediately
)
```

**Note:** Stress plots automatically handle holes and complex geometries, masking stress values outside the material. Holes are automatically clipped to only show where they intersect with solid regions, matching the property calculation behavior.

For more details on stress analysis, see the [Stress Analysis](stress.md) documentation.

## 5. Saving, Loading, and Import/Export

You can save your section geometry to JSON files for later use, or import geometry from DXF files created in CAD software.

### Saving to JSON

The JSON format preserves exact curve definitions (not just approximated points), making it ideal for storing custom sections.

```python
# Save geometry to JSON
my_section.geometry.to_json("my_section.json")

# You can also use the dictionary format for programmatic access
geom_dict = my_section.geometry.to_dict()
```

### Loading from JSON

```python
from sectiony import Geometry, Section

# Load geometry from JSON
geom = Geometry.from_json("my_section.json")

# Create section from loaded geometry
section = Section(name="Loaded Section", geometry=geom)

# Verify properties match
print(f"Area: {section.A:.2f}")
```

### Importing from DXF

Import geometry from CAD software (AutoCAD, LibreCAD, etc.):

```python
from sectiony import Geometry, Section

# Import from DXF
geom = Geometry.from_dxf("drawing.dxf")
section = Section(name="DXF Section", geometry=geom)
```

### Exporting to DXF

Export your geometry for use in CAD:

```python
# Export geometry to DXF
my_section.geometry.to_dxf("output.dxf")
```

**Coordinate Mapping:**
- DXF X-axis → Section Y-axis (horizontal)
- DXF Y-axis → Section Z-axis (vertical)

For detailed information on supported formats, DXF entity types, and best practices, see the [Import and Export](import_export.md) guide.

## 6. Units and Coordinate System

### Units

**sectiony** is unit-agnostic. It performs calculations based on the numerical values you provide. You must ensure consistency:

*   **Length**: If geometry is in millimeters, all length properties (Area, Inertia) will be in $mm^2$, $mm^4$, etc.
*   **Force**: If loads are in Newtons, moments should be in $N \cdot mm$ (or $N \cdot m$ if lengths are in meters).
*   **Stress**: Resulting stress will be in $Force / Length^2$.
    *   Example: $N$ and $mm$ → $MPa$ ($N/mm^2$)
    *   Example: $kN$ and $m$ → $kPa$ ($kN/m^2$)

### Coordinate System

The library uses a standard right-handed Cartesian coordinate system:

*   **y-axis**: Vertical (Positive Up)
*   **z-axis**: Horizontal (Positive Right)
*   **x-axis**: Longitudinal (Positive Out of Plane) - used for internal force vectors

Points are defined as tuples `(y, z)`.

**Sign Conventions:**
*   **N (Axial)**: Positive = Tension
*   **My (Bending about Y)**: Positive compresses +z fibers (right side)
*   **Mz (Bending about Z)**: Positive compresses +y fibers (top side)
*   **Mx (Torsion)**: Positive vector points out of plane (+x)

For more details, see the [Units and Coordinates](units and coordinates.md) documentation.

## Complete Example

Here's a complete workflow example:

```python
from sectiony.library import i
from sectiony import Geometry, Contour, Line

# Option 1: Use standard library
beam = i(d=300.0, b=150.0, tf=12.0, tw=8.0, r=10.0)

# Option 2: Create custom geometry
points = [(10, 5), (10, -5), (-10, -5), (-10, 5)]
contour = Contour.from_points(points, hollow=False)
geom = Geometry(contours=[contour])
custom_section = Section(name="Custom", geometry=geom)

# Calculate properties
print(f"Area: {beam.A:.2f}")
print(f"Iz: {beam.Iz:.2f}")
print(f"Shear Center: ({beam.SCy:.2f}, {beam.SCz:.2f})")

# Visualize geometry
beam.plot()

# Calculate stress
stress = beam.calculate_stress(N=-50000, Mz=100000, Vy=10000)

# Analyze stress
print(f"Max tension: {stress.max('sigma'):.2f}")
print(f"Max compression: {stress.min('sigma'):.2f}")
print(f"Max Von Mises: {stress.max('von_mises'):.2f}")

# Visualize stress
stress.plot("sigma")
stress.plot("von_mises")

# Save for later
beam.geometry.to_json("my_beam.json")
```

## Next Steps

*   Learn more about [Creating Sections](creating sections.md) with custom geometry
*   Explore the [Standard Library](library.md) of pre-built shapes
*   Understand [Section Properties](section properties.md) in detail
*   Dive deeper into [Stress Analysis](stress.md)
*   Learn about [Import and Export](import_export.md) formats

