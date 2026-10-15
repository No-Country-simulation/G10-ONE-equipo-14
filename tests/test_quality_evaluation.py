import json
from pathlib import Path

from scripts.evaluate_quality import EvaluationDataset, evaluate


DATASET = Path("data/evaluation/human_sample_v1.json")


def test_human_sample_is_complete_and_traceable():
    raw = json.loads(DATASET.read_text(encoding="utf-8"))
    dataset = EvaluationDataset.model_validate(raw)

    assert len(dataset.items) == 20
    assert len({item.id for item in dataset.items}) == 20
    assert all(item.rationale for item in dataset.items)
    assert {item.expected_public_opportunity for item in dataset.items} == {
        True,
        False,
    }


def test_quality_evaluation_meets_baseline():
    dataset = EvaluationDataset.model_validate_json(DATASET.read_text(encoding="utf-8"))

    report = evaluate(dataset)

    assert report["sample_size"] == 20
    assert report["output_validity"] == 1.0
    assert report["grounding_rate"] == 1.0
    assert report["opportunity_precision"] >= 0.9
    assert report["opportunity_recall"] >= 0.9
