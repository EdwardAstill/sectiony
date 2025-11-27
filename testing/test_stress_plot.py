import sys
import unittest
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for testing
import matplotlib.pyplot as plt

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from sectiony.geometry import Geometry, Shape
from sectiony.section import Section
from sectiony.stress import Stress


class TestStressCalculations(unittest.TestCase):
    def setUp(self):
        print(f"\nRunning test: {self._testMethodName}")
        # Simple 10x10 square centered at origin
        points = [(5, 5), (5, -5), (-5, -5), (-5, 5)]
        self.square_section = Section(
            name="Square",
            geometry=Geometry(shapes=[Shape(points=points)])
        )

    def test_sigma_axial(self):
        stress = Stress(self.square_section, N=1000.0)
        # A = 100, so sigma = 1000/100 = 10
        sigma = stress.sigma_axial(0, 0)
        self.assertAlmostEqual(sigma, 10.0, places=5)

    def test_sigma_axial_uniform(self):
        stress = Stress(self.square_section, N=500.0)
        # Axial stress is uniform across section
        self.assertAlmostEqual(stress.sigma_axial(0, 0), stress.sigma_axial(5, 5))
        self.assertAlmostEqual(stress.sigma_axial(0, 0), stress.sigma_axial(-5, -5))

    def test_sigma_bending_mz(self):
        stress = Stress(self.square_section, Mz=1000.0)
        # sigma = -Mz * y / Iz
        # At y=5: sigma = -1000 * 5 / Iz (compression at top)
        # At y=-5: sigma = -1000 * (-5) / Iz (tension at bottom)
        sigma_top = stress.sigma_bending(5, 0)
        sigma_bottom = stress.sigma_bending(-5, 0)
        self.assertLess(sigma_top, 0)  # Compression at top
        self.assertGreater(sigma_bottom, 0)  # Tension at bottom
        self.assertAlmostEqual(sigma_top, -sigma_bottom)  # Symmetric

    def test_sigma_bending_my(self):
        stress = Stress(self.square_section, My=1000.0)
        # sigma = My * z / Iy
        sigma_left = stress.sigma_bending(0, -5)
        sigma_right = stress.sigma_bending(0, 5)
        self.assertLess(sigma_left, 0)
        self.assertGreater(sigma_right, 0)
        self.assertAlmostEqual(sigma_left, -sigma_right)

    def test_sigma_combined(self):
        stress = Stress(self.square_section, N=1000.0, Mz=500.0)
        # Total sigma = N/A - Mz*y/Iz
        sigma = stress.sigma(0, 0)
        # At centroid, bending stress = 0
        self.assertAlmostEqual(sigma, 10.0, places=5)

    def test_tau_shear(self):
        stress = Stress(self.square_section, Vy=100.0)
        # Approximate: tau = V/A = 100/100 = 1
        tau = stress.tau_shear(0, 0)
        self.assertAlmostEqual(tau, 1.0, places=5)

    def test_tau_shear_combined(self):
        stress = Stress(self.square_section, Vy=60.0, Vz=80.0)
        # tau = sqrt(60^2 + 80^2) / 100 = 100/100 = 1
        tau = stress.tau_shear(0, 0)
        self.assertAlmostEqual(tau, 1.0, places=5)

    def test_tau_torsion(self):
        stress = Stress(self.square_section, Mx=1000.0)
        # At centroid (r=0), torsion stress = 0
        tau_center = stress.tau_torsion(0, 0)
        self.assertAlmostEqual(tau_center, 0.0, places=5)
        # Away from center, stress increases
        tau_corner = stress.tau_torsion(5, 5)
        self.assertGreater(tau_corner, 0)

    def test_von_mises(self):
        stress = Stress(self.square_section, N=1000.0, Vy=100.0)
        # von_mises = sqrt(sigma^2 + 3*tau^2)
        sigma = stress.sigma(0, 0)
        tau = stress.tau(0, 0)
        expected = math.sqrt(sigma**2 + 3 * tau**2)
        vm = stress.von_mises(0, 0)
        self.assertAlmostEqual(vm, expected, places=5)

    def test_at_method(self):
        stress = Stress(self.square_section, N=1000.0)
        # Test .at() method with different stress types
        self.assertAlmostEqual(stress.at(0, 0, "sigma_axial"), 10.0)
        self.assertAlmostEqual(stress.at(0, 0, "sigma"), 10.0)


class TestStressMinMax(unittest.TestCase):
    def setUp(self):
        print(f"\nRunning test: {self._testMethodName}")
        points = [(5, 5), (5, -5), (-5, -5), (-5, 5)]
        self.section = Section(
            name="Square",
            geometry=Geometry(shapes=[Shape(points=points)])
        )

    def test_max_axial(self):
        stress = Stress(self.section, N=1000.0)
        # Axial is uniform, so max = min = 10
        self.assertAlmostEqual(stress.max("sigma_axial"), 10.0)
        self.assertAlmostEqual(stress.min("sigma_axial"), 10.0)

    def test_max_bending(self):
        stress = Stress(self.section, Mz=1000.0)
        max_sigma = stress.max("sigma_bending")
        min_sigma = stress.min("sigma_bending")
        # Max and min should be at opposite corners
        self.assertGreater(max_sigma, 0)
        self.assertLess(min_sigma, 0)
        self.assertAlmostEqual(max_sigma, -min_sigma)

    def test_invalid_stress_type(self):
        stress = Stress(self.section, N=100.0)
        with self.assertRaises(ValueError):
            stress.get_stress_func("invalid_type")


class TestStressPlot(unittest.TestCase):
    def setUp(self):
        print(f"\nRunning test: {self._testMethodName}")
        points = [(5, 5), (5, -5), (-5, -5), (-5, 5)]
        self.section = Section(
            name="Square",
            geometry=Geometry(shapes=[Shape(points=points)])
        )

    def tearDown(self):
        plt.close('all')

    def test_plot_returns_axes(self):
        stress = Stress(self.section, Mz=1000.0)
        ax = stress.plot(show=False)
        self.assertIsNotNone(ax)

    def test_plot_von_mises(self):
        stress = Stress(self.section, N=1000.0, Mz=500.0)
        ax = stress.plot(stress_type="von_mises", show=False)
        self.assertIsNotNone(ax)

    def test_plot_sigma(self):
        stress = Stress(self.section, Mz=1000.0)
        ax = stress.plot(stress_type="sigma", show=False)
        self.assertIsNotNone(ax)

    def test_plot_tau(self):
        stress = Stress(self.section, Vy=100.0, Mx=500.0)
        ax = stress.plot(stress_type="tau", show=False)
        self.assertIsNotNone(ax)

    def test_plot_with_custom_axes(self):
        fig, ax = plt.subplots()
        stress = Stress(self.section, Mz=1000.0)
        returned_ax = stress.plot(ax=ax, show=False)
        self.assertIs(returned_ax, ax)

    def test_plot_with_cmap(self):
        stress = Stress(self.section, Mz=1000.0)
        ax = stress.plot(cmap="coolwarm", show=False)
        self.assertIsNotNone(ax)

    def test_plot_no_geometry_returns_none(self):
        section = Section(name="NoGeom", A=100.0)
        stress = Stress(section, N=1000.0)
        ax = stress.plot(show=False)
        self.assertIsNone(ax)


class TestStressHollowSection(unittest.TestCase):
    def setUp(self):
        print(f"\nRunning test: {self._testMethodName}")
        outer = [(10, 10), (10, -10), (-10, -10), (-10, 10)]
        inner = [(5, 5), (5, -5), (-5, -5), (-5, 5)]
        self.section = Section(
            name="Hollow",
            geometry=Geometry(shapes=[
                Shape(points=outer),
                Shape(points=inner, hollow=True)
            ])
        )

    def tearDown(self):
        plt.close('all')

    def test_hollow_area(self):
        # A = 400 - 100 = 300
        self.assertAlmostEqual(self.section.A, 300.0, places=5)

    def test_hollow_axial_stress(self):
        stress = Stress(self.section, N=3000.0)
        # sigma = 3000/300 = 10
        self.assertAlmostEqual(stress.sigma_axial(0, 0), 10.0)

    def test_hollow_plot(self):
        stress = Stress(self.section, Mz=1000.0)
        ax = stress.plot(show=False)
        self.assertIsNotNone(ax)


if __name__ == '__main__':
    unittest.main()


