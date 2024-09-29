from functools import wraps
from typing import Awaitable, Callable, Any, Type, Sequence, get_args

from pydantic import TypeAdapter

from core import r_cache, settings


def redis_cache(
    model_type: Type,
    expire: int | None = settings.cache.resp.expire,
    inactive: bool = settings.cache.resp.inactive,
):
    def decorator(func: Callable[..., Awaitable[Any]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with r_cache.rclient_getter() as cache:
                func_name = func.__name__
                type_adapter = TypeAdapter(model_type)

                if cached_response := await cache.get(func_name):
                    decoded_response = type_adapter.validate_json(cached_response)
                    return decoded_response

                response = await func(*args, **kwargs)
                if isinstance(response, Sequence) and not isinstance(response, str):
                    sub_type: Any = get_args(model_type)[0]
                    schm = [sub_type.model_validate(db_model) for db_model in response]
                encoded = type_adapter.dump_json(schm).decode("utf-8")
                await cache.set(func_name, encoded, ex=expire)
            return response

        if inactive:
            return func
        return wrapper

    return decorator
