__all__ = (
    "CreateArticleSchm",
    "ChangeArticleSchm",
    "ReadArticleSchm",
    "ReadArticleWithCommentsSchm",
    "CreateCommentSchm",
    "ChangeCommentSchm",
    "ReadCommentSchm",
)


from .article import (
    CreateArticleSchm,
    ChangeArticleSchm,
    ReadArticleSchm,
    ReadArticleWithCommentsSchm,
)
from .comment import CreateCommentSchm, ChangeCommentSchm, ReadCommentSchm
