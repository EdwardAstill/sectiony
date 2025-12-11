"""
Example: RHS (Rectangular Hollow Section) Properties

This script demonstrates creating and analyzing an RHS section:
- 150mm x 250mm outer dimensions
- 6mm wall thickness
- 12.6mm outer corner radius
- 6.6mm inner corner radius
"""

import sys
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sectiony.library import rhs

# Create RHS section (dimensions in meters)
# Parameters: b (width), h (height), t (thickness), r (outer corner radius)
section = rhs(b=0.15, h=0.25, t=0.006, r=0.012)

# Display section properties
print("=" * 70)
print(f"SECTION: {section.name}")
print("=" * 70)

print("\nGeometry:")
print(f"  Width (b):            0.15 m")
print(f"  Height (h):           0.25 m")
print(f"  Wall thickness (t):   0.006 m")
print(f"  Outer corner radius:  0.0126 m")
print(f"  Inner corner radius:  0.0066 m")

print("\nSection Properties:")
print(f"  Area (A):             {section.A:.6f} m²")
print(f"  Centroid (Cy, Cz):    ({section.Cy:.6f}, {section.Cz:.6f}) m")

print("\nSecond Moments of Area:")
print(f"  Iy:                   {section.Iy:.6e} m⁴")
print(f"  Iz:                   {section.Iz:.6e} m⁴")
print(f"  Iyz:                  {section.Iyz:.6e} m⁴")

print("\nRadii of Gyration:")
print(f"  ry:                   {section.ry:.6f} m")
print(f"  rz:                   {section.rz:.6f} m")

print("\nElastic Section Moduli:")
print(f"  Sy:                   {section.Sy:.6e} m³")
print(f"  Sz:                   {section.Sz:.6e} m³")

print("\nPlastic Section Moduli:")
print(f"  Zpl_y:                {section.Zpl_y:.6e} m³")
print(f"  Zpl_z:                {section.Zpl_z:.6e} m³")

print("\nTorsion & Shear:")
print(f"  Torsion constant (J): {section.J:.6e} m⁴")
print(f"  Warping constant (Cw):{section.Cw:.6e} m⁶")
print(f"  Shear center (SCy):   {section.SCy:.6f} m")
print(f"  Shear center (SCz):   {section.SCz:.6f} m")

print("\nExtreme Fiber Distances:")
print(f"  y_max:                {section.y_max:.6f} m")
print(f"  z_max:                {section.z_max:.6f} m")

# Generate and save plot
print("\n" + "=" * 70)
print("Generating plot...")
print("=" * 70)

fig, ax = plt.subplots(figsize=(8, 10))
section.plot(ax=ax, show=False)
ax.set_title(
    f"{section.name}\n"
    f"A={section.A:.1f} mm², Iy={section.Iy:.2e} mm⁴, Iz={section.Iz:.2e} mm⁴",
    fontsize=11
)

# Save plot
output_path = Path(__file__).parent.parent / "gallery" / "rhs_example.svg"
output_path.parent.mkdir(exist_ok=True)
fig.savefig(output_path, format='svg', bbox_inches='tight', dpi=150)
plt.close(fig)

print(f"\nPlot saved to: {output_path.relative_to(Path(__file__).parent.parent)}")
print("\nDone!")

