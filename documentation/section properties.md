# Section Properties

**sectiony** calculates a comprehensive set of geometric and mechanical properties for any cross-section. These properties are calculated using a hybrid approach:
- **Exact Integration (Green's Theorem)**: For Area, Centroids, and Moments of Inertia ($I_x, I_y, I_{xy}$).
- **Grid Discretization (Finite Difference)**: For complex torsion ($J$), plastic properties ($Z_{pl}$), and Shear Center.

## Geometric Properties

| Symbol | Property | Description |
| :--- | :--- | :--- |
| **A** | Area | Total cross-sectional area ($\int dA$). |
| **Cx** | Centroid (x) | Horizontal location of the geometric center. |
| **Cy** | Centroid (y) | Vertical location of the geometric center. |
| **x_max** | Max x-distance | Distance from centroid to the furthest fiber in x-direction. |
| **y_max** | Max y-distance | Distance from centroid to the furthest fiber in y-direction. |

## Inertia & Stiffness Properties

| Symbol | Property | Description |
| :--- | :--- | :--- |
| **Ix** | Moment of Inertia (x) | Second moment of area about the **x-axis** ($\int y^2 dA$). Resistance to bending about the x-axis. |
| **Iy** | Moment of Inertia (y) | Second moment of area about the **y-axis** ($\int x^2 dA$). Resistance to bending about the y-axis. |
| **Ixy** | Product of Inertia | Measure of asymmetry ($\int x y \, dA$). Zero for symmetric sections. Used to find principal axes. |
| **J** | Torsional Constant | Resistance to twisting. Calculated by solving the Poisson equation on a grid. |
| **Cw** | Warping Constant | Resistance to warping (non-uniform torsion). Calculated using the warping function. |

## Strength & Stability Properties

| Symbol | Property | Description |
| :--- | :--- | :--- |
| **Sx** | Elastic Modulus (x) | $I_x / y_{max}$. Used for elastic stress calculation ($\sigma = M_x / S_x$). |
| **Sy** | Elastic Modulus (y) | $I_y / x_{max}$. Used for elastic stress calculation ($\sigma = M_y / S_y$). |
| **rx** | Radius of Gyration (x) | $\sqrt{I_x / A}$. Used for column buckling analysis about the x-axis. |
| **ry** | Radius of Gyration (y) | $\sqrt{I_y / A}$. Used for column buckling analysis about the y-axis. |
| **Zpl_x** | Plastic Modulus (x) | First moment of area about the plastic neutral axis (horizontal). Used for plastic moment capacity. |
| **Zpl_y** | Plastic Modulus (y) | First moment of area about the plastic neutral axis (vertical). Used for plastic moment capacity. |

## Shape Factors

| Symbol | Property | Description |
| :--- | :--- | :--- |
| **shape_factor_x** | Shape Factor (x) | Ratio of plastic to elastic section modulus: $Z_{pl,x} / S_x$. Equal to 1.5 for a rectangle. Always > 1.0 for any solid section. |
| **shape_factor_y** | Shape Factor (y) | Ratio of plastic to elastic section modulus: $Z_{pl,y} / S_y$. Equal to 1.5 for a rectangle. Always > 1.0 for any solid section. |

## Principal Second Moments of Area

| Symbol | Property | Description |
| :--- | :--- | :--- |
| **I1** | Major Principal Inertia | Maximum second moment of area: $\frac{I_x+I_y}{2} + \sqrt{\left(\frac{I_x-I_y}{2}\right)^2 + I_{xy}^2}$ |
| **I2** | Minor Principal Inertia | Minimum second moment of area: $\frac{I_x+I_y}{2} - \sqrt{\left(\frac{I_x-I_y}{2}\right)^2 + I_{xy}^2}$ |
| **principal_angle** | Principal Angle | Angle in radians from the x-axis to the I1 (major) axis: $\frac{1}{2} \arctan\!\left(\frac{-2I_{xy}}{I_x - I_y}\right)$. Zero for doubly-symmetric sections. |

## Section Methods

### `rotate(angle)`

Returns a new `Section` with the geometry rotated counter-clockwise by `angle` radians. All properties are recalculated on the rotated geometry. For example, rotating by π/2 swaps `Ix` and `Iy`.

```python
import math
rotated = section.rotate(math.pi / 2)
```

### `+` Operator (`__add__`)

Merges the geometries of two sections into a single combined section. Properties are recalculated from the combined geometry. Useful for built-up sections.

```python
combined = sec_a + sec_b
```

### `print(sec)` / `str(sec)` (`__str__`)

Prints a formatted table of all section properties.

```python
print(section)
```

## Shear Center

| Symbol | Property | Description |
| :--- | :--- | :--- |
| **SCx** | Shear Center (x) | Horizontal coordinate of the shear center. |
| **SCy** | Shear Center (y) | Vertical coordinate of the shear center. |

The **shear center** is the point through which transverse loads must act to produce bending without torsion. It's calculated using numerical methods on the discretized grid:

- **Doubly symmetric sections** (I-beams with equal flanges, rectangles, circles): The shear center coincides with the centroid ($SC_x = C_x$, $SC_y = C_y$).
- **Singly symmetric sections** (channels, T-sections): The shear center lies on the axis of symmetry but is offset from the centroid.
- **Asymmetric sections**: The shear center is offset from the centroid in both directions.

For open thin-walled sections (like channels), the shear center can be significantly offset from the centroid. Loads not applied through the shear center will induce torsion in addition to bending.

## Example: Calculating Properties for a Pentagon

Here is a complete example of creating a pentagonal section and inspecting its calculated properties.

```python
import math
from sectiony import Section, Geometry, Contour, Line

# Define a regular pentagon
radius = 10.0
points = []

# Generate points for a pentagon
for i in range(5):
    angle = 2 * math.pi * i / 5  # 72 degrees steps
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    points.append((x, y))

# Create section using Contour.from_points() convenience method
contour = Contour.from_points(points, hollow=False)
geom = Geometry(contours=[contour])
pentagon = Section(name="Pentagon", geometry=geom)

# Access calculated properties
print(f"--- Section Properties for Pentagon (R={radius}) ---")
print(f"Area (A): {pentagon.A:.4f}")
print(f"Centroid (Cx, Cy): ({pentagon.Cx:.4f}, {pentagon.Cy:.4f})")
print(f"Moment of Inertia (Ix): {pentagon.Ix:.4f}")
print(f"Moment of Inertia (Iy): {pentagon.Iy:.4f}")
print(f"Torsional Constant (J): {pentagon.J:.4f}")
print(f"Plastic Modulus x (Zpl_x): {pentagon.Zpl_x:.4f}")
```

### Explanation of Calculations

1.  **Exact Area & Inertia**: When `pentagon` is initialized, `geometry.calculate_properties()` is called. It iterates through the segments, discretizes them into points, and uses Green's Theorem (polygon area formulas) to compute `A`, `Cx`, `Cy`, `Ix`, `Iy`, and `Ixy` exactly.
2.  **Hole Handling**: For sections with holes (`hollow=True` contours), holes are automatically clipped to only subtract from regions where they intersect with solid material. This ensures property calculations are physically meaningful.
3.  **Grid Properties**: For `J` and `Zpl`, the code automatically creates a 2D grid (mask) over the shape's bounding box.
    *   **Plastic Modulus ($Z_{pl}$)**: It finds the plastic neutral axis (PNA) that bisects the area on the grid and sums the first moments of area about that axis.
    *   **Torsion ($J$)**: It solves the Poisson partial differential equation ($\nabla^2 \phi = -2$) on the grid to find the Prandtl stress function $\phi$, and integrates it to find $J$.
    *   **Warping Constant ($C_w$)**: It solves the Laplace equation to find the warping function $\omega$, computes the normalized sectorial coordinate $\omega_n$, and integrates $\omega_n^2$ over the area.
