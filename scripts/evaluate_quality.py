"""Evaluate output validity, evidence grounding and opportunity precision."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from pydantic import BaseModel, Field

from app.ai.mock_provider import MockAnalysisProvider
from app.schemas.v1.analysis import Analysis
from app.schemas.v1.interaction import InteractionRequest
from app.services.opportunity_detection import detect_content_opportunity


class EvaluationItem(BaseModel):
    id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    type: str = Field(min_length=1)
    publication_consent: bool = True
    opt_out: bool = False
    expected_public_opportunity: bool
    rationale: str = Field(min_length=1)


class EvaluationDataset(BaseModel):
    schema_version: str
    annotated_at: str
    reviewer_role: str
    guideline_version: str
    items: list[EvaluationItem] = Field(min_length=1)


def evaluate(dataset: EvaluationDataset) -> dict:
    provider = MockAnalysisProvider()
    valid = grounded = true_positive = false_positive = false_negative = 0
    rows = []

    for item in dataset.items:
        interaction_id = uuid5(NAMESPACE_URL, item.id)
        interaction = InteractionRequest(
            external_id=item.id,
            author="human-evaluation",
            channel="evaluation",
            type=item.type,
            text=item.text,
            publication_consent=item.publication_consent,
            opt_out=item.opt_out,
        )
        analysis = provider.analyze(interaction_id, interaction)
        Analysis.model_validate(analysis.model_dump(mode="json"))
        valid += 1

        is_grounded = bool(analysis.evidence) and all(
            evidence.source_interaction_id == interaction_id
            and evidence.excerpt in interaction.text
            for evidence in analysis.evidence
        )
        grounded += int(is_grounded)

        decision = detect_content_opportunity(
            uuid5(NAMESPACE_URL, f"opportunity:{item.id}"),
            analysis,
            opt_out=item.opt_out,
        )
        predicted = decision is not None and decision.status.value == "PENDING"
        true_positive += int(predicted and item.expected_public_opportunity)
        false_positive += int(predicted and not item.expected_public_opportunity)
        false_negative += int(not predicted and item.expected_public_opportunity)
        rows.append(
            {
                "id": item.id,
                "expected_public_opportunity": item.expected_public_opportunity,
                "predicted_public_opportunity": predicted,
                "grounded": is_grounded,
            }
        )

    count = len(dataset.items)
    precision_denominator = true_positive + false_positive
    recall_denominator = true_positive + false_negative
    return {
        "schema_version": "v1",
        "sample_size": count,
        "output_validity": round(valid / count, 4),
        "grounding_rate": round(grounded / count, 4),
        "opportunity_precision": round(
            true_positive / precision_denominator if precision_denominator else 0,
            4,
        ),
        "opportunity_recall": round(
            true_positive / recall_denominator if recall_denominator else 0,
            4,
        ),
        "confusion": {
            "true_positive": true_positive,
            "false_positive": false_positive,
            "false_negative": false_negative,
            "true_negative": count - true_positive - false_positive - false_negative,
        },
        "items": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "dataset",
        nargs="?",
        type=Path,
        default=Path("data/evaluation/human_sample_v1.json"),
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    dataset = EvaluationDataset.model_validate_json(
        args.dataset.read_text(encoding="utf-8")
    )
    report = evaluate(dataset)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
