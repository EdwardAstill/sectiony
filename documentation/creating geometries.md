# Creating Geometries

A `Geometry` object defines the shape of a cross-section. There are several ways to create geometries in **sectiony**:

## 1. From Points (Simple Polygons)

The quickest way to create simple polygonal shapes is using `Contour.from_points()`:

```python
from sectiony import Contour, Geometry

# Create a triangle
points = [(10, 0), (-5, 8.66), (-5, -8.66)]
contour = Contour.from_points(points, hollow=False)
geometry = Geometry(contours=[contour])

# Create a rectangle with a hole
outer_points = [(50, 30), (50, -30), (-50, -30), (-50, 30)]
inner_points = [(30, 20), (30, -20), (-30, -20), (-30, 20)]

outer = Contour.from_points(outer_points, hollow=False)
inner = Contour.from_points(inner_points, hollow=True)

geometry = Geometry(contours=[outer, inner])
```

## 2. Manual Method (Curves and Lines)

For shapes with curves, create a `Geometry` by defining segments explicitly:

```python
from sectiony import Geometry, Contour, Line, Arc, CubicBezier
import math

# Define segments
segments = [
    Line(start=(10, 0), end=(-10, 0)),
    Arc(center=(0, 0), radius=10.0, 
        start_angle=3*math.pi/2, end_angle=5*math.pi/2)
]

# Create contour and geometry
contour = Contour(segments=segments, hollow=False)
geometry = Geometry(contours=[contour])
```

**Available Segment Types:**

- **Line**: `Line(start=(y1, z1), end=(y2, z2))`
- **Arc**: `Arc(center=(y, z), radius=r, start_angle=θ1, end_angle=θ2)`
  - Angles in radians: 0 is +z (Right), π/2 is +y (Up)
- **CubicBezier**: `CubicBezier(p0, p1, p2, p3)`
  - p0 = start, p3 = end, p1/p2 = control points

## 3. From DXF Files

Import geometry directly from CAD drawings:

```python
from sectiony import Geometry

# Load from DXF file
geometry = Geometry.from_dxf("path/to/drawing.dxf")
```

The DXF parser supports:
- LINE entities
- ARC entities  
- LWPOLYLINE entities (with bulge factors for arcs)

DXF coordinates are automatically mapped to match **sectiony**'s coordinate system (DXF X → Section Z, DXF Y → Section Y).

## 4. From Standard Library Shapes

Library functions return `Section` objects that contain pre-built geometry:

```python
from sectiony.library import rhs, chs, i, u

# Get geometry from a library section
my_rhs = rhs(b=100, h=200, t=10, r=15)
geometry = my_rhs.geometry  # Access the Geometry object
```

## Coordinate System

- **y-axis**: Vertical (Positive Up)
- **z-axis**: Horizontal (Positive Right)
- Points are tuples: `(y, z)`

## Validation

`Geometry` objects can contain open or closed contours. However, to create a `Section` for property calculations, all contours **must be closed** (start point connects to end point).

```python
# Valid geometry (can be used for Section)
closed_geom = Geometry(contours=[Contour.from_points([(0,0), (10,0), (0,10)])])

# Valid geometry, but cannot be used for Section (open contour)
open_geom = Geometry(contours=[Contour.from_points([(0,0), (10,0)])])
```

## Handling Holes

To create hollow sections, add multiple contours with `hollow=True` for voids. Holes are automatically clipped to only subtract from solid regions.

```python
outer = Contour(segments=[...], hollow=False)
hole = Contour(segments=[...], hollow=True)

geometry = Geometry(contours=[outer, hole])
```

## JSON Serialization

Save and load geometries to/from JSON:

```python
# Save to JSON
geometry.to_json("section.json")

# Load from JSON
geometry = Geometry.from_json("section.json")

# Dictionary conversion
geom_dict = geometry.to_dict()
geometry = Geometry.from_dict(geom_dict)
```
