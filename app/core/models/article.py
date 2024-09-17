from sqlalchemy import Unicode, UnicodeText, Integer, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from .base import Base

from .comment import Comment


class Article(Base):
    __tablename__ = "articles"

    title: Mapped[str] = mapped_column(Unicode(120))
    text: Mapped[str] = mapped_column(UnicodeText)
    topic: Mapped[str] = mapped_column(Unicode(36))
    author_name: Mapped[str] = mapped_column(Unicode(50))
    import_article_id: Mapped[int | None] = mapped_column(Integer)

    comments: Mapped[list["Comment"]] = relationship(
        back_populates="article",
        lazy="immediate",
        order_by="Comment.created_at.desc()",
    )

    @hybrid_property
    def score(self) -> float | int:

        if not self.comments:
            return 0

        score_sum = 0
        comments_qty = 0
        for comment in self.comments:
            score_sum += comment.score
            comments_qty += 1
        return round(score_sum / comments_qty, 2)

    @hybrid_property
    def absolut_score(self) -> int:
        if not self.comments:
            return 0

        score_sum = 0
        for comment in self.comments:
            score_sum += comment.score
        return score_sum

    @absolut_score.expression
    def absolut_score(cls):
        return (
            select(func.count(Comment.score))
            .where(Comment.article_id == cls.id)
            .label("absolut_score")
        )
