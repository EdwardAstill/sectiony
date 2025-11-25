# Section Properties

**sectiony** calculates a comprehensive set of geometric and mechanical properties for any cross-section. These properties are calculated using a hybrid approach:
- **Exact Integration (Green's Theorem)**: For Area, Centroids, and Moments of Inertia ($I_y, I_z, I_{yz}$).
- **Grid Discretization (Finite Difference)**: For complex torsion ($J$) and plastic properties ($Z_{pl}$).

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
