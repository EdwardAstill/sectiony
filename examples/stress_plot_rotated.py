"""
Example: Rotated Stress Plot Visualization

This example demonstrates the rotate parameter in stress plots.
When rotate=True, the stress plot is rotated 90° counter-clockwise:
- x-axis becomes vertical (pointing up)
- y-axis points left (negative x direction)
- The colorbar/scale remains on the right side and is properly sized
"""

import sys
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sectiony.library import rhs, i

# 1. Define the Section
# RHS 200x100x10
section = rhs(b=100, h=200, t=10, r=15)

# 2. Define Internal Forces (Combined Loading)
# Units: N, mm
N = 50e3       # 50 kN Tension
Vx = 10e3      # 10 kN Shear X
Vy = 20e3      # 20 kN Shear Y
Mx = 10e6      # 10 kNm Bending about X
My = 5e6       # 5 kNm Bending about Y
Mz = 5e6       # 5 kNm Torsion

stress = section.calculate_stress(N=N, Vx=Vx, Vy=Vy, Mx=Mx, My=My, Mz=Mz)

# 3. Visualization - Comparison of Normal vs Rotated Views
fig, axes = plt.subplots(1, 2, figsize=(16, 8))
fig.suptitle(f"Stress Analysis: {section.name}\nNormal vs Rotated View", fontsize=14, fontweight='bold')

# Normal plot (rotate=False, default)
stress.plot(stress_type="von_mises", ax=axes[0], show=False, cmap='viridis', rotate=False)
axes[0].set_title("Normal View\n(x horizontal, y vertical)", fontsize=12)
axes[0].grid(True, alpha=0.3)

# Rotated plot (rotate=True)
stress.plot(stress_type="von_mises", ax=axes[1], show=False, cmap='viridis', rotate=True)
axes[1].set_title("Rotated View\n(x vertical, y pointing left)", fontsize=12)
axes[1].grid(True, alpha=0.3)

# Adjust layout
plt.tight_layout()
plt.subplots_adjust(top=0.9)  # Make room for suptitle

# Save plot
output_path = Path(__file__).parent.parent / "gallery" / "stress_rotated_comparison.svg"
output_path.parent.mkdir(exist_ok=True)
fig.savefig(output_path, format='svg', bbox_inches='tight', dpi=150)
plt.close(fig)

print(f"Saved: {output_path.relative_to(Path(__file__).parent.parent)}")

# 4. Individual stress types in rotated view
print("\nGenerating individual stress type plots (rotated)...")

stress_types = [
    ("sigma_axial", "Axial Stress", "RdBu_r"),
    ("sigma_bending", "Bending Stress", "RdBu_r"),
    ("sigma", "Total Normal Stress", "RdBu_r"),
    ("tau_shear", "Shear Stress (Transverse)", "viridis"),
    ("tau_torsion", "Shear Stress (Torsion)", "viridis"),
    ("von_mises", "Von Mises Stress", "plasma")
]

for stype, title, cmap in stress_types:
    fig, ax = plt.subplots(figsize=(8, 8))
    stress.plot(stress_type=stype, ax=ax, show=False, cmap=cmap, rotate=True)
    ax.set_title(f"{title} (Rotated View)", fontsize=12)
    ax.grid(True, alpha=0.3)
    
    output_path = Path(__file__).parent.parent / "gallery" / f"stress_rotated_{stype}.svg"
    plt.tight_layout()
    fig.savefig(output_path, format='svg', bbox_inches='tight', dpi=150)
    plt.close(fig)
    
    print(f"  Saved: gallery/stress_rotated_{stype}.svg")

print("\nDone! Rotated stress plot examples generated.")
