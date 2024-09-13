from fastapi import APIRouter

from .routes.article import router as articles_router
from .routes.comment import router as comments_router
from .routes.administration import router as admin_router

from core import settings


router = APIRouter(prefix=settings.api.prefix)

router.include_router(
    router=articles_router,
    prefix=settings.api.articles.prefix,
    tags=[settings.api.articles.tag],
)
router.include_router(
    router=comments_router,
    prefix=settings.api.comments.prefix,
    tags=[settings.api.comments.tag],
)
router.include_router(
    router=admin_router,
    prefix=settings.api.admin.prefix,
    tags=[settings.api.admin.tag],
)
