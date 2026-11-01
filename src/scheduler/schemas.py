import uuid
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from scheduler.cron import InvalidCronError, validate_cron


class JobCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    cron_expression: str = Field(max_length=100)
    payload: Optional[dict[str, Any]] = None
    catch_up_policy: Literal["SKIP", "CATCH_UP"] = "SKIP"
    max_retries: int = Field(default=3, ge=0, le=10)

    @field_validator("name")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name must not be blank")
        return v

    @field_validator("cron_expression")
    @classmethod
    def _valid_cron(cls, v: str) -> str:
        try:
            return validate_cron(v)
        except InvalidCronError as exc:
            raise ValueError(str(exc)) from None


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    cron_expression: str
    payload: Optional[dict[str, Any]]
    is_active: bool
    catch_up_policy: str
    max_retries: int
    next_run_time: Optional[datetime]
    created_at: datetime
