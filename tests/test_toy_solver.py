import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from scenarioops.baseline import generate_baseline
from scenarioops.models import ScenarioKnobs
from scenarioops.scenarios import apply_knobs
from scenarioops.toy_solver import run_toy_solver


class TestToySolver(unittest.TestCase):
    def test_solver_outputs_have_expected_keys(self):
        data = generate_baseline(seed=7)
        out = run_toy_solver(data)

        self.assertIsInstance(out.fact_production, list)
        self.assertGreater(len(out.fact_production), 0)

        for key in ["total_cost", "chosen_site", "total_capacity", "total_demand", "capacity_utilization"]:
            self.assertIn(key, out.kpi_total)

        for key in ["variable_cost", "overtime_cost", "inbound_logistics_cost", "outbound_logistics_cost"]:
            self.assertIn(key, out.kpi_cost_breakdown)

    def test_cost_reconciliation_matches_total(self):
        data = generate_baseline(seed=7)
        out = run_toy_solver(data)

        breakdown_sum = round(
            out.kpi_cost_breakdown["variable_cost"]
            + out.kpi_cost_breakdown["overtime_cost"]
            + out.kpi_cost_breakdown["inbound_logistics_cost"]
            + out.kpi_cost_breakdown["outbound_logistics_cost"],
            2,
        )
        self.assertEqual(out.kpi_total["total_cost"], breakdown_sum)

    def test_overtime_increases_with_higher_demand(self):
        baseline = generate_baseline(seed=7)
        high_demand = apply_knobs(
            baseline,
            ScenarioKnobs(demand_scale=1.3, variable_cost_scale=1.0, logistics_cost_scale=1.0),
        )

        base_out = run_toy_solver(baseline)
        high_out = run_toy_solver(high_demand)

        self.assertGreaterEqual(high_out.kpi_cost_breakdown["overtime_cost"], base_out.kpi_cost_breakdown["overtime_cost"])


if __name__ == "__main__":
    unittest.main()
