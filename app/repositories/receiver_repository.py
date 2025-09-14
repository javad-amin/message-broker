from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import ReceiverState


async def get_receiver_state(session: AsyncSession, receiver_id: str, channel: str) -> ReceiverState | None:
    result = await session.execute(
        select(ReceiverState).where(
            ReceiverState.id == receiver_id,
            ReceiverState.channel == channel,
        )
    )
    return result.scalar_one_or_none()


async def upsert_receiver_state(
    session: AsyncSession, receiver_id: str, channel: str, last_read_index: int
) -> ReceiverState:
    state = await get_receiver_state(session, receiver_id, channel)
    if state is None:
        state = ReceiverState(id=receiver_id, channel=channel, last_read_index=last_read_index)
        session.add(state)
    else:
        state.last_read_index = last_read_index

    await session.commit()
    await session.refresh(state)
    return state
