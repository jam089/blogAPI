from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, ScalarResult, insert, update, or_
from sqlalchemy.orm import selectinload

from core.models import Article
from api.schemes import CreateArticleSchm, ChangeArticleSchm


async def get_all_articles(sess: AsyncSession) -> Sequence[Article]:
    stmt = select(Article).order_by(Article.created_at.desc())
    result: ScalarResult = await sess.scalars(stmt)
    return result.all()


async def get_article(
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


async def get_trend_articles(
    sess: AsyncSession,
) -> Sequence[Article]:
    stmt = select(Article).order_by(Article.absolut_score.desc()).limit(20)
    result: ScalarResult = await sess.scalars(stmt)
    return result.all()


async def create_article(
    sess: AsyncSession,
    article_in: CreateArticleSchm,
) -> Article:
    new_article = Article(**article_in.model_dump())
    sess.add(new_article)
    await sess.commit()
    await sess.refresh(new_article)
    return new_article


async def update_article(
    sess: AsyncSession,
    article_to_update: Article,
    article_in: ChangeArticleSchm,
) -> Article:
    for name, value in article_in.model_dump(exclude_unset=True).items():
        setattr(article_to_update, name, value)

    await sess.commit()
    await sess.refresh(article_to_update)
    return article_to_update


async def delete_article(
    sess: AsyncSession,
    article_to_del: Article,
) -> None:
    await sess.delete(article_to_del)
    await sess.commit()


async def bulk_load_article(
    sess: AsyncSession,
    json_file: list[dict[Article]],
) -> bool:
    try:
        stmt = insert(Article).values(json_file)
        await sess.execute(stmt)
        await sess.commit()
        return True
    except Exception:
        await sess.rollback()
        return False


async def inactive_imported_articles(sess: AsyncSession):
    update_value = {"import_article_id": -9999}
    stmt = (
        update(Article)
        .values(update_value)
        .where(
            or_(
                Article.import_article_id != None,
                Article.import_article_id != -9999,
            )
        )
    )
    await sess.execute(stmt)
    await sess.commit()
