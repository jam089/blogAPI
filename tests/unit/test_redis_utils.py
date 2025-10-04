import json
from typing import Any

import pytest
from pydantic import BaseModel
from pytest_mock import MockerFixture
from services.redis import redis_cache


class DummyModel(BaseModel):
    id: int
    name: str


@pytest.mark.asyncio
async def test_redis_cache_docorator_get_cached(mocker: MockerFixture) -> None:
    fake_cache = mocker.AsyncMock()
    fake_cache.get.return_value = DummyModel(id=1, name="cached").model_dump_json()
    mocker.patch(
        "services.redis.redis_helper.r_cache.redis_client", return_value=fake_cache
    )

    @redis_cache(DummyModel)
    async def victim_func() -> DummyModel:
        return DummyModel(id=2, name="new")

    result = await victim_func()

    assert result == DummyModel(id=1, name="cached")
    fake_cache.get.assert_awaited_once()
    fake_cache.set.assert_not_awaited()


@pytest.mark.asyncio
async def test_redis_cache_docorator_set_cache(mocker: MockerFixture) -> None:
    fake_cache = mocker.AsyncMock()
    fake_cache.get.return_value = None
    mocker.patch(
        "services.redis.redis_helper.r_cache.redis_client", return_value=fake_cache
    )

    @redis_cache(DummyModel)
    async def victim_func() -> DummyModel:
        return DummyModel(id=2, name="new")

    result = await victim_func()

    assert result == DummyModel(id=2, name="new")
    fake_cache.set.assert_awaited_once()
    key, value, *_ = fake_cache.set.call_args[0]
    assert key == "victim_func"
    value_dict: dict[str, Any] = json.loads(value)
    assert value_dict.get("id") == 2


@pytest.mark.asyncio
async def test_redis_cache_chack_inactive_flg_by_return_value_active(
    mocker: MockerFixture,
) -> None:
    fake_cache = mocker.AsyncMock()
    mocker.patch(
        "services.redis.redis_helper.r_cache.redis_client", return_value=fake_cache
    )

    @redis_cache(DummyModel, inactive=True)
    async def victim_func() -> DummyModel:
        return DummyModel(id=4, name="inactive")

    result = await victim_func()

    assert result == DummyModel(id=4, name="inactive")
    fake_cache.get.assert_not_awaited()
    fake_cache.set.assert_not_awaited()


@pytest.mark.asyncio
async def test_redis_cache_chack_inactive_flg_by_func_signature_inactive() -> None:
    async def victim_func() -> DummyModel:
        return DummyModel(id=4, name="inactive")

    decorated = redis_cache(DummyModel, inactive=False)(victim_func)

    assert decorated is not victim_func


@pytest.mark.asyncio
async def test_redis_cache_chack_inactive_flg_by_func_signature_active() -> None:
    async def victim_func() -> DummyModel:
        return DummyModel(id=4, name="inactive")

    decorated = redis_cache(DummyModel, inactive=True)(victim_func)

    assert decorated is victim_func
