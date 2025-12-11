# Sectiony

A Python library for calculating section properties and performing stress analysis of structural cross-sections.

## Library of Standard Shapes

Sectiony provides a library of common structural shapes that can be easily generated. These are available under `sectiony.library`.

### Circular Hollow Section (chs)
`sectiony.library.chs(d, t)`

**Parameters:**
- `d` (float): Outer diameter
- `t` (float): Wall thickness

---

### Rectangular Hollow Section (rhs)
`sectiony.library.rhs(b, h, t, r)`

**Parameters:**
- `b` (float): Width (z-direction)
- `h` (float): Height (y-direction)
- `t` (float): Wall thickness
- `r` (float): Outer corner radius

---

### I Section (i)
`sectiony.library.i(d, b, tf, tw, r)`

**Parameters:**
- `d` (float): Depth (Height, y-direction)
- `b` (float): Width (Base, z-direction)
- `tf` (float): Flange thickness
- `tw` (float): Web thickness
- `r` (float): Root radius (fillet between web and flange)

---

### U (Channel) Section (u)
`sectiony.library.u(b, h, t, r)`

**Parameters:**
- `b` (float): Width (z-direction)
- `h` (float): Height (y-direction)
- `t` (float): Thickness (uniform for web and flanges)
- `r` (float): Outside corner radius

---

## Features

### Geometry Visualization
You can visualize the cross-section geometry, including accurate rendering of curved segments. Holes are automatically clipped to only show where they intersect with solid material.

```python
from sectiony.library import i

# Create an I-section
beam = i(d=100.0, b=50.0, tf=10.0, tw=5.0, r=5.0)

# Plot the section
beam.plot()

# Save plot to file
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
beam.plot(ax=ax, show=False)
fig.savefig("beam.svg", format='svg')
```

### Stress Analysis and Plotting
Sectiony can calculate and visualize stress distributions resulting from internal forces (Axial, Bending, Shear, Torsion).

```python
# Apply loads to the section
# N: Axial force, Vy/Vz: Shear forces, Mx: Torsion, My/Mz: Bending moments
stress_analysis = beam.calculate_stress(
    N=1000,    # Tension
    Mz=50000,  # Bending about Z-axis
    Vy=500     # Shear in Y-direction
)

# Plot von Mises stress distribution
stress_analysis.plot(stress_type="von_mises", cmap="inferno")

# Available stress types:
# "sigma" (Normal), "tau" (Shear), "von_mises" (Combined)
# "sigma_axial", "sigma_bending"
# "tau_shear", "tau_torsion"
```

### JSON Serialization
You can save and load complex section geometries using JSON. The format preserves exact curve definitions (not just discretized points) and includes schema versioning.

```python
from sectiony import Geometry

# Save geometry
beam.geometry.to_json("my_beam.json")

# Load geometry
loaded_geom = Geometry.from_json("my_beam.json")

# Properties are preserved exactly
new_section = Section(name="Loaded", geometry=loaded_geom)
print(f"Area: {new_section.A:.2f}")  # Same as original
```

**See Examples:**
- `examples/making_sections.py` - Comprehensive examples of creating sections
- `examples/gallery/` - Visual gallery of section types
- `examples/json/` - Sample JSON files for all section types

## Section Properties

Sectiony automatically calculates a comprehensive set of properties for any geometry.

| Symbol | Property | Description |
| :--- | :--- | :--- |
| **A** | Area | Total cross-sectional area. |
| **Cy**, **Cz** | Centroids | Geometric center of the section. |
| **Iy**, **Iz** | Moments of Inertia | Resistance to bending about y and z axes. |
| **Iyz** | Product of Inertia | Measure of asymmetry. |
| **J** | Torsional Constant | Resistance to twisting. |
| **Sy**, **Sz** | Elastic Moduli | Used for elastic stress calculation ($I/c$). |
| **Zpl_y**, **Zpl_z** | Plastic Moduli | Used for plastic moment capacity. |
| **ry**, **rz** | Radii of Gyration | Used for buckling analysis ($\sqrt{I/A}$). |
| **SCy**, **SCz** | Shear Center | Point where transverse loads induce no torsion. |

### Accessing Properties

Properties are available as attributes on the `Section` object:

```python
# Print properties
print(f"Area: {beam.A:.2f}")
print(f"Iyy: {beam.Iy:.2f}")
print(f"J: {beam.J:.2f}")
```

