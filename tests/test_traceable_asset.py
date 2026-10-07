from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.v1.analysis import Analysis, Evidence
from app.schemas.v1.traceable_asset import (
    AssetClaim,
    ClaimEvidence,
)
from app.services.asset_generation import build_traceable_asset


def make_analysis(with_evidence: bool = True) -> Analysis:
    interaction_id = uuid4()

    evidence = (
        [
            Evidence(
                source_interaction_id=interaction_id,
                excerpt="Usuarios reportan problemas configurando Docker.",
            )
        ]
        if with_evidence
        else []
    )

    return Analysis(
        interaction_id=interaction_id,
        sentiment="negative",
        topics=["docker"],
        entities=["Docker"],
        relevance=0.90,
        confidence=0.90,
        evidence=evidence,
        model="mock-analysis-v1",
        prompt_version="v1",
    )


def test_every_claim_has_source_interaction_ids():
    analysis = make_analysis()

    asset = build_traceable_asset(
        opportunity_id=uuid4(),
        title="Guía de Docker",
        claims=[
            "Los usuarios reportan problemas configurando Docker.",
            "Una guía de configuración puede responder a esta necesidad.",
        ],
        analysis=analysis,
    )

    assert len(asset.claims) == 2

    for claim in asset.claims:
        assert claim.source_interaction_ids


def test_every_claim_has_evidence():
    analysis = make_analysis()

    asset = build_traceable_asset(
        opportunity_id=uuid4(),
        title="Guía de Docker",
        claims=["Los usuarios reportan problemas con Docker."],
        analysis=analysis,
    )

    claim = asset.claims[0]

    assert claim.evidence
    assert claim.evidence[0].excerpt


def test_claim_sources_match_evidence_sources():
    analysis = make_analysis()

    asset = build_traceable_asset(
        opportunity_id=uuid4(),
        title="Guía de Docker",
        claims=["Existe una necesidad de contenido sobre Docker."],
        analysis=analysis,
    )

    claim = asset.claims[0]

    evidence_ids = {
        item.source_interaction_id
        for item in claim.evidence
    }

    assert set(claim.source_interaction_ids) <= evidence_ids


def test_claim_without_source_ids_is_rejected():
    interaction_id = uuid4()

    with pytest.raises(ValidationError):
        AssetClaim(
            text="Claim sin fuentes.",
            source_interaction_ids=[],
            evidence=[
                ClaimEvidence(
                    source_interaction_id=interaction_id,
                    excerpt="Evidence",
                )
            ],
        )


def test_claim_without_evidence_is_rejected():
    with pytest.raises(ValidationError):
        AssetClaim(
            text="Claim sin evidence.",
            source_interaction_ids=[uuid4()],
            evidence=[],
        )


def test_claim_with_unmatched_source_is_rejected():
    with pytest.raises(ValidationError):
        AssetClaim(
            text="Claim inconsistente.",
            source_interaction_ids=[uuid4()],
            evidence=[
                ClaimEvidence(
                    source_interaction_id=uuid4(),
                    excerpt="Evidence from another interaction.",
                )
            ],
        )


def test_asset_generation_without_analysis_evidence_is_rejected():
    with pytest.raises(
        ValueError,
        match="without analysis evidence",
    ):
        build_traceable_asset(
            opportunity_id=uuid4(),
            title="Asset sin evidencia",
            claims=["Una afirmación."],
            analysis=make_analysis(with_evidence=False),
        )


def test_asset_generation_without_claims_is_rejected():
    with pytest.raises(
        ValueError,
        match="without claims",
    ):
        build_traceable_asset(
            opportunity_id=uuid4(),
            title="Asset vacío",
            claims=[],
            analysis=make_analysis(),
        )


def test_traceability_survives_json_serialization():
    analysis = make_analysis()

    asset = build_traceable_asset(
        opportunity_id=uuid4(),
        title="Guía de Docker",
        claims=["Los usuarios reportan problemas con Docker."],
        analysis=analysis,
    )

    payload = asset.model_dump(mode="json")
    claim = payload["claims"][0]

    assert claim["source_interaction_ids"]
    assert claim["evidence"]
    assert claim["evidence"][0]["source_interaction_id"]
    assert claim["evidence"][0]["excerpt"]
