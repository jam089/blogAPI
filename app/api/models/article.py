from typing import TYPE_CHECKING

from sqlalchemy import Unicode, UnicodeText
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .comment import Comment


class Article(Base):
    __tablename__ = "articles"

    title: Mapped[str] = mapped_column(Unicode(120))
    text: Mapped[str] = mapped_column(UnicodeText)
    topic: Mapped[str] = mapped_column(Unicode(36))
    author_name: Mapped[str] = mapped_column(Unicode(50))

    comments: Mapped[list["Comment"]] = relationship(back_populates="article")
