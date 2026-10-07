from uuid import UUID
from app.ai.base import AnalysisProvider
from app.schemas.v1.analysis import Analysis
from app.schemas.v1.interaction import InteractionRequest


def analyze_interaction(
    provider: AnalysisProvider,
    interaction_id: UUID,
    interaction: InteractionRequest,
) -> Analysis:
    result = provider.analyze(interaction_id=interaction_id, interaction=interaction)
    return Analysis.model_validate(result)
