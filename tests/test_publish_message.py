import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {"payload": {"key": "value"}},
        {"payload": {"nested": {"a": 1, "b": [1, 2, 3]}}},
        {"payload": {"empty_str": ""}},
        {"payload": {"bool": True, "none": None}},
    ],
)
async def test_publish_message_valid_payloads(payload: dict) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/channels/my-channel/messages", json=payload)

    assert resp.status_code == 201
    body = resp.json()
    assert body["channel"] == "my-channel"
    assert body["payload"] == payload["payload"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "json_body,expected_msg",
    [
        ({"payload": "hello"}, "Input should be a valid dictionary"),
        ({"payload": {}}, "Value error, Payload must not be empty"),
        ({}, "Field required"),
    ],
)
async def test_publish_message_invalid_payloads(json_body: dict, expected_msg: str) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/channels/my-channel/messages", json=json_body)

    assert resp.status_code == 422
    body = resp.json()
    # We don't care about exact location details, just that the right message is in there
    assert any(expected_msg in d["msg"] for d in body["detail"])


@pytest.mark.asyncio
async def test_publish_message_invalid_json() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post(
            "/channels/my-channel/messages",
            content="not-json",
            headers={"Content-Type": "application/json"},
        )

    assert resp.status_code == 422
    assert resp.json()["detail"][0]["msg"] == "JSON decode error"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "channel,expected_detail",
    [
        (
            "invalid channel!",
            "Channel name may only contain letters, numbers, underscores, and hyphens",
        ),
        (
            "a",
            "Channel name must be between 3 and 100 characters",
        ),
        (
            "a" * 101,
            "Channel name must be between 3 and 100 characters",
        ),
    ],
)
async def test_publish_message_invalid_channel_names(channel: str, expected_detail: str) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {"payload": {"msg": "hello"}}
        resp = await ac.post(f"/channels/{channel}/messages", json=payload)

    assert resp.status_code == 422
    assert resp.json()["detail"] == expected_detail


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "channel",
    [
        "general",
        "room-123_",
        "a" * 100,
    ],
)
async def test_publish_message_valid_channel_names(channel: str) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {"payload": {"msg": "hello"}}
        resp = await ac.post(f"/channels/{channel}/messages", json=payload)

    assert resp.status_code == 201
    body = resp.json()
    assert body["channel"] == channel
    assert body["payload"] == payload["payload"]
