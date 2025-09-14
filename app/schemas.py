from typing import Any

from pydantic import BaseModel, Field, field_validator


class MessageIn(BaseModel):
    payload: dict[str, Any] = Field(
        ...,
        description="Message payload (must be non-empty)",
        examples=[{"msg": "hello world"}],
    )

    @field_validator("payload")
    @classmethod
    def payload_must_not_be_empty(cls, v: dict[str, Any]) -> dict[str, Any]:
        if not v:
            raise ValueError("Payload must not be empty")
        return v


class MessageOut(MessageIn):
    id: str
    channel: str
    index: int
