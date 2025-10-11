from datetime import datetime

import pytest
from core import settings
from core.models import Article, Comment
from httpx import AsyncClient

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_get_comments_of_article(
    async_client: AsyncClient,
    test_articles_with_comments: Article,
) -> None:
    comments_expected_author_list = [
        comment.author_name for comment in test_articles_with_comments.comments
    ]
    comments_expected_id_list = [
        comment.id for comment in test_articles_with_comments.comments
    ]
    url = f"{settings.api.comments.prefix}{settings.api.articles.prefix}/{test_articles_with_comments.id}/"

    response = await async_client.get(url=url)
    assert response.status_code == 200

    for comment in response.json():
        assert comment["id"] in comments_expected_id_list
        assert comment["author_name"] in comments_expected_author_list


@pytest.mark.asyncio
async def test_get_comment(
    async_client: AsyncClient,
    test_comments: Comment,
) -> None:
    response = await async_client.get(
        url=f"{settings.api.comments.prefix}/{test_comments.id}/"
    )

    assert response.status_code == 200
    assert response.json()["id"] == test_comments.id
    assert response.json()["author_name"] == test_comments.author_name


@pytest.mark.parametrize(
    "comment_to_create",
    [
        {
            "comment_text": "TestComment1",
            "author_name": "JimBeam",
            "score": 7,
        },
        {
            "comment_text": "TestComment2",
            "author_name": "JohnBom",
            "score": 3,
        },
    ],
)
@pytest.mark.parametrize(
    "test_article_selector", ["test_article_a", "test_article_with_comments_b"]
)
@pytest.mark.asyncio
async def test_create_comment(
    async_client: AsyncClient,
    test_article_a: Article,
    test_article_with_comments_b: Article,
    test_article_selector: str,
    comment_to_create: dict[str, str],
) -> None:
    if test_article_selector == "test_article_a":
        test_article = test_article_a
    else:
        test_article = test_article_with_comments_b
    comment_to_create["article_id"] = str(test_article.id)
    response = await async_client.post(
        url=f"{settings.api.comments.prefix}/",
        json=comment_to_create,
    )
    assert response.status_code == 201
    assert response.json()["id"] is not None
    assert response.json()["created_at"] is not None
    assert response.json()["score"] == comment_to_create["score"]
    assert response.json()["article_id"] == int(comment_to_create["article_id"])
    if comment_to_create.get("comment_text"):
        assert response.json()["comment_text"] == comment_to_create["comment_text"]
    if comment_to_create.get("author_name"):
        assert response.json()["author_name"] == comment_to_create["author_name"]


@pytest.mark.parametrize(
    "comment_to_update",
    [
        {
            "comment_text": "TestComment1",
            "author_name": "JimBeam",
            "score": 7,
        },
        {
            "comment_text": "TestComment2",
            "author_name": "JohnBom",
        },
        {
            "score": 9,
        },
    ],
)
@pytest.mark.asyncio
async def test_update_comment(
    async_client: AsyncClient,
    comment_to_update: dict[str, str],
    test_comments: Comment,
) -> None:
    response = await async_client.patch(
        url=f"{settings.api.comments.prefix}/{test_comments.id}/",
        json=comment_to_update,
    )
    assert response.status_code == 200
    assert response.json()["id"] == test_comments.id
    assert (
        datetime.fromisoformat(response.json()["created_at"])
        == test_comments.created_at
    )
    assert response.json()["last_updated_at"] is not None
    assert response.json()["article_id"] == test_comments.article_id
    if comment_to_update.get("comment_text"):
        assert response.json()["comment_text"] == comment_to_update["comment_text"]
    if comment_to_update.get("author_name"):
        assert response.json()["author_name"] == comment_to_update["author_name"]
    if comment_to_update.get("score"):
        assert response.json()["score"] == comment_to_update["score"]


@pytest.mark.asyncio
async def test_delete_comment(
    async_client: AsyncClient, test_comments: Comment
) -> None:
    response = await async_client.delete(
        url=f"{settings.api.comments.prefix}/{test_comments.id}/",
    )
    assert response.status_code == 204
    checking_response = await async_client.get(
        url=f"{settings.api.comments.prefix}/{test_comments.id}/",
    )
    assert checking_response.status_code == 404
