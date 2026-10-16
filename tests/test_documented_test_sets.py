import json
from pathlib import Path

import pytest

from app.schemas.v1.process import ProcessRequest
from app.services.csv_ingestion import parse_interactions_csv


TEST_SETS = Path("docs/sets_pruebas")
JSON_INPUTS = sorted(TEST_SETS.glob("set_*/entrada*.json"))


@pytest.mark.parametrize("input_path", JSON_INPUTS, ids=lambda path: path.parent.name)
def test_documented_json_inputs_match_process_contract(input_path):
    request = ProcessRequest.model_validate(
        json.loads(input_path.read_text(encoding="utf-8"))
    )

    assert request.interactions
    assert all(item.author and item.type for item in request.interactions)


def test_documented_csv_input_matches_process_contract():
    input_path = TEST_SETS / "set_04_prueba_inicial" / "entrada_interacciones_25.csv"

    items, errors = parse_interactions_csv(input_path.read_bytes())

    assert errors == []
    assert len(items) == 25
