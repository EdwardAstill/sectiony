"""
Example: Rotated Plot Visualization

This example demonstrates the rotate parameter in the plot method.
When rotate=True, the section is rotated 90° counter-clockwise:
- x-axis becomes vertical (pointing up)
- y-axis points left (negative x direction)
- The scale remains on the right side
"""

import sys
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sectiony.library import rhs, i, chs

# Create example sections

sections = [
    ("RHS 150x100x10", rhs(b=100, h=150, t=10, r=15)),
    ("I-Section 200x150", i(d=200, b=150, tf=12, tw=8, r=10)),
    ("CHS 100x5", chs(d=100, t=5)),
]

# Create comparison plots
for name, section in sections:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle(f"{name} - Normal vs Rotated View", fontsize=14, fontweight='bold')
    
    # Normal plot (rotate=False, default)
    section.plot(ax=ax1, show=False, rotate=False)
    ax1.set_title("Normal View\n(x horizontal, y vertical)", fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    # Rotated plot (rotate=True)
    section.plot(ax=ax2, show=False, rotate=True)
    ax2.set_title("Rotated View\n(x vertical, y pointing left)", fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # Save plot
    output_path = Path(__file__).parent.parent / "gallery" / f"rotated_{name.lower().replace(' ', '_').replace('-', '_')}.svg"
    output_path.parent.mkdir(exist_ok=True)
    fig.savefig(output_path, format='svg', bbox_inches='tight', dpi=150)
    plt.close(fig)
    
    print(f"Saved: {output_path.relative_to(Path(__file__).parent.parent)}")

print("\nDone! Rotated plot examples generated.")
