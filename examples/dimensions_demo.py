"""
Demonstration of the dimensions attribute for library shapes.
Shows how to access original dimensions from library sections.
"""
import sys
from pathlib import Path

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sectiony.library import chs, rhs, i, u

def main():
    print("=" * 60)
    print("Library Shapes - Dimensions Attribute Demo")
    print("=" * 60)
    
    # Create CHS
    chs_section = chs(d=200.0, t=10.0)
    print(f"\n{chs_section.name}")
    print(f"  Dimensions: {chs_section.dimensions}")
    print(f"  Diameter: {chs_section.dimensions['d']} mm")
    print(f"  Thickness: {chs_section.dimensions['t']} mm")
    print(f"  Area: {chs_section.A:.2f} mm²")
    
    # Create RHS
    rhs_section = rhs(b=100.0, h=200.0, t=10.0, r=15.0)
    print(f"\n{rhs_section.name}")
    print(f"  Dimensions: {rhs_section.dimensions}")
    print(f"  Width: {rhs_section.dimensions['b']} mm")
    print(f"  Height: {rhs_section.dimensions['h']} mm")
    print(f"  Thickness: {rhs_section.dimensions['t']} mm")
    print(f"  Corner radius: {rhs_section.dimensions['r']} mm")
    print(f"  Area: {rhs_section.A:.2f} mm²")
    
    # Create I-section
    i_section = i(d=300.0, b=150.0, tf=12.0, tw=8.0, r=10.0)
    print(f"\n{i_section.name}")
    print(f"  Dimensions: {i_section.dimensions}")
    print(f"  Depth: {i_section.dimensions['d']} mm")
    print(f"  Width: {i_section.dimensions['b']} mm")
    print(f"  Flange thickness: {i_section.dimensions['tf']} mm")
    print(f"  Web thickness: {i_section.dimensions['tw']} mm")
    print(f"  Root radius: {i_section.dimensions['r']} mm")
    print(f"  Area: {i_section.A:.2f} mm²")
    
    # Create U-channel
    u_section = u(b=100.0, h=200.0, tw=8.0, tf=10.0, r=5.0)
    print(f"\n{u_section.name}")
    print(f"  Dimensions: {u_section.dimensions}")
    print(f"  Width: {u_section.dimensions['b']} mm")
    print(f"  Height: {u_section.dimensions['h']} mm")
    print(f"  Web thickness: {u_section.dimensions['tw']} mm")
    print(f"  Flange thickness: {u_section.dimensions['tf']} mm")
    print(f"  Corner radius: {u_section.dimensions['r']} mm")
    print(f"  Area: {u_section.A:.2f} mm²")
    
    print("\n" + "=" * 60)
    print("Dimensions are stored and easily accessible!")
    print("=" * 60)

if __name__ == "__main__":
    main()

