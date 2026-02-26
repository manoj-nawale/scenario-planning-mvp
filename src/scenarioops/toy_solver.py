from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .baseline import BaselineData


@dataclass(frozen=True)
class SolverOutputs:
    fact_production: List[Dict]
    kpi_total: Dict[str, object]
    kpi_cost_breakdown: Dict[str, float]


def run_toy_solver(data: BaselineData) -> SolverOutputs:
    """
    Option C (ops-y): capacity + overtime penalty

    Heuristic:
    - choose best (cheapest) site for logistics (avg inbound+outbound)
    - for each period:
        - allocate demand across lines in order of cheapest unit variable cost
        - each line has capacity
        - any overflow becomes overtime (premium cost bucket)

    Notes:
    - inbound/outbound logistics are charged for ALL quantity (including overtime),
      because stuff still needs to ship.
    - overtime premium is applied only on the VARIABLE part (not logistics),
      and only for the overflow quantity.
    """

    # Cheapest site by avg (in+out) logistics across orders/periods
    site_avg: Dict[str, float] = {}
    for s in data.sites:
        vals = []
        for o in data.orders:
            for t in data.periods:
                vals.append(
                    float(data.inbound_log_cost[(o, s, t)]) + float(data.outbound_log_cost[(o, s, t)])
                )
        site_avg[s] = sum(vals) / max(1, len(vals))
    best_site = min(site_avg, key=site_avg.get)

    overtime_multiplier = 1.8  # premium vs base variable cost
    # premium portion only: overtime_qty * vc * (mult - 1)

    fact_production: List[Dict] = []

    total_variable = 0.0
    total_inbound = 0.0
    total_outbound = 0.0
    total_overtime_premium = 0.0

    # Precompute per-period line ranking by unit variable cost
    # (cheapest line first, per period)
    line_rank_by_t: Dict[int, List[str]] = {}
    for t in data.periods:
        costs = {l: float(data.variable_cost[(l, t)]) for l in data.lines}
        line_rank_by_t[t] = sorted(costs.keys(), key=lambda l: costs[l])

    # Track used capacity per (line, period)
    used_capacity: Dict[tuple, float] = {(l, t): 0.0 for l in data.lines for t in data.periods}

    for t in data.periods:
        ranked_lines = line_rank_by_t[t]

        for o in data.orders:
            qty_total = float(data.demand[(o, t)])
            if qty_total <= 0:
                continue

            ic = float(data.inbound_log_cost[(o, best_site, t)])
            oc = float(data.outbound_log_cost[(o, best_site, t)])

            # logistics applies to all units (regular + overtime)
            total_inbound += qty_total * ic
            total_outbound += qty_total * oc

            remaining_qty = qty_total

            # allocate across lines by cheapest variable cost first
            for l in ranked_lines:
                if remaining_qty <= 0:
                    break

                cap = float(data.capacity[(l, t)])
                used = used_capacity[(l, t)]
                remaining_cap = max(0.0, cap - used)

                alloc = min(remaining_qty, remaining_cap)
                if alloc <= 0:
                    continue

                vc = float(data.variable_cost[(l, t)])
                used_capacity[(l, t)] = used + alloc
                remaining_qty -= alloc

                total_variable += alloc * vc

                fact_production.append(
                    {
                        "order": o,
                        "period": t,
                        "line": l,
                        "site": best_site,
                        "quantity": qty_total,
                        "regular_qty": alloc,
                        "overtime_qty": 0.0,
                        "capacity": cap,
                        "used_capacity_regular": used_capacity[(l, t)],
                        "unit_var_cost": vc,
                        "unit_in_cost": ic,
                        "unit_out_cost": oc,
                        "overtime_multiplier": overtime_multiplier,
                        "cost_variable": round(alloc * vc, 6),
                        "cost_overtime_premium": 0.0,
                        "cost_inbound": round(qty_total * ic, 6),
                        "cost_outbound": round(qty_total * oc, 6),
                    }
                )

            # whatever couldn't fit is overtime
            if remaining_qty > 0:
                # assign overtime to the CHEAPEST line’s vc for that period
                # (simplify: overtime uses same line cost base, plus premium bucket)
                overtime_line = ranked_lines[0]
                vc_ot = float(data.variable_cost[(overtime_line, t)])

                premium = remaining_qty * vc_ot * (overtime_multiplier - 1.0)
                total_overtime_premium += premium

                # Note: base variable cost for overtime units is NOT counted again here.
                # We only add the premium bucket, since the "regular" variable cost
                # conceptually still applies — but because we couldn't allocate capacity,
                # we treat overtime as premium-on-top to avoid double counting.
                fact_production.append(
                    {
                        "order": o,
                        "period": t,
                        "line": overtime_line,
                        "site": best_site,
                        "quantity": qty_total,
                        "regular_qty": 0.0,
                        "overtime_qty": remaining_qty,
                        "capacity": float(data.capacity[(overtime_line, t)]),
                        "used_capacity_regular": float(used_capacity[(overtime_line, t)]),
                        "unit_var_cost": vc_ot,
                        "unit_in_cost": ic,
                        "unit_out_cost": oc,
                        "overtime_multiplier": overtime_multiplier,
                        "cost_variable": 0.0,
                        "cost_overtime_premium": round(premium, 6),
                        "cost_inbound": round(qty_total * ic, 6),
                        "cost_outbound": round(qty_total * oc, 6),
                    }
                )

    total = total_variable + total_overtime_premium + total_inbound + total_outbound

    kpi_cost_breakdown = {
        "variable_cost": round(total_variable, 2),
        "overtime_cost": round(total_overtime_premium, 2),
        "inbound_logistics_cost": round(total_inbound, 2),
        "outbound_logistics_cost": round(total_outbound, 2),
    }

    # tiny “explainability” nuggets
    total_cap = sum(float(data.capacity[(l, t)]) for l in data.lines for t in data.periods)
    total_dem = sum(float(data.demand[(o, t)]) for o in data.orders for t in data.periods)

    kpi_total = {
        "total_cost": round(total, 2),
        "chosen_site": best_site,
        "total_capacity": round(total_cap, 2),
        "total_demand": round(total_dem, 2),
        "capacity_utilization": round((total_dem / total_cap) if total_cap > 0 else 0.0, 4),
    }

    return SolverOutputs(
        fact_production=fact_production,
        kpi_total=kpi_total,
        kpi_cost_breakdown=kpi_cost_breakdown,
    )
