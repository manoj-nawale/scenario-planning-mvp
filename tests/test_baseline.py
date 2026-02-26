import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from scenarioops.baseline import generate_baseline, summarize_baseline


class TestBaseline(unittest.TestCase):
    def test_generate_baseline_is_deterministic_with_same_seed(self):
        a = generate_baseline(seed=7)
        b = generate_baseline(seed=7)

        self.assertEqual(a.orders, b.orders)
        self.assertEqual(a.sites, b.sites)
        self.assertEqual(a.lines, b.lines)
        self.assertEqual(a.periods, b.periods)
        self.assertEqual(a.demand, b.demand)
        self.assertEqual(a.variable_cost, b.variable_cost)
        self.assertEqual(a.capacity, b.capacity)
        self.assertEqual(a.inbound_log_cost, b.inbound_log_cost)
        self.assertEqual(a.outbound_log_cost, b.outbound_log_cost)

    def test_summarize_baseline_contains_expected_shape(self):
        data = generate_baseline(seed=7)
        summary = summarize_baseline(data)

        self.assertIn("orders", summary)
        self.assertIn("sites", summary)
        self.assertIn("lines", summary)
        self.assertIn("periods", summary)
        self.assertIn("total_demand_by_period", summary)
        self.assertIn("total_capacity_by_period", summary)
        self.assertIn("capacity_by_line", summary)

        self.assertEqual(len(summary["orders"]), 20)
        self.assertEqual(len(summary["periods"]), 8)

        # Capacity is intentionally generated with ~5% slack, so capacity >= demand by period
        for t in summary["periods"]:
            self.assertGreaterEqual(summary["total_capacity_by_period"][t], summary["total_demand_by_period"][t])


if __name__ == "__main__":
    unittest.main()
