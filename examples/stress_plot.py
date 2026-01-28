"""
Example: Comprehensive stress analysis visualization.

This example demonstrates the different stress components that can be visualized
using the Stress class. We use a Rectangular Hollow Section (RHS) subjected to
combined loading:
- Axial Tension
- Bending about both axes
- Transverse Shear
- Torsion
"""

import sys
import matplotlib.pyplot as plt
from pathlib import Path

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sectiony.library import rhs

# 1. Define the Section
# RHS 200x100x10
section = rhs(b=100, h=200, t=10, r=15)

# 2. Define Internal Forces (Combined Loading)
# Units: N, mm
# Convention:
# N: Axial Force
# Vx, Vy: Shear Forces
# Mx: Bending Moment about X (Vertical Bending for sectiony convention where y is vertical)
# My: Bending Moment about Y (Horizontal Bending)
# Mz: Torsion about Z

N = 50e3       # 50 kN Tension
Vx = 10e3      # 10 kN Shear X
Vy = 20e3      # 20 kN Shear Y
Mx = 10e6      # 10 kNm Bending about X
My = 5e6       # 5 kNm Bending about Y
Mz = 5e6       # 5 kNm Torsion

stress = section.calculate_stress(N=N, Vx=Vx, Vy=Vy, Mx=Mx, My=My, Mz=Mz)

# 3. Visualization
# Create a 2x3 grid of subplots
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle(f"Stress Analysis: {section.name}\nCombined Loading", fontsize=16)

# Flatten axes for easy iteration
ax_list = axes.flatten()

# Plot configurations
plots = [
    ("sigma_axial", "Axial Stress", "RdBu_r"),
    ("sigma_bending", "Bending Stress", "RdBu_r"),
    ("sigma", "Total Normal Stress", "RdBu_r"),
    ("tau_shear", "Shear Stress (Transverse)", "viridis"),
    ("tau_torsion", "Shear Stress (Torsion)", "viridis"),
    ("von_mises", "Von Mises Stress", "plasma")
]

for ax, (stype, title, cmap) in zip(ax_list, plots):
    stress.plot(stress_type=stype, ax=ax, show=False, cmap=cmap)
    ax.set_title(title)

# Adjust layout
plt.tight_layout()
plt.subplots_adjust(top=0.9)  # Make room for suptitle

print("Displaying plots...")
plt.show()
