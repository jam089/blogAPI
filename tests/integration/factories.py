from collections.abc import Callable
from typing import (
    Any,
    Awaitable,
    Type,
    TypeVar,
    cast,
)

import factory
import pytest
from core.models import Article, Comment
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

T = TypeVar("T", bound=factory.alchemy.SQLAlchemyModelFactory)


class ArticleFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Article
        sqlalchemy_session_persistence = "flush"

    title = factory.Faker("sentence")
    text = factory.Faker("text")
    topic = factory.Faker("word")
    author_name = factory.Faker("user_name")
    import_article_id = None


class CommentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Comment
        sqlalchemy_session_persistence = "flush"

    author_name = factory.Faker("user_name")
    comment_text = factory.Faker("paragraph", nb_sentences=4)
    score = factory.Faker("random_int", min=2, max=10)
    article = factory.SubFactory(ArticleFactory)


@pytest.fixture(scope="function")
def create_from_factory(
    create_test_session_factory: async_sessionmaker[AsyncSession],
) -> Callable[..., Awaitable[T]]:
    async def _create(
        factory_class: Type[T],
        **kwargs: Any,
    ) -> T:
        obj: T = factory_class.build(**kwargs)
        async with create_test_session_factory() as session:
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
        return obj

    return cast(Callable[..., Awaitable[T]], _create)
