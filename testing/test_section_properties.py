import sys
import unittest
import math
import numpy as np
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from sectiony.geometry import Geometry, Shape
from sectiony.section import Section

class TestSectionProperties(unittest.TestCase):
    def setUp(self):
        print(f"\nRunning test: {self._testMethodName}")

    def test_solid_rectangle(self):
        print("  - Creating solid rectangle: h=20, b=10")
        # Rectangle h=20 (y), b=10 (z)
        # Centered at (0,0)
        h, b = 20.0, 10.0
        points = [
            (h/2, b/2),
            (h/2, -b/2),
            (-h/2, -b/2),
            (-h/2, b/2)
        ]
        shape = Shape(points=points)
        geom = Geometry(shapes=[shape])
        sec = Section(name="Rect", geometry=geom)
        
        expected_A = b * h
        expected_Iy = (h * b**3) / 12  # about y-axis (z^2 integral)
        expected_Iz = (b * h**3) / 12  # about z-axis (y^2 integral)
        expected_Sy = expected_Iy / (b/2)
        expected_Sz = expected_Iz / (h/2)
        expected_Zpl_y = h * (b**2 / 4) # Plastic modulus about y axis
        expected_Zpl_z = b * (h**2 / 4) # Plastic modulus about z axis
        
        self.assertAlmostEqual(sec.A, expected_A, places=5)
        self.assertAlmostEqual(sec.Iy, expected_Iy, places=5)
        self.assertAlmostEqual(sec.Iz, expected_Iz, places=5)
        self.assertAlmostEqual(sec.Sy, expected_Sy, places=5)
        self.assertAlmostEqual(sec.Sz, expected_Sz, places=5)
        
        # Grid properties might have some error
        print(f"  - Zpl_z (Grid): {sec.Zpl_z:.4f} vs {expected_Zpl_z:.4f}")
        self.assertAlmostEqual(sec.Zpl_z, expected_Zpl_z, delta=expected_Zpl_z * 0.05)
        self.assertAlmostEqual(sec.Zpl_y, expected_Zpl_y, delta=expected_Zpl_y * 0.05)
        
        # Radius of gyration
        self.assertAlmostEqual(sec.ry, math.sqrt(expected_Iy/expected_A), places=5)
        self.assertAlmostEqual(sec.rz, math.sqrt(expected_Iz/expected_A), places=5)

    def test_offset_rectangle(self):
        print("  - Creating offset rectangle to test centroid calculation")
        # Rectangle 10x10 centered at y=5, z=5
        # h=10, b=10
        points = [
            (10.0, 10.0),
            (10.0, 0.0),
            (0.0, 0.0),
            (0.0, 10.0)
        ]
        sec = Section(name="Offset Rect", geometry=Geometry(shapes=[Shape(points=points)]))
        
        # Parallel Axis Theorem implicitly handled by geometry calculation?
        # No, properties are calculated about the CENTROID.
        # So A, Iy, Iz should be identical to a centered 10x10.
        
        expected_A = 100.0
        expected_I = 10000.0 / 12.0
        
        self.assertAlmostEqual(sec.A, expected_A, places=5)
        self.assertAlmostEqual(sec.Iy, expected_I, places=5)
        self.assertAlmostEqual(sec.Iz, expected_I, places=5)
        
        # Max distances should be relative to centroid (which is at 5,5)
        # y range 0..10 -> centroid 5 -> max dist 5.
        self.assertAlmostEqual(sec.y_max, 5.0, places=5)
        self.assertAlmostEqual(sec.z_max, 5.0, places=5)

    def test_hollow_rectangle(self):
        print("  - Creating hollow rectangle")
        # Outer: 20x20
        # Inner: 10x10 (Hole)
        points_outer = [(10,10), (10,-10), (-10,-10), (-10,10)]
        points_inner = [(5,5), (5,-5), (-5,-5), (-5,5)]
        
        geom = Geometry(shapes=[
            Shape(points=points_outer),
            Shape(points=points_inner, hollow=True)
        ])
        sec = Section(name="Hollow Box", geometry=geom)
        
        expected_A = 400.0 - 100.0
        expected_I_outer = (20 * 20**3) / 12
        expected_I_inner = (10 * 10**3) / 12
        expected_I = expected_I_outer - expected_I_inner
        
        self.assertAlmostEqual(sec.A, expected_A, places=5)
        self.assertAlmostEqual(sec.Iy, expected_I, places=5)
        self.assertAlmostEqual(sec.Iz, expected_I, places=5)
        
        # J for thin-walled tube approximation vs Grid
        # Using exact formula for hollow square not trivial, 
        # but Bredt's formula good for thin wall.
        # Here wall is thick (5.0), so grid will find a value.
        # Just check it's non-zero and reasonable (less than Ip)
        Ip = sec.Iy + sec.Iz
        self.assertTrue(0 < sec.J < Ip)
        print(f"  - J: {sec.J:.2f} (Ip: {Ip:.2f})")

    def test_asymmetric_section_iyz(self):
        print("  - Creating asymmetric L-section for Iyz check")
        # L shape
        # Vertical leg: 10x2 (y=0..10, z=0..2)
        # Bottom leg: 2x8 (y=0..2, z=2..10)
        # Total: y=0..10, z=0..10
        
        # Let's define as one polygon
        points = [
            (10, 2),  # Top inner
            (10, 0),  # Top left
            (0, 0),   # Bottom left
            (0, 10),  # Bottom right
            (2, 10),  # Bottom right inner
            (2, 2)    # Inner corner
        ]
        # Wait, order: (10,0) -> (0,0) -> (0,10) -> (2,10) -> (2,2) -> (10,2)?
        # CCW: 
        # (0,0) -> (0,10) -> (2,10) -> (2,2) -> (10,2) -> (10,0)
        points = [
            (0,0), (0,10), (2,10), (2,2), (10,2), (10,0)
        ]
        # Note: My geometry uses (y, z). 
        # So (0,0) -> (0,10) means z changes 0->10 (Right).
        # (0,10) -> (2,10) means y changes 0->2 (Up).
        # Let's visualize:
        # P1(0,0)
        # P2(0,10) -> z=10. Horizontal leg.
        # P3(2,10) -> y=2. Up.
        # P4(2,2) -> z=2. Left.
        # P5(10,2) -> y=10. Up.
        # P6(10,0) -> z=0. Left.
        # Close to (0,0).
        # This is an L shape.
        
        sec = Section(name="L-Section", geometry=Geometry(shapes=[Shape(points=points)]))
        
        # Iyz should be non-zero because it's asymmetric about centroidal axes
        print(f"  - Iyz: {sec.Iyz:.4f}")
        self.assertNotAlmostEqual(sec.Iyz, 0.0)
        
        # Verify Area
        # Rect1 (Bottom): 2x10 = 20
        # Rect2 (Vertical): 8x2 = 16 (from y=2 to 10)
        # Total A = 36
        self.assertAlmostEqual(sec.A, 36.0, places=5)

if __name__ == '__main__':
    unittest.main()
