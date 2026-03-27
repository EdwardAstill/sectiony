# Standard Library Shapes

The `sectiony.library` module provides functions to easily generate common structural sections. All library functions use native curve representations (`Arc`, `Line`) which are preserved for high-quality plotting and can be serialized to JSON.

## Circular Hollow Section (chs)
`chs(d, t)`

*   **d**: Outer diameter
*   **t**: Wall thickness

**Example:**
```python
from sectiony.library import chs

# CHS with 200mm outer diameter, 10mm wall thickness
section = chs(d=200.0, t=10.0)
```

## Rectangular Hollow Section (rhs)
`rhs(b, h, t, r)`

*   **b**: Width (z-direction)
*   **h**: Height (y-direction)
*   **t**: Wall thickness
*   **r**: Outer corner radius (0 for sharp corners)

**Example:**
```python
from sectiony.library import rhs

# RHS with rounded corners
section = rhs(b=100.0, h=200.0, t=10.0, r=15.0)

# RHS with sharp corners
section = rhs(b=100.0, h=200.0, t=10.0, r=0.0)
```

## I Section (i)
`i(d, b, tf, tw, r)`

*   **d**: Depth (Height, y-direction)
*   **b**: Width (Base, z-direction)
*   **tf**: Flange thickness
*   **tw**: Web thickness
*   **r**: Root radius (fillet between web and flange, 0 for sharp corners)

**Example:**
```python
from sectiony.library import i

# I-beam with fillets
section = i(d=300.0, b=150.0, tf=12.0, tw=8.0, r=10.0)

# I-beam with sharp corners
section = i(d=300.0, b=150.0, tf=12.0, tw=8.0, r=0.0)
```

## U (Channel) Section (u)
`u(b, h, tw, tf, r)`

*   **b**: Width (z-direction)
*   **h**: Height (y-direction)
*   **tw**: Web thickness
*   **tf**: Flange thickness
*   **r**: Outside corner radius (0 for sharp corners)

**Example:**
```python
from sectiony.library import u

# U-channel with rounded corners
section = u(b=100.0, h=200.0, tw=8.0, tf=10.0, r=5.0)
```

## Solid Rectangle (solid_rect)
`solid_rect(b, h)`

*   **b**: Width (x-direction)
*   **h**: Height (y-direction)

Solid rectangular section centered at the origin. No hollow.

**Example:**
```python
from sectiony.library import solid_rect

# Solid rectangle 100mm wide, 200mm tall
section = solid_rect(b=100.0, h=200.0)
```

## Solid Circle (solid_circle)
`solid_circle(d)`

*   **d**: Outer diameter

Solid circular section centered at the origin.

**Example:**
```python
from sectiony.library import solid_circle

# Solid circle with 150mm diameter
section = solid_circle(d=150.0)
```

## Square Hollow Section (shs)
`shs(d, t, r=0.0)`

*   **d**: Side length
*   **t**: Wall thickness
*   **r**: Outer corner radius (0 for sharp corners)

Square Hollow Section (equal-sided RHS).

**Example:**
```python
from sectiony.library import shs

# SHS with rounded corners
section = shs(d=100.0, t=6.0, r=10.0)

# SHS with sharp corners
section = shs(d=100.0, t=6.0)
```

## Angle (angle)
`angle(b, h, t, r=0.0)`

*   **b**: Horizontal leg width (x-direction)
*   **h**: Vertical leg height (y-direction)
*   **t**: Leg thickness
*   **r**: Root fillet radius (0 for sharp corners)

L-shaped section centered at the origin. **Note:** The centroid is NOT at the origin (asymmetric section). For equal legs, `Ixy ≠ 0`.

**Example:**
```python
from sectiony.library import angle

# Equal angle 100x100x10 with fillet
section = angle(b=100.0, h=100.0, t=10.0, r=8.0)

# Unequal angle, sharp corners
section = angle(b=100.0, h=75.0, t=8.0)
```

## T-Section (t_section)
`t_section(b, d, tf, tw, r=0.0)`

*   **b**: Flange width
*   **d**: Total depth
*   **tf**: Flange thickness
*   **tw**: Web thickness
*   **r**: Fillet radius (0 for sharp corners)

T-section with flange at top and web below, centered at the origin. Symmetric about the y-axis (`Cx=0`, `Ixy=0`), but centroid `Cy ≠ 0`.

**Example:**
```python
from sectiony.library import t_section

# T-section with fillets
section = t_section(b=150.0, d=200.0, tf=12.0, tw=8.0, r=10.0)

# T-section with sharp corners
section = t_section(b=150.0, d=200.0, tf=12.0, tw=8.0)
```

## Notes

- All library functions return a `Section` object with automatically calculated properties
- Sections use native curve representations for accurate geometry and plotting
- All sections can be serialized to JSON and loaded back with exact curve preservation
- See `examples/gallery/` for visual examples of all library sections

## Accessing Original Dimensions

All library shapes retain their original dimensions in a `dimensions` attribute (dictionary). This allows you to retrieve the parameters used to create the section:

**Example:**
```python
from sectiony.library import rhs

section = rhs(b=100.0, h=200.0, t=10.0, r=15.0)

# Access original dimensions
print(section.dimensions)
# Output: {'b': 100.0, 'h': 200.0, 't': 10.0, 'r': 15.0}

# Access individual dimensions
thickness = section.dimensions["t"]
height = section.dimensions["h"]
```

The `dimensions` dictionary contains:
- **CHS**: `d` (diameter), `t` (thickness)
- **RHS**: `b` (width), `h` (height), `t` (thickness), `r` (corner radius)
- **I Section**: `d` (depth), `b` (width), `tf` (flange thickness), `tw` (web thickness), `r` (root radius)
- **U Section**: `b` (width), `h` (height), `tw` (web thickness), `tf` (flange thickness), `r` (corner radius)
- **Solid Rect**: `b` (width), `h` (height)
- **Solid Circle**: `d` (diameter)
- **SHS**: `d` (side length), `t` (thickness), `r` (corner radius)
- **Angle**: `b` (horizontal leg), `h` (vertical leg), `t` (thickness), `r` (fillet radius)
- **T-Section**: `b` (flange width), `d` (total depth), `tf` (flange thickness), `tw` (web thickness), `r` (fillet radius)
