from typing import TYPE_CHECKING

from sqlalchemy import Unicode, UnicodeText
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from .base import Base

if TYPE_CHECKING:
    from .comment import Comment


class Article(Base):
    __tablename__ = "articles"

    title: Mapped[str] = mapped_column(Unicode(120))
    text: Mapped[str] = mapped_column(UnicodeText)
    topic: Mapped[str] = mapped_column(Unicode(36))
    author_name: Mapped[str] = mapped_column(Unicode(50))

    comments: Mapped[list["Comment"]] = relationship(
        back_populates="article",
        lazy="immediate",
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
