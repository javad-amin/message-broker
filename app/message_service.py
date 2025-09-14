import uuid
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Message
from app.repositories import message_repository, receiver_repository
from app.schemas import MessageOut


async def publish_message(session: AsyncSession, channel: str, payload: dict) -> Message:
    max_index = await message_repository.get_max_index(session, channel)
    next_index = 0 if max_index is None else max_index + 1

    db_message = Message(
        id=str(uuid.uuid4()),
        channel=channel,
        index=next_index,
        payload=payload,
    )
    return await message_repository.insert_message(session, db_message)


async def fetch_messages_from_index(
    session: AsyncSession, channel: str, start_index: int, limit: int
) -> List[MessageOut]:
    messages = await message_repository.get_messages_from_index(session, channel, start_index, limit)
    return [MessageOut.model_validate(m.__dict__) for m in messages]


async def fetch_new_messages_for_receiver(
    session: AsyncSession, receiver_id: str, channel: str, limit: int
) -> list[MessageOut]:
    # 1. Load receiver state
    state = await receiver_repository.get_receiver_state(session, receiver_id, channel)
    start_index = (state.last_read_index + 1) if state else 0

    # 2. Fetch messages
    messages = await message_repository.get_messages_from_index(session, channel, start_index, limit)

    # 3. Update receiver state with new "last_read_index"
    if messages:
        last_index = messages[-1].index
        await receiver_repository.upsert_receiver_state(session, receiver_id, channel, last_index)

    return [MessageOut.model_validate(m.__dict__) for m in messages]


async def get_message_by_id(session: AsyncSession, channel: str, message_id: str) -> Message | None:
    return await message_repository.get_message_by_id(session, channel, message_id)
