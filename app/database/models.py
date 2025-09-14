import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    channel: Mapped[str] = mapped_column(index=True, nullable=False)
    index: Mapped[int] = mapped_column(nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    __table_args__ = (UniqueConstraint("channel", "index", name="uq_channel_index"),)


class ReceiverState(Base):
    __tablename__ = "receivers"

    id: Mapped[str] = mapped_column(primary_key=True)
    channel: Mapped[str] = mapped_column(nullable=False)
    last_read_index: Mapped[int] = mapped_column(default=-1, nullable=False)
