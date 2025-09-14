import pytest
from httpx import ASGITransport, AsyncClient

from app import message_service
from app.main import app


@pytest.mark.asyncio
async def test_publish_message_internal_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # Force publish_message to raise an exception
    async def broken_publish_message(*args: object, **kwargs: object) -> None:
        raise RuntimeError("Database is down")

    monkeypatch.setattr(message_service, "publish_message", broken_publish_message)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {"payload": {"msg": "hello"}}
        resp = await ac.post("/channels/test-channel/messages", json=payload)

    assert resp.status_code == 500
    body = resp.json()
    assert body["detail"] == "Internal Server Error"
