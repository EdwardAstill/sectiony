# User Guide

Welcome to **sectiony**, a Python library for cross-section analysis and stress calculation. This guide will walk you through defining sections, calculating properties, and analyzing stresses.

## 1. Defining a Section

A `Section` is built from `Geometry`, which is a collection of `Shape` objects. Shapes are defined by a list of $(y, z)$ coordinates (where $y$ is vertical and $z$ is horizontal).

### Creating Shapes

You can create solid shapes and hollow shapes (holes).

```python
from sectiony import Section, Geometry, Shape

# Define a solid rectangle (10 wide, 20 high)
points_outer = [
    (10.0, 5.0),   # Top Right (y, z)
    (-10.0, 5.0),  # Bottom Right
    (-10.0, -5.0), # Bottom Left
    (10.0, -5.0)   # Top Left
]
solid = Shape(points=points_outer)

# Define a hole
points_inner = [
    (5.0, 2.5),
    (-5.0, 2.5),
    (-5.0, -2.5),
    (5.0, -2.5)
]
hole = Shape(points=points_inner, hollow=True)
```

### creating the Section

Combine shapes into a `Geometry` object and then create the `Section`.

```python
# Create geometry with both shapes
geom = Geometry(shapes=[solid, hole])

# Create the section
# Properties (Area, Inertia, etc.) are calculated automatically
my_section = Section(name="Hollow Rect", geometry=geom)
```

## 2. Accessing Section Properties

Once a `Section` is initialized, its geometric properties are available as attributes.

```python
print(f"Area: {my_section.A}")
print(f"Iyy (bending about y-axis): {my_section.Iy}")
print(f"Izz (bending about z-axis): {my_section.Iz}")
print(f"Centroidal Axis Distances: y_max={my_section.y_max}, z_max={my_section.z_max}")
```

*   **A**: Area
*   **Iy**: Second moment of area about the vertical axis (resistance to bending in the horizontal plane).
*   **Iz**: Second moment of area about the horizontal axis (resistance to bending in the vertical plane).
*   **J**: Polar moment of area (approximation for non-circular sections).

## 3. Visualizing the Section

You can plot the cross-section geometry easily.

```python
# Plots the section in a new window
my_section.plot()
```

## 4. Stress Analysis

You can calculate and visualize stresses resulting from internal forces (Normal force, Shear, Bending Moments, Torsion).

### Defining Loads

You can define a stress state by applying loads to your section.

*   **N**: Axial Force
*   **Vy, Vz**: Shear Forces
*   **Mx**: Torsional Moment
*   **My**: Bending Moment about Y (bending horizontally)
*   **Mz**: Bending Moment about Z (bending vertically)

```python
# Apply 10kN compression and 5kNm bending moment
stress = my_section.calculate_stress(N=-10000, Mz=5000)
```

### Calculating Values

You can get specific stress values at any $(y, z)$ coordinate or find maximums.

```python
# Get Von Mises stress at specific point
vm = stress.von_mises(y=10.0, z=0.0)

# Get maximum normal stress (sigma)
max_sigma = stress.max("sigma")

# Get minimum normal stress (e.g. max compression)
max_comp = stress.min("sigma")
```

### Visualizing Stress

Plot contour maps of the stress distribution.

```python
# Plot Normal Stress (Sigma)
stress.plot("sigma")

# Plot Von Mises Stress
stress.plot("von_mises")
```

The plots automatically handle holes and complex geometries, masking the stress values outside the material.

