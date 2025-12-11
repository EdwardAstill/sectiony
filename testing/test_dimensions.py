"""
Test dimensions attribute for library shapes.
"""
import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sectiony.library import chs, rhs, i, u


class TestDimensions(unittest.TestCase):
    """Test that library shapes retain their dimensions."""
    
    def test_chs_dimensions(self):
        """Test CHS dimensions are stored correctly."""
        section = chs(d=200.0, t=10.0)
        self.assertIsNotNone(section.dimensions)
        self.assertEqual(section.dimensions["d"], 200.0)
        self.assertEqual(section.dimensions["t"], 10.0)
        self.assertEqual(len(section.dimensions), 2)
    
    def test_rhs_dimensions(self):
        """Test RHS dimensions are stored correctly."""
        section = rhs(b=100.0, h=200.0, t=10.0, r=15.0)
        self.assertIsNotNone(section.dimensions)
        self.assertEqual(section.dimensions["b"], 100.0)
        self.assertEqual(section.dimensions["h"], 200.0)
        self.assertEqual(section.dimensions["t"], 10.0)
        self.assertEqual(section.dimensions["r"], 15.0)
        self.assertEqual(len(section.dimensions), 4)
    
    def test_i_dimensions(self):
        """Test I-section dimensions are stored correctly."""
        section = i(d=300.0, b=150.0, tf=12.0, tw=8.0, r=10.0)
        self.assertIsNotNone(section.dimensions)
        self.assertEqual(section.dimensions["d"], 300.0)
        self.assertEqual(section.dimensions["b"], 150.0)
        self.assertEqual(section.dimensions["tf"], 12.0)
        self.assertEqual(section.dimensions["tw"], 8.0)
        self.assertEqual(section.dimensions["r"], 10.0)
        self.assertEqual(len(section.dimensions), 5)
    
    def test_u_dimensions(self):
        """Test U-channel dimensions are stored correctly."""
        section = u(b=100.0, h=200.0, t=8.0, r=5.0)
        self.assertIsNotNone(section.dimensions)
        self.assertEqual(section.dimensions["b"], 100.0)
        self.assertEqual(section.dimensions["h"], 200.0)
        self.assertEqual(section.dimensions["t"], 8.0)
        self.assertEqual(section.dimensions["r"], 5.0)
        self.assertEqual(len(section.dimensions), 4)
    
    def test_dimensions_dictionary_access(self):
        """Test that dimensions can be accessed like a dictionary."""
        section = rhs(b=100.0, h=200.0, t=10.0, r=15.0)
        
        # Test key access
        self.assertIn("b", section.dimensions)
        self.assertIn("h", section.dimensions)
        self.assertIn("t", section.dimensions)
        self.assertIn("r", section.dimensions)
        
        # Test iteration
        keys = list(section.dimensions.keys())
        self.assertEqual(set(keys), {"b", "h", "t", "r"})
        
        # Test values
        values = list(section.dimensions.values())
        self.assertEqual(set(values), {100.0, 200.0, 10.0, 15.0})
    
    def test_dimensions_different_values(self):
        """Test that different sections have different dimension values."""
        section1 = rhs(b=100.0, h=200.0, t=10.0, r=15.0)
        section2 = rhs(b=150.0, h=250.0, t=12.0, r=20.0)
        
        self.assertNotEqual(section1.dimensions["b"], section2.dimensions["b"])
        self.assertNotEqual(section1.dimensions["h"], section2.dimensions["h"])
        self.assertNotEqual(section1.dimensions["t"], section2.dimensions["t"])
        self.assertNotEqual(section1.dimensions["r"], section2.dimensions["r"])


if __name__ == "__main__":
    unittest.main()

