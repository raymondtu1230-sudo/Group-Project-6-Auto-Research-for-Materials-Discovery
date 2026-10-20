"""Synthetic report-shape tests only; these are not scientific experiments."""

import copy
import unittest

from M2.verify_stage_closeout import validate_coverage

SYSTEMS = [["Au", "K", "Tb"], ["Co", "Dy", "W"], ["Co", "Mg", "Na"],
           ["Ga", "Pt", "Tm"], ["Hf", "Ni", "Zr"], ["Mg", "Sn", "Sr"]]


def fixture():
    rows = [
        {"method": method, "split": "dev", "system": "-".join(system),
         "seed": str(seed), "B": "20", "oracle_queries": "20"}
        for method in ["random_generator_baseline", "chemeleon_generative_baseline"]
        for system in SYSTEMS for seed in [17, 29, 43]
    ]
    validation = {"split": "dev", "issues": [], "validated_runs": 36,
                  "missing_baseline_units": [], "baseline_sweep_complete": True,
                  "missing_units": [["m1_full", "dev", "Au-K-Tb", 17]]}
    return validation, rows


class StageCloseoutTests(unittest.TestCase):
    def test_full_baselines_do_not_require_m1_reference(self):
        validation, rows = fixture()
        self.assertTrue(validate_coverage(validation, rows, SYSTEMS)["baseline_data_complete"])

    def test_partial_sweep_never_becomes_complete(self):
        validation, rows = fixture()
        removed = rows.pop()
        validation.update(validated_runs=35, baseline_sweep_complete=False,
                          missing_baseline_units=[[removed["method"], "dev",
                                                   removed["system"], int(removed["seed"])]])
        self.assertFalse(validate_coverage(validation, rows, SYSTEMS)["baseline_data_complete"])

    def test_duplicate_cannot_replace_missing_unit(self):
        validation, rows = fixture()
        rows[-1] = copy.deepcopy(rows[0])
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate_coverage(validation, rows, SYSTEMS)

    def test_query_or_budget_shortfall_rejected(self):
        for field in ["B", "oracle_queries"]:
            validation, rows = fixture()
            rows[0][field] = "19"
            with self.assertRaisesRegex(ValueError, "B=20"):
                validate_coverage(validation, rows, SYSTEMS)

    def test_missing_list_cannot_hide_incomplete_unit(self):
        validation, rows = fixture()
        rows.pop()
        validation["validated_runs"] = 35
        with self.assertRaisesRegex(ValueError, "disagree"):
            validate_coverage(validation, rows, SYSTEMS)

    def test_official_validation_issue_blocks_acceptance(self):
        validation, rows = fixture()
        validation["issues"] = [{"kind": "bad_input"}]
        with self.assertRaisesRegex(ValueError, "validation issues"):
            validate_coverage(validation, rows, SYSTEMS)


if __name__ == "__main__":
    unittest.main()
