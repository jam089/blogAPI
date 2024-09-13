from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, ScalarResult

from core.models import Comment, Article
from api.schemes import CreateCommentSchm, ChangeCommentSchm


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


async def update_comment(
    sess: AsyncSession,
    comment_to_update: Comment,
    comment_in: ChangeCommentSchm,
) -> Comment:
    for name, value in comment_in.model_dump(exclude_unset=True).items():
        setattr(comment_to_update, name, value)

    await sess.commit()
    await sess.refresh(comment_to_update)
    return comment_to_update


async def delete_comment(
    sess: AsyncSession,
    comment_to_delete: Comment,
) -> None:
    await sess.delete(comment_to_delete)
    await sess.commit()


async def bulk_load_comments(
    sess: AsyncSession,
    json_file: list[dict],
) -> bool:
    try:
        for in_file_comment in json_file:
            import_id = in_file_comment.get("import_article_id")
            stmt = select(Article).where(Article.import_article_id == import_id)
            article = await sess.scalar(stmt)
            in_file_comment.pop("import_article_id")
            new_comment_dict = {
                "article_id": article.id,
                **in_file_comment,
            }
            new_comment = Comment(**new_comment_dict)
            sess.add(new_comment)
            await sess.commit()

        return True
    except Exception:
        await sess.rollback()
        return False
