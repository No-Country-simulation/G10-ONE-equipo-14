"""Deterministic, channel-specific content generation for the MVP."""

from dataclasses import dataclass
from uuid import UUID

from app.schemas.v1.analysis import Analysis
from app.services.asset_generation import build_traceable_asset


LINKEDIN_PROMPT_VERSION = "linkedin-v1"
FAQ_PROMPT_VERSION = "faq-v1"

#---------------------------------------------------------------------------------------------------------------------------------------------
# COMLAB-40: Rangos de longitud del copy de LinkedIn. Borrador demasiado corto no se publica; borrador demasiado largo dificulta la curaduría.
#---------------------------------------------------------------------------------------------------------------------------------------------
LINKEDIN_MIN_LENGTH = 80
LINKEDIN_MAX_LENGTH = 3000

#---------------------------------------------------------------------------------------------------------------------------------------------
# COMLAB-41: Rangos de longitud de la respuesta FAQ. La pregunta va en el título; el cuerpo debe ser didáctico y acotado.
#---------------------------------------------------------------------------------------------------------------------------------------------
FAQ_MIN_LENGTH = 40
FAQ_MAX_LENGTH = 2000


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
#--------------------------
# COMLAB-40 y COMLAB-41: Validación temprana de evidencia
#-----------------------------------
    if not analysis.evidence:
        raise ValueError(
            "Cannot generate content without analysis evidence."
        )

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

#------------------------------------------------------------------------------------------------------------------------------------------------
# COMLAB 40 y COMLAB 41: Validación específica por canal.
# El contenido generado (post LinkedIn o FAQ) debe cumplir el criterio de aceptación. Si no lo cumple se rechaza antes de devolverlo al pipeline.
#------------------------------------------------------------------------------------------------------------------------------------------------
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


#---------------------------------------------------------------------------------------------------------------------------------------------
# COMLAB 40 y COMLAB 41: Validaciones específicas por canal.
#---------------------------------------------------------------------------------------------------------------------------------------------
def _validate_channel_output(
    *,
    channel: str,
    title: str,
    body: str,
    traceable,
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

    # Criterio común a E4-S02 y E4-S03: Evidencia vinculada.
    if not traceable.claims:
        raise ValueError(f"{channel}: at least one claim with evidence is required")
    for claim in traceable.claims:
        if not claim.source_interaction_ids:
            raise ValueError(
                f"{channel}: every claim must declare source_interaction_ids"
            )
        if not claim.evidence:
            raise ValueError(
                f"{channel}: every claim must include evidence"
            )

    if channel == "LINKEDIN":
        # E4-S02: copy adaptado a LinkedIn (longitud razonable).
        if not (LINKEDIN_MIN_LENGTH <= len(body) <= LINKEDIN_MAX_LENGTH):
            raise ValueError(
                f"LINKEDIN: body length {len(body)} out of range "
                f"[{LINKEDIN_MIN_LENGTH}, {LINKEDIN_MAX_LENGTH}]"
            )

    elif channel == "FAQ":
        # E4-S03: La FAQ se formula como pregunta.
        if not title.strip().endswith("?"):
            raise ValueError("FAQ: title must be phrased as a question")
        # E4-S03: la respuesta debe ser didáctica y acotada.
        if not (FAQ_MIN_LENGTH <= len(body) <= FAQ_MAX_LENGTH):
            raise ValueError(
                f"FAQ: body length {len(body)} out of range "
                f"[{FAQ_MIN_LENGTH}, {FAQ_MAX_LENGTH}]"
            )