import json

import pytest
from core import config, settings
from core.models import Article
from elasticsearch import AsyncElasticsearch
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ping(async_client: AsyncClient) -> None:
    response = await async_client.get(url=f"{settings.api.admin.prefix}/ping/")
    assert response.status_code == 200
    assert response.json().get("status") == "pong"


@pytest.mark.asyncio
async def test_import_data_from_file(
    async_client: AsyncClient,
) -> None:
    articles = [
        {
            "title": "Test1",
            "text": "Test_one",
            "topic": "Test",
            "author_name": "Test One",
            "import_article_id": 1,
        },
        {
            "title": "Test2",
            "text": "Test_two",
            "topic": "Test",
            "author_name": "Test Two",
            "import_article_id": 2,
        },
    ]
    comments = [
        {
            "comment_text": "CTest1",
            "author_name": "Com Test One",
            "score": 2,
            "import_article_id": 1,
        },
        {
            "comment_text": "CTest2",
            "author_name": "Com Test Two",
            "score": 3,
            "import_article_id": 2,
        },
        {
            "comment_text": "CTest3",
            "author_name": "Com Test Three",
            "score": 5,
            "import_article_id": 2,
        },
    ]
    articles_file = config.BASE_DIR.parent / "data" / "articles.json"
    articles_file.write_text(json.dumps(articles), encoding="utf-8")
    comments_file = config.BASE_DIR.parent / "data" / "comments.json"
    comments_file.write_text(json.dumps(comments), encoding="utf-8")

    resource = await async_client.get(url=f"{settings.api.admin.prefix}/import-data/")
    assert resource.status_code == 201

    check_articles_response = await async_client.get(
        url=f"{settings.api.articles.prefix}/"
    )
    assert check_articles_response.status_code == 200
    assert len(check_articles_response.json()) == 2

    comment_counter = 0
    for article in check_articles_response.json():
        check_comments_response = await async_client.get(
            url=f"{settings.api.comments.prefix}{settings.api.articles.prefix}/{article["id"]}/"
        )
        assert check_comments_response.status_code == 200
        comment_counter += len(check_comments_response.json())
    assert comment_counter == 3


@pytest.mark.asyncio
async def test_index_articles(
    async_client: AsyncClient,
    es_client: AsyncElasticsearch,
    test_articles_to_bulk_in_es: list[Article],
) -> None:
    resource = await async_client.get(
        url=f"{settings.api.admin.prefix}/es_index_articles/"
    )
    assert resource.status_code == 200
    for article in test_articles_to_bulk_in_es:
        assert await es_client.exists(
            index=settings.es.articles_index,
            id=str(article.id),
        ), f"article {article.id} not indexed"
