import io
import json
import logging
from uuid import uuid4

import pytest

from app.core.observability import JsonFormatter, log_event
from app.schemas.v1.interaction import InteractionRequest
from app.services.resilient_analysis import AnalysisProviderUnavailable, analyze_with_resilience


class FailingProvider:
    def analyze(self, interaction_id, interaction):
        raise RuntimeError(f"provider failed for sensitive text: {interaction.text}")


def _capture(name):
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.disabled = False
    logger.propagate = False
    return logger, handler, stream


def test_json_log_has_stable_structured_fields():
    logger, handler, stream = _capture("communitylab.test")
    try:
        log_event(logger, "operation_completed", duration_ms=12.5, status=200)
        payload = json.loads(stream.getvalue().splitlines()[-1])
        assert payload["event"] == "operation_completed"
        assert payload["level"] == "INFO"
        assert payload["duration_ms"] == 12.5
        assert payload["status"] == 200
        assert payload["timestamp"]
    finally:
        logger.removeHandler(handler)


def test_analysis_retry_logs_metadata_without_sensitive_text():
    logger, handler, stream = _capture("communitylab.analysis")
    secret = "correo privado ana@example.com"
    try:
        with pytest.raises(AnalysisProviderUnavailable):
            analyze_with_resilience(
                provider=FailingProvider(),
                interaction_id=uuid4(),
                interaction=InteractionRequest(
                    author="Ana", channel="test", type="question", text=secret
                ),
                max_attempts=2,
            )
        output = stream.getvalue()
        assert secret not in output
        events = [json.loads(line) for line in output.splitlines()]
        assert [event["attempt"] for event in events] == [1, 2]
        assert all(event["event"] == "analysis_retry" for event in events)
        assert all(event["error_type"] == "RuntimeError" for event in events)
    finally:
        logger.removeHandler(handler)
