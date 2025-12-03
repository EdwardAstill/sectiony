# Creating Sections

There are two primary ways to create a section in **sectiony**: using the **library** of standard shapes or defining a **custom geometry**.

## 1. Using the Standard Library

The easiest way to create common structural sections is using the built-in library functions. These functions automatically generate the geometry and calculate all properties.

```python
from sectiony.library import chs, rhs, i, u

# Circular Hollow Section (Outer diameter 20, thickness 2)
my_chs = chs(d=20.0, t=2.0)

# Rectangular Hollow Section (Width 10, Height 20, Thickness 1, Radius 0)
my_rhs = rhs(b=10.0, h=20.0, t=1.0, r=0.0)

# I-Section (Depth 100, Width 50, Flange t=10, Web t=5, Radius 0)
my_beam = i(d=100.0, b=50.0, tf=10.0, tw=5.0, r=0.0)

# U-Channel (Width 50, Height 100, Thickness 5)
my_channel = u(b=50.0, h=100.0, t=5.0, r=0.0)
```

## 2. Defining Custom Geometry

For arbitrary shapes, you define the section by constructing a `Geometry` object. A `Geometry` consists of one or more `Contour` objects, which in turn are made up of connected curve segments (`Line`, `Arc`, or `CubicBezier`).

### Coordinate System
- **y**: Vertical axis (Up is positive)
- **z**: Horizontal axis (Right is positive)
- Points are defined as tuples `(y, z)`.

### Step-by-Step

1.  **Define Segments**: Create a list of connected segments (`Line`, `Arc`, `CubicBezier`) that form a closed loop.
2.  **Create Contour**: Initialize a `Contour` with these segments. Use `hollow=True` for holes.
3.  **Create Geometry**: Combine contours into a `Geometry` object.
4.  **Create Section**: Initialize the `Section` with the geometry.

### Available Curves

The library supports exact curve definitions, which are discretized automatically for property calculation but preserved for plotting.

#### Line
A simple straight line segment.
```python
from sectiony import Line
# From (y1, z1) to (y2, z2)
line = Line(start=(0, 0), end=(10, 0))
```

#### Arc
A circular arc defined by center, radius, and start/end angles.
- Angles are in radians.
- 0 is +z (Right), pi/2 is +y (Up).
- Direction is typically Counter-Clockwise (CCW).

```python
from sectiony import Arc
import math
# Quarter circle arc from (10,0) to (0,10) centered at origin
arc = Arc(
    center=(0, 0), 
    radius=10.0, 
    start_angle=0, 
    end_angle=math.pi/2
)
```

#### CubicBezier
A cubic Bezier curve defined by 4 control points.
- `p0`: Start point
- `p1`: First control point
- `p2`: Second control point
- `p3`: End point

```python
from sectiony import CubicBezier
# A curve starting at (0,0) and ending at (10,10)
curve = CubicBezier(
    p0=(0, 0),
    p1=(0, 5),  # Control point 1 pulls curve up
    p2=(10, 5), # Control point 2 pulls curve right
    p3=(10, 10)
)
```

### Example: Custom Rounded Shape

Here is an example of creating a custom shape with rounded corners using `Line` and `Arc` segments.

```python
from sectiony import Section, Geometry, Contour, Line, Arc
import math

# Define a "D" shape (Vertical straight back, rounded front)
# Points:
# Top: (10, 0)
# Bottom: (-10, 0)
# Right-most point of curve: (0, 10)

segments = []

# 1. Vertical line going down (the back of the D)
segments.append(Line(start=(10, 0), end=(-10, 0)))

# 2. Bottom quarter arc (from -10,0 to 0,10)
# Center is (0,0), radius 10
# Angle 270 deg (3pi/2) to 360 deg (2pi or 0) -> this goes UP on the right side
# Let's do a single 180 degree arc for simplicity
segments.append(Arc(
    center=(0, 0),
    radius=10.0,
    start_angle=3*math.pi/2, # Bottom (-y)
    end_angle=math.pi/2      # Top (+y)
))

# Note: The Arc goes from (0, -10) around to (0, 10)
# But our Line ended at (-10, 0)? 
# Wait, (y, z): 
#   (10, 0) is Top Center
#   (-10, 0) is Bottom Center
#   We want the back to be at z=0? No, let's make the straight edge at z=0.

# Corrected Logic for "D" Shape:
# Straight vertical line from (10, 0) down to (-10, 0).
# Arc centered at (0,0) from angle -pi/2 to pi/2?
# -pi/2 is -y (down). pi/2 is +y (up).
# Arc starts at (0, -10) -> equivalent to (-10, 0) in (y,z)? NO.
# (y,z) coordinates: 
#   y is vertical, z is horizontal.
#   (-10, 0) means y=-10, z=0.
#   Arc angle 3pi/2 corresponds to negative y-axis. Correct.
#   Arc angle pi/2 corresponds to positive y-axis. Correct.
#   So Arc(center=(0,0), radius=10, start=3pi/2, end=5pi/2) covers the right side.

# Final segments list:
segments = [
    # Line from Top (10,0) to Bottom (-10,0)
    Line(start=(10, 0), end=(-10, 0)),
    
    # Arc from Bottom (-10,0) back to Top (10,0) via the right side (+z)
    Arc(
        center=(0, 0),
        radius=10.0,
        start_angle=3*math.pi/2, # 270 deg (Bottom)
        end_angle=5*math.pi/2    # 450 deg (Top, same as 90)
    )
]

contour = Contour(segments=segments, hollow=False)
geom = Geometry(contours=[contour])

my_d_section = Section(name="D Shape", geometry=geom)
```

### Handling Holes

To create a hollow section, simply add multiple contours to the geometry. Set `hollow=True` for internal voids.

**Important:** Holes are automatically clipped to only subtract from regions where they intersect with solid material. This means:
- Property calculations only subtract the portion of holes that overlap with solids
- Visualizations only show holes where they actually intersect solids
- Holes that extend beyond solid boundaries are automatically trimmed

```python
# Outer contour (defined as above)
outer_contour = Contour(segments=..., hollow=False)

# Inner hole (e.g., a circle)
# Full circle arc
hole_arc = Arc(center=(0,0), radius=5.0, start_angle=0, end_angle=2*math.pi)
inner_contour = Contour(segments=[hole_arc], hollow=True)

geom = Geometry(contours=[outer_contour, inner_contour])
sec = Section(name="Hollow D", geometry=geom)
```

**Example: I-Beam with Web Opening**

```python
# Create I-beam with a rectangular web opening
# The opening will be automatically clipped to only subtract from the web region
i_beam_contour = Contour(segments=[...], hollow=False)  # I-beam outline
opening_contour = Contour.from_points([...], hollow=True)  # Rectangular opening

geom = Geometry(contours=[i_beam_contour, opening_contour])
section = Section(name="I-Beam with Opening", geometry=geom)
# The opening is automatically clipped to only affect the web, not the flanges
```

### Creating Simple Polygons from Points

For simple polygonal shapes without curves, use `Contour.from_points()`:

```python
from sectiony import Contour, Geometry, Section

# Create a triangle from points
points = [(10, 0), (-5, 8.66), (-5, -8.66)]
contour = Contour.from_points(points, hollow=False)

geom = Geometry(contours=[contour])
triangle_section = Section(name="Triangle", geometry=geom)
```

### JSON Serialization

Geometries can be saved to and loaded from JSON files with full curve preservation:

```python
# Save geometry
geom.to_json("my_section.json")

# Load geometry
loaded_geom = Geometry.from_json("my_section.json")

# The JSON includes a schema version for forward compatibility
# Version 1: Supports Line, Arc, and CubicBezier segments
```

**JSON Structure:**

The JSON format preserves exact curve definitions (not just discretized points):

```json
{
  "version": 1,
  "contours": [
    {
      "segments": [
        {
          "type": "line",
          "start": [0, 0],
          "end": [10, 0]
        },
        {
          "type": "arc",
          "center": [5, 0],
          "radius": 5.0,
          "start_angle": 0,
          "end_angle": 3.14159
        }
      ],
      "hollow": false
    }
  ]
}
```

**Validation:**

The `from_dict()` and `from_json()` methods validate required fields and provide clear error messages if data is missing or invalid.