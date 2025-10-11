import asyncio
import json

import pytest
from core import settings
from core.models import Article
from elastic_transport import HeadApiResponse, ObjectApiResponse
from elasticsearch import AsyncElasticsearch
from httpx import AsyncClient
from redis.asyncio import Redis


@pytest.mark.asyncio
async def test_get_trends_articles_redis_active(
    async_client: AsyncClient,
    test_articles: Article,
    redis_client: Redis,
) -> None:
    response = await async_client.get(url=f"{settings.api.articles.prefix}/trends/")

    assert await redis_client.exists("get_trends_articles"), "Not cached"
    redis_response = await redis_client.get("get_trends_articles")
    assert json.loads(redis_response) == response.json()

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    expected_id = test_articles.id
    expected_title = test_articles.title
    id_flg = False
    title_flg = False
    for article_json in response.json():
        if article_json["title"] == expected_title:
            title_flg = True
        if article_json["id"] == expected_id:
            id_flg = True
    assert id_flg, "no article with test_article.id in response"
    assert title_flg, "no article with test_article.title in response"
    await asyncio.sleep(settings.cache.resp.expire_s or 1)


@pytest.mark.asyncio
async def test_get_trends_articles_redis_inactive(
    async_client_app_redis_inactive: AsyncClient,
    test_articles: Article,
) -> None:
    response = await async_client_app_redis_inactive.get(
        url=f"{settings.api.articles.prefix}/trends/"
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    expected_id = test_articles.id
    expected_title = test_articles.title
    id_flg = False
    title_flg = False
    for article_json in response.json():
        if article_json["title"] == expected_title:
            title_flg = True
        if article_json["id"] == expected_id:
            id_flg = True
    assert id_flg, "no article with test_article.id in response"
    assert title_flg, "no article with test_article.title in response"


@pytest.mark.asyncio
async def test_search_articles_in_elasticsearch(
    async_client: AsyncClient,
    es_client: AsyncElasticsearch,
    test_articles: Article,
) -> None:
    index = settings.es.articles_index
    await es_client.index(
        index=index,
        id=str(test_articles.id),
        document={
            "title": test_articles.title,
            "text": test_articles.text,
            "author_name": test_articles.author_name,
            "topic": test_articles.topic,
        },
        refresh=True,
    )

    query = test_articles.title.split()[1]
    response = await async_client.get(
        url=f"{settings.api.articles.prefix}/search/",
        params={"query": query},
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert "articles" in data
    assert "search_response" in data

    articles = data["articles"]
    assert isinstance(articles, dict)
    assert len(articles) > 0

    assert str(test_articles.id) in articles
    article = articles[str(test_articles.id)]

    assert article["title"] == test_articles.title
    assert article["topic"] == test_articles.topic
    assert article["author_name"] == test_articles.author_name
    assert "created_at" in article

    search_response = data["search_response"]
    assert isinstance(search_response, dict)
    assert "hits" in search_response
    assert "took" in search_response


@pytest.mark.asyncio
async def test_get_all_articles_redis_active(
    async_client: AsyncClient,
    test_articles: Article,
    redis_client: Redis,
) -> None:
    response = await async_client.get(url=f"{settings.api.articles.prefix}/")

    assert await redis_client.exists("get_all_articles"), "Not cached"
    redis_response = await redis_client.get("get_all_articles")
    assert json.loads(redis_response) == response.json()

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    expected_id = test_articles.id
    expected_title = test_articles.title
    id_flg = False
    title_flg = False
    for article_json in response.json():
        if article_json["title"] == expected_title:
            title_flg = True
        if article_json["id"] == expected_id:
            id_flg = True
    assert id_flg, "no article with test_article.id in response"
    assert title_flg, "no article with test_article.title in response"
    await asyncio.sleep(settings.cache.resp.expire_s or 1)


@pytest.mark.asyncio
async def test_get_all_articles_redis_inactive(
    async_client_app_redis_inactive: AsyncClient,
    test_articles: Article,
) -> None:
    response = await async_client_app_redis_inactive.get(
        url=f"{settings.api.articles.prefix}/"
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    expected_id = test_articles.id
    expected_title = test_articles.title
    id_flg = False
    title_flg = False
    for article_json in response.json():
        if article_json["title"] == expected_title:
            title_flg = True
        if article_json["id"] == expected_id:
            id_flg = True
    assert id_flg, "no article with test_article.id in response"
    assert title_flg, "no article with test_article.title in response"


@pytest.mark.asyncio
async def test_get_article(
    async_client: AsyncClient,
    test_articles_with_comments: Article,
    elasticsearch_service: str,
    redis_service: dict,
) -> None:
    expected_comments_id_list = [
        comment.id for comment in test_articles_with_comments.comments
    ]
    response = await async_client.get(
        url=f"{settings.api.articles.prefix}/{test_articles_with_comments.id}/"
    )
    assert response.status_code == 200
    article_from_resp = response.json()
    comments_list = article_from_resp["comments"]
    assert len(comments_list) == len(expected_comments_id_list)
    for comment in comments_list:
        assert comment["id"] in expected_comments_id_list


@pytest.mark.parametrize(
    "article_to_create",
    [
        {
            "title": "TestArticle",
            "text": "TestText",
            "topic": "TestTopic",
            "author_name": "j_lenin",
        },
        {
            "title": "TestArticle",
            "text": "TestTextTestTextTestText",
            "topic": "TestTopic",
            "author_name": "jayK",
        },
    ],
)
@pytest.mark.asyncio
async def test_create_article(
    async_client: AsyncClient,
    es_client: AsyncElasticsearch,
    article_to_create: dict[str, str],
) -> None:
    response = await async_client.post(
        url=f"{settings.api.articles.prefix}/",
        json=article_to_create,
    )
    es_doc_response: HeadApiResponse = await es_client.exists(
        index=settings.es.articles_index, id=response.json()["id"]
    )
    assert es_doc_response.body, "No doc in ElasticSearch"
    assert response.status_code == 201
    assert response.json()["title"] == article_to_create["title"]
    assert response.json()["text"] == article_to_create["text"]
    assert response.json()["author_name"] == article_to_create["author_name"]
    assert response.json()["id"] is not None
    assert response.json()["created_at"] is not None
    assert response.json()["score"] is not None


@pytest.mark.parametrize(
    "article_to_update",
    [
        {
            "title": "New Title",
            "author_name": "SCP_fun",
        },
        {
            "text": "New TextNew TextNew TextNew TextNew TextNew Text",
            "topic": "NotTopic",
        },
    ],
)
@pytest.mark.asyncio
async def test_update_article(
    async_client: AsyncClient,
    es_client: AsyncElasticsearch,
    article_to_update: dict[str, str],
    test_article_a: Article,
) -> None:
    updating_fields = list(article_to_update.keys())
    response = await async_client.patch(
        url=f"{settings.api.articles.prefix}/{test_article_a.id}/",
        json=article_to_update,
    )
    es_doc_response: ObjectApiResponse[dict] = await es_client.get(
        index=settings.es.articles_index, id=response.json()["id"]
    )
    assert es_doc_response.body, "No doc in ElasticSearch"

    assert response.status_code == 200
    for field in updating_fields:
        assert response.json()[field] == article_to_update[field]
        assert es_doc_response.body["_source"][field] == article_to_update[field]


@pytest.mark.parametrize(
    "article_to_del",
    ["test_article_a", "test_article_b"],
)
@pytest.mark.asyncio
async def test_delete_article(
    async_client: AsyncClient,
    es_client: AsyncElasticsearch,
    article_to_del: list[str],
    test_article_a: Article,
    test_article_b: Article,
) -> None:
    if article_to_del == "test_article_a":
        deleting_article = test_article_a
    else:
        deleting_article = test_article_b

    response = await async_client.delete(
        url=f"{settings.api.articles.prefix}/{deleting_article.id}/",
    )
    es_doc_response: HeadApiResponse = await es_client.exists(
        index=settings.es.articles_index, id=str(deleting_article.id)
    )
    assert not es_doc_response.body, "deleting from ElasticSearch didn't work"

    assert response.status_code == 204


@pytest.mark.parametrize(
    "article_to_del",
    ["test_article_a", "test_article_b"],
)
@pytest.mark.asyncio
async def test_delete_article_with_comments(
    async_client: AsyncClient,
    es_client: AsyncElasticsearch,
    article_to_del: list[str],
    test_article_with_comments_a: Article,
    test_article_with_comments_b: Article,
) -> None:
    if article_to_del == "test_article_a":
        deleting_article = test_article_with_comments_a
    else:
        deleting_article = test_article_with_comments_b
    comments_id_list = [comment.id for comment in deleting_article.comments]
    response = await async_client.delete(
        url=f"{settings.api.articles.prefix}/{deleting_article.id}/",
    )
    es_doc_response: HeadApiResponse = await es_client.exists(
        index=settings.es.articles_index, id=str(deleting_article.id)
    )
    assert not es_doc_response.body, "deleting from ElasticSearch didn't work"

    assert response.status_code == 204
    for comment_id in comments_id_list:
        response_comments = await async_client.get(
            url=f"{settings.api.comments.prefix}/{comment_id}/",
        )
        assert response_comments.status_code == 404
