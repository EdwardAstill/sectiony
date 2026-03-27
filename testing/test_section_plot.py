import sys
import unittest
import math
from pathlib import Path
from unittest.mock import patch
import matplotlib.pyplot as plt

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from sectiony.library import chs, rhs, i, u
from sectiony.geometry import Geometry, Contour
from sectiony.section import Section

class TestSectionPlot(unittest.TestCase):
    def setUp(self):
        print(f"\nRunning test: {self._testMethodName}")

    @patch('matplotlib.pyplot.show')
    def test_plot_custom_geometry(self, mock_show):
        """Test plotting a custom defined geometry with holes."""
        points_outer = [(10,10), (10,-10), (-10,-10), (-10,10)]
        points_inner = [(5,5), (5,-5), (-5,-5), (-5,5)]
        
        outer_contour = Contour.from_points(points_outer, hollow=False)
        inner_contour = Contour.from_points(points_inner, hollow=True)
        
        geom = Geometry(contours=[outer_contour, inner_contour])
        sec = Section(name="Plot Test Hollow", geometry=geom)
        
        fig, ax = plt.subplots()
        returned_ax = sec.plot(ax=ax, show=True)
        self.assertIsNotNone(returned_ax)
        mock_show.assert_called_once()
        plt.close(fig)

    @patch('matplotlib.pyplot.show')
    def test_plot_library_sections(self, mock_show):
        """Test plotting standard library sections."""
        sections = [
            chs(d=20, t=1),
            rhs(b=10, h=20, t=1, r=1),
            i(d=20, b=10, tf=1, tw=1, r=0),
            u(b=10, h=20, tw=1, tf=1, r=0)
        ]
        
        for sec in sections:
            print(f"  - Plotting {sec.name}")
            fig, ax = plt.subplots()
            sec.plot(ax=ax, show=True)
            plt.close(fig)
            
        self.assertEqual(mock_show.call_count, len(sections))

    def test_plot_settings(self):
        """Test plot settings like aspect ratio."""
        sec = rhs(b=10, h=20, t=1, r=0)
        fig, ax = plt.subplots()
        sec.plot(ax=ax, show=False)
        
        # Check aspect ratio is equal (matplotlib may return 'equal' or 1.0)
        aspect = ax.get_aspect()
        self.assertTrue(aspect == 'equal' or aspect == 1.0)
        
        # Labels are not set by default (caller controls styling)
        self.assertEqual(ax.get_xlabel(), '')
        self.assertEqual(ax.get_ylabel(), '')
        plt.close(fig)

class TestPlotMarkers(unittest.TestCase):
    def test_centroid_marker_plotted(self):
        """Centroid marker adds a scatter artist."""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from sectiony.library import rhs

        sec = rhs(100.0, 200.0, 10.0, 0.0)
        fig, ax = plt.subplots()
        sec.plot(ax=ax, show=False, show_centroid=True)
        collections = ax.collections
        self.assertGreater(len(collections), 0)
        plt.close(fig)

    def test_no_markers_by_default(self):
        """Default plot has no scatter collections."""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from sectiony.library import rhs

        sec = rhs(100.0, 200.0, 10.0, 0.0)
        fig, ax = plt.subplots()
        sec.plot(ax=ax, show=False)
        self.assertEqual(len(ax.collections), 0)
        plt.close(fig)


if __name__ == "__main__":
    unittest.main()
