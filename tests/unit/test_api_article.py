from typing import Any

import pytest
from api.routes.article import (
    HTTP_404,
    delete_article,
    get_article,
    search_articles,
    update_article,
)
from api.schemes.article import ChangeArticleSchm
from core.models import Article
from fastapi import HTTPException
from pytest_mock import MockFixture

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_search_articles_aggregates_articles_from_ids(
    mocker: MockFixture,
) -> None:
    fake_es_resp = mocker.Mock()
    fake_es_resp.body = {"hits": []}
    mocker.patch(
        "api.routes.article.searching_docs",
        return_value=(fake_es_resp, [1, 2]),
    )

    mocker.patch(
        "api.routes.article.crud.get_article",
        side_effect=[
            Article(id=1, title="First"),
            Article(id=2, title="Second"),
        ],
    )
    mocker.patch(
        "api.routes.article.ReadArticleSchm.model_validate",
        side_effect=[
            mocker.Mock(
                model_dump=mocker.Mock(return_value={"id": 1, "title": "First"})
            ),
            mocker.Mock(
                model_dump=mocker.Mock(return_value={"id": 2, "title": "Second"})
            ),
        ],
    )
    result: dict[str, Any] = await search_articles(
        db_sess=mocker.Mock(), es_sess=mocker.Mock(), query="some query"
    )
    assert result["articles"][1]["id"] == 1
    assert result["articles"][2]["id"] == 2
    assert result["search_response"] == {"hits": []}


@pytest.mark.asyncio
async def test_get_article_returns_article(mocker: MockFixture) -> None:
    mock_article = mocker.Mock()
    mocker.patch("api.routes.article.crud.get_article", return_value=mock_article)
    result = await get_article(sess=mocker.Mock(), article_id=1)
    assert result == mock_article


@pytest.mark.asyncio
async def test_get_article_raises_404(mocker: MockFixture) -> None:
    mocker.patch("api.routes.article.crud.get_article", return_value=None)
    with pytest.raises(HTTPException) as exc:
        await get_article(sess=mocker.Mock(), article_id=999)
    assert exc.value == HTTP_404


@pytest.mark.asyncio
async def test_update_article_without_add_docs_to_index(mocker: MockFixture) -> None:
    mocker.patch("api.routes.article.crud.get_article", return_value=True)
    mocker.patch("api.routes.article.check_doc", return_value=False)
    mock_add_doc = mocker.patch("api.routes.article.add_doc")
    mocker.patch("api.routes.article.get_doc", return_value=2)
    mocker.patch("api.routes.article.ESReadArticleSchm.model_validate", return_value=1)
    mocker.patch(
        "api.routes.article.crud.update_article", return_value=Article(title="Nice")
    )
    mock_update_doc = mocker.patch("api.routes.article.update_doc")

    await update_article(
        db_sess=mocker.Mock(),
        es_sess=mocker.Mock(),
        article_id=1,
        article_in=ChangeArticleSchm(title="ghfsd"),
    )

    assert mock_add_doc.call_count == 2
    mock_update_doc.assert_called_once()


@pytest.mark.asyncio
async def test_update_article_add_docs_to_index(mocker: MockFixture) -> None:
    mocker.patch("api.routes.article.crud.get_article", return_value=True)
    mocker.patch("api.routes.article.check_doc", return_value=True)
    mocker.patch("api.routes.article.get_doc", return_value=1)
    mocker.patch("api.routes.article.ESReadArticleSchm.model_validate", return_value=1)
    mocker.patch(
        "api.routes.article.crud.update_article", return_value=Article(title="Nice")
    )
    mock_update_doc = mocker.patch("api.routes.article.update_doc")

    await update_article(
        db_sess=mocker.Mock(),
        es_sess=mocker.Mock(),
        article_id=1,
        article_in=ChangeArticleSchm(title="ghfd"),
    )

    mock_update_doc.assert_called_once()


@pytest.mark.asyncio
async def test_update_article_not_found(mocker: MockFixture) -> None:
    mocker.patch("api.routes.article.crud.get_article", return_value=False)
    with pytest.raises(HTTPException) as exc:
        await update_article(
            db_sess=mocker.Mock(),
            es_sess=mocker.Mock(),
            article_id=1,
            article_in=ChangeArticleSchm(title="dfgh"),
        )
    assert exc.value == HTTP_404


@pytest.mark.asyncio
async def test_delete_article_add_docs_to_index(mocker: MockFixture) -> None:
    mocker.patch("api.routes.article.crud.get_article", return_value=True)
    mock_delete_article = mocker.patch("api.routes.article.crud.delete_article")
    mock_remove_doc = mocker.patch("api.routes.article.remove_doc")

    await delete_article(
        db_sess=mocker.Mock(),
        es_sess=mocker.Mock(),
        article_id=1,
    )

    mock_delete_article.assert_called_once()
    mock_remove_doc.assert_called_once()


@pytest.mark.asyncio
async def test_delete_article_not_found(mocker: MockFixture) -> None:
    mocker.patch("api.routes.article.crud.get_article", return_value=False)
    with pytest.raises(HTTPException) as exc:
        await delete_article(
            db_sess=mocker.Mock(),
            es_sess=mocker.Mock(),
            article_id=1,
        )
    assert exc.value == HTTP_404
