from uuid import uuid4

import pytest

from app.schemas.v1.analysis import Analysis, Evidence
from app.services.content_generation import generate_content


def _analysis():
    interaction_id = uuid4()
    return Analysis(
        interaction_id=interaction_id,
        sentiment="positive",
        topics=["fastapi"],
        entities=["FastAPI"],
        relevance=1,
        confidence=1,
        evidence=[Evidence(source_interaction_id=interaction_id, excerpt="FastAPI permitió entregar una API estable.")],
        model="mock-analysis-v1",
        prompt_version="v1",
    )


@pytest.mark.parametrize(
    ("channel", "prompt_version"),
    [("LINKEDIN", "linkedin-v1"), ("FAQ", "faq-v1")],
)
def test_channel_generators_are_versioned_and_traceable(channel, prompt_version):
    generated = generate_content(channel=channel, opportunity_id=uuid4(), analysis=_analysis())

    assert generated.prompt_version == prompt_version
    assert generated.title
    assert generated.body
    assert generated.content["claims"][0]["evidence"]


def test_unknown_channel_is_rejected():
    with pytest.raises(ValueError, match="Unsupported"):
        generate_content(channel="UNKNOWN", opportunity_id=uuid4(), analysis=_analysis())
