import unittest
import math
import os
import json
from sectiony.geometry import Line, Arc, CubicBezier, Contour, Geometry

class TestGeometryJSON(unittest.TestCase):
    def setUp(self):
        self.filename = "test_geometry.json"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_line_serialization(self):
        line = Line(start=(0, 0), end=(10, 10))
        data = line.to_dict()
        self.assertEqual(data["type"], "line")
        self.assertEqual(tuple(data["start"]), (0, 0))
        self.assertEqual(tuple(data["end"]), (10, 10))
        
        loaded = Line.from_dict(data)
        self.assertEqual(loaded.start, (0, 0))
        self.assertEqual(loaded.end, (10, 10))

    def test_arc_serialization(self):
        arc = Arc(center=(0, 0), radius=5, start_angle=0, end_angle=math.pi)
        data = arc.to_dict()
        self.assertEqual(data["type"], "arc")
        self.assertEqual(tuple(data["center"]), (0, 0))
        self.assertEqual(data["radius"], 5)
        
        loaded = Arc.from_dict(data)
        self.assertEqual(loaded.center, (0, 0))
        self.assertEqual(loaded.radius, 5)

    def test_bezier_serialization(self):
        bz = CubicBezier(p0=(0,0), p1=(1,1), p2=(2,2), p3=(3,3))
        data = bz.to_dict()
        self.assertEqual(data["type"], "bezier")
        self.assertEqual(tuple(data["p0"]), (0, 0))
        
        loaded = CubicBezier.from_dict(data)
        self.assertEqual(loaded.p0, (0, 0))
        self.assertEqual(loaded.p3, (3, 3))

    def test_geometry_json_file(self):
        # Create a mixed geometry
        line = Line(start=(0, 0), end=(10, 0))
        arc = Arc(center=(5, 0), radius=5, start_angle=0, end_angle=math.pi)
        contour = Contour(segments=[line, arc], hollow=False)
        geom = Geometry(contours=[contour])
        
        # Save
        geom.to_json(self.filename)
        
        # Verify file exists and content
        self.assertTrue(os.path.exists(self.filename))
        with open(self.filename, 'r') as f:
            content = json.load(f)
            self.assertIn("contours", content)
            self.assertEqual(len(content["contours"]), 1)
            self.assertEqual(len(content["contours"][0]["segments"]), 2)
            
        # Load
        loaded_geom = Geometry.from_json(self.filename)
        self.assertEqual(len(loaded_geom.contours), 1)
        segments = loaded_geom.contours[0].segments
        self.assertEqual(len(segments), 2)
        self.assertIsInstance(segments[0], Line)
        self.assertIsInstance(segments[1], Arc)

if __name__ == '__main__':
    unittest.main()

