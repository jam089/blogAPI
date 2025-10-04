import pytest
from api.crud.comment import bulk_load_comments
from core.models import Article
from pytest_mock import MockFixture


@pytest.mark.asyncio
async def test_bulk_load_comments(mocker: MockFixture) -> None:
    sess = mocker.AsyncMock()
    sess.scalar.return_value = Article(id=1, import_article_id=123)
    sess.add = mocker.Mock()
    sess.commit = mocker.AsyncMock()

    json_file = [
        {
            "import_article_id": 123,
            "comment_text": "x" * 200,
            "author_name": "John",
            "score": "7",
        }
    ]
    max_len = 50
    mocker.patch(
        "api.crud.comment.settings",
        new=mocker.Mock(comment_param=mocker.Mock(comment_text_max_length=max_len)),
    )

    result = await bulk_load_comments(sess, json_file)

    assert result is True
    added_comment = sess.add.call_args[0][0]
    assert len(added_comment.comment_text) == max_len
    sess.commit.assert_awaited()


@pytest.mark.asyncio
async def test_bulk_load_comments_exc(mocker: MockFixture) -> None:
    sess = mocker.AsyncMock()
    sess.scalar.side_effect = Exception("boom")
    sess.rollback = mocker.AsyncMock()

    result = await bulk_load_comments(sess, mocker.Mock())

    assert result is False
    sess.rollback.assert_awaited()
