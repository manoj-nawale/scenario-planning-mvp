from __future__ import annotations

from .baseline import BaselineData
from .models import ScenarioKnobs
from dataclasses import replace


def apply_knobs(baseline: BaselineData, knobs: ScenarioKnobs) -> BaselineData:
    """
    Pure function: returns a new BaselineData with knobs applied.
    - demand_scale -> demand
    - variable_cost_scale -> variable_cost
    - logistics_cost_scale -> inbound/outbound logistics
    """
    return replace(
        baseline,
        demand={k: v * knobs.demand_scale for k, v in baseline.demand.items()},
        variable_cost={k: v * knobs.variable_cost_scale for k, v in baseline.variable_cost.items()},
        inbound_log_cost={k: v * knobs.logistics_cost_scale for k, v in baseline.inbound_log_cost.items()},
        outbound_log_cost={k: v * knobs.logistics_cost_scale for k, v in baseline.outbound_log_cost.items()},
    )

