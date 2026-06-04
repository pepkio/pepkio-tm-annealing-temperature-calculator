"""Typed API request/response models (from manifest input/output schemas)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .exceptions import PepkioAPIError


class RunOptions(BaseModel):
    """Optional fields for POST .../run."""

    idempotency_key: str | None = None
    label: str | None = None


class TmAnnealingToolInput(BaseModel):
    """Tool input (manifest: mode and polymerase_id required)."""

    model_config = ConfigDict(extra="allow")

    mode: str = Field(..., description="single or batch")
    polymerase_id: str = Field(
        ...,
        description="q5 | phusion | taq | kapa_hifi | custom",
    )


class TmAnnealingSingleResult(BaseModel):
    """Single-mode result row (manifest output.single)."""

    model_config = ConfigDict(extra="allow")

    status: str | None = None
    tm_fwd: float | None = None
    tm_rev: float | None = None
    suggested_ta: float | None = None
    error: str | None = None


class TmAnnealingBatchRow(BaseModel):
    """Batch-mode result row (manifest output.batch items)."""

    model_config = ConfigDict(extra="allow")

    status: str | None = None
    tm_fwd: float | None = None
    tm_rev: float | None = None
    suggested_ta: float | None = None
    error: str | None = None


class TmAnnealingToolOutput(BaseModel):
    """Tool handler output shape (from manifest output schema)."""

    model_config = ConfigDict(extra="allow")

    mode: str | None = None
    method_used: str | None = None
    warnings: list[Any] | None = None
    metadata: dict[str, Any] | None = None
    corrections_applied: dict[str, Any] | None = None
    single: dict[str, Any] | TmAnnealingSingleResult | None = None
    batch: list[Any] | None = None
    error: str | None = None


class RunResult(BaseModel):
    """Tool run response envelope."""

    model_config = ConfigDict(extra="allow")

    run_id: str
    status: str
    result: dict[str, Any] | None = None
    error: dict[str, Any] | None = None
    result_url: str | None = None
    permalink: str | None = None
    duration_ms: int | None = None

    def raise_for_error(self) -> None:
        """Raise PepkioAPIError if the run response includes an error field."""
        if self.error is None:
            return
        err = self.error
        raise PepkioAPIError(
            err.get("message", "Tool run failed"),
            code=err.get("code"),
            details=err.get("details") if isinstance(err.get("details"), dict) else {},
            response_body={"run_id": self.run_id, "status": self.status, "error": self.error},
        )


def parse_run_response(data: dict[str, Any]) -> RunResult:
    """Parse a run API JSON body into RunResult."""
    return RunResult.model_validate(data)
