from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class BaselineData:
    """
    Minimal Stage-2-ish snapshot for MVP.
    Keep it small, deterministic, and easy to explain.
    """
    orders: List[str]
    sites: List[str]
    lines: List[str]
    periods: List[int]

    demand: Dict[Tuple[str, int], float]                      # (order, period) -> qty
    variable_cost: Dict[Tuple[str, int], float]               # (line, period) -> €/unit (toy)
    inbound_log_cost: Dict[Tuple[str, str, int], float]       # (order, site, period) -> €/unit
    outbound_log_cost: Dict[Tuple[str, str, int], float]      # (order, site, period) -> €/unit
    capacity: Dict[Tuple[str, int], float]                    # (line, period) -> units capacity


def generate_baseline(seed: int = 7) -> BaselineData:
    rng = random.Random(seed)

    orders = [f"O{idx:03d}" for idx in range(1, 21)]   # 20 orders
    sites = ["DE_KA", "DE_ST", "PL_PO"]
    lines = ["L1", "L2", "L3"]
    periods = list(range(0, 8))  # 8 periods

    demand: Dict[Tuple[str, int], float] = {}
    for o in orders:
        base = rng.randint(50, 200)
        for t in periods:
            # mild seasonality + noise
            demand[(o, t)] = max(0.0, base * (1.0 + 0.1 * (t % 3)) + rng.randint(-10, 10))

    variable_cost: Dict[Tuple[str, int], float] = {}
    for l in lines:
        base = rng.uniform(8.0, 15.0)
        for t in periods:
            variable_cost[(l, t)] = round(base * (1.0 + 0.02 * t), 2)

    # --- Capacity: derived from baseline demand (so baseline has ~5% slack) ---
    total_demand_by_period = {
        t: sum(demand[(o, t)] for o in orders)
        for t in periods
    }

    slack = 1.05  # 5% headroom so baseline overtime is ~0
    total_capacity_by_period = {t: total_demand_by_period[t] * slack for t in periods}

    # Split capacity across lines using fixed shares (explainable)
    shares = {"L1": 0.40, "L2": 0.35, "L3": 0.25}

    capacity: Dict[Tuple[str, int], float] = {}
    for t in periods:
        for l in lines:
            cap = total_capacity_by_period[t] * shares[l]
            capacity[(l, t)] = round(cap, 1)


    inbound_log_cost: Dict[Tuple[str, str, int], float] = {}
    outbound_log_cost: Dict[Tuple[str, str, int], float] = {}
    for o in orders:
        for s in sites:
            base_in = rng.uniform(0.5, 2.0)
            base_out = rng.uniform(0.8, 3.0)
            for t in periods:
                inbound_log_cost[(o, s, t)] = round(base_in * (1.0 + 0.01 * t), 3)
                outbound_log_cost[(o, s, t)] = round(base_out * (1.0 + 0.01 * t), 3)

    return BaselineData(
        orders=orders,
        sites=sites,
        lines=lines,
        periods=periods,
        demand=demand,
        variable_cost=variable_cost,
        capacity=capacity,
        inbound_log_cost=inbound_log_cost,
        outbound_log_cost=outbound_log_cost,
    )

def summarize_baseline(data):
    total_demand_by_period = {
        t: round(sum(float(data.demand[(o, t)]) for o in data.orders), 2)
        for t in data.periods
    }

    # capacity by period per line
    capacity_by_line = {
        l: {t: float(data.capacity[(l, t)]) for t in data.periods}
        for l in data.lines
    }

    # also useful: sum capacity across lines per period
    total_capacity_by_period = {
        t: round(sum(float(data.capacity[(l, t)]) for l in data.lines), 2)
        for t in data.periods
    }

    return {
        "orders": data.orders,
        "sites": data.sites,
        "lines": data.lines,
        "periods": data.periods,
        "total_demand_by_period": total_demand_by_period,
        "total_capacity_by_period": total_capacity_by_period,
        "capacity_by_line": capacity_by_line,
    }
