"""
Examples: Discretizing Geometry with sectiony

This file demonstrates:
1. Standard discretization with `discretize` method
2. Uniform discretization with `discretize_uniform` method
3. Visualizing discretized points
4. Comparing spacing between methods
"""

import sys
import math
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sectiony import Section, Geometry, Contour, Line, Arc
from sectiony.library import rhs, chs, i


# Setup output directory
ROOT_DIR = Path(__file__).resolve().parent.parent
GALLERY_DIR = ROOT_DIR / "gallery"
GALLERY_DIR.mkdir(exist_ok=True)


def plot_discretized_points(
    points: list,
    title: str,
    filename: str,
    show_segments: bool = True
) -> None:
    """Plot discretized points and optionally connect them."""
    fig, ax = plt.subplots(figsize=(10, 10))
    
    y_coords = [p[0] for p in points]
    z_coords = [p[1] for p in points]
    
    # Plot connecting lines
    if show_segments:
        ax.plot(z_coords + [z_coords[0]], y_coords + [y_coords[0]], 
                'b-', linewidth=0.5, alpha=0.5, label='Segments')
    
    # Plot points
    ax.scatter(z_coords, y_coords, c='red', s=20, zorder=5, label=f'Points ({len(points)})')
    
    ax.set_xlabel('z')
    ax.set_ylabel('y')
    ax.set_title(title)
    ax.set_aspect('equal')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    output_path = GALLERY_DIR / f"{filename}.svg"
    fig.savefig(output_path, format='svg', bbox_inches='tight')
    plt.close(fig)
    print(f"   Saved: gallery/{filename}.svg")


def calculate_segment_lengths(points: list) -> list:
    """Calculate the length of each segment between consecutive points."""
    lengths = []
    for idx in range(len(points) - 1):
        p1 = points[idx]
        p2 = points[idx + 1]
        length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        lengths.append(length)
    return lengths


def print_length_stats(lengths: list, label: str) -> None:
    """Print statistics about segment lengths."""
    if not lengths:
        print(f"   {label}: No segments")
        return
    avg = sum(lengths) / len(lengths)
    min_len = min(lengths)
    max_len = max(lengths)
    variance = sum((x - avg) ** 2 for x in lengths) / len(lengths)
    std_dev = math.sqrt(variance)
    
    print(f"   {label}:")
    print(f"      Segments: {len(lengths)}")
    print(f"      Average length: {avg:.4f}")
    print(f"      Min: {min_len:.4f}, Max: {max_len:.4f}")
    print(f"      Std deviation: {std_dev:.4f}")


# =============================================================================
# Example 1: Line Discretization
# =============================================================================
def example_line_discretization() -> None:
    """Demonstrate that lines are now properly split into segments."""
    print("\n" + "="*60)
    print("Example 1: Line Discretization")
    print("="*60)
    
    line = Line(start=(0, 0), end=(100, 0))
    
    # Old behavior would return just 2 points
    # New behavior respects resolution
    points_10 = line.discretize(resolution=10)
    points_50 = line.discretize(resolution=50)
    
    print(f"\n   Line from (0,0) to (100,0) - Length: {line.length}")
    print(f"   discretize(resolution=10): {len(points_10)} points")
    print(f"   discretize(resolution=50): {len(points_50)} points")
    
    # Verify uniform spacing
    lengths_10 = calculate_segment_lengths(points_10)
    print_length_stats(lengths_10, "Resolution 10")


# =============================================================================
# Example 2: Standard vs Uniform Discretization on Mixed Contour
# =============================================================================
def example_standard_vs_uniform() -> None:
    """Compare standard and uniform discretization on a contour with mixed segments."""
    print("\n" + "="*60)
    print("Example 2: Standard vs Uniform Discretization")
    print("="*60)
    
    # Create a closed contour with mixed segment types
    # A rectangle with rounded corners (like an RHS cross-section outline)
    # Dimensions: 60 wide (z) x 100 tall (y) with corner radius 10
    
    w, h, r = 60, 100, 10
    hw, hh = w/2, h/2  # half-width, half-height
    
    segments = [
        # Bottom edge (left to right)
        Line(start=(-hh, -hw + r), end=(-hh, hw - r)),
        # Bottom-right corner
        Arc(center=(-hh + r, hw - r), radius=r,
            start_angle=3*math.pi/2, end_angle=2*math.pi),
        # Right edge (bottom to top)
        Line(start=(-hh + r, hw), end=(hh - r, hw)),
        # Top-right corner
        Arc(center=(hh - r, hw - r), radius=r,
            start_angle=0, end_angle=math.pi/2),
        # Top edge (right to left)
        Line(start=(hh, hw - r), end=(hh, -hw + r)),
        # Top-left corner
        Arc(center=(hh - r, -hw + r), radius=r,
            start_angle=math.pi/2, end_angle=math.pi),
        # Left edge (top to bottom)
        Line(start=(hh - r, -hw), end=(-hh + r, -hw)),
        # Bottom-left corner
        Arc(center=(-hh + r, -hw + r), radius=r,
            start_angle=math.pi, end_angle=3*math.pi/2),
    ]
    contour = Contour(segments=segments)
    
    total_length = contour.length
    print(f"\n   Rounded rectangle: {w}x{h} with r={r}")
    print(f"   Contour total length: {total_length:.2f}")
    print(f"   (4 straight edges + 4 quarter arcs)")
    
    # Standard discretization - each segment gets same resolution
    standard_points = contour.discretize(resolution=10)
    standard_lengths = calculate_segment_lengths(standard_points)
    
    print(f"\n   Standard discretize(resolution=10):")
    print_length_stats(standard_lengths, "Standard")
    
    # Uniform discretization - equal spacing across entire contour
    uniform_points = contour.discretize_uniform(count=80)
    uniform_lengths = calculate_segment_lengths(uniform_points)
    
    print(f"\n   Uniform discretize_uniform(count=80):")
    print_length_stats(uniform_lengths, "Uniform")
    
    # Plot both
    plot_discretized_points(
        standard_points, 
        f"Standard Discretization (resolution=10)\n{len(standard_points)} points, variable spacing",
        "discretize_standard"
    )
    plot_discretized_points(
        uniform_points, 
        f"Uniform Discretization (count=80)\n{len(uniform_points)} points, equal spacing",
        "discretize_uniform"
    )


# =============================================================================
# Example 3: Uniform Discretization on Library Sections
# =============================================================================
def example_library_sections() -> None:
    """Demonstrate uniform discretization on standard library sections."""
    print("\n" + "="*60)
    print("Example 3: Library Sections Uniform Discretization")
    print("="*60)
    
    # RHS with rounded corners
    my_rhs = rhs(b=100, h=200, t=10, r=15)
    
    # Get uniform discretization
    discretized = my_rhs.discretize_uniform(count=100)
    
    for idx, (points, is_hollow) in enumerate(discretized):
        contour_type = "Hollow" if is_hollow else "Solid"
        lengths = calculate_segment_lengths(points)
        print(f"\n   RHS Contour {idx} ({contour_type}):")
        print_length_stats(lengths, f"Contour {idx}")
        
        plot_discretized_points(
            points,
            f"RHS {contour_type} Contour - Uniform ({len(points)} points)",
            f"discretize_rhs_{contour_type.lower()}"
        )
    
    # CHS (circular section)
    my_chs = chs(d=100, t=10)
    discretized_chs = my_chs.discretize_uniform(count=64)
    
    for idx, (points, is_hollow) in enumerate(discretized_chs):
        contour_type = "Hollow" if is_hollow else "Solid"
        print(f"\n   CHS Contour {idx} ({contour_type}):")
        lengths = calculate_segment_lengths(points)
        print_length_stats(lengths, f"Contour {idx}")


# =============================================================================
# Example 4: Comparison Plot - Side by Side
# =============================================================================
def example_comparison_plot() -> None:
    """Create a side-by-side comparison of discretization methods."""
    print("\n" + "="*60)
    print("Example 4: Side-by-Side Comparison")
    print("="*60)
    
    # Create an I-section
    my_i = i(d=200, b=100, tf=15, tw=10, r=10)
    
    if my_i.geometry is None:
        print("   No geometry available")
        return
        
    contour = my_i.geometry.contours[0]  # Outer contour
    
    # Get both discretizations
    standard_points = contour.discretize(resolution=16)
    uniform_points = contour.discretize_uniform(count=100)
    
    # Create comparison plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 8))
    
    # Standard discretization
    ax1 = axes[0]
    y1 = [p[0] for p in standard_points]
    z1 = [p[1] for p in standard_points]
    ax1.plot(z1 + [z1[0]], y1 + [y1[0]], 'b-', linewidth=0.5, alpha=0.5)
    ax1.scatter(z1, y1, c='red', s=30, zorder=5)
    ax1.set_title(f"Standard Discretization\nresolution=16 → {len(standard_points)} points\nVariable segment lengths")
    ax1.set_xlabel('z')
    ax1.set_ylabel('y')
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3)
    
    # Uniform discretization
    ax2 = axes[1]
    y2 = [p[0] for p in uniform_points]
    z2 = [p[1] for p in uniform_points]
    ax2.plot(z2 + [z2[0]], y2 + [y2[0]], 'b-', linewidth=0.5, alpha=0.5)
    ax2.scatter(z2, y2, c='green', s=30, zorder=5)
    ax2.set_title(f"Uniform Discretization\ncount=100 → {len(uniform_points)} points\nEqual segment lengths")
    ax2.set_xlabel('z')
    ax2.set_ylabel('y')
    ax2.set_aspect('equal')
    ax2.grid(True, alpha=0.3)
    
    fig.suptitle("I-Section Discretization Comparison", fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output_path = GALLERY_DIR / "discretize_comparison.svg"
    fig.savefig(output_path, format='svg', bbox_inches='tight')
    plt.close(fig)
    print(f"   Saved: gallery/discretize_comparison.svg")
    
    # Print stats
    standard_lengths = calculate_segment_lengths(standard_points)
    uniform_lengths = calculate_segment_lengths(uniform_points)
    
    print("\n   Segment length statistics:")
    print_length_stats(standard_lengths, "Standard (res=16)")
    print_length_stats(uniform_lengths, "Uniform (count=100)")


# =============================================================================
# Example 5: Practical Use Case - Perimeter Sampling
# =============================================================================
def example_perimeter_sampling() -> None:
    """Demonstrate practical use case of sampling points along perimeter."""
    print("\n" + "="*60)
    print("Example 5: Perimeter Sampling for Analysis")
    print("="*60)
    
    # Create a section
    my_rhs = rhs(b=100, h=150, t=8, r=12)
    
    # Get uniformly spaced points for analysis
    discretized = my_rhs.discretize_uniform(count=200)
    outer_points, _ = discretized[0]  # Outer contour
    
    print(f"\n   RHS 100x150x8 with r=12 corners")
    print(f"   Sampled {len(outer_points)} uniformly spaced points")
    
    # Calculate perimeter
    total_perimeter = sum(calculate_segment_lengths(outer_points + [outer_points[0]]))
    print(f"   Approximate perimeter: {total_perimeter:.2f} mm")
    
    # Average segment length
    avg_segment = total_perimeter / len(outer_points)
    print(f"   Average segment length: {avg_segment:.4f} mm")
    
    # This is useful for:
    # - Weld analysis (equal sampling along weld path)
    # - Stress distribution (equal spacing for numerical integration)
    # - Thermal analysis (consistent mesh density)
    
    print("\n   Use cases for uniform discretization:")
    print("   - Weld stress analysis along perimeter")
    print("   - Numerical integration of stress distributions")
    print("   - Thermal/heat transfer boundary conditions")
    print("   - Creating mesh boundaries for FEA")


# =============================================================================
# Main
# =============================================================================
def main() -> None:
    """Run all discretization examples."""
    print("\n" + "="*60)
    print("DISCRETIZATION EXAMPLES")
    print("="*60)
    
    example_line_discretization()
    example_standard_vs_uniform()
    example_library_sections()
    example_comparison_plot()
    example_perimeter_sampling()
    
    print("\n" + "="*60)
    print("All examples complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

