# Stress Analysis Implementation Design

## Concept

For a straight prismatic beam in classical beam theory, the internal resultants $(N, V_y, V_z, M_x, M_y, M_z)$ at any cross-section completely describe the loading state. 

We propose a `Stress` class that combines a `Section` object (geometry & properties) with these load resultants to calculate and visualize the stress distribution.

## Class Interface

### Initialization

The `Stress` object is initialized with a reference to a `Section` and the internal forces acting at that section.

```python
class Stress:
    def __init__(self, section: Section, 
                 N: float = 0.0,   # Axial Force
                 Vy: float = 0.0,  # Shear Force in Y
                 Vz: float = 0.0,  # Shear Force in Z
                 Mx: float = 0.0,  # Torsional Moment (T)
                 My: float = 0.0,  # Bending Moment about Y
                 Mz: float = 0.0): # Bending Moment about Z
        ...
```

### Core Methods

1.  **`sigma_axial(y, z) -> float`**
    *   Calculates normal stress due to axial force ($N/A$).
    
2.  **`sigma_bending(y, z) -> float`**
    *   Calculates normal stress due to bending moments.
    *   Formula: $\sigma = \frac{M_y z}{I_y} - \frac{M_z y}{I_z}$ (assuming principal axes).

3.  **`sigma(y, z) -> float`**
    *   Total normal stress: $\sigma_{axial} + \sigma_{bending}$.

4.  **`tau_shear(y, z) -> float`**
    *   Calculates shear stress due to transverse shear forces ($V_y, V_z$).
    *   *Note: Exact distribution requires numerical analysis (e.g., shear flow integration).*

5.  **`tau_torsion(y, z) -> float`**
    *   Calculates shear stress due to torsion ($M_x$).
    *   *Note: Requires solving the Poisson equation for non-circular sections.*

6.  **`tau(y, z) -> float`**
    *   Total shear stress magnitude.

7.  **`von_mises(y, z) -> float`**
    *   Calculates Von Mises yield criterion: $\sqrt{\sigma^2 + 3\tau^2}$.

### Visualization & Analysis

1.  **`plot(type: str = "von_mises", ax=None)`**
    *   Generates a contour plot of the specified stress component over the section geometry.
    *   Supported types: `"sigma"`, `"tau"`, `"von_mises"`.

2.  **`max(type: str) -> float`**
    *   Returns the maximum value of the specified stress component.

3.  **`min(type: str) -> float`**
    *   Returns the minimum value (useful for compressive normal stress).

## Usage Example

```python
from sectiony.section import Section
# from sectiony.stress import Stress

# 1. Define Section
rect = Section.from_shape(...)

# 2. Define Internal Loads at a cut
# e.g., Compression of 10kN, Bending of 5kNm
stress_state = Stress(section=rect, N=-10000, Mz=5000)

# 3. Analyze
max_tension = stress_state.max("sigma")
max_compression = stress_state.min("sigma")

# 4. Visualize
stress_state.plot("sigma")  # Plots normal stress distribution
stress_state.plot("von_mises") # Plots yield criterion
```

## Integration

Ideally, `Section` could have a helper method:

```python
# In Section class
def calculate_stress(self, N=0, Vy=0, Vz=0, Mx=0, My=0, Mz=0) -> Stress:
    return Stress(self, N, Vy, Vz, Mx, My, Mz)
```
