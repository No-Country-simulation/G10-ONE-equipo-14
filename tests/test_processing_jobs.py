from copy import deepcopy

from sqlalchemy.orm import sessionmaker

from app.db.models.processing_job import ProcessingJob
from app.db.models.run import Run
from app.workers.processing_worker import process_next_job


PAYLOAD = {
    "organization_id": "one",
    "community_id": "async-test",
    "reference_period": "2026-W42",
    "requested_assets": ["LINKEDIN"],
    "interactions": [
        {
            "external_id": "async-1",
            "author": "Ana",
            "channel": "community",
            "type": "achievement",
            "text": "Completé el curso y conseguí mi primer empleo.",
            "publication_consent": True,
            "opt_out": False,
        }
    ],
}


def test_enqueue_replay_status_and_worker(client, db_session):
    session_factory = sessionmaker(bind=db_session.get_bind(), expire_on_commit=False)
    headers = {"Idempotency-Key": "async-stable"}
    first = client.post("/api/v1/process/async", json=PAYLOAD, headers=headers)
    replay = client.post("/api/v1/process/async", json=PAYLOAD, headers=headers)

    assert first.status_code == 202
    assert replay.status_code == 202
    assert first.json()["job_id"] == replay.json()["job_id"]
    assert first.json()["status"] == "QUEUED"

    assert process_next_job(session_factory) is True
    db_session.expire_all()

    status_response = client.get(first.json()["status_url"])
    assert status_response.status_code == 200
    result = status_response.json()
    assert result["status"] == "SUCCEEDED"
    assert result["attempts"] == 1
    assert result["run_id"] is not None
    assert db_session.get(Run, result["run_id"]).status == "ACCEPTED"
    assert process_next_job(session_factory) is False


def test_enqueue_rejects_same_key_with_different_payload(client):
    headers = {"Idempotency-Key": "async-conflict"}
    assert (
        client.post("/api/v1/process/async", json=PAYLOAD, headers=headers).status_code
        == 202
    )
    changed = deepcopy(PAYLOAD)
    changed["reference_period"] = "different"

    response = client.post("/api/v1/process/async", json=changed, headers=headers)

    assert response.status_code == 409


def test_unknown_job_returns_404(client):
    response = client.get("/api/v1/jobs/00000000-0000-0000-0000-000000000001")
    assert response.status_code == 404


def test_worker_marks_invalid_payload_failed(db_session):
    session_factory = sessionmaker(bind=db_session.get_bind(), expire_on_commit=False)
    job = ProcessingJob(
        organization_id="one",
        community_id="invalid",
        idempotency_key="invalid-payload",
        request_hash="a" * 64,
        request_json={"invalid": True},
    )
    db_session.add(job)
    db_session.commit()
    job_id = job.id

    assert process_next_job(session_factory) is True
    db_session.expire_all()
    failed = db_session.get(ProcessingJob, job_id)
    assert failed.status == "FAILED"
    assert failed.error_type == "ValidationError"
    assert failed.finished_at is not None
