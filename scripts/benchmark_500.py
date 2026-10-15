"""Benchmark the synchronous CommunityLab pipeline with its maximum batch."""

from __future__ import annotations

import argparse
import json
import os
from time import perf_counter, sleep, time
from urllib.request import Request, urlopen


def build_payload(count: int, nonce: str) -> dict:
    if not 1 <= count <= 500:
        raise ValueError("count must be between 1 and 500")

    def marker(index: int) -> str:
        """Return a letters-only unique marker that cannot resemble phone PII."""
        value = index
        result = ""
        while True:
            result = chr(ord("a") + value % 26) + result
            value = value // 26 - 1
            if value < 0:
                return result

    nonce_marker = "".join(
        chr(ord("a") + int(character)) if character.isdigit() else character
        for character in nonce.lower()
        if character.isalnum()
    )
    interactions = [
        {
            "external_id": f"benchmark-{nonce}-{index:03d}",
            "author": "benchmark-user",
            "channel": "performance",
            "type": "achievement",
            "text": (
                "Terminé con éxito una integración de Docker, FastAPI y "
                f"PostgreSQL para el marcador {marker(index)} del lote "
                f"{nonce_marker}."
            ),
            "publication_consent": True,
            "opt_out": False,
        }
        for index in range(count)
    ]
    return {
        "schema_version": "v1",
        "organization_id": "benchmark",
        "community_id": "batch-500",
        "reference_period": "performance",
        "requested_assets": ["LINKEDIN"],
        "interactions": interactions,
    }


def validate_result(result: dict, expected_count: int) -> None:
    summary = result.get("summary", {})
    expected = {
        "received": expected_count,
        "accepted": expected_count,
        "duplicates": 0,
        "errors": 0,
    }
    actual = {key: summary.get(key) for key in expected}
    if actual != expected:
        raise RuntimeError(f"Unexpected benchmark summary: {actual!r}")
    for collection in ("analyses", "opportunities", "assets"):
        if len(result.get(collection, [])) != expected_count:
            raise RuntimeError(
                f"Expected {expected_count} {collection}, "
                f"got {len(result.get(collection, []))}"
            )


def run_benchmark(
    api_url: str,
    *,
    count: int,
    max_seconds: float,
    api_key: str | None,
) -> dict:
    nonce = str(int(time() * 1000))
    payload = build_payload(count, nonce)
    headers = {
        "Content-Type": "application/json",
        "Idempotency-Key": f"benchmark-{nonce}",
    }
    if api_key:
        headers["X-API-Key"] = api_key
    request = Request(
        f"{api_url.rstrip('/')}/api/v1/process",
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    started = perf_counter()
    with urlopen(request, timeout=max(120, int(max_seconds * 4))) as response:
        result = json.load(response)
        status = response.status
    wall_seconds = round(perf_counter() - started, 3)
    if status != 202:
        raise RuntimeError(f"Expected HTTP 202, got {status}")
    validate_result(result, count)
    report = {
        "run_id": result["run_id"],
        "count": count,
        "wall_seconds": wall_seconds,
        "api_processing_seconds": round(
            result["summary"]["processing_time_ms"] / 1000,
            3,
        ),
        "target_seconds": max_seconds,
        "target_met": wall_seconds <= max_seconds,
        "analyses": len(result["analyses"]),
        "opportunities": len(result["opportunities"]),
        "assets": len(result["assets"]),
    }
    print(json.dumps(report, indent=2))
    if not report["target_met"]:
        raise RuntimeError(
            f"Batch took {wall_seconds}s, exceeding the {max_seconds}s target; "
            "an asynchronous worker must be evaluated."
        )
    return report


def run_async_benchmark(
    api_url: str,
    *,
    count: int,
    max_enqueue_seconds: float,
    completion_timeout_seconds: float,
    api_key: str | None,
) -> dict:
    nonce = str(int(time() * 1000))
    payload = build_payload(count, nonce)
    headers = {
        "Content-Type": "application/json",
        "Idempotency-Key": f"benchmark-async-{nonce}",
    }
    if api_key:
        headers["X-API-Key"] = api_key
    request = Request(
        f"{api_url.rstrip('/')}/api/v1/process/async",
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    started = perf_counter()
    with urlopen(request, timeout=30) as response:
        job = json.load(response)
        status = response.status
    enqueue_seconds = round(perf_counter() - started, 3)
    if status != 202:
        raise RuntimeError(f"Expected HTTP 202, got {status}")

    deadline = perf_counter() + completion_timeout_seconds
    while perf_counter() < deadline:
        with urlopen(
            f"{api_url.rstrip('/')}{job['status_url']}", timeout=30
        ) as response:
            current = json.load(response)
        if current["status"] == "SUCCEEDED":
            report = {
                "job_id": current["job_id"],
                "run_id": current["run_id"],
                "count": count,
                "enqueue_seconds": enqueue_seconds,
                "completion_seconds": round(perf_counter() - started, 3),
                "target_enqueue_seconds": max_enqueue_seconds,
                "target_met": enqueue_seconds <= max_enqueue_seconds,
                "attempts": current["attempts"],
            }
            print(json.dumps(report, indent=2))
            if not report["target_met"]:
                raise RuntimeError("Asynchronous enqueue exceeded its target")
            return report
        if current["status"] == "FAILED":
            raise RuntimeError(f"Asynchronous job failed: {current['error_type']}")
        sleep(0.5)
    raise TimeoutError("Asynchronous job did not finish before the timeout")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--count", type=int, default=500)
    parser.add_argument("--max-seconds", type=float, default=30)
    parser.add_argument("--async-mode", action="store_true")
    parser.add_argument("--completion-timeout-seconds", type=float, default=180)
    args = parser.parse_args()
    if args.async_mode:
        run_async_benchmark(
            args.api_url,
            count=args.count,
            max_enqueue_seconds=args.max_seconds,
            completion_timeout_seconds=args.completion_timeout_seconds,
            api_key=os.getenv("API_WRITE_KEY"),
        )
    else:
        run_benchmark(
            args.api_url,
            count=args.count,
            max_seconds=args.max_seconds,
            api_key=os.getenv("API_WRITE_KEY"),
        )


if __name__ == "__main__":
    main()
