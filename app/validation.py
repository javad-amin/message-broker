# app/validation.py
import re

from fastapi import HTTPException

CHANNEL_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")
CHANNEL_NAME_MIN_LENGTH = 3
CHANNEL_NAME_MAX_LENGTH = 100


def validate_channel_name(channel: str) -> str:
    if not (CHANNEL_NAME_MIN_LENGTH <= len(channel) <= CHANNEL_NAME_MAX_LENGTH):
        raise HTTPException(
            status_code=422,
            detail=f"Channel name must be between {CHANNEL_NAME_MIN_LENGTH} and {CHANNEL_NAME_MAX_LENGTH} characters",
        )

    if not CHANNEL_NAME_PATTERN.match(channel):
        raise HTTPException(
            status_code=422,
            detail="Channel name may only contain letters, numbers, underscores, and hyphens",
        )

    return channel
