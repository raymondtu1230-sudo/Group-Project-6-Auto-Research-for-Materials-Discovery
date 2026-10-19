"""Runner and retained-data evidence; these synthetic checks are not scores."""

from copy import deepcopy

from M2.verify_batch_recovery import runner_checks


def test_distinct_runner_ids_are_accepted_even_with_repeated_hostnames():
    before = {"name": "runner-before", "hostname": "shared-hostname"}
    after = {"name": "runner-after", "hostname": "shared-hostname"}
    jobs = [
        {"runner_name": "runner-before", "runner_id": 42, "id": 1},
        {"runner_name": "runner-after", "runner_id": 48, "id": 2},
    ]
    assert all(runner_checks(before, after, jobs).values())
    same_runner = deepcopy(jobs)
    same_runner[1]["runner_id"] = 42
    assert not runner_checks(before, after, same_runner)["different_runner_ids"]


def test_missing_or_ambiguous_runner_metadata_does_not_pass():
    before, after = {"name": "a"}, {"name": "b"}
    assert not any(runner_checks(before, after, []).values())
    duplicated = [
        {"runner_name": "a", "runner_id": 1, "id": 1},
        {"runner_name": "a", "runner_id": 2, "id": 2},
        {"runner_name": "b", "runner_id": 3, "id": 3},
    ]
    assert not any(runner_checks(before, after, duplicated).values())
