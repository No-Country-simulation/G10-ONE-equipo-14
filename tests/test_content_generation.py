"""Acceptance tests for COMLAB-40 (LinkedIn) and COMLAB-41 (FAQ)."""

from uuid import uuid4

import pytest

from app.schemas.v1.analysis import Analysis, Evidence
from app.services.content_generation import (
    FAQ_MAX_LENGTH,
    FAQ_MIN_LENGTH,
    LINKEDIN_MAX_LENGTH,
    LINKEDIN_MIN_LENGTH,
    generate_content,
)


def _analysis(with_evidence: bool = True):
    interaction_id = uuid4()
    return Analysis(
        interaction_id=interaction_id,
        sentiment="positive",
        topics=["fastapi"],
        entities=["FastAPI"],
        relevance=1,
        confidence=1,
        evidence=(
            [Evidence(
                source_interaction_id=interaction_id,
                excerpt="FastAPI permitió entregar una API estable.",
            )]
            if with_evidence
            else []
        ),
        model="mock-analysis-v1",
        prompt_version="v1",
    )


# ---------------------------------------------------------------------------
# COMLAB-40 y COMLAB-41: Versionado y trazabilidad
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("channel", "prompt_version"),
    [("LINKEDIN", "linkedin-v1"), ("FAQ", "faq-v1")],
)
def test_channel_generators_are_versioned_and_traceable(channel, prompt_version):
    generated = generate_content(
        channel=channel,
        opportunity_id=uuid4(),
        analysis=_analysis(),
    )

    assert generated.prompt_version == prompt_version
    assert generated.title
    assert generated.body
    # Trazabilidad: cada claim lleva evidence y source_interaction_ids.
    claim = generated.content["claims"][0]
    assert claim["evidence"]
    assert claim["source_interaction_ids"]


# ---------------------------------------------------------------------------
# COMLAB-40: Validaciones específicas del generador de LinkedIn
# ---------------------------------------------------------------------------

def test_linkedin_body_length_is_within_channel_range():
    """E4-S02: el copy debe respetar el rango de longitud esperado."""
    generated = generate_content(
        channel="LINKEDIN",
        opportunity_id=uuid4(),
        analysis=_analysis(),
    )
    assert LINKEDIN_MIN_LENGTH <= len(generated.body) <= LINKEDIN_MAX_LENGTH


def test_linkedin_without_evidence_is_rejected():
    """E4-S02: no se genera LinkedIn sin evidencia vinculada."""
    with pytest.raises(ValueError, match="evidence"):
        generate_content(
            channel="LINKEDIN",
            opportunity_id=uuid4(),
            analysis=_analysis(with_evidence=False),
        )


def test_linkedin_has_title_and_body():
    """E4-S02: el borrador debe incluir título y cuerpo."""
    generated = generate_content(
        channel="LINKEDIN",
        opportunity_id=uuid4(),
        analysis=_analysis(),
    )
    assert generated.title.strip()
    assert generated.body.strip()


# ---------------------------------------------------------------------------
# COMLAB-41: Validaciones específicas del generador de FAQ
# ---------------------------------------------------------------------------

def test_faq_title_is_phrased_as_question():
    """E4-S03: la FAQ debe formularse como pregunta."""
    generated = generate_content(
        channel="FAQ",
        opportunity_id=uuid4(),
        analysis=_analysis(),
    )
    assert generated.title.strip().endswith("?")


def test_faq_body_length_is_within_channel_range():
    """E4-S03: la respuesta debe respetar el rango de longitud esperado."""
    generated = generate_content(
        channel="FAQ",
        opportunity_id=uuid4(),
        analysis=_analysis(),
    )
    assert FAQ_MIN_LENGTH <= len(generated.body) <= FAQ_MAX_LENGTH


def test_faq_without_evidence_is_rejected():
    """E4-S03: no se genera FAQ sin evidencia vinculada."""
    with pytest.raises(ValueError, match="evidence"):
        generate_content(
            channel="FAQ",
            opportunity_id=uuid4(),
            analysis=_analysis(with_evidence=False),
        )


def test_unknown_channel_is_rejected():
    with pytest.raises(ValueError, match="Unsupported"):
        generate_content(
            channel="UNKNOWN",
            opportunity_id=uuid4(),
            analysis=_analysis(),
        )
