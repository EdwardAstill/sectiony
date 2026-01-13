# Units and Coordinates

## Unit System

**sectiony** is unit-agnostic. It performs calculations based on the numerical values provided. It is up to the user to ensure consistency.

*   **Length**: If you define geometry in millimeters ($mm$), all length properties (Area, Inertia) will be in $mm^2$, $mm^4$, etc.
*   **Force**: If you apply loads in Newtons ($N$), moments should be in $N \cdot mm$.
*   **Stress**: The resulting stress will be in $Force / Length^2$.
    *   Example: $N$ and $mm$ $\rightarrow$ $MPa$ ($N/mm^2$).
    *   Example: $kN$ and $m$ $\rightarrow$ $kPa$ ($kN/m^2$).

## Coordinate System

The library uses a standard right-handed Cartesian coordinate system for the cross-section:

*   **x-axis**: Horizontal (Positive Right)
*   **y-axis**: Vertical (Positive Up)
*   **z-axis**: Longitudinal (Positive Out of Plane/Towards Viewer) - used for internal force vectors.

Points are defined as tuples `(x, y)`.

### Internal Force Sign Convention

*   **N (Axial)**: Positive = Tension.
*   **Vx (Shear in X)**: Positive = +x (Right).
*   **Vy (Shear in Y)**: Positive = +y (Up).
*   **Mx (Bending about X)**: Positive vector points right (+x). Induces compression in +y fibers (Top side).
*   **My (Bending about Y)**: Positive vector points up (+y). Induces compression in +x fibers (Right side).
*   **Mz (Torsion about Z)**: Positive vector points out of plane (+z).

## DXF Coordinates

DXF uses the same in-plane axes as **sectiony**:

*   **DXF X-axis** (Horizontal) $\leftrightarrow$ **Section x-axis** (Horizontal)
*   **DXF Y-axis** (Vertical) $\leftrightarrow$ **Section y-axis** (Vertical)

This ensures that a cross-section drawn in the XY plane in CAD appears with the same orientation in **sectiony** plots and calculations.
