"""
Examples: Creating Sections with sectiony

This file demonstrates:
1. Using the standard library sections (CHS, RHS, I, U)
2. Creating custom sections without holes
3. Creating custom sections with holes
4. JSON serialization and loading
5. Generating plots for gallery
"""

import sys
import math
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sectiony import Section, Geometry, Contour, Line, Arc, CubicBezier
from sectiony.library import chs, rhs, i, u


# Setup output directories
ROOT_DIR = Path(__file__).resolve().parent.parent
GALLERY_DIR = ROOT_DIR / "gallery"
JSON_DIR = ROOT_DIR / "jsons"

# Create directories if they don't exist
GALLERY_DIR.mkdir(exist_ok=True)
JSON_DIR.mkdir(exist_ok=True)


def save_plot(section: Section, filename: str) -> None:
    """Save a section plot to the gallery directory."""
    fig, ax = plt.subplots(figsize=(8, 8))
    section.plot(ax=ax, show=False)
    ax.set_title(f"{section.name}\nA={section.A:.1f} mm², Iy={section.Iy:.1e} mm⁴", 
                 fontsize=10)
    output_path = GALLERY_DIR / f"{filename}.svg"
    fig.savefig(output_path, format='svg', bbox_inches='tight', dpi=150)
    plt.close(fig)
    print(f"   Plot saved: gallery/{filename}.svg")


def save_json(section: Section, filename: str) -> None:
    """Save a section geometry to JSON directory."""
    if section.geometry:
        output_path = JSON_DIR / f"{filename}.json"
        section.geometry.to_json(str(output_path))
        print(f"   JSON saved: json/{filename}.json")


# ============================================================================
# 1. USING STANDARD LIBRARY SECTIONS
# ============================================================================

print("=" * 70)
print("1. STANDARD LIBRARY SECTIONS")
print("=" * 70)

# Circular Hollow Section (CHS)
print("\n1.1 Circular Hollow Section (CHS)")
chs_section = chs(d=200.0, t=10.0)  # Outer diameter 200mm, thickness 10mm
print(f"   Section: {chs_section.name}")
print(f"   Area: {chs_section.A:.2f} mm²")
print(f"   Iy: {chs_section.Iy:.2f} mm⁴")
print(f"   Centroid: ({chs_section.Cy:.2f}, {chs_section.Cz:.2f})")
save_plot(chs_section, "01_chs")
save_json(chs_section, "01_chs")

# Rectangular Hollow Section (RHS)
print("\n1.2 Rectangular Hollow Section (RHS)")
rhs_section = rhs(b=100.0, h=200.0, t=10.0, r=15.0)  # Width, Height, Thickness, Corner radius
print(f"   Section: {rhs_section.name}")
print(f"   Area: {rhs_section.A:.2f} mm²")
print(f"   Iy: {rhs_section.Iy:.2f} mm⁴")
print(f"   Iz: {rhs_section.Iz:.2f} mm⁴")
save_plot(rhs_section, "02_rhs")
save_json(rhs_section, "02_rhs")

# I-Section
print("\n1.3 I-Section")
i_section = i(d=300.0, b=150.0, tf=12.0, tw=8.0, r=10.0)  # Depth, Width, Flange t, Web t, Radius
print(f"   Section: {i_section.name}")
print(f"   Area: {i_section.A:.2f} mm²")
print(f"   Strong axis Iz: {i_section.Iz:.2f} mm⁴")
save_plot(i_section, "03_i_section")
save_json(i_section, "03_i_section")

# U-Channel
print("\n1.4 U-Channel")
u_section = u(b=100.0, h=200.0, tw=8.0, tf=10.0, r=5.0)  # Width, Height, Web thickness, Flange thickness, Corner radius
print(f"   Section: {u_section.name}")
print(f"   Area: {u_section.A:.2f} mm²")
print(f"   Shear Center: ({u_section.SCy:.2f}, {u_section.SCz:.2f})")
save_plot(u_section, "04_u_channel")
save_json(u_section, "04_u_channel")


# ============================================================================
# 2. CUSTOM SECTIONS WITHOUT HOLES
# ============================================================================

print("\n" + "=" * 70)
print("2. CUSTOM SECTIONS WITHOUT HOLES")
print("=" * 70)

# Example 2.1: Simple Rectangle using Contour.from_points()
print("\n2.1 Simple Rectangle (using Contour.from_points)")
rect_points = [
    (50, 25),   # Top-right
    (50, -25),  # Bottom-right
    (-50, -25), # Bottom-left
    (-50, 25)   # Top-left
]
rect_contour = Contour.from_points(rect_points, hollow=False)
rect_geom = Geometry(contours=[rect_contour])
rect_section = Section(name="Custom Rectangle", geometry=rect_geom)
print(f"   Section: {rect_section.name}")
print(f"   Area: {rect_section.A:.2f} mm²")
print(f"   Expected: 100 × 50 = 5000 mm²")
save_plot(rect_section, "05_rectangle")
save_json(rect_section, "05_rectangle")

# Example 2.2: Triangle using Line segments
print("\n2.2 Triangle (using Line segments)")
triangle_segments = [
    Line(start=(0, 0), end=(50, 0)),      # Base
    Line(start=(50, 0), end=(25, 86.6)),   # Right side
    Line(start=(25, 86.6), end=(0, 0))    # Left side (closes loop)
]
triangle_contour = Contour(segments=triangle_segments, hollow=False)
triangle_geom = Geometry(contours=[triangle_contour])
triangle_section = Section(name="Equilateral Triangle", geometry=triangle_geom)
print(f"   Section: {triangle_section.name}")
print(f"   Area: {triangle_section.A:.2f} mm²")
print(f"   Centroid: ({triangle_section.Cy:.2f}, {triangle_section.Cz:.2f})")
save_plot(triangle_section, "06_triangle")
save_json(triangle_section, "06_triangle")

# Example 2.3: D-Shape with Arc
print("\n2.3 D-Shape (using Line and Arc)")
# Vertical straight back, rounded front
d_segments = [
    # Vertical line going down (the back of the D)
    Line(start=(50, 0), end=(-50, 0)),
    # Arc from bottom to top via the right side
    Arc(
        center=(0, 0),
        radius=50.0,
        start_angle=3*math.pi/2,  # Bottom (-y)
        end_angle=5*math.pi/2     # Top (+y), same as pi/2
    )
]
d_contour = Contour(segments=d_segments, hollow=False)
d_geom = Geometry(contours=[d_contour])
d_section = Section(name="D-Shape", geometry=d_geom)
print(f"   Section: {d_section.name}")
print(f"   Area: {d_section.A:.2f} mm²")
print(f"   Expected: π × 50² / 2 ≈ 3927 mm²")
save_plot(d_section, "07_d_shape")
save_json(d_section, "07_d_shape")

# Example 2.4: Rounded Rectangle with Arcs
print("\n2.4 Rounded Rectangle (using Lines and Arcs)")
corner_radius = 10.0
half_h = 40.0
half_b = 20.0
cy = half_h - corner_radius
cz = half_b - corner_radius

rounded_rect_segments = [
    # Top-Right corner arc
    Arc(center=(cy, cz), radius=corner_radius, start_angle=0, end_angle=math.pi/2),
    # Top edge
    Line(start=(half_h, cz), end=(half_h, -cz)),
    # Top-Left corner arc
    Arc(center=(cy, -cz), radius=corner_radius, start_angle=math.pi/2, end_angle=math.pi),
    # Left edge
    Line(start=(cy, -half_b), end=(-cy, -half_b)),
    # Bottom-Left corner arc
    Arc(center=(-cy, -cz), radius=corner_radius, start_angle=math.pi, end_angle=3*math.pi/2),
    # Bottom edge
    Line(start=(-half_h, -cz), end=(-half_h, cz)),
    # Bottom-Right corner arc
    Arc(center=(-cy, cz), radius=corner_radius, start_angle=3*math.pi/2, end_angle=2*math.pi),
    # Right edge (back to start)
    Line(start=(-cy, half_b), end=(cy, half_b))
]
rounded_rect_contour = Contour(segments=rounded_rect_segments, hollow=False)
rounded_rect_geom = Geometry(contours=[rounded_rect_contour])
rounded_rect_section = Section(name="Rounded Rectangle", geometry=rounded_rect_geom)
print(f"   Section: {rounded_rect_section.name}")
print(f"   Area: {rounded_rect_section.A:.2f} mm²")
save_plot(rounded_rect_section, "08_rounded_rectangle")
save_json(rounded_rect_section, "08_rounded_rectangle")


# ============================================================================
# 3. CUSTOM SECTIONS WITH HOLES
# ============================================================================

print("\n" + "=" * 70)
print("3. CUSTOM SECTIONS WITH HOLES")
print("=" * 70)

# Example 3.1: Hollow Rectangle
print("\n3.1 Hollow Rectangle")
outer_points = [(50, 30), (50, -30), (-50, -30), (-50, 30)]
inner_points = [(30, 20), (30, -20), (-30, -20), (-30, 20)]

outer_contour = Contour.from_points(outer_points, hollow=False)
inner_contour = Contour.from_points(inner_points, hollow=True)  # Mark as hole

hollow_rect_geom = Geometry(contours=[outer_contour, inner_contour])
hollow_rect_section = Section(name="Hollow Rectangle", geometry=hollow_rect_geom)
print(f"   Section: {hollow_rect_section.name}")
print(f"   Area: {hollow_rect_section.A:.2f} mm²")
print(f"   Expected: 100×60 - 60×40 = 3600 mm²")
save_plot(hollow_rect_section, "09_hollow_rectangle")
save_json(hollow_rect_section, "09_hollow_rectangle")

# Example 3.2: Hollow Circle (Ring)
print("\n3.2 Hollow Circle (Ring)")
outer_circle = Contour(
    segments=[Arc(center=(0, 0), radius=50.0, start_angle=0, end_angle=2*math.pi)],
    hollow=False
)
inner_circle = Contour(
    segments=[Arc(center=(0, 0), radius=30.0, start_angle=0, end_angle=2*math.pi)],
    hollow=True  # Mark as hole
)
ring_geom = Geometry(contours=[outer_circle, inner_circle])
ring_section = Section(name="Ring", geometry=ring_geom)
print(f"   Section: {ring_section.name}")
print(f"   Area: {ring_section.A:.2f} mm²")
print(f"   Expected: π(50² - 30²) ≈ 5027 mm²")
save_plot(ring_section, "10_ring")
save_json(ring_section, "10_ring")

# Example 3.3: I-Beam with Web Opening
print("\n3.3 I-Beam with Rectangular Web Opening")
# Create I-beam segments
web_height = 200.0
flange_width = 100.0
flange_thickness = 15.0
web_thickness = 10.0

half_h = web_height / 2 + flange_thickness
half_b = flange_width / 2
half_tw = web_thickness / 2

i_beam_segments = [
    # Top flange
    Line(start=(half_h, half_b), end=(half_h, -half_b)),
    Line(start=(half_h, -half_b), end=(half_h - flange_thickness, -half_b)),
    # Left web
    Line(start=(half_h - flange_thickness, -half_b), end=(half_h - flange_thickness, -half_tw)),
    Line(start=(half_h - flange_thickness, -half_tw), end=(-half_h + flange_thickness, -half_tw)),
    # Bottom flange
    Line(start=(-half_h + flange_thickness, -half_tw), end=(-half_h + flange_thickness, -half_b)),
    Line(start=(-half_h + flange_thickness, -half_b), end=(-half_h, -half_b)),
    Line(start=(-half_h, -half_b), end=(-half_h, half_b)),
    # Right web
    Line(start=(-half_h, half_b), end=(-half_h + flange_thickness, half_b)),
    Line(start=(-half_h + flange_thickness, half_b), end=(-half_h + flange_thickness, half_tw)),
    Line(start=(-half_h + flange_thickness, half_tw), end=(half_h - flange_thickness, half_tw)),
    # Close
    Line(start=(half_h - flange_thickness, half_tw), end=(half_h - flange_thickness, half_b)),
    Line(start=(half_h - flange_thickness, half_b), end=(half_h, half_b))
]

i_beam_contour = Contour(segments=i_beam_segments, hollow=False)

# Web opening (rectangular hole)
opening_points = [
    (50, 20),   # Top-right of opening
    (50, -20),  # Bottom-right
    (-50, -20), # Bottom-left
    (-50, 20)   # Top-left
]
opening_contour = Contour.from_points(opening_points, hollow=True)

i_beam_with_opening_geom = Geometry(contours=[i_beam_contour, opening_contour])
i_beam_with_opening_section = Section(name="I-Beam with Opening", geometry=i_beam_with_opening_geom)
print(f"   Section: {i_beam_with_opening_section.name}")
print(f"   Area: {i_beam_with_opening_section.A:.2f} mm²")
save_plot(i_beam_with_opening_section, "11_i_beam_with_opening")
save_json(i_beam_with_opening_section, "11_i_beam_with_opening")


# ============================================================================
# 4. JSON SERIALIZATION DEMONSTRATION
# ============================================================================

print("\n" + "=" * 70)
print("4. JSON SERIALIZATION DEMONSTRATION")
print("=" * 70)

# Example 4.1: Load and verify JSON
print("\n4.1 Loading and Verifying JSON")
loaded_geom = Geometry.from_json(str(JSON_DIR / "08_rounded_rectangle.json"))
loaded_section = Section(name="Loaded Rounded Rectangle", geometry=loaded_geom)
print(f"   Loaded section: {loaded_section.name}")
print(f"   Area: {loaded_section.A:.2f} mm²")
print(f"   Original area: {rounded_rect_section.A:.2f} mm²")
print(f"   Match: {abs(loaded_section.A - rounded_rect_section.A) < 0.01}")

# Example 4.2: Inspect JSON structure
print("\n4.2 JSON Structure Example")
import json
json_file = JSON_DIR / "08_rounded_rectangle.json"
with open(json_file, 'r') as f:
    json_data = json.load(f)
print(f"   Schema version: {json_data['version']}")
print(f"   Number of contours: {len(json_data['contours'])}")
print(f"   First contour segments: {len(json_data['contours'][0]['segments'])}")
print(f"   Segment types: {[s['type'] for s in json_data['contours'][0]['segments']]}")

# Example 4.3: Manual dictionary serialization
print("\n4.3 Manual Dictionary Serialization")
geom_dict = rounded_rect_section.geometry.to_dict()
print(f"   Dictionary keys: {list(geom_dict.keys())}")
print(f"   Version: {geom_dict['version']}")

# Recreate from dictionary
recreated_geom = Geometry.from_dict(geom_dict)
recreated_section = Section(name="Recreated from Dict", geometry=recreated_geom)
print(f"   Recreated section area: {recreated_section.A:.2f} mm²")


# ============================================================================
# 5. SUMMARY
# ============================================================================

print("\n" + "=" * 70)
print("5. SUMMARY")
print("=" * 70)
print(f"""
This example demonstrated:

1. Standard Library Sections:
   - chs(): Circular Hollow Section
   - rhs(): Rectangular Hollow Section  
   - i(): I-Section (with separate web and flange thickness)
   - u(): U-Channel (with separate web and flange thickness)

2. Custom Sections (No Holes):
   - Contour.from_points() for simple polygons
   - Line segments for straight edges
   - Arc segments for curved edges
   - Combined Line + Arc for complex shapes

3. Custom Sections (With Holes):
   - Multiple contours in one Geometry
   - Set hollow=True for internal voids
   - Supports any combination of shapes

4. JSON Serialization:
   - geometry.to_json(file_path) to save
   - Geometry.from_json(file_path) to load
   - geometry.to_dict() / Geometry.from_dict() for programmatic use
   - Includes schema versioning for forward compatibility

Output Files:
   - Plots saved to: {GALLERY_DIR}
   - JSON files saved to: {JSON_DIR}

All sections automatically calculate:
- Area (A)
- Centroid (Cy, Cz)
- Second moments (Iy, Iz, Iyz)
- Section moduli (Sy, Sz)
- Plastic moduli (Zpl_y, Zpl_z)
- Torsion constant (J)
- Shear center (SCy, SCz)
""")

print(f"\nDone! Generated {len(list(GALLERY_DIR.glob('*.svg')))} plots and {len(list(JSON_DIR.glob('*.json')))} JSON files.")
