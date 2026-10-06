from uuid import UUID

from app.schemas.v1.analysis import Analysis, Evidence
from app.schemas.v1.interaction import InteractionRequest


class MockAnalysisProvider:
    """Deterministic provider for tests and local development."""

    model_name = "mock-analysis-v1"
    prompt_version = "v1"

    TOPIC_KEYWORDS = {
        "docker": ("docker", "docker compose", "container"),
        "postgresql": ("postgresql", "postgres", "database"),
        "fastapi": ("fastapi", "api"),
        "langgraph": ("langgraph",),
        "artificial_intelligence": (
            "inteligencia artificial",
            " ia ",
            "ai",
            "llm",
            "modelo",
        ),
    }

    ENTITY_KEYWORDS = {
        "Docker": ("docker", "docker compose"),
        "PostgreSQL": ("postgresql", "postgres"),
        "FastAPI": ("fastapi",),
        "LangGraph": ("langgraph",),
        "LLM": ("llm",),
    }

    POSITIVE_KEYWORDS = (
        "gracias",
        "logré",
        "conseguí",
        "terminé",
        "éxito",
        "excelente",
        "ayudó",
    )

    NEGATIVE_KEYWORDS = (
        "problema",
        "problemas",
        "error",
        "falla",
        "falló",
        "difícil",
        "cuesta",
    )

    def analyze(
        self,
        interaction_id: UUID,
        interaction: InteractionRequest,
    ) -> Analysis:
        text = interaction.text.strip()
        lowered = f" {text.lower()} "

        topics = self._detect_topics(lowered)
        entities = self._detect_entities(lowered)
        sentiment = self._detect_sentiment(lowered)

        relevance = self._calculate_relevance(
            topics=topics,
            entities=entities,
        )

        confidence = self._calculate_confidence(
            topics=topics,
            entities=entities,
        )

        return Analysis(
            interaction_id=interaction_id,
            sentiment=sentiment,
            topics=topics,
            entities=entities,
            relevance=relevance,
            confidence=confidence,
            evidence=[
                Evidence(
                    source_interaction_id=interaction_id,
                    excerpt=text[:240],
                )
            ],
            model=self.model_name,
            prompt_version=self.prompt_version,
        )

    def _detect_topics(self, text: str) -> list[str]:
        return [
            topic
            for topic, keywords in self.TOPIC_KEYWORDS.items()
            if any(keyword in text for keyword in keywords)
        ]

    def _detect_entities(self, text: str) -> list[str]:
        return [
            entity
            for entity, keywords in self.ENTITY_KEYWORDS.items()
            if any(keyword in text for keyword in keywords)
        ]

    def _detect_sentiment(self, text: str) -> str:
        positive = sum(
            keyword in text
            for keyword in self.POSITIVE_KEYWORDS
        )

        negative = sum(
            keyword in text
            for keyword in self.NEGATIVE_KEYWORDS
        )

        if positive > negative:
            return "positive"

        if negative > positive:
            return "negative"

        return "neutral"

    def _calculate_relevance(
        self,
        topics: list[str],
        entities: list[str],
    ) -> float:
        if topics and entities:
            return 1.0

        if topics or entities:
            return 0.75

        return 0.5

    def _calculate_confidence(
        self,
        topics: list[str],
        entities: list[str],
    ) -> float:
        signals = len(topics) + len(entities)

        if signals >= 4:
            return 1.0

        if signals >= 2:
            return 0.9

        if signals == 1:
            return 0.75

        return 0.5
