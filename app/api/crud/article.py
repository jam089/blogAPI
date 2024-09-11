from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, ScalarResult

from api.models import Article


async def get_all_articles(sess: AsyncSession) -> Sequence[Article]:
    stmt = select(Article).order_by(Article.created_at.desc())
    result: ScalarResult = await sess.scalars(stmt)
    return result.all()
