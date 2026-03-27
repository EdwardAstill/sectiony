import sys
import unittest
import math
import numpy as np
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from sectiony.geometry import Geometry, Contour
from sectiony.section import Section

class TestSectionProperties(unittest.TestCase):
    def setUp(self):
        print(f"\nRunning test: {self._testMethodName}")

    def test_solid_rectangle(self):
        print("  - Creating solid rectangle: h=20, b=10")
        # Rectangle h=20 (y), b=10 (x)
        # Centered at (0,0)
        h, b = 20.0, 10.0
        points = [
            (b / 2, h / 2),
            (b / 2, -h / 2),
            (-b / 2, -h / 2),
            (-b / 2, h / 2),
        ]
        contour = Contour.from_points(points)
        geom = Geometry(contours=[contour])
        sec = Section(name="Rect", geometry=geom)
        
        expected_A = b * h
        expected_Ix = (b * h**3) / 12  # about x-axis (y^2 integral)
        expected_Iy = (h * b**3) / 12  # about y-axis (x^2 integral)
        expected_Sx = expected_Ix / (h / 2)
        expected_Sy = expected_Iy / (b / 2)
        expected_Zpl_x = b * (h**2 / 4)  # Plastic modulus about x axis
        expected_Zpl_y = h * (b**2 / 4)  # Plastic modulus about y axis
        
        self.assertAlmostEqual(sec.A, expected_A, places=5)
        self.assertAlmostEqual(sec.Ix, expected_Ix, places=5)
        self.assertAlmostEqual(sec.Iy, expected_Iy, places=5)
        self.assertAlmostEqual(sec.Sx, expected_Sx, places=5)
        self.assertAlmostEqual(sec.Sy, expected_Sy, places=5)
        
        # Grid properties might have some error
        print(f"  - Zpl_x (Grid): {sec.Zpl_x:.4f} vs {expected_Zpl_x:.4f}")
        self.assertAlmostEqual(sec.Zpl_x, expected_Zpl_x, delta=expected_Zpl_x * 0.05)
        self.assertAlmostEqual(sec.Zpl_y, expected_Zpl_y, delta=expected_Zpl_y * 0.05)
        
        # Radius of gyration
        self.assertAlmostEqual(sec.rx, math.sqrt(expected_Ix / expected_A), places=5)
        self.assertAlmostEqual(sec.ry, math.sqrt(expected_Iy / expected_A), places=5)

    def test_offset_rectangle(self):
        print("  - Creating offset rectangle to test centroid calculation")
        # Rectangle 10x10 centered at x=5, y=5
        points = [
            (10.0, 10.0),
            (10.0, 0.0),
            (0.0, 0.0),
            (0.0, 10.0)
        ]
        contour = Contour.from_points(points)
        sec = Section(name="Offset Rect", geometry=Geometry(contours=[contour]))
        
        # Parallel Axis Theorem implicitly handled by geometry calculation?
        # No, properties are calculated about the CENTROID.
        # So A, Iy, Iz should be identical to a centered 10x10.
        
        expected_A = 100.0
        expected_I = 10000.0 / 12.0
        
        self.assertAlmostEqual(sec.A, expected_A, places=5)
        self.assertAlmostEqual(sec.Ix, expected_I, places=5)
        self.assertAlmostEqual(sec.Iy, expected_I, places=5)
        
        # Max distances should be relative to centroid (which is at 5,5)
        self.assertAlmostEqual(sec.x_max, 5.0, places=5)
        self.assertAlmostEqual(sec.y_max, 5.0, places=5)

    def test_hollow_rectangle(self):
        print("  - Creating hollow rectangle")
        # Outer: 20x20
        # Inner: 10x10 (Hole)
        points_outer = [(10,10), (10,-10), (-10,-10), (-10,10)]
        points_inner = [(5,5), (5,-5), (-5,-5), (-5,5)]
        
        outer_contour = Contour.from_points(points_outer, hollow=False)
        inner_contour = Contour.from_points(points_inner, hollow=True)
        
        geom = Geometry(contours=[outer_contour, inner_contour])
        sec = Section(name="Hollow Box", geometry=geom)
        
        expected_A = 400.0 - 100.0
        expected_I_outer = (20 * 20**3) / 12
        expected_I_inner = (10 * 10**3) / 12
        expected_I = expected_I_outer - expected_I_inner
        
        self.assertAlmostEqual(sec.A, expected_A, places=5)
        self.assertAlmostEqual(sec.Ix, expected_I, places=5)
        self.assertAlmostEqual(sec.Iy, expected_I, places=5)
        
        # J for thin-walled tube approximation vs Grid
        # Using exact formula for hollow square not trivial, 
        # but Bredt's formula good for thin wall.
        # Here wall is thick (5.0), so grid will find a value.
        # Just check it's non-zero and reasonable (less than Ip)
        Ip = sec.Ix + sec.Iy
        self.assertTrue(0 < sec.J < Ip)
        print(f"  - J: {sec.J:.2f} (Ip: {Ip:.2f})")

    def test_asymmetric_section_ixy(self):
        print("  - Creating asymmetric L-section for Ixy check")
        # L shape
        # Vertical leg: 10x2 (y=0..10, x=0..2)
        # Bottom leg: 2x8 (y=0..2, x=2..10)
        # Total: y=0..10, x=0..10
        
        # Let's define as one polygon
        # CCW: 
        # (0,0) -> (0,10) -> (2,10) -> (2,2) -> (10,2) -> (10,0)
        points = [
            (0,0), (0,10), (2,10), (2,2), (10,2), (10,0)
        ]
        
        contour = Contour.from_points(points)
        sec = Section(name="L-Section", geometry=Geometry(contours=[contour]))
        
        # Ixy should be non-zero because it's asymmetric about centroidal axes
        print(f"  - Ixy: {sec.Ixy:.4f}")
        self.assertNotAlmostEqual(sec.Ixy, 0.0)
        
        # Verify Area
        # Rect1 (Bottom): 2x10 = 20
        # Rect2 (Vertical): 8x2 = 16 (from y=2 to 10)
        # Total A = 36
        self.assertAlmostEqual(sec.A, 36.0, places=5)

class TestDerivedProperties(unittest.TestCase):
    def setUp(self):
        from sectiony.library import rhs
        self.rhs = rhs(100.0, 200.0, 10.0, 0.0)

    def test_shape_factor_x_rectangle(self):
        from sectiony.library import solid_rect
        sec = solid_rect(50.0, 100.0)
        # For rectangle, shape factor = 1.5 (Zpl/S = (bh^2/4)/(bh^2/6) = 1.5)
        self.assertAlmostEqual(sec.shape_factor_x, 1.5, delta=0.05)

    def test_shape_factor_positive(self):
        self.assertGreater(self.rhs.shape_factor_x, 1.0)
        self.assertGreater(self.rhs.shape_factor_y, 1.0)

    def test_principal_moments_symmetric(self):
        # For a doubly-symmetric section (Ixy=0): I1=max(Ix,Iy), I2=min(Ix,Iy)
        self.assertAlmostEqual(self.rhs.I1, max(self.rhs.Ix, self.rhs.Iy), places=3)
        self.assertAlmostEqual(self.rhs.I2, min(self.rhs.Ix, self.rhs.Iy), places=3)

    def test_principal_angle_symmetric_zero(self):
        angle = self.rhs.principal_angle
        self.assertAlmostEqual(abs(angle) % (math.pi / 2), 0.0, places=5)

    def test_principal_moments_angle_section(self):
        from sectiony.library import angle
        sec = angle(80.0, 80.0, 8.0, r=0.0)
        # I1 > I2, both positive, I1*I2 = Ix*Iy - Ixy^2
        self.assertGreater(sec.I1, sec.I2)
        self.assertGreater(sec.I2, 0.0)
        self.assertAlmostEqual(
            sec.I1 * sec.I2,
            sec.Ix * sec.Iy - sec.Ixy**2,
            delta=abs(sec.Ix * sec.Iy) * 0.001,
        )

    def test_str_contains_properties(self):
        s = str(self.rhs)
        self.assertIn("A", s)
        self.assertIn("Ix", s)
        self.assertIn("RHS", s)


class TestRotation(unittest.TestCase):
    def test_rotate_preserves_area(self):
        from sectiony.library import rhs
        import math
        sec = rhs(100.0, 200.0, 10.0, 0.0)
        rotated = sec.rotate(math.pi / 4)
        self.assertAlmostEqual(rotated.A, sec.A, places=3)

    def test_rotate_90_swaps_ix_iy(self):
        from sectiony.library import rhs
        import math
        sec = rhs(100.0, 200.0, 10.0, 0.0)
        rotated = sec.rotate(math.pi / 2)
        self.assertAlmostEqual(rotated.Ix, sec.Iy, delta=sec.Iy * 0.01)
        self.assertAlmostEqual(rotated.Iy, sec.Ix, delta=sec.Ix * 0.01)

    def test_rotate_360_identity(self):
        from sectiony.library import solid_rect
        import math
        sec = solid_rect(30.0, 50.0)
        rotated = sec.rotate(2 * math.pi)
        self.assertAlmostEqual(rotated.Ix, sec.Ix, delta=sec.Ix * 0.001)
        self.assertAlmostEqual(rotated.Iy, sec.Iy, delta=sec.Iy * 0.001)


if __name__ == '__main__':
    unittest.main()
