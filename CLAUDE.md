# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

This project uses `uv` for dependency management (Python 3.13+).

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest testing/

# Run a single test file
uv run pytest testing/test_geometry.py

# Run a single test
uv run pytest testing/test_geometry.py::test_name

# Run an example
uv run python examples/making_sections.py
```

## Architecture

**Sectiony** is a Python library for structural cross-section property calculation and stress analysis.

### Layer Structure

1. **Geometry Layer** (`geometry.py`) — Immutable dataclasses: `Line`, `Arc`, `CubicBezier`, `Contour`, `Geometry`. Arcs are stored exactly (center, radius, angles in radians) and converted to cubic Béziers only for rendering. `Geometry` handles JSON serialization with schema versioning.

2. **Section Layer** (`section.py`) — `Section` wraps a `Geometry` and auto-calculates all properties in `__post_init__`. All contours must be closed loops.

3. **Properties** (`properties.py`) — `SectionProperties` dataclass; `calculate_exact_properties()` uses Green's theorem for exact (not grid-based) computation of area, centroids, moments of inertia (Ix, Iy, Ixy), torsional constant J, plastic moduli, shear center, and warping constant.

4. **Stress Analysis** (`stress.py`) — `Stress` class computes axial (σ), bending (σ), shear (τ), and torsion (τ) from applied internal forces. Torsional properties use a Poisson solver in `utils.py`.

5. **Visualization** (`plotter.py`) — Matplotlib-based; renders native curves (Lines and Arcs via Béziers) and stress field contours.

6. **Shape Library** (`library/`) — Parametric generators returning ready-to-use `Section` objects: `chs` (Circular Hollow Section), `rhs` (Rectangular Hollow Section), `i` (I-beam), `u` (U/Channel).

### Data Flow

```
Geometry (contours of Line/Arc) → Section → SectionProperties
                                          → Stress → plots
```

### DXF Import

`dxf_utils.py` handles DXF files (LINE, ARC, LWPOLYLINE entities) and converts them to `Geometry` objects.
