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

*   **y-axis**: Vertical (Positive Up)
*   **z-axis**: Horizontal (Positive Right)
*   **x-axis**: Longitudinal (Positive Out of Plane/Towards Viewer) - used for internal force vectors.

Points are defined as tuples `(y, z)`.

### Internal Force Sign Convention

*   **N (Axial)**: Positive = Tension.
*   **My (Bending about Y)**: Positive vector points up (+y). Induces compression in +z fibers (Right side).
*   **Mz (Bending about Z)**: Positive vector points right (+z). Induces compression in +y fibers (Top side).
*   **Mx (Torsion)**: Positive vector points out of plane (+x).
