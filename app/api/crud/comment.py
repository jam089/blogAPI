from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, ScalarResult

from core.models import Comment, Article
from api.schemes import CreateCommentSchm


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


async def create_comment(
    sess: AsyncSession,
    comment_in: CreateCommentSchm,
) -> Comment:
    new_comment = Comment(**comment_in.model_dump())
    sess.add(new_comment)
    await sess.commit()
    await sess.refresh(new_comment)
    return new_comment
