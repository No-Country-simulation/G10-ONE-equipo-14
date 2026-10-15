import pytest

from scripts.benchmark_500 import build_payload, validate_result


def test_benchmark_builds_maximum_unique_batch():
    payload = build_payload(500, "test")

    assert len(payload["interactions"]) == 500
    assert len({item["external_id"] for item in payload["interactions"]}) == 500
    assert payload["requested_assets"] == ["LINKEDIN"]
    assert (
        payload["interactions"][0]["text"]
        != build_payload(1, "other")["interactions"][0]["text"]
    )


def test_benchmark_rejects_more_than_contract_maximum():
    with pytest.raises(ValueError, match="between 1 and 500"):
        build_payload(501, "test")


def test_benchmark_validates_pipeline_cardinality():
    result = {
        "summary": {"received": 2, "accepted": 2, "duplicates": 0, "errors": 0},
        "analyses": [{}, {}],
        "opportunities": [{}, {}],
        "assets": [{}, {}],
    }
    validate_result(result, 2)


def test_benchmark_detects_incomplete_output():
    result = {
        "summary": {"received": 2, "accepted": 2, "duplicates": 0, "errors": 0},
        "analyses": [{}, {}],
        "opportunities": [{}],
        "assets": [{}, {}],
    }
    with pytest.raises(RuntimeError, match="Expected 2 opportunities"):
        validate_result(result, 2)
