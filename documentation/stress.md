# Stress Analysis

## Concept

For a straight prismatic beam in classical beam theory, the internal resultants $(N, V_x, V_y, M_x, M_y, M_z)$ at any cross-section completely describe the loading state. 

The `Stress` class combines a `Section` object (geometry & properties) with these load resultants to calculate and visualize the stress distribution.

## Class Interface

### Initialization

```python
from sectiony.stress import Stress

stress = Stress(
    section,          # Section object
    N=0.0,            # Axial Force (positive = tension)
    Vx=0.0,           # Shear Force in x (horizontal)
    Vy=0.0,           # Shear Force in y (vertical)
    Mx=0.0,           # Bending Moment about x axis
    My=0.0,           # Bending Moment about y axis
    Mz=0.0            # Torsional Moment about z axis
)
```

### Stress Calculation Methods

| Method | Description |
|--------|-------------|
| `sigma_axial(x, y)` | Normal stress due to axial force: $\sigma = N/A$ |
| `sigma_bending(x, y)` | Normal stress due to bending (principal axes): $\sigma = -\frac{M_x y}{I_x} - \frac{M_y x}{I_y}$ |
| `sigma(x, y)` | Total normal stress: $\sigma_{axial} + \sigma_{bending}$ |
| `tau_shear(x, y)` | Shear stress due to transverse forces (approximate) |
| `tau_torsion(x, y)` | Shear stress due to torsion (approximate) |
| `tau(x, y)` | Total shear stress magnitude |
| `von_mises(x, y)` | Von Mises stress: $\sqrt{\sigma^2 + 3\tau^2}$ |

### Analysis Methods

| Method | Description |
|--------|-------------|
| `at(x, y, stress_type)` | Stress value at a specific point |
| `max(stress_type)` | Maximum stress over geometry vertices |
| `min(stress_type)` | Minimum stress over geometry vertices |

### Stress Types

Supported `stress_type` values:
- `"sigma"` - Total normal stress
- `"sigma_axial"` - Axial component only
- `"sigma_bending"` - Bending component only
- `"tau"` - Total shear stress
- `"tau_shear"` - Transverse shear component
- `"tau_torsion"` - Torsional shear component
- `"von_mises"` - Von Mises equivalent stress

### Visualization

```python
stress.plot(
    stress_type="von_mises",  # Type of stress to plot
    ax=None,                   # Optional matplotlib axes
    show=True,                 # Whether to display
    cmap="viridis"             # Colormap
)
```

## Usage Example

```python
from sectiony.geometry import Geometry, Contour, Line
from sectiony.section import Section

# 1. Define Section
points = [(10, 5), (10, -5), (-10, -5), (-10, 5)]
contour = Contour(segments=[
    Line(start=(10, 5), end=(10, -5)),
    Line(start=(10, -5), end=(-10, -5)),
    Line(start=(-10, -5), end=(-10, 5)),
    Line(start=(-10, 5), end=(10, 5))
])
section = Section(
    name="Rect 20x10",
    geometry=Geometry(contours=[contour])
)

# 2. Create stress state (compression + bending)
stress = section.calculate_stress(N=-10000, Mx=5000)

# 3. Analyze
max_tension = stress.max("sigma")
max_compression = stress.min("sigma")
stress_at_corner = stress.at(10, 5, "von_mises")

# 4. Visualize
stress.plot("sigma")       # Normal stress distribution
stress.plot("von_mises")   # Von Mises stress
```

## Notes

- Shear stress calculations (`tau_shear`, `tau_torsion`) use simplified approximations. Accurate distributions require numerical methods.
- Sign convention: positive `Mx` compresses positive `y` fibers (top of section), and positive `My` compresses positive `x` fibers (right side of section).
- Stress plots automatically handle holes and clip them to only show where they intersect with solid material, matching the property calculation behavior.
