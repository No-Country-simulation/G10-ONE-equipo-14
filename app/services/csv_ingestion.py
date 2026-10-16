import csv
import io
from pydantic import ValidationError
from app.schemas.v1.interaction import FIELD_ALIASES, InteractionRequest
from app.services.ingestion import RecordError

REQUIRED_COLUMNS = {"author", "channel", "type", "text"}
SUPPORTED_ENCODINGS = ("utf-8-sig", "cp1252")


def _decode(content: bytes) -> str:
    last_error: UnicodeDecodeError | None = None
    for encoding in SUPPORTED_ENCODINGS:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError as exc:
            last_error = exc
    assert last_error is not None
    raise last_error


def _canonical_columns(fieldnames: list[str]) -> set[str]:
    return {FIELD_ALIASES.get(name, name) for name in fieldnames}


def parse_interactions_csv(
    content: bytes,
) -> tuple[list[InteractionRequest], list[RecordError]]:
    try:
        decoded = _decode(content)
    except UnicodeDecodeError as exc:
        return [], [RecordError(0, None, "invalid_encoding", str(exc))]

    reader = csv.DictReader(io.StringIO(decoded))
    if not reader.fieldnames:
        return [], [RecordError(0, None, "missing_header", "CSV header is required")]

    missing = REQUIRED_COLUMNS - _canonical_columns(reader.fieldnames)
    if missing:
        return [], [
            RecordError(
                0,
                None,
                "missing_columns",
                f"Missing columns: {', '.join(sorted(missing))}",
            )
        ]

    items: list[InteractionRequest] = []
    errors: list[RecordError] = []
    for index, row in enumerate(reader, start=1):
        payload = {
            key: (value if value not in (None, "") else None)
            for key, value in row.items()
        }
        try:
            items.append(InteractionRequest.model_validate(payload))
        except ValidationError as exc:
            errors.append(
                RecordError(index, row.get("external_id"), "validation_error", str(exc))
            )
    return items, errors
