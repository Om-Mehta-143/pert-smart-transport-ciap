"""
Automated Unit Tests for PERT and Critical Path Calculation Engine
Contains 13 comprehensive unit tests with hand-verified calculations.
"""

import math
import unittest
from pert_engine import PERTEngine, PERTValidationError


class TestPERTEngine(unittest.TestCase):
    """
    HAND CALCULATION REFERENCE CASE 1 (Single linear sequence A -> B):
    Activity A: O=1, M=2, P=3
      TE_A = (1 + 4*2 + 3) / 6 = 12 / 6 = 2.0
      Var_A = ((3 - 1) / 6)^2 = (2 / 6)^2 = (1/3)^2 = 1/9 ≈ 0.1111
      ES_A = 0, EF_A = 2.0
    Activity B: Pred=[A], O=2, M=4, P=6
      TE_B = (2 + 4*4 + 6) / 6 = 24 / 6 = 4.0
      Var_B = ((6 - 2) / 6)^2 = (4 / 6)^2 = (2/3)^2 = 4/9 ≈ 0.4444
      ES_B = 2.0, EF_B = 6.0
    Project Duration = 6.0
    Critical Path = ['A', 'B']
    Project Variance = 1/9 + 4/9 = 5/9 ≈ 0.5556
    Project StdDev = sqrt(5/9) ≈ 0.7454
    """

    def test_01_hand_calculation_case_linear(self):
        activities = [
            {"id": "A", "name": "Task A", "predecessors": [], "optimistic": 1, "most_likely": 2, "pessimistic": 3},
            {"id": "B", "name": "Task B", "predecessors": ["A"], "optimistic": 2, "most_likely": 4, "pessimistic": 6},
        ]
        engine = PERTEngine(activities)
        res = engine.compute()

        self.assertAlmostEqual(res["project_duration"], 6.0, places=3)
        self.assertEqual(res["critical_path"], ["A", "B"])
        self.assertAlmostEqual(res["project_variance"], 5.0 / 9.0, places=3)
        self.assertAlmostEqual(res["project_std_dev"], math.sqrt(5.0 / 9.0), places=3)

        # Check activity node values
        act_map = {a["id"]: a for a in res["activities"]}
        self.assertAlmostEqual(act_map["A"]["te"], 2.0, places=3)
        self.assertAlmostEqual(act_map["A"]["slack"], 0.0, places=3)
        self.assertAlmostEqual(act_map["B"]["te"], 4.0, places=3)
        self.assertAlmostEqual(act_map["B"]["slack"], 0.0, places=3)

    """
    HAND CALCULATION REFERENCE CASE 2 (Diamond graph with slack on branch):
    Node Start A: O=3, M=3, P=3 -> TE=3, Var=0, ES=0, EF=3
    Branch 1: B (Pred=[A]): O=4, M=4, P=4 -> TE=4, ES=3, EF=7
    Branch 2: C (Pred=[A]): O=2, M=2, P=2 -> TE=2, ES=3, EF=5
    Join: D (Pred=[B, C]): O=5, M=5, P=5 -> TE=5
      ES_D = max(EF_B=7, EF_C=5) = 7, EF_D = 12
    Project Duration = 12
    Critical Path = ['A', 'B', 'D']
    Slack for C:
      LF_C = LS_D = 12 - 5 = 7.
      EF_C = 5.
      Slack_C = LF_C - EF_C = 7 - 5 = 2.0.
    """

    def test_02_hand_calculation_diamond_slack(self):
        activities = [
            {"id": "A", "name": "Start", "predecessors": [], "optimistic": 3, "most_likely": 3, "pessimistic": 3},
            {"id": "B", "name": "Heavy Branch", "predecessors": ["A"], "optimistic": 4, "most_likely": 4, "pessimistic": 4},
            {"id": "C", "name": "Light Branch", "predecessors": ["A"], "optimistic": 2, "most_likely": 2, "pessimistic": 2},
            {"id": "D", "name": "Finish", "predecessors": ["B", "C"], "optimistic": 5, "most_likely": 5, "pessimistic": 5},
        ]
        engine = PERTEngine(activities)
        res = engine.compute()

        self.assertAlmostEqual(res["project_duration"], 12.0, places=3)
        self.assertEqual(res["critical_path"], ["A", "B", "D"])

        act_map = {a["id"]: a for a in res["activities"]}
        self.assertEqual(act_map["C"]["slack"], 2.0)
        self.assertFalse(act_map["C"]["is_critical"])
        self.assertEqual(act_map["B"]["slack"], 0.0)
        self.assertTrue(act_map["B"]["is_critical"])

    def test_03_parallel_critical_paths(self):
        """Case with two parallel critical paths having equal durations."""
        activities = [
            {"id": "Start", "name": "Start", "predecessors": [], "optimistic": 2, "most_likely": 2, "pessimistic": 2},
            {"id": "Path1", "name": "Path 1", "predecessors": ["Start"], "optimistic": 6, "most_likely": 6, "pessimistic": 6},
            {"id": "Path2", "name": "Path 2", "predecessors": ["Start"], "optimistic": 6, "most_likely": 6, "pessimistic": 6},
            {"id": "End", "name": "End", "predecessors": ["Path1", "Path2"], "optimistic": 3, "most_likely": 3, "pessimistic": 3},
        ]
        engine = PERTEngine(activities)
        res = engine.compute()

        self.assertAlmostEqual(res["project_duration"], 11.0, places=3)
        self.assertEqual(len(res["critical_paths"]), 2)
        expected_paths = [["Start", "Path1", "End"], ["Start", "Path2", "End"]]
        self.assertTrue(all(p in res["critical_paths"] for p in expected_paths))

    def test_04_cycle_detection_error(self):
        """Validates detection of cyclic dependency graph (A -> B -> C -> A)."""
        activities = [
            {"id": "A", "name": "Task A", "predecessors": ["C"], "optimistic": 1, "most_likely": 2, "pessimistic": 3},
            {"id": "B", "name": "Task B", "predecessors": ["A"], "optimistic": 2, "most_likely": 3, "pessimistic": 4},
            {"id": "C", "name": "Task C", "predecessors": ["B"], "optimistic": 1, "most_likely": 2, "pessimistic": 3},
        ]
        engine = PERTEngine(activities)
        with self.assertRaises(PERTValidationError) as ctx:
            engine.compute()
        self.assertIn("Cyclic dependency detected", str(ctx.exception))

    def test_05_omp_order_violation(self):
        """Validates error raised when Optimistic > Most Likely or Most Likely > Pessimistic."""
        activities = [
            {"id": "A", "name": "Invalid Task", "predecessors": [], "optimistic": 8, "most_likely": 5, "pessimistic": 4}
        ]
        engine = PERTEngine(activities)
        with self.assertRaises(PERTValidationError) as ctx:
            engine.compute()
        self.assertIn("Violation of O <= M <= P requirement", str(ctx.exception))

    def test_06_negative_or_zero_estimates(self):
        """Validates error raised when time estimates are non-positive."""
        activities = [
            {"id": "A", "name": "Negative Task", "predecessors": [], "optimistic": -1, "most_likely": 2, "pessimistic": 4}
        ]
        engine = PERTEngine(activities)
        with self.assertRaises(PERTValidationError) as ctx:
            engine.compute()
        self.assertIn("strictly positive", str(ctx.exception))

    def test_07_missing_predecessor_reference(self):
        """Validates error raised when referencing an unknown predecessor ID."""
        activities = [
            {"id": "A", "name": "Task A", "predecessors": ["NON_EXISTENT"], "optimistic": 1, "most_likely": 2, "pessimistic": 3}
        ]
        engine = PERTEngine(activities)
        with self.assertRaises(PERTValidationError) as ctx:
            engine.compute()
        self.assertIn("unknown predecessor 'NON_EXISTENT'", str(ctx.exception))

    def test_08_self_loop_detected(self):
        """Validates error raised when activity lists itself as predecessor."""
        activities = [
            {"id": "A", "name": "Self Loop", "predecessors": ["A"], "optimistic": 1, "most_likely": 2, "pessimistic": 3}
        ]
        engine = PERTEngine(activities)
        with self.assertRaises(PERTValidationError) as ctx:
            engine.compute()
        self.assertIn("cannot list itself as a predecessor", str(ctx.exception))

    def test_09_probability_z_score_calculation(self):
        """
        Validates Z-Score and Normal CDF calculation for target deadlines.
        Linear path: Duration = 10, StdDev = 2.
        For Deadline = 10, Z = (10-10)/2 = 0 -> Probability = 50.0%
        For Deadline = 12, Z = (12-10)/2 = 1.0 -> Probability ≈ 84.13%
        For Deadline = 6,  Z = (6-10)/2 = -2.0 -> Probability ≈ 2.28%
        """
        activities = [
            {"id": "A", "name": "Single Task", "predecessors": [], "optimistic": 4, "most_likely": 10, "pessimistic": 16}
        ]
        engine = PERTEngine(activities)
        engine.compute()

        p50 = engine.calculate_probability(10.0)
        self.assertAlmostEqual(p50["z_score"], 0.0, places=2)
        self.assertAlmostEqual(p50["probability_percent"], 50.0, places=1)

        p84 = engine.calculate_probability(12.0)
        self.assertAlmostEqual(p84["z_score"], 1.0, places=2)
        self.assertAlmostEqual(p84["probability_percent"], 84.13, delta=0.2)

        p02 = engine.calculate_probability(6.0)
        self.assertAlmostEqual(p02["z_score"], -2.0, places=2)
        self.assertAlmostEqual(p02["probability_percent"], 2.28, delta=0.2)

    def test_10_bus_tracking_dataset_functional(self):
        """Validates realistic smart-transit bus live-tracking application dataset."""
        bus_dataset = [
            {"id": "A", "name": "Requirements & Route Specs", "predecessors": [], "optimistic": 2, "most_likely": 4, "pessimistic": 6},
            {"id": "B", "name": "GPS Module Hardware Proc", "predecessors": ["A"], "optimistic": 3, "most_likely": 6, "pessimistic": 9},
            {"id": "C", "name": "Backend Ingestion API", "predecessors": ["A"], "optimistic": 4, "most_likely": 7, "pessimistic": 16},
            {"id": "D", "name": "Firmware & GPS Testing", "predecessors": ["B"], "optimistic": 2, "most_likely": 5, "pessimistic": 8},
            {"id": "E", "name": "Mobile Rider UI", "predecessors": ["A"], "optimistic": 3, "most_likely": 6, "pessimistic": 9},
            {"id": "F", "name": "Cloud Stream Processor", "predecessors": ["C"], "optimistic": 2, "most_likely": 4, "pessimistic": 6},
            {"id": "G", "name": "System Integration", "predecessors": ["D", "E", "F"], "optimistic": 2, "most_likely": 3, "pessimistic": 4},
            {"id": "H", "name": "Security Audit & PenTest", "predecessors": ["G"], "optimistic": 1, "most_likely": 2, "pessimistic": 3},
            {"id": "I", "name": "Pilot Fleet Rollout", "predecessors": ["H"], "optimistic": 1, "most_likely": 3, "pessimistic": 5},
        ]
        engine = PERTEngine(bus_dataset)
        res = engine.compute()

        self.assertAlmostEqual(res["project_duration"], 24.0, places=3)
        self.assertEqual(res["critical_path"], ["A", "C", "F", "G", "H", "I"])

    def test_11_ciap_project_delivery_plan_dataset(self):
        """Validates the 3-day CIAP Microproject delivery schedule itself."""
        ciap_plan = [
            {"id": "T1", "name": "Architecture & Scope Definition", "predecessors": [], "optimistic": 1, "most_likely": 2, "pessimistic": 3},
            {"id": "T2", "name": "Core PERT Engine & Math Tests", "predecessors": ["T1"], "optimistic": 2, "most_likely": 3, "pessimistic": 4},
            {"id": "T3", "name": "Flask Web UI & SVG Visualizer", "predecessors": ["T2"], "optimistic": 2, "most_likely": 4, "pessimistic": 6},
            {"id": "T4", "name": "Dockerfile & Non-Root Hardening", "predecessors": ["T3"], "optimistic": 1, "most_likely": 2, "pessimistic": 3},
            {"id": "T5", "name": "Jenkins CI/CD Pipeline Setup", "predecessors": ["T4"], "optimistic": 2, "most_likely": 3, "pessimistic": 4},
            {"id": "T6", "name": "SonarQube & Trivy Scan Hardening", "predecessors": ["T5"], "optimistic": 2, "most_likely": 3, "pessimistic": 4},
            {"id": "T7", "name": "Terraform AWS Free Tier Config", "predecessors": ["T5"], "optimistic": 2, "most_likely": 3, "pessimistic": 4},
            {"id": "T8", "name": "Integration & Cloud Verification", "predecessors": ["T6", "T7"], "optimistic": 1, "most_likely": 2, "pessimistic": 3},
            {"id": "T9", "name": "Academic Report & PPT Drafting", "predecessors": ["T8"], "optimistic": 3, "most_likely": 5, "pessimistic": 7},
            {"id": "T10", "name": "Video Demo & Final QA Audit", "predecessors": ["T9"], "optimistic": 1, "most_likely": 2, "pessimistic": 3},
        ]
        engine = PERTEngine(ciap_plan)
        res = engine.compute()

        self.assertGreater(res["project_duration"], 20.0)
        self.assertIn("T1", res["critical_path"])
        self.assertIn("T10", res["critical_path"])

    def test_12_empty_activities_validation(self):
        """Validates error on completely empty input list."""
        engine = PERTEngine([])
        with self.assertRaises(PERTValidationError):
            engine.compute()

    def test_13_sample_transit_full_precision_variance(self):
        """
        Verifies that variance and std deviation are computed at full float precision
        without premature rounding error, asserting project variance for the sample dataset
        equals exactly 5.5556 when displayed.
        Critical Path: A (Var=4/9) + C (Var=36/9) + F (Var=4/9) + G (Var=1/9) + H (Var=1/9) + I (Var=4/9) = 50/9 = 5.555555...
        """
        bus_dataset = [
            {"id": "A", "name": "Requirements & Route Specs", "predecessors": [], "optimistic": 2, "most_likely": 4, "pessimistic": 6},
            {"id": "B", "name": "GPS Module Hardware Proc", "predecessors": ["A"], "optimistic": 3, "most_likely": 6, "pessimistic": 9},
            {"id": "C", "name": "Backend Ingestion API", "predecessors": ["A"], "optimistic": 4, "most_likely": 7, "pessimistic": 16},
            {"id": "D", "name": "Firmware & GPS Testing", "predecessors": ["B"], "optimistic": 2, "most_likely": 5, "pessimistic": 8},
            {"id": "E", "name": "Mobile Rider UI", "predecessors": ["A"], "optimistic": 3, "most_likely": 6, "pessimistic": 9},
            {"id": "F", "name": "Cloud Stream Processor", "predecessors": ["C"], "optimistic": 2, "most_likely": 4, "pessimistic": 6},
            {"id": "G", "name": "System Integration", "predecessors": ["D", "E", "F"], "optimistic": 2, "most_likely": 3, "pessimistic": 4},
            {"id": "H", "name": "Security Audit & PenTest", "predecessors": ["G"], "optimistic": 1, "most_likely": 2, "pessimistic": 3},
            {"id": "I", "name": "Pilot Fleet Rollout", "predecessors": ["H"], "optimistic": 1, "most_likely": 3, "pessimistic": 5},
        ]
        engine = PERTEngine(bus_dataset)
        res = engine.compute()

        # Raw float precision check
        self.assertAlmostEqual(engine.project_variance, 50.0 / 9.0, places=9)
        self.assertAlmostEqual(engine.project_std_dev, math.sqrt(50.0 / 9.0), places=9)

        # Rounded display output check
        self.assertEqual(res["project_variance"], 5.5556)
        self.assertEqual(res["project_std_dev"], 2.357)


if __name__ == "__main__":
    unittest.main()
