from uuid import UUID

from app.schemas.v1.analysis import Analysis
from app.schemas.v1.traceable_asset import (
    AssetClaim,
    ClaimEvidence,
    TraceableAsset,
)


def build_traceable_asset(
    *,
    opportunity_id: UUID,
    title: str,
    claims: list[str],
    analysis: Analysis,
) -> TraceableAsset:
    """Build an asset whose every claim is grounded in interaction evidence.

    The backend owns provenance. Claims cannot be emitted without evidence.
    """
    if not analysis.evidence:
        raise ValueError(
            "Cannot generate an asset without analysis evidence."
        )

    claim_items = [
        _build_grounded_claim(
            claim_text=claim_text,
            analysis=analysis,
        )
        for claim_text in claims
    ]

    if not claim_items:
        raise ValueError(
            "Cannot generate an asset without claims."
        )

    return TraceableAsset(
        opportunity_id=opportunity_id,
        title=title,
        claims=claim_items,
    )


def _build_grounded_claim(
    *,
    claim_text: str,
    analysis: Analysis,
) -> AssetClaim:
    evidence = [
        ClaimEvidence(
            source_interaction_id=item.source_interaction_id,
            excerpt=item.excerpt,
        )
        for item in analysis.evidence
    ]

    source_ids = list(
        dict.fromkeys(
            item.source_interaction_id
            for item in analysis.evidence
        )
    )

    return AssetClaim(
        text=claim_text,
        source_interaction_ids=source_ids,
        evidence=evidence,
    )
