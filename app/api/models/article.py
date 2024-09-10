from sqlalchemy import Unicode, UnicodeText
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Article(Base):
    __tablename__ = "articles"

    title: Mapped[str] = mapped_column(Unicode(120))
    text: Mapped[str] = mapped_column(UnicodeText)
    topic: Mapped[str] = mapped_column(Unicode(36))
    author_name: Mapped[str] = mapped_column(Unicode(50))
