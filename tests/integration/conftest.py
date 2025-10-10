from typing import Awaitable, Callable

import pytest_asyncio
from api.schemes import CreateArticleSchm
from core import settings
from core.models import Article, Comment
from elasticsearch import AsyncElasticsearch
from pytest import FixtureRequest
from services.elasticsearch import add_doc

from tests.integration.database import (  # noqa: F401
    async_client,
    async_client_app_redis_inactive,
    create_test_engine,
    create_test_session_factory,
    override_dependency,
    prepare_db,
    test_db_url,
    test_session,
)
from tests.integration.docker_conteiners import (  # noqa: F401
    app_service,
    app_service_redis_inactive,
    docker_compose_file,
    docker_compose_project_name,
    docker_setup,
    elasticsearch_service,
    pg_service,
    redis_service,
)
from tests.integration.factories import (  # noqa: F401
    ArticleFactory,
    CommentFactory,
    create_from_factory,
)
from tests.integration.service_clients import es_client, redis_client  # noqa: F401


@pytest_asyncio.fixture(scope="function")
async def test_article_a(
    create_from_factory: Callable[..., Awaitable[Article]],  # noqa: F811
    es_client: AsyncElasticsearch,  # noqa: F811
) -> Article:
    create_article = create_from_factory
    article = await create_article(ArticleFactory)
    await add_doc(es_client, settings.es.articles_index, article, CreateArticleSchm)
    return article


@pytest_asyncio.fixture(scope="function")
async def test_article_b(
    create_from_factory: Callable[..., Awaitable[Article]],  # noqa: F811
    es_client: AsyncElasticsearch,  # noqa: F811
) -> Article:
    create_article = create_from_factory
    article = await create_article(ArticleFactory)
    await add_doc(es_client, settings.es.articles_index, article, CreateArticleSchm)
    return article


@pytest_asyncio.fixture(params=["test_article_a", "test_article_b"])
async def test_articles(
    request: FixtureRequest, test_article_a: Article, test_article_b: Article
) -> Article:
    if request.param == "test_article_a":
        return test_article_a
    else:
        return test_article_b


@pytest_asyncio.fixture(scope="function")
async def test_article_a_comment_a(
    create_from_factory: Callable[..., Awaitable[Comment]],  # noqa: F811
    test_article_a: Article,
) -> Comment:
    create_comment = create_from_factory
    comment_a = await create_comment(CommentFactory, article=test_article_a)
    return comment_a


@pytest_asyncio.fixture(scope="function")
async def test_article_a_comment_b(
    create_from_factory: Callable[..., Awaitable[Comment]],  # noqa: F811
    test_article_a: Article,
) -> Comment:
    create_comment = create_from_factory
    comment_b = await create_comment(CommentFactory, article=test_article_a)
    return comment_b


@pytest_asyncio.fixture(scope="function")
async def test_article_b_comment_a(
    create_from_factory: Callable[..., Awaitable[Comment]],  # noqa: F811
    test_article_b: Article,
) -> Comment:
    create_comment = create_from_factory
    comment_a = await create_comment(CommentFactory, article=test_article_b)
    return comment_a


@pytest_asyncio.fixture(
    params=["test_comment_aa", "test_comment_ab", "test_comment_ba"]
)
async def test_comments(
    request: FixtureRequest,
    test_article_a_comment_a: Comment,
    test_article_a_comment_b: Comment,
    test_article_b_comment_a: Comment,
) -> Comment:
    if request.param == "test_comment_aa":
        return test_article_a_comment_a
    elif request.param == "test_comment_ab":
        return test_article_a_comment_b
    else:
        return test_article_b_comment_a


@pytest_asyncio.fixture(scope="function")
async def test_article_with_comments_a(
    create_from_factory: Callable[..., Awaitable[Comment]],  # noqa: F811
    test_article_a: Article,
) -> Article:
    create_comment = create_from_factory
    await create_comment(CommentFactory, article=test_article_a)
    await create_comment(CommentFactory, article=test_article_a)
    return test_article_a


@pytest_asyncio.fixture(scope="function")
async def test_article_with_comments_b(
    create_from_factory: Callable[..., Awaitable[Comment]],  # noqa: F811
    test_article_b: Article,
) -> Article:
    create_comment = create_from_factory
    await create_comment(CommentFactory, article=test_article_b)
    return test_article_b


@pytest_asyncio.fixture(
    params=["test_article_with_comments_a", "test_article_with_comments_b"]
)
async def test_articles_with_comments(
    request: FixtureRequest,
    test_article_with_comments_a: Comment,
    test_article_with_comments_b: Comment,
) -> Comment:
    if request.param == "test_article_with_comments_a":
        return test_article_with_comments_a
    else:
        return test_article_with_comments_b
