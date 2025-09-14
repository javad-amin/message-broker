from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Message


async def get_max_index(session: AsyncSession, channel: str) -> int | None:
    result = await session.execute(select(func.max(Message.index)).where(Message.channel == channel))
    return result.scalar()


async def insert_message(session: AsyncSession, message: Message) -> Message:
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


async def get_messages_from_index(session: AsyncSession, channel: str, start_index: int, limit: int) -> List[Message]:
    stmt = (
        select(Message)
        .where(Message.channel == channel, Message.index >= start_index)
        .order_by(Message.index)
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_message_by_id(session: AsyncSession, channel: str, message_id: str) -> Message | None:
    stmt = select(Message).where(Message.channel == channel, Message.id == message_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
