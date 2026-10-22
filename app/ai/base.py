from typing import Protocol
from uuid import UUID

from app.schemas.v1.analysis import Analysis
from app.schemas.v1.interaction import InteractionRequest


class AnalysisProvider(Protocol):
    def analyze(
        self, interaction_id: UUID, interaction: InteractionRequest
    ) -> Analysis: ...

    def generate_linkedin(
        self,
        *,
        topic: str,
        evidence: list[str],
    ) -> tuple[str, str]:
        """Return a freely written, evidence-grounded LinkedIn title and body."""
        ...

    def generate_faq(
        self,
        *,
        topic: str,
        questions: list[str],
        evidence: list[str],
    ) -> tuple[str, str]:
        """Return FAQ drafts with recurring questions and proposed general answers."""
        ...
