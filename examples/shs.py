"""
Example: SHS (Square Hollow Section) Properties

This script demonstrates creating and analyzing an SHS section:
- 150mm x 150mm outer dimensions
- 6mm wall thickness
- 12mm outer corner radius
"""

import sys
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sectiony.library import rhs

# Create SHS section (dimensions in meters)
# Parameters: b (width), h (height), t (thickness), r (outer corner radius)
# SHS is just RHS with b = h
section = rhs(b=0.15, h=0.15, t=0.006, r=0.0126)

# Display section properties
print("=" * 70)
print(f"SECTION: {section.name}")
print("=" * 70)

print("\nGeometry:")
print(f"  Width (b):            0.15 m")
print(f"  Height (h):           0.15 m")
print(f"  Wall thickness (t):   0.006 m")
print(f"  Outer corner radius:  0.0126 m")

print("\nSection Properties:")
print(f"  Area (A):             {section.A:.6f} m^2")
print(f"  Centroid (Cx, Cy):    ({section.Cx:.6f}, {section.Cy:.6f}) m")

print("\nSecond Moments of Area:")
print(f"  Ix:                   {section.Ix:.6e} m^4")
print(f"  Iy:                   {section.Iy:.6e} m^4")
print(f"  Ixy:                  {section.Ixy:.6e} m^4")

print("\nRadii of Gyration:")
print(f"  rx:                   {section.rx:.6f} m")
print(f"  ry:                   {section.ry:.6f} m")

print("\nElastic Section Moduli:")
print(f"  Sx:                   {section.Sx:.6e} m^3")
print(f"  Sy:                   {section.Sy:.6e} m^3")

print("\nPlastic Section Moduli:")
print(f"  Zpl_x:                {section.Zpl_x:.6e} m^3")
print(f"  Zpl_y:                {section.Zpl_y:.6e} m^3")

print("\nTorsion & Shear:")
print(f"  Torsion constant (J): {section.J:.6e} m^4")
print(f"  Warping constant (Cw):{section.Cw:.6e} m^6")
print(f"  Shear center (SCx):   {section.SCx:.6f} m")
print(f"  Shear center (SCy):   {section.SCy:.6f} m")

print("\nExtreme Fiber Distances:")
print(f"  x_max:                {section.x_max:.6f} m")
print(f"  y_max:                {section.y_max:.6f} m")

# Generate and save plot
print("\n" + "=" * 70)
print("Generating plot...")
print("=" * 70)

fig, ax = plt.subplots(figsize=(8, 8))  # Square figure for square section
section.plot(ax=ax, show=False)
ax.set_title(
    f"{section.name}\n"
    f"A={section.A:.1f} mm^2, Ix={section.Ix:.2e} mm^4, Iy={section.Iy:.2e} mm^4",
    fontsize=11
)

# Save plot
output_path = Path(__file__).parent.parent / "gallery" / "shs_example.svg"
output_path.parent.mkdir(exist_ok=True)
fig.savefig(output_path, format='svg', bbox_inches='tight', dpi=150)
plt.close(fig)

print(f"\nPlot saved to: {output_path.relative_to(Path(__file__).parent.parent)}")
print("\nDone!")

