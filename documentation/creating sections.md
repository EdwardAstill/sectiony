# Creating Sections

There are two primary ways to create a section in **sectiony**: using the **library** of standard shapes or defining a **custom geometry**.

## 1. Using the Standard Library

The easiest way to create common structural sections is using the built-in library functions. These functions automatically generate the geometry and calculate all properties.

```python
from sectiony.library import chs, rhs, i_section, u_section

# Circular Hollow Section (Outer diameter 20, thickness 2)
my_chs = chs(d=20.0, t=2.0)

# Rectangular Hollow Section (Width 10, Height 20, Thickness 1, Radius 0)
my_rhs = rhs(b=10.0, h=20.0, t=1.0, r=0.0)

# I-Section (Depth 100, Width 50, Flange t=10, Web t=5, Radius 0)
my_beam = i_section(d=100.0, b=50.0, tf=10.0, tw=5.0, r=0.0)

# U-Channel (Width 50, Height 100, Thickness 5)
my_channel = u_section(b=50.0, h=100.0, t=5.0, r=0.0)
```

## 2. Defining Custom Geometry

For arbitrary shapes, you define the section by creating `Shape` objects from points and combining them into a `Geometry`.

### Coordinate System
- **y**: Vertical axis (Up is positive)
- **z**: Horizontal axis (Right is positive)
- Points are defined as tuples `(y, z)`.

### Step-by-Step

1.  **Define Points**: Create lists of `(y, z)` coordinates for your polygons. Order matters (counter-clockwise for solids is standard, though the library handles signed area automatically).
2.  **Create Shapes**: Initialize `Shape` objects. Use `hollow=True` for holes.
3.  **Create Geometry**: Combine shapes into a `Geometry` object.
4.  **Create Section**: Initialize the `Section` with the geometry.

```python
from sectiony import Section, Geometry, Shape

# Define a custom T-shape
# Flange (Top)
p1 = [(10, 5), (10, -5), (8, -5), (8, 5)]
# Web (Bottom)
p2 = [(8, 1), (8, -1), (0, -1), (0, 1)]

# You can combine them into one polygon or keep separate solids
points = [
    (10, 5),   # Top Right
    (10, -5),  # Top Left
    (8, -5),   # Flange Bottom Left
    (8, -1),   # Web Top Left
    (0, -1),   # Web Bottom Left
    (0, 1),    # Web Bottom Right
    (8, 1),    # Web Top Right
    (8, 5)     # Flange Bottom Right
]

custom_shape = Shape(points=points)
geom = Geometry(shapes=[custom_shape])

# Create the section (properties are auto-calculated)
my_custom_section = Section(name="Custom T", geometry=geom)
```

### Handling Holes

To create a hollow section, define the outer boundary as a solid and the inner boundary as a hollow shape.

```python
# Outer square
outer = Shape(points=[(10,10), (10,-10), (-10,-10), (-10,10)])

# Inner circular hole (approximation)
import math
radius = 5
inner_points = [(radius*math.sin(t), radius*math.cos(t)) for t in [0, 1, ...]] 
hole = Shape(points=inner_points, hollow=True)

geom = Geometry(shapes=[outer, hole])
sec = Section(name="Square with Hole", geometry=geom)
```

