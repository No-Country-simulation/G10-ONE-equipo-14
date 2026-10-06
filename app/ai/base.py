from typing import Protocol
from uuid import UUID

from app.schemas.v1.analysis import Analysis
from app.schemas.v1.interaction import InteractionRequest


class AnalysisProvider(Protocol):
    def analyze(self, interaction_id: UUID, interaction: InteractionRequest) -> Analysis:
        ...
