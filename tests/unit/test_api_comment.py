import pytest
from api.routes.comment import (
    HTTP_404_article,
    HTTP_404_comment,
    create_comment,
    delete_comment,
    get_comment,
    get_comments_of_article,
    update_comment,
)
from api.schemes.comment import ChangeCommentSchm, CreateCommentSchm
from fastapi import HTTPException
from pytest_mock import MockFixture


@pytest.mark.asyncio
async def test_get_comments_of_article(mocker: MockFixture) -> None:
    mocker.patch("api.routes.comment.crud.get_article", return_value=True)
    mocker.patch(
        "api.routes.comment.crud.get_comments_of_article",
        return_value={"text": "Comment"},
    )
    comment = await get_comments_of_article(
        sess=mocker.AsyncMock(),
        article_id=1,
    )
    assert comment == {"text": "Comment"}


@pytest.mark.asyncio
async def test_get_comments_of_article_that_not_found(mocker: MockFixture) -> None:
    mocker.patch("api.routes.comment.crud.get_article", return_value=False)
    with pytest.raises(HTTPException) as exc:
        await get_comments_of_article(
            sess=mocker.AsyncMock(),
            article_id=999,
        )
    assert exc.value == HTTP_404_article


@pytest.mark.asyncio
async def test_get_comment(mocker: MockFixture) -> None:
    mocker.patch(
        "api.routes.comment.crud.get_comment", return_value={"text": "Comment"}
    )
    comment = await get_comment(
        sess=mocker.AsyncMock(),
        comment_id=1,
    )
    assert comment == {"text": "Comment"}


@pytest.mark.asyncio
async def test_get_comment_not_found(mocker: MockFixture) -> None:
    mocker.patch("api.routes.comment.crud.get_comment", return_value=False)
    with pytest.raises(HTTPException) as exc:
        await get_comment(
            sess=mocker.AsyncMock(),
            comment_id=999,
        )
    assert exc.value == HTTP_404_comment


@pytest.mark.asyncio
async def test_create_comment(mocker: MockFixture) -> None:
    mocker.patch("api.routes.comment.crud.get_article", return_value=True)
    mocker.patch(
        "api.routes.comment.crud.create_comment",
        return_value={"text": "Comment"},
    )
    comment = await create_comment(
        sess=mocker.AsyncMock(),
        comment_in=CreateCommentSchm(
            comment_text="text",
            article_id=1,
            score=9,
            author_name="Nick",
        ),
    )
    assert comment == {"text": "Comment"}


@pytest.mark.asyncio
async def test_create_comment_article_not_found(mocker: MockFixture) -> None:
    mocker.patch("api.routes.comment.crud.get_article", return_value=False)
    with pytest.raises(HTTPException) as exc:
        await create_comment(
            sess=mocker.AsyncMock(),
            comment_in=CreateCommentSchm(
                comment_text="text",
                article_id=1,
                score=9,
                author_name="Nick",
            ),
        )
    assert exc.value == HTTP_404_article


@pytest.mark.asyncio
async def test_update_comment(mocker: MockFixture) -> None:
    mocker.patch("api.routes.comment.crud.get_comment", return_value=True)
    mocker.patch(
        "api.routes.comment.crud.update_comment", return_value={"text": "Comment"}
    )
    comment = await update_comment(
        sess=mocker.AsyncMock(),
        comment_id=1,
        comment_in=ChangeCommentSchm(
            comment_text="text",
            author_name="Nick",
        ),
    )
    assert comment == {"text": "Comment"}


@pytest.mark.asyncio
async def test_update_comment_not_found(mocker: MockFixture) -> None:
    mocker.patch("api.routes.comment.crud.get_comment", return_value=False)
    with pytest.raises(HTTPException) as exc:
        await update_comment(
            sess=mocker.AsyncMock(),
            comment_id=999,
            comment_in=ChangeCommentSchm(
                comment_text="text",
                author_name="Nick",
            ),
        )
    assert exc.value == HTTP_404_comment


@pytest.mark.asyncio
async def test_delete_comment(mocker: MockFixture) -> None:
    mocker.patch("api.routes.comment.crud.get_comment", return_value=True)
    mock_delete_crud = mocker.patch(
        "api.routes.comment.crud.delete_comment", return_value=True
    )
    await delete_comment(
        sess=mocker.AsyncMock(),
        comment_id=1,
    )
    mock_delete_crud.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_comment_not_found(mocker: MockFixture) -> None:
    mocker.patch("api.routes.comment.crud.get_comment", return_value=False)
    with pytest.raises(HTTPException) as exc:
        await delete_comment(
            sess=mocker.AsyncMock(),
            comment_id=999,
        )
    assert exc.value == HTTP_404_comment
