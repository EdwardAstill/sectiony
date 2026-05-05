# Line Groups

Line groups model open geometry with an effective weight per unit length. They
are intended for general line-based engineering calculations such as weld
groups, seams, adhesive lines, or other distributed connection paths.

```python
from sectiony import Line, LineElement, LineGroup

group = LineGroup(
    elements=(
        LineElement(
            name="left",
            segment=Line(start=(-1.0, -1.0), end=(-1.0, 1.0)),
            weight=0.01,
        ),
        LineElement(
            name="right",
            segment=Line(start=(1.0, -1.0), end=(1.0, 1.0)),
            weight=0.01,
        ),
    )
)

props = group.properties
print(props.weighted_area, props.Cx, props.Cy, props.J)
```

## Properties

`LineGroup.properties` returns centroidal properties for the weighted line
geometry:

* `length`: total geometric length.
* `weighted_area`: sum of `weight * segment length`.
* `Cx`, `Cy`: centroid of the weighted line group.
* `Ix`, `Iy`, `Ixy`: centroidal second moments of the weighted line group.
* `J`: polar line inertia, calculated as `Ix + Iy`.

Straight lines are integrated exactly. Arcs and cubic Beziers are approximated
by chord integration using `curve_resolution`; increase this value when curved
line properties need tighter approximation.

## Elastic Stress

Line groups can evaluate a standards-free elastic in-plane stress distribution:

```python
stress = group.elastic_stress(force_x=400.0, force_y=0.0, moment_z=40.0)

state = stress.at(1.0, 0.0)
print(state.tau_x, state.tau_y, state.tau_resultant)

worst = stress.max()
print(worst.x, worst.y, worst.tau_resultant)
```

The stress evaluator distributes direct force over `weighted_area` and
distributes `moment_z` elastically about the line-group centroid using `J`. It
does not perform a resistance check, code check, fatigue check, or nonlinear
instantaneous-center analysis.
