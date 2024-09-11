from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, ScalarResult
from sqlalchemy.orm import selectinload

from api.models import Article


async def get_all_articles(sess: AsyncSession) -> Sequence[Article]:
    stmt = select(Article).order_by(Article.created_at.desc())
    result: ScalarResult = await sess.scalars(stmt)
    return result.all()


async def get_article_with_five_last_comments(
    sess: AsyncSession,
    article_id: int,
) -> Article:
    stmt = (
        select(Article)
        .options(selectinload(Article.comments))
        .where(Article.id == article_id)
    )
    article: Article = await sess.scalar(stmt)
    return article
