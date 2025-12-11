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
`u(b, h, t, r)`

*   **b**: Width (z-direction)
*   **h**: Height (y-direction)
*   **t**: Thickness (uniform for web and flanges)
*   **r**: Outside corner radius (0 for sharp corners)

**Example:**
```python
from sectiony.library import u

# U-channel with rounded corners
section = u(b=100.0, h=200.0, t=8.0, r=5.0)
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
- **U Section**: `b` (width), `h` (height), `t` (thickness), `r` (corner radius)
