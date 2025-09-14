import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_receiver_first_fetch_gets_all_messages() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post("/channels/general/messages", json={"payload": {"msg": "hello"}})
        await ac.post("/channels/general/messages", json={"payload": {"msg": "world"}})

        resp = await ac.get("/channels/general/messages/receiver1/new")
        assert resp.status_code == 200
        messages = resp.json()

    assert [m["payload"]["msg"] for m in messages] == ["hello", "world"]


@pytest.mark.asyncio
async def test_receiver_second_fetch_only_gets_new_messages() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post("/channels/general/messages", json={"payload": {"msg": "first"}})

        # consume first
        await ac.get("/channels/general/messages/receiver2/new")

        # publish another
        await ac.post("/channels/general/messages", json={"payload": {"msg": "second"}})

        resp = await ac.get("/channels/general/messages/receiver2/new")
        messages = resp.json()

    assert [m["payload"]["msg"] for m in messages] == ["second"]


@pytest.mark.asyncio
async def test_receiver_fetch_with_no_new_messages_returns_empty_list() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post("/channels/general/messages", json={"payload": {"msg": "only"}})
        # consume
        await ac.get("/channels/general/messages/receiver3/new")

        # no new messages published
        resp = await ac.get("/channels/general/messages/receiver3/new")
        assert resp.status_code == 200
        messages = resp.json()

    assert messages == []


@pytest.mark.asyncio
async def test_receiver_fetch_newer_after_multiple_writes() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post("/channels/general/messages", json={"payload": {"msg": "m1"}})
        await ac.post("/channels/general/messages", json={"payload": {"msg": "m2"}})
        await ac.get("/channels/general/messages/receiver4/new")  # consumes both

        # publish 2 more
        await ac.post("/channels/general/messages", json={"payload": {"msg": "m3"}})
        await ac.post("/channels/general/messages", json={"payload": {"msg": "m4"}})

        resp = await ac.get("/channels/general/messages/receiver4/new")
        messages = resp.json()

    assert [m["payload"]["msg"] for m in messages] == ["m3", "m4"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "from_index,limit,expected",
    [
        (1, 2, ["two", "three"]),  # normal subset
        (10, 5, []),  # from_index beyond last
        (0, 10, ["one", "two", "three"]),  # limit bigger than available
    ],
)
async def test_fetch_messages_with_from_index_and_limit(from_index: int, limit: int, expected: list[str]) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Reset channel with known data
        await ac.post("/channels/general/messages", json={"payload": {"msg": "one"}})
        await ac.post("/channels/general/messages", json={"payload": {"msg": "two"}})
        await ac.post("/channels/general/messages", json={"payload": {"msg": "three"}})

        resp = await ac.get(f"/channels/general/messages?from_index={from_index}&limit={limit}")
        messages = resp.json()

    assert [m["payload"]["msg"] for m in messages] == expected


@pytest.mark.asyncio
async def test_get_message_by_id_existing_message() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # first publish a message
        payload = {"payload": {"msg": "hello"}}
        post_resp = await ac.post("/channels/test/messages", json=payload)
        assert post_resp.status_code == 201
        message_id = post_resp.json()["id"]

        # fetch that same message
        get_resp = await ac.get(f"/channels/test/messages/{message_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == message_id
        assert get_resp.json()["payload"] == {"msg": "hello"}


@pytest.mark.asyncio
async def test_get_message_by_id_not_found() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # try to fetch a non-existing message
        resp = await ac.get("/channels/test/messages/nonexistent-id")
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"]
