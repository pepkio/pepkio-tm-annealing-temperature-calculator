"""Pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest
from dotenv import load_dotenv

# Load monorepo .env for local integration runs (never log keys).
_monorepo_env = Path(__file__).resolve().parents[3] / ".env"
if _monorepo_env.is_file():
    load_dotenv(_monorepo_env, override=True)

_package_env = Path(__file__).resolve().parents[1] / ".env"
if _package_env.is_file():
    load_dotenv(_package_env, override=True)


@pytest.fixture
def mock_manifest() -> dict:
    return {
        "tool_id": "tm-annealing-temperature-calculator",
        "title": "Tm / Annealing Temperature Calculator",
        "execution_mode": "sync",
        "examples": [
            {
                "name": "single_q5_pair",
                "input": {
                    "mode": "single",
                    "name": "test_pair",
                    "fwd_seq": "ATGCGTACGTACGTACGTACG",
                    "rev_seq": "CGTACGTACGTACGTACGCAT",
                    "polymerase_id": "q5",
                    "dmso_percent": 0,
                    "betaine_M": 0,
                },
                "output": {"single": {"status": "go"}},
            },
            {
                "name": "batch_multiplex",
                "input": {
                    "mode": "batch",
                    "polymerase_id": "taq",
                    "batch_csv": (
                        "name,fwd,rev\n"
                        "GAPDH_F,GAAGGTGAAGGTCGGAGTC,GAAGATGGTGATGGGATTTC\n"
                        "ACTB_F,GGCTGGGGTGTTGAAGGT,CCGCTCGTTGTAGACAGG\n"
                    ),
                },
                "output": {"batch": [{"status": "go"}]},
            },
            {
                "name": "invalid_base_row",
                "input": {
                    "mode": "batch",
                    "polymerase_id": "q5",
                    "batch_rows": [
                        {"name": "bad", "fwd_seq": "ATGCX", "rev_seq": "ATGC"},
                    ],
                },
                "output": {"batch": [{"error": "Invalid forward sequence"}]},
            },
        ],
    }


@pytest.fixture
def mock_run_response() -> dict:
    return {
        "run_id": "run_test123",
        "status": "completed",
        "result": {
            "mode": "single",
            "method_used": "santalucia_1998",
            "single": {
                "status": "go",
                "tm_fwd": 62.5,
                "tm_rev": 61.2,
                "suggested_ta": 60.2,
            },
            "warnings": [],
        },
        "error": None,
        "result_url": "https://tools.pepkio.com/api/tools/v1/runs/run_test123",
        "permalink": "https://tools.pepkio.com/r/run_test123",
    }
