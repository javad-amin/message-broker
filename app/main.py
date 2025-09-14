from contextlib import asynccontextmanager
from typing import AsyncGenerator, List

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app import message_service
from app.database.db import AsyncSessionLocal, Base, engine
from app.schemas import MessageIn, MessageOut
from app.validation import validate_channel_name


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


@app.post("/channels/{channel}/messages", response_model=MessageOut, status_code=201)
async def publish_message_endpoint(
    channel: str,
    message: MessageIn,
    session: AsyncSession = Depends(get_session),
) -> MessageOut:
    validate_channel_name(channel)
    try:
        return await message_service.publish_message(session, channel, message.payload)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/channels/{channel}/messages/{receiver_id}/new", response_model=List[MessageOut])
async def get_new_messages_for_receiver_endpoint(
    channel: str,
    receiver_id: str,
    limit: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> List[MessageOut]:
    validate_channel_name(channel)
    try:
        return await message_service.fetch_new_messages_for_receiver(session, receiver_id, channel, limit)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/channels/{channel}/messages", response_model=List[MessageOut])
async def get_messages_from_index_endpoint(
    channel: str,
    from_index: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> List[MessageOut]:
    validate_channel_name(channel)
    try:
        return await message_service.fetch_messages_from_index(session, channel, from_index, limit)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/channels/{channel}/messages/{message_id}", response_model=MessageOut)
async def get_message_by_id_endpoint(
    channel: str,
    message_id: str,
    session: AsyncSession = Depends(get_session),
) -> MessageOut:
    validate_channel_name(channel)
    try:
        message = await message_service.get_message_by_id(session, channel, message_id)
        if not message:
            raise HTTPException(
                status_code=404,
                detail=f"Message '{message_id}' not found in channel '{channel}'",
            )
        return message
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
