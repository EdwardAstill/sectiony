from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .line_properties import LineGroup


@dataclass(frozen=True)
class LineStressState:
    """Elastic in-plane stress state at a point on a weighted line group."""

    x: float
    y: float
    tau_x: float
    tau_y: float

    @property
    def tau_resultant(self) -> float:
        """Resultant in-plane shear stress."""
        return math.hypot(self.tau_x, self.tau_y)

    def line_force_x(self, *, weight: float) -> float:
        """Line force in x direction for a local effective width."""
        return self.tau_x * weight

    def line_force_y(self, *, weight: float) -> float:
        """Line force in y direction for a local effective width."""
        return self.tau_y * weight

    def line_force_resultant(self, *, weight: float) -> float:
        """Resultant line force for a local effective width."""
        return self.tau_resultant * weight


@dataclass(frozen=True)
class ElasticLineGroupStress:
    """Elastic in-plane stress evaluator for weighted open-line groups."""

    group: LineGroup
    force_x: float = 0.0
    force_y: float = 0.0
    moment_z: float = 0.0

    def at(self, x: float, y: float) -> LineStressState:
        """Return stress at ``(x, y)``."""
        props = self.group.properties
        tau_x = self.force_x / props.weighted_area
        tau_y = self.force_y / props.weighted_area

        if self.moment_z and props.J:
            tau_x += -self.moment_z * (y - props.Cy) / props.J
            tau_y += self.moment_z * (x - props.Cx) / props.J

        return LineStressState(x=x, y=y, tau_x=tau_x, tau_y=tau_y)

    def max(self, *, resolution: int | None = None) -> LineStressState:
        """Return the maximum resultant stress from sampled group points."""
        states = (self.at(x, y) for x, y in self.group.sample_points(resolution))
        return max(states, key=lambda state: state.tau_resultant)
