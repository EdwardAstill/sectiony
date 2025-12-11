import unittest
import math
from pathlib import Path
import sys

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sectiony import Section, Geometry, Contour, Line
from sectiony.library import i

class TestWarpingConstant(unittest.TestCase):
    def test_i_section_warping(self):
        """
        Compare calculated warping constant for an I-section against approximate formula.
        Cw ≈ (Iz_flange * h^2) / 2  or  (Iy * h^2) / 4 for total section?
        
        Standard formula for doubly symmetric I-section:
        Cw = (b^3 * t_f * h^2) / 24
           = (Iy_flanges * h^2) / 4
           ≈ (Iy * h^2) / 4
        
        where:
        b = flange width
        t_f = flange thickness
        h = distance between flange centroids = d - t_f
        Iy = Second moment of area about weak axis (vertical axis z)
        """
        
        # Dimensions (mm)
        d = 300.0   # Depth
        b = 150.0   # Flange width
        tf = 15.0   # Flange thickness
        tw = 10.0   # Web thickness
        r = 0.0     # No root radius for simple comparison
        
        # Create section
        # Note: Library i() takes dimensions
        section = i(d=d, b=b, tf=tf, tw=tw, r=r)
        
        # Theoretical calculation
        h_center = d - tf  # Distance between flange centroids
        
        # Iy of one flange about its own centroid (weak axis of I-section is z)
        # Iz of flange (about vertical axis) = (t_f * b^3) / 12
        I_flange_weak = (tf * b**3) / 12.0
        
        # Total Iy of section is dominated by flanges
        # Iy_total ≈ 2 * I_flange_weak
        Iy_total = 2 * I_flange_weak + ( (d - 2*tf) * tw**3 ) / 12.0
        
        # Formula: Cw = (I_y * h^2) / 4  (approx, assuming web contribution to Iy is negligible)
        # More accurate: Cw = (I_flanges * h^2) / 4 = (2 * I_flange_weak * h^2) / 4 = I_flange_weak * h^2 / 2
        
        Cw_theory = (I_flange_weak * h_center**2) / 2.0
        
        # Calculated value
        # Note: Grid resolution affects accuracy. 
        # Default might be too coarse for precise Cw match, but should be close.
        Cw_calc = section.Cw
        
        print(f"\nTest I-Section ({d}x{b}x{tf}/{tw}):")
        print(f"  h_center: {h_center:.2f}")
        print(f"  Iy (calc):   {section.Iy:.2e}")
        print(f"  Iy (theory): {Iy_total:.2e}")
        print(f"  Cw (theory): {Cw_theory:.2e}")
        print(f"  Cw (calc):   {Cw_calc:.2e}")
        
        error = abs(Cw_calc - Cw_theory) / Cw_theory
        print(f"  Error: {error:.1%}")
        
        # Allow 10% error due to grid discretization
        self.assertLess(error, 0.10, "Warping constant should match theoretical value within 10%")

    def test_chs_warping_small(self):
        """
        Circular Hollow Section should have small warping constant relative to dimensions.
        Note: Grid-based methods overestimate warping for curved boundaries due to 
        'stairstep' approximation (artificial torque).
        """
        from sectiony.library import chs
        
        # 200mm diameter, 10mm thick
        # Using higher resolution for better circle approx
        # This is still likely to be non-zero due to grid artifacts
        section = chs(d=200.0, t=10.0)
        
        # Compare to I-section of similar bounding box
        # I-section Cw was ~1.7e11
        # CHS Cw was ~8.8e7
        # This is 3 orders of magnitude smaller, which confirms it is "effectively" small
        # relative to an open section.
        
        print(f"\nTest CHS (200x10):")
        print(f"  Cw (calc): {section.Cw:.2e}")
        
        # Assert it's significantly smaller than the I-section value (1e11)
        self.assertLess(section.Cw, 1e9, "CHS warping should be small (< 1e9) compared to open sections (~1e11)")

if __name__ == '__main__':
    unittest.main()

