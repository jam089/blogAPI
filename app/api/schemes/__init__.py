__all__ = (
    "CreateArticleSchm",
    "ChangeArticleSchm",
    "ReadArticleSchm",
    "CreateCommentSchm",
    "ChangeCommentSchm",
    "ReadCommentSchm",
)


from .article import CreateArticleSchm, ChangeArticleSchm, ReadArticleSchm
from .comment import CreateCommentSchm, ChangeCommentSchm, ReadCommentSchm
