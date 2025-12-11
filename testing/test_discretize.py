import math
import unittest
from sectiony.geometry import Line, Arc, Contour

class TestDiscretize(unittest.TestCase):
    def test_line_discretize_resolution(self):
        # Test that Line.discretize respects resolution
        line = Line((0, 0), (10, 0))
        points = line.discretize(resolution=10)
        self.assertEqual(len(points), 11)  # 10 segments = 11 points
        
        # Check point spacing
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i+1]
            dist = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
            self.assertAlmostEqual(dist, 1.0)

    def test_contour_discretize_uniform(self):
        # Create a contour with two lines of unequal length
        # Line 1: (0,0) -> (10,0) (Length 10)
        # Line 2: (10,0) -> (10,5) (Length 5)
        # Total length = 15
        
        l1 = Line((0, 0), (10, 0))
        l2 = Line((10, 0), (10, 5))
        contour = Contour(segments=[l1, l2])
        
        # Discretize into 15 segments (16 points) -> spacing should be 1.0
        # Wait, if open, 15 segments = 16 points.
        points = contour.discretize_uniform(count=16) 
        
        self.assertEqual(len(points), 16)
        
        # Check total length covered
        p_start = points[0]
        p_end = points[-1]
        self.assertEqual(p_start, (0, 0))
        self.assertEqual(p_end, (10, 5))
        
        # Check uniform spacing
        dists = []
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i+1]
            dist = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
            dists.append(dist)
            
        # Expected spacing = 15 / 15 = 1.0
        avg_dist = sum(dists) / len(dists)
        self.assertAlmostEqual(avg_dist, 1.0, places=5)
        
        # Max deviation should be small
        for d in dists:
            self.assertAlmostEqual(d, 1.0, places=4)

    def test_arc_discretize_uniform(self):
        # Semi-circle radius 10. Length = 10 * pi approx 31.4159
        arc = Arc((0, 0), 10.0, 0.0, math.pi)
        contour = Contour(segments=[arc])
        
        count = 32
        points = contour.discretize_uniform(count=count)
        
        self.assertEqual(len(points), count)
        
        dists = []
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i+1]
            dist = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
            dists.append(dist)
            
        # Spacing should be roughly equal (chord lengths)
        # For arc, chords are slightly shorter than arc length, so sum(dists) < true arc length
        # But they should be equal to each other
        first_dist = dists[0]
        for d in dists:
            # We allow small tolerance because 'point_at' is exact arc position, 
            # but chords approximate the arc.
            # Wait, 'discretize_uniform' picks points at equal arc lengths along the curve.
            # So the chords between them should be equal length for a constant curvature arc.
            self.assertAlmostEqual(d, first_dist, places=4)

if __name__ == '__main__':
    unittest.main()

