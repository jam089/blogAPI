from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, ScalarResult

from core.models import Comment


async def get_comment(
    sess: AsyncSession,
    comment_id: int,
) -> Comment | None:
    return await sess.get(Comment, comment_id)
