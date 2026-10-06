from uuid import UUID
from app.schemas.v1.analysis import Analysis, Evidence
from app.schemas.v1.interaction import InteractionRequest


class MockAnalysisProvider:
    model_name = "mock-analysis-v1"
    prompt_version = "v1"

    def analyze(self, interaction_id: UUID, interaction: InteractionRequest) -> Analysis:
        text = interaction.text.strip()
        lowered = text.lower()
        topics = [x for x in ("docker", "postgresql", "fastapi", "langgraph", "ia") if x in lowered]
        positive = ("gracias", "logré", "conseguí", "terminé")
        sentiment = "positive" if any(x in lowered for x in positive) else "neutral"

        return Analysis(
            interaction_id=interaction_id,
            sentiment=sentiment,
            topics=topics,
            entities=[],
            relevance=1.0,
            confidence=1.0,
            evidence=[Evidence(source_interaction_id=interaction_id, excerpt=text[:240])],
            model=self.model_name,
            prompt_version=self.prompt_version,
        )
