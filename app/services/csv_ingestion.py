import csv
import io
from pydantic import ValidationError
from app.schemas.v1.interaction import InteractionRequest
from app.services.ingestion import RecordError

REQUIRED_COLUMNS = {"author", "channel", "type", "text"}


def parse_interactions_csv(content: bytes) -> tuple[list[InteractionRequest], list[RecordError]]:
    try:
        decoded = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        return [], [RecordError(0, None, "invalid_encoding", str(exc))]

    reader = csv.DictReader(io.StringIO(decoded))
    if not reader.fieldnames:
        return [], [RecordError(0, None, "missing_header", "CSV header is required")]

    missing = REQUIRED_COLUMNS - set(reader.fieldnames)
    if missing:
        return [], [RecordError(0, None, "missing_columns", f"Missing columns: {', '.join(sorted(missing))}")]

    items: list[InteractionRequest] = []
    errors: list[RecordError] = []
    for index, row in enumerate(reader, start=1):
        payload = {key: (value if value not in (None, "") else None) for key, value in row.items()}
        try:
            items.append(InteractionRequest.model_validate(payload))
        except ValidationError as exc:
            errors.append(RecordError(index, row.get("external_id"), "validation_error", str(exc)))
    return items, errors
