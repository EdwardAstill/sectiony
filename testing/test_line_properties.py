import math
import sys
from pathlib import Path

import pytest

src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from sectiony import Line, LineElement, LineGroup
from sectiony.geometry import Arc


def test_single_vertical_line_properties_use_weight_as_effective_width():
    group = LineGroup(
        elements=(
            LineElement(
                segment=Line(start=(0.0, -1.0), end=(0.0, 1.0)),
                weight=0.25,
            ),
        )
    )

    props = group.properties

    assert props.length == pytest.approx(2.0)
    assert props.weighted_area == pytest.approx(0.5)
    assert props.Cx == pytest.approx(0.0)
    assert props.Cy == pytest.approx(0.0)
    assert props.Ix == pytest.approx(0.25 * 2.0 / 3.0)
    assert props.Iy == pytest.approx(0.0)
    assert props.Ixy == pytest.approx(0.0)
    assert props.J == pytest.approx(props.Ix)


def test_two_vertical_lines_include_parallel_axis_contribution():
    group = LineGroup(
        elements=(
            LineElement(
                segment=Line(start=(-2.0, -1.0), end=(-2.0, 1.0)),
                weight=0.25,
            ),
            LineElement(
                segment=Line(start=(2.0, -1.0), end=(2.0, 1.0)),
                weight=0.25,
            ),
        )
    )

    props = group.properties

    assert props.weighted_area == pytest.approx(1.0)
    assert props.Cx == pytest.approx(0.0)
    assert props.Cy == pytest.approx(0.0)
    assert props.Ix == pytest.approx(2.0 * 0.25 * 2.0 / 3.0)
    assert props.Iy == pytest.approx(4.0)
    assert props.J == pytest.approx(props.Ix + props.Iy)


def test_arc_line_group_uses_chord_integration_with_configurable_resolution():
    quarter_arc = Arc(
        center=(0.0, 0.0),
        radius=1.0,
        start_angle=0.0,
        end_angle=math.pi / 2.0,
    )

    coarse = LineGroup(elements=(LineElement(segment=quarter_arc),), curve_resolution=4)
    fine = LineGroup(elements=(LineElement(segment=quarter_arc),), curve_resolution=128)

    assert fine.properties.length == pytest.approx(math.pi / 2.0, rel=1e-4)
    assert abs(fine.properties.length - math.pi / 2.0) < abs(
        coarse.properties.length - math.pi / 2.0
    )


def test_line_group_rejects_empty_or_non_positive_weight():
    with pytest.raises(ValueError, match="at least one"):
        LineGroup(elements=())

    with pytest.raises(ValueError, match="weight must be positive"):
        LineElement(
            segment=Line(start=(0.0, 0.0), end=(1.0, 0.0)),
            weight=0.0,
        )


def test_elastic_line_group_stress_reports_stress_and_line_force_at_point():
    group = LineGroup(
        elements=(
            LineElement(
                segment=Line(start=(-1.0, -1.0), end=(-1.0, 1.0)),
                weight=0.01,
            ),
            LineElement(
                segment=Line(start=(1.0, -1.0), end=(1.0, 1.0)),
                weight=0.01,
            ),
        )
    )

    stress = group.elastic_stress(force_x=400.0, force_y=0.0, moment_z=40.0)
    center = stress.at(0.0, 0.0)
    right_mid = stress.at(1.0, 0.0)

    assert center.tau_x == pytest.approx(10_000.0)
    assert center.tau_y == pytest.approx(0.0)
    assert center.tau_resultant == pytest.approx(10_000.0)
    assert center.line_force_x(weight=0.01) == pytest.approx(100.0)

    assert right_mid.tau_x == pytest.approx(10_000.0)
    assert right_mid.tau_y == pytest.approx(750.0)
    assert right_mid.tau_resultant == pytest.approx(math.hypot(10_000.0, 750.0))
    assert right_mid.line_force_y(weight=0.01) == pytest.approx(7.5)


def test_elastic_line_group_stress_finds_sampled_maximum():
    group = LineGroup(
        elements=(
            LineElement(
                segment=Line(start=(-1.0, -1.0), end=(-1.0, 1.0)),
                weight=0.01,
            ),
            LineElement(
                segment=Line(start=(1.0, -1.0), end=(1.0, 1.0)),
                weight=0.01,
            ),
        )
    )

    stress = group.elastic_stress(force_x=400.0, force_y=0.0, moment_z=40.0)
    state = stress.max()

    assert state.y == pytest.approx(-1.0)
    assert state.tau_resultant == pytest.approx(math.hypot(10_750.0, 750.0))
