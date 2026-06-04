"""Integration tests against live Pepkio Tools API."""

from __future__ import annotations

import os

import pytest

from pepkio_tm_annealing_temperature_calculator.client import PepkioClient
from pepkio_tm_annealing_temperature_calculator.exceptions import PepkioAPIError

ENVIRONMENTS = [
    ("local", "https://tools.localtest.me"),
    ("production", "https://tools.pepkio.com"),
]


def _api_key_for(base_url: str) -> str | None:
    if "localtest.me" in base_url:
        return os.getenv("LOCAL_PEPKIO_API_KEY")
    return os.getenv("PEPKIO_API_KEY")


def _resolve_environments() -> list[tuple[str, str]]:
    override = os.getenv("PEPKIO_API_BASE_URL")
    if override:
        name = "local" if "localtest.me" in override else "production"
        return [(name, override.rstrip("/"))]
    return ENVIRONMENTS


@pytest.fixture(params=_resolve_environments(), ids=lambda p: p[0])
def live_client(request):
    env_name, base_url = request.param
    api_key = _api_key_for(base_url)
    if not api_key:
        pytest.skip(f"No API key for {env_name} (set LOCAL_PEPKIO_API_KEY or PEPKIO_API_KEY)")
    with PepkioClient(api_key=api_key, base_url=base_url) as client:
        try:
            client.get_manifest(refresh=True)
        except PepkioAPIError as exc:
            if exc.status_code == 404 and exc.code == "TOOL_NOT_FOUND":
                pytest.skip(f"Tool not deployed on {env_name} ({base_url})")
            raise
        yield client


def test_get_manifest(live_client: PepkioClient):
    manifest = live_client.get_manifest(refresh=True)
    assert manifest["tool_id"] == "tm-annealing-temperature-calculator"
    names = live_client.list_examples()
    for expected in ("single_q5_pair", "batch_multiplex", "invalid_base_row"):
        assert expected in names


def test_run_single_q5_pair(live_client: PepkioClient):
    inp = live_client.get_example_input("single_q5_pair")
    result = live_client.run(inp)
    assert result.status == "completed"
    assert result.run_id
    assert result.permalink
    assert result.result is not None
    single = result.result.get("single")
    assert isinstance(single, dict)
    assert single.get("tm_fwd", 0) > 50
    assert single.get("status") is not None


def test_run_batch_multiplex(live_client: PepkioClient):
    inp = live_client.get_example_input("batch_multiplex")
    result = live_client.run(inp)
    assert result.status == "completed"
    assert result.result is not None
    batch = result.result.get("batch")
    assert isinstance(batch, list)
    assert len(batch) == 2
    first = batch[0]
    assert isinstance(first, dict)
    assert first.get("tm_fwd", 0) > 50


def test_run_invalid_base_row(live_client: PepkioClient):
    inp = live_client.get_example_input("invalid_base_row")
    result = live_client.run(inp)
    assert result.status == "completed"
    assert result.result is not None
    batch = result.result.get("batch")
    assert isinstance(batch, list)
    assert len(batch) >= 1
    err = batch[0].get("error", "")
    assert "Invalid" in str(err)
