"""
Example: Loading and Plotting Sections from DXF Files

This file demonstrates:
1. Loading geometry from a DXF file
2. Creating a section from imported geometry
3. Plotting and saving to gallery
"""

import sys
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sectiony import Section, Geometry

# Setup output directories
ROOT_DIR = Path(__file__).resolve().parent.parent
GALLERY_DIR = ROOT_DIR / "gallery"

# Create directories if they don't exist
GALLERY_DIR.mkdir(exist_ok=True)

# Path to the DXF file
DXF_PATH = Path(r"C:\Users\Ed\Desktop\base1.dxf")


def save_plot(section: Section, filename: str) -> None:
    """Save a section plot to the gallery directory."""
    fig, ax = plt.subplots(figsize=(10, 10))
    section.plot(ax=ax, show=False)
    
    # Create informative title
    title_parts = [f"{section.name}"]
    if section.A is not None:
        title_parts.append(f"A={section.A:.1f} mm²")
    if section.Iy is not None:
        title_parts.append(f"Iy={section.Iy:.1e} mm⁴")
    if section.Iz is not None:
        title_parts.append(f"Iz={section.Iz:.1e} mm⁴")
    
    ax.set_title("\n".join(title_parts), fontsize=10)
    output_path = GALLERY_DIR / f"{filename}.svg"
    fig.savefig(output_path, format='svg', bbox_inches='tight', dpi=150)
    plt.close(fig)
    print(f"   Plot saved: gallery/{filename}.svg")


def main() -> None:
    """Load DXF file and create section plot."""
    print("\n" + "="*60)
    print("DXF Import Example")
    print("="*60)
    
    # Check if DXF file exists
    if not DXF_PATH.exists():
        print(f"\n   Error: DXF file not found at:")
        print(f"   {DXF_PATH}")
        print(f"\n   Please ensure the file exists and the path is correct.")
        return
    
    print(f"\n   Loading DXF file: {DXF_PATH.name}")
    
    try:
        # Load geometry from DXF
        geometry = Geometry.from_dxf(str(DXF_PATH))
        
        print(f"   Loaded {len(geometry.contours)} contour(s)")
        
        # Print contour information
        for idx, contour in enumerate(geometry.contours):
            contour_type = "Hollow" if contour.hollow else "Solid"
            num_segments = len(contour.segments)
            is_closed = contour.is_closed
            print(f"      Contour {idx}: {contour_type}, {num_segments} segments, "
                  f"closed={is_closed}")
        
        # Create section from geometry
        section_name = DXF_PATH.stem  # Use filename without extension
        section = Section(name=section_name, geometry=geometry)
        
        print(f"\n   Created section: {section.name}")
        print(f"   Area: {section.A:.2f} mm²")
        print(f"   Centroid: ({section.Cy:.2f}, {section.Cz:.2f})")
        
        # Save plot to gallery
        print(f"\n   Generating plot...")
        save_plot(section, f"dxf_{section_name}")
        
        print(f"\n   Successfully imported and plotted DXF file!")
        
    except Exception as e:
        print(f"\n   Error loading DXF file:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

