from uuid import UUID, uuid5, NAMESPACE_URL
from app.domain.fingerprint import interaction_fingerprint
from app.schemas.process import ProcessRequest, ProcessResponse, RunSummary


def mock_process(payload: ProcessRequest, idempotency_key: str) -> ProcessResponse:
    """
    Week 1 integration seam.

    No LLM is called. A deterministic run_id is derived from the idempotency
    key so teammates can build against a stable contract.
    """
    run_id: UUID = uuid5(
        NAMESPACE_URL,
        f"{payload.organization_id}:{payload.community_id}:{idempotency_key}",
    )

    fingerprints = {
        interaction_fingerprint(
            payload.community_id,
            item.author,
            item.channel,
            item.text,
        )
        for item in payload.interactions
    }
    duplicates = len(payload.interactions) - len(fingerprints)

    return ProcessResponse(
        run_id=run_id,
        status="ACCEPTED",
        summary=RunSummary(
            received=len(payload.interactions),
            accepted=len(fingerprints),
            duplicates=duplicates,
            errors=0,
        ),
        analyses=[],
        opportunities=[],
        assets=[],
        storage=None,
    )
