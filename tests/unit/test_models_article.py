import pytest
from core.models import Article, Comment

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_article_score_property_non_comment() -> None:
    article = Article(title="test_title", text="test_text")
    article.comments = []
    assert article.score == 0


@pytest.mark.asyncio
async def test_article_score_property_with_comments() -> None:
    article = Article(title="test_title", text="test_text", id=1)
    comment_1 = Comment(comment_text="test_text", score=2, article_id=1)
    comment_2 = Comment(comment_text="test_text", score=4, article_id=1)
    comment_3 = Comment(comment_text="test_text", score=6, article_id=1)
    comment_4 = Comment(comment_text="test_text", score=8, article_id=1)
    article.comments = [comment_1, comment_2, comment_3, comment_4]
    assert article.score == 5


@pytest.mark.asyncio
async def test_article_absolute_score_property_non_comment() -> None:
    article = Article(title="test_title", text="test_text")
    article.comments = []
    assert article.absolut_score == 0


@pytest.mark.asyncio
async def test_article_absolute_score_property_with_comments() -> None:
    article = Article(title="test_title", text="test_text", id=1)
    comment_1 = Comment(comment_text="test_text", score=2, article_id=1)
    comment_2 = Comment(comment_text="test_text", score=4, article_id=1)
    comment_3 = Comment(comment_text="test_text", score=6, article_id=1)
    comment_4 = Comment(comment_text="test_text", score=8, article_id=1)
    article.comments = [comment_1, comment_2, comment_3, comment_4]
    assert article.absolut_score == 20
