"""Deterministic, channel-specific content generation for the MVP."""

from dataclasses import dataclass
from uuid import UUID

from app.schemas.v1.analysis import Analysis
from app.services.asset_generation import build_traceable_asset


LINKEDIN_PROMPT_VERSION = "linkedin-v1"
FAQ_PROMPT_VERSION = "faq-v1"


@dataclass(frozen=True)
class GeneratedContent:
    channel: str
    title: str
    body: str
    content: dict
    prompt_version: str


def generate_content(
    *,
    channel: str,
    opportunity_id: UUID,
    analysis: Analysis,
) -> GeneratedContent:
    if channel == "LINKEDIN":
        title = "Aprendizaje destacado de la comunidad"
        body = (
            f"Nuestra comunidad compartió este avance: {analysis.evidence[0].excerpt} "
            "Seguimos construyendo y aprendiendo juntos."
        )
        prompt_version = LINKEDIN_PROMPT_VERSION
    elif channel == "FAQ":
        topic = analysis.topics[0] if analysis.topics else "esta experiencia"
        title = f"¿Qué aprendimos sobre {topic}?"
        body = f"La evidencia compartida por la comunidad indica: {analysis.evidence[0].excerpt}"
        prompt_version = FAQ_PROMPT_VERSION
    else:
        raise ValueError(f"Unsupported asset channel: {channel}")

    traceable = build_traceable_asset(
        opportunity_id=opportunity_id,
        title=title,
        claims=[body],
        analysis=analysis,
    )
    return GeneratedContent(
        channel=channel,
        title=title,
        body=body,
        prompt_version=prompt_version,
        content=traceable.model_dump(mode="json"),
    )
