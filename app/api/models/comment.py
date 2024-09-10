from typing import TYPE_CHECKING

from sqlalchemy import Unicode, Integer, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .article import Article


class Comment(Base):
    __tablename__ = "comments"

    comment_text: Mapped[str] = mapped_column(Unicode(260))
    author_name: Mapped[str] = mapped_column(Unicode(50))
    score: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint(
            "score >= 1 AND score <=10",
            name="ScoreRestriction",
        ),
    )
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"))

    article: Mapped["Article"] = relationship(back_populates="comments")
