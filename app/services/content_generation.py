"""Channel-specific content generation and validation for the MVP."""

from dataclasses import dataclass
from uuid import UUID

from app.ai.base import AnalysisProvider
from app.ai.provider_factory import (
    configured_analysis_provider,
    configured_fallback_provider,
)
from app.schemas.v1.analysis import Analysis
from app.schemas.v1.traceable_asset import TraceableAsset
from app.services.asset_generation import build_traceable_asset
from app.services.pii_detection import redact_pii


LINKEDIN_PROMPT_VERSION = "linkedin-v4"
FAQ_PROMPT_VERSION = "faq-v2"

# Keep LinkedIn drafts within the channel's supported character range.
LINKEDIN_MIN_LENGTH = 80
LINKEDIN_MAX_LENGTH = 3000

# COMLAB-41: rango permitido para una respuesta FAQ didáctica y acotada.
FAQ_MIN_LENGTH = 40
FAQ_MAX_LENGTH = 2000


class ContentProviderUnavailable(RuntimeError):
    """Raised when the configured provider cannot generate channel content."""


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
    provider: AnalysisProvider | None = None,
    fallback: AnalysisProvider | None = None,
    questions: list[str] | None = None,
    draft: tuple[str, str] | None = None,
) -> GeneratedContent:
    # COMLAB-40/41: ambos canales requieren evidencia desde el comienzo.
    if not analysis.evidence:
        raise ValueError("Cannot generate content without analysis evidence.")

    if channel == "LINKEDIN":
        topic = _display_topic(analysis)
        if draft is None:
            content_provider = provider or configured_analysis_provider()
            fallback_provider = fallback or configured_fallback_provider()
            evidence = [item.excerpt for item in analysis.evidence]
            title, body = _generate_linkedin_with_fallback(
                content_provider=content_provider,
                fallback_provider=fallback_provider,
                topic=topic,
                evidence=evidence,
            )
        else:
            title, body = draft
        title = redact_pii(title)
        body = redact_pii(body)
        prompt_version = LINKEDIN_PROMPT_VERSION
    elif channel == "FAQ":
        topic = _display_topic(analysis)
        if draft is None:
            content_provider = provider or configured_analysis_provider()
            fallback_provider = fallback or configured_fallback_provider()
            question_list = questions or [item.excerpt for item in analysis.evidence]
            title, body = _generate_faq_with_fallback(
                content_provider=content_provider,
                fallback_provider=fallback_provider,
                topic=topic,
                questions=question_list,
                evidence=[item.excerpt for item in analysis.evidence],
            )
        else:
            title, body = draft
        title = redact_pii(title)
        body = redact_pii(body)
        prompt_version = FAQ_PROMPT_VERSION
    else:
        raise ValueError(f"Unsupported asset channel: {channel}")

    traceable = build_traceable_asset(
        opportunity_id=opportunity_id,
        title=title,
        claims=[body],
        analysis=analysis,
    )

    # Rechazar antes de devolver al pipeline si el contenido no cumple el canal.
    _validate_channel_output(
        channel=channel,
        title=title,
        body=body,
        traceable=traceable,
    )

    return GeneratedContent(
        channel=channel,
        title=title,
        body=body,
        prompt_version=prompt_version,
        content=traceable.model_dump(mode="json"),
    )


def _generate_linkedin_with_fallback(
    *,
    content_provider: AnalysisProvider,
    fallback_provider: AnalysisProvider | None,
    topic: str,
    evidence: list[str],
) -> tuple[str, str]:
    try:
        return content_provider.generate_linkedin(
            topic=topic,
            evidence=evidence,
        )
    except Exception as primary_error:
        if fallback_provider is None or fallback_provider is content_provider:
            raise ContentProviderUnavailable(
                "The configured content provider is unavailable."
            ) from primary_error
        try:
            return fallback_provider.generate_linkedin(
                topic=topic,
                evidence=evidence,
            )
        except Exception as fallback_error:
            raise ContentProviderUnavailable(
                "The configured content provider and fallback are unavailable."
            ) from fallback_error


def _generate_faq_with_fallback(
    *,
    content_provider: AnalysisProvider,
    fallback_provider: AnalysisProvider | None,
    topic: str,
    questions: list[str],
    evidence: list[str],
) -> tuple[str, str]:
    try:
        return content_provider.generate_faq(
            topic=topic,
            questions=questions,
            evidence=evidence,
        )
    except Exception as primary_error:
        if fallback_provider is None or fallback_provider is content_provider:
            raise ContentProviderUnavailable(
                "The configured content provider is unavailable."
            ) from primary_error
        try:
            return fallback_provider.generate_faq(
                topic=topic,
                questions=questions,
                evidence=evidence,
            )
        except Exception as fallback_error:
            raise ContentProviderUnavailable(
                "The configured content provider and fallback are unavailable."
            ) from fallback_error


def _validate_channel_output(
    *,
    channel: str,
    title: str,
    body: str,
    traceable: TraceableAsset,
) -> None:
    """Verify channel-specific acceptance criteria from the roadmap.

    E4-S02 (LinkedIn): "produce borrador adaptado a LinkedIn con
    evidencia vinculada".

    E4-S03 (FAQ): "produce pregunta/respuesta útil con evidencia
    vinculada".
    """
    if not title or not title.strip():
        raise ValueError(f"{channel}: title must be non-empty")
    if not body or not body.strip():
        raise ValueError(f"{channel}: body must be non-empty")

    if channel == "LINKEDIN" and not (
        LINKEDIN_MIN_LENGTH <= len(body) <= LINKEDIN_MAX_LENGTH
    ):
        raise ValueError(
            f"LINKEDIN: body length {len(body)} out of range "
            f"[{LINKEDIN_MIN_LENGTH}, {LINKEDIN_MAX_LENGTH}]"
        )

    # Criterio común a E4-S02 y E4-S03: Evidencia vinculada.
    if not traceable.claims:
        raise ValueError(f"{channel}: at least one claim with evidence is required")
    for claim in traceable.claims:
        if not claim.source_interaction_ids:
            raise ValueError(
                f"{channel}: every claim must declare source_interaction_ids"
            )
        if not claim.evidence:
            raise ValueError(f"{channel}: every claim must include evidence")

    if channel == "FAQ":
        # FAQ responses should remain concise and educational.
        if not (FAQ_MIN_LENGTH <= len(body) <= FAQ_MAX_LENGTH):
            raise ValueError(
                f"FAQ: body length {len(body)} out of range "
                f"[{FAQ_MIN_LENGTH}, {FAQ_MAX_LENGTH}]"
            )


def _display_topic(analysis: Analysis) -> str:
    if analysis.topics:
        return analysis.topics[0].replace("_", " ")
    if analysis.entities:
        return analysis.entities[0]
    return "aprendizaje"
