from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, ScalarResult

from core.models import Comment, Article


async def get_comment(
    sess: AsyncSession,
    comment_id: int,
) -> Comment | None:
    return await sess.get(Comment, comment_id)


async def get_comments_of_article(
    sess: AsyncSession,
    article: Article,
) -> Sequence[Comment]:
    stmt = (
        select(Comment)
        .where(Comment.article_id == article.id)
        .order_by(Comment.created_at.desc())
    )
    result: ScalarResult = await sess.scalars(stmt)
    return result.all()
