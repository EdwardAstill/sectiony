# Import and Export

**sectiony** supports saving and loading geometry using JSON and DXF formats. This allows you to store your custom sections or import geometry from CAD software.

## JSON Format

The native JSON format is the recommended way to save **sectiony** geometries because it preserves the exact mathematical definition of curves (including `Arc` and `CubicBezier` segments), rather than just approximated points.

### Saving to JSON

```python
from sectiony import Geometry, Section

# Assuming you have a section or geometry object
my_section.geometry.to_json("my_section.json")
```

### Loading from JSON

```python
from sectiony import Geometry, Section

# Load geometry
geometry = Geometry.from_json("my_section.json")

# Create section from loaded geometry
section = Section(name="Imported Section", geometry=geometry)
```

### JSON Structure

The JSON file contains a versioned schema describing the contours and segments.

```json
{
  "version": 1,
  "contours": [
    {
      "segments": [
        {
          "type": "line",
          "start": [0.0, 0.0],
          "end": [10.0, 0.0]
        },
        {
          "type": "arc",
          "center": [5.0, 0.0],
          "radius": 5.0,
          "start_angle": 0.0,
          "end_angle": 3.14159
        }
      ],
      "hollow": false
    }
  ]
}
```

---

## DXF Format

You can import geometry from DXF (Drawing Exchange Format) files, which is supported by most CAD software (AutoCAD, LibreCAD, etc.).

### Importing from DXF

```python
from sectiony import Geometry, Section

# Import geometry from a DXF file
geometry = Geometry.from_dxf("drawing.dxf")

# Create section
section = Section(name="DXF Section", geometry=geometry)
```

**Note on Coordinates:**
*   **DXF X-axis** maps to **Section Y-axis** (Horizontal in engineering convention)
*   **DXF Y-axis** maps to **Section Z-axis** (Vertical in engineering convention)

### Supported DXF Entities

The importer handles the following entities found in the `ENTITIES` section of the DXF file:

1.  **LINE**: Imported as `Line` segments.
2.  **ARC**: Imported as `Arc` segments.
3.  **LWPOLYLINE**:
    *   Imported as a connected `Contour`.
    *   Supports straight segments and arc segments (via bulge factors).
    *   Closed polylines are automatically treated as closed contours.

### Preparing DXF Files for Import

For best results when creating DXF files in CAD:
*   **Use Polylines**: Draw your section using closed Polylines (`LWPOLYLINE`). This ensures the contour is continuous and closed.
*   **Clean Geometry**: Ensure there are no gaps, overlapping lines, or stray entities.
*   **Units**: Be aware of your drawing units. **sectiony** imports raw coordinate values.
*   **Origin**: Place the geometric center of your shape near the origin (0,0) in CAD, or expect to see large offset values in the imported section.

### Exporting to DXF

You can also export your geometry to a DXF file for use in CAD.

```python
# Export geometry to DXF
my_section.geometry.to_dxf("output.dxf")
```

*   `Line` and `Arc` segments are exported natively.
*   `CubicBezier` segments are approximated as a series of small `Line` segments (since standard DXF R12/minimal parsers often don't support splines easily, or for compatibility).

