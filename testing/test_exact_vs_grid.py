import sys
import unittest
import math
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from sectiony.library import chs, rhs
from sectiony.section import Section
from sectiony.geometry import Geometry, Contour

class TestExactVsGrid(unittest.TestCase):
    def setUp(self):
        print(f"\nRunning test: {self._testMethodName}")

    def test_rectangular_section(self):
        """Compare Exact vs Grid properties for a simple rectangle."""
        b, h = 10.0, 20.0
        # Create manually
        points = [(h/2, b/2), (h/2, -b/2), (-h/2, -b/2), (-h/2, b/2)]
        contour = Contour.from_points(points)
        sec = Section(name="Rect", geometry=Geometry(contours=[contour]))
        
        # Exact (Green's theorem)
        exact_A = sec.A
        exact_Iy = sec.Iy
        exact_Iz = sec.Iz
        
        print(f"  Exact: A={exact_A:.4f}, Iy={exact_Iy:.4f}, Iz={exact_Iz:.4f}")
        
        # Zpl for rectangle
        expected_Zpl_y = h * b**2 / 4
        expected_Zpl_z = b * h**2 / 4
        
        print(f"  Zpl_y: Calc={sec.Zpl_y:.4f}, Exact={expected_Zpl_y:.4f}")
        print(f"  Zpl_z: Calc={sec.Zpl_z:.4f}, Exact={expected_Zpl_z:.4f}")
        
        # Check within 5%
        self.assertAlmostEqual(sec.Zpl_y, expected_Zpl_y, delta=expected_Zpl_y * 0.05)
        self.assertAlmostEqual(sec.Zpl_z, expected_Zpl_z, delta=expected_Zpl_z * 0.05)

    def test_circular_section(self):
        """Compare Exact vs Grid for solid circle."""
        d = 20.0
        # Solid circle: CHS with t = d/2 (full radius)
        sec = chs(d=d, t=d/2)
        
        # Exact J for solid circle = Polar Moment = pi * d^4 / 32
        expected_J = math.pi * d**4 / 32
        
        print(f"  J: Calc={sec.J:.4f}, Exact={expected_J:.4f}")
        
        # Grid J uses Poisson solver
        self.assertAlmostEqual(sec.J, expected_J, delta=expected_J * 0.10)  # 10% tolerance for grid method
        
        # Zpl for circle = d^3 / 6
        expected_Zpl = d**3 / 6
        print(f"  Zpl: Calc={sec.Zpl_y:.4f}, Exact={expected_Zpl:.4f}")
        
        self.assertAlmostEqual(sec.Zpl_y, expected_Zpl, delta=expected_Zpl * 0.10)

if __name__ == '__main__':
    unittest.main()
