from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass(frozen=True)
class ScenarioKnobs:
    """3-knob scenario control for the MVP."""
    demand_scale: float = 1.0
    variable_cost_scale: float = 1.0
    logistics_cost_scale: float = 1.0


@dataclass(frozen=True)
class ScenarioSpec:
    scenario_id: str
    created_at_utc: str
    knobs: ScenarioKnobs
    notes: str = ""


@dataclass(frozen=True)
class RunSpec:
    run_id: str
    dt: str  # YYYY-MM-DD
    created_at_utc: str
    mode: Literal["mvp"] = "mvp"

    @staticmethod
    def now(run_id: str) -> "RunSpec":
        now = datetime.utcnow()
        return RunSpec(
            run_id=run_id,
            dt=now.date().isoformat(),
            created_at_utc=now.isoformat() + "Z",
        )
