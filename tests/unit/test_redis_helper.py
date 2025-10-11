import pytest
from services.redis.redis_helper import RedisHelper

pytestmark = pytest.mark.unit


def test_single_client() -> None:
    redis_helper = RedisHelper(
        url="redis://",
        encoding="utf-8",
        decode_responses=True,
    )
    expected_pool = redis_helper.pool
    client_1 = redis_helper.redis_client()
    client_2 = redis_helper.redis_client()
    expected_client = redis_helper._client
    client_1_pool = client_1.connection_pool
    client_2_pool = client_2.connection_pool

    assert client_1_pool == expected_pool
    assert client_2_pool == expected_pool
    assert client_2_pool == client_1_pool
    assert client_1 == expected_client
    assert client_2 == expected_client
    assert client_2 == client_1
