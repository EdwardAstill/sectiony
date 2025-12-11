# Section Properties

**sectiony** calculates a comprehensive set of geometric and mechanical properties for any cross-section. These properties are calculated using a hybrid approach:
- **Exact Integration (Green's Theorem)**: For Area, Centroids, and Moments of Inertia ($I_y, I_z, I_{yz}$).
- **Grid Discretization (Finite Difference)**: For complex torsion ($J$), plastic properties ($Z_{pl}$), and Shear Center.

## Geometric Properties

| Symbol | Property | Description |
| :--- | :--- | :--- |
| **A** | Area | Total cross-sectional area ($\int dA$). |
| **Cy** | Centroid (y) | Vertical location of the geometric center. |
| **Cz** | Centroid (z) | Horizontal location of the geometric center. |
| **y_max** | Max y-distance | Distance from centroid to the furthest fiber in y-direction. |
| **z_max** | Max z-distance | Distance from centroid to the furthest fiber in z-direction. |

## Inertia & Stiffness Properties

| Symbol | Property | Description |
| :--- | :--- | :--- |
| **Iy** | Moment of Inertia (y) | Second moment of area about the **y-axis** ($\int z^2 dA$). Resistance to bending about the vertical axis (sideways bending). |
| **Iz** | Moment of Inertia (z) | Second moment of area about the **z-axis** ($\int y^2 dA$). Resistance to bending about the horizontal axis (vertical bending). |
| **Iyz** | Product of Inertia | Measure of asymmetry ($\int yz dA$). Zero for symmetric sections. Used to find principal axes. |
| **J** | Torsional Constant | Resistance to twisting. Calculated by solving the Poisson equation on a grid. |

## Strength & Stability Properties

| Symbol | Property | Description |
| :--- | :--- | :--- |
| **Sy** | Elastic Modulus (y) | $I_y / z_{max}$. Used for elastic stress calculation ($\sigma = M_y / S_y$). |
| **Sz** | Elastic Modulus (z) | $I_z / y_{max}$. Used for elastic stress calculation ($\sigma = M_z / S_z$). |
| **ry** | Radius of Gyration (y) | $\sqrt{I_y / A}$. Used for column buckling analysis about the y-axis. |
| **rz** | Radius of Gyration (z) | $\sqrt{I_z / A}$. Used for column buckling analysis about the z-axis. |
| **Zpl_y** | Plastic Modulus (y) | First moment of area about the plastic neutral axis (vertical). Used for plastic moment capacity. |
| **Zpl_z** | Plastic Modulus (z) | First moment of area about the plastic neutral axis (horizontal). Used for plastic moment capacity. |

## Shear Center

| Symbol | Property | Description |
| :--- | :--- | :--- |
| **SCy** | Shear Center (y) | Vertical coordinate of the shear center. |
| **SCz** | Shear Center (z) | Horizontal coordinate of the shear center. |

The **shear center** is the point through which transverse loads must act to produce bending without torsion. It's calculated using numerical methods on the discretized grid:

- **Doubly symmetric sections** (I-beams with equal flanges, rectangles, circles): The shear center coincides with the centroid ($SC_y = C_y$, $SC_z = C_z$).
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
    # y is vertical (sin), z is horizontal (cos)
    # Using +y as up (pi/2 is top)
    theta = angle + math.pi/2 
    y = radius * math.sin(theta)
    z = radius * math.cos(theta)
    points.append((y, z))

# Create section using Contour.from_points() convenience method
contour = Contour.from_points(points, hollow=False)
geom = Geometry(contours=[contour])
pentagon = Section(name="Pentagon", geometry=geom)

# Access calculated properties
print(f"--- Section Properties for Pentagon (R={radius}) ---")
print(f"Area (A): {pentagon.A:.4f}")
print(f"Centroid (Cy, Cz): ({pentagon.Cy:.4f}, {pentagon.Cz:.4f})")
print(f"Moment of Inertia (Iy): {pentagon.Iy:.4f}")
print(f"Moment of Inertia (Iz): {pentagon.Iz:.4f}")
print(f"Torsional Constant (J): {pentagon.J:.4f}")
print(f"Plastic Modulus z (Zpl_z): {pentagon.Zpl_z:.4f}")
```

### Explanation of Calculations

1.  **Exact Area & Inertia**: When `pentagon` is initialized, `geometry.calculate_properties()` is called. It iterates through the segments, discretizes them into points, and uses Green's Theorem (polygon area formulas) to compute `A`, `Cy`, `Cz`, `Iy`, `Iz`, and `Iyz` exactly.
2.  **Hole Handling**: For sections with holes (`hollow=True` contours), holes are automatically clipped to only subtract from regions where they intersect with solid material. This ensures property calculations are physically meaningful.
3.  **Grid Properties**: For `J` and `Zpl`, the code automatically creates a 2D grid (mask) over the shape's bounding box.
    *   **Plastic Modulus ($Z_{pl}$)**: It finds the plastic neutral axis (PNA) that bisects the area on the grid and sums the first moments of area about that axis.
    *   **Torsion ($J$)**: It solves the Poisson partial differential equation ($\nabla^2 \phi = -2$) on the grid to find the Prandtl stress function $\phi$, and integrates it to find $J$.
