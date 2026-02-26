import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from scenarioops.baseline import generate_baseline
from scenarioops.models import ScenarioKnobs
from scenarioops.scenarios import apply_knobs


class TestScenarios(unittest.TestCase):
    def test_apply_knobs_scales_expected_fields(self):
        baseline = generate_baseline(seed=7)
        knobs = ScenarioKnobs(demand_scale=1.1, variable_cost_scale=1.2, logistics_cost_scale=0.9)

        out = apply_knobs(baseline, knobs)

        sample_demand_key = next(iter(baseline.demand.keys()))
        sample_var_key = next(iter(baseline.variable_cost.keys()))
        sample_in_key = next(iter(baseline.inbound_log_cost.keys()))
        sample_out_key = next(iter(baseline.outbound_log_cost.keys()))

        self.assertAlmostEqual(out.demand[sample_demand_key], baseline.demand[sample_demand_key] * 1.1)
        self.assertAlmostEqual(out.variable_cost[sample_var_key], baseline.variable_cost[sample_var_key] * 1.2)
        self.assertAlmostEqual(out.inbound_log_cost[sample_in_key], baseline.inbound_log_cost[sample_in_key] * 0.9)
        self.assertAlmostEqual(out.outbound_log_cost[sample_out_key], baseline.outbound_log_cost[sample_out_key] * 0.9)

        # Capacity should remain unchanged by scenario knobs
        self.assertEqual(out.capacity, baseline.capacity)

    def test_apply_knobs_is_pure_for_input(self):
        baseline = generate_baseline(seed=7)
        original_demand = dict(baseline.demand)

        _ = apply_knobs(baseline, ScenarioKnobs(demand_scale=1.2, variable_cost_scale=1.0, logistics_cost_scale=1.0))

        self.assertEqual(baseline.demand, original_demand)


if __name__ == "__main__":
    unittest.main()
