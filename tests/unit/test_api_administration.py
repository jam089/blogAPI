import pytest
from api.routes.administration import import_data_from_file
from fastapi import HTTPException
from pytest_mock import MockFixture


@pytest.mark.asyncio
async def test_import_data_from_file(mocker: MockFixture) -> None:
    mocker.patch("api.routes.administration.crud.bulk_load_article", return_value=True)
    mocker.patch("api.routes.administration.crud.bulk_load_comments", return_value=True)
    fake_inactive_imported_articles = mocker.patch(
        "api.routes.administration.crud.inactive_imported_articles"
    )
    await import_data_from_file(mocker.AsyncMock())
    fake_inactive_imported_articles.assert_awaited_once()


@pytest.mark.asyncio
async def test_import_data_from_file_with_exc(mocker: MockFixture) -> None:
    mocker.patch("api.routes.administration.crud.bulk_load_article", return_value=True)
    mocker.patch(
        "api.routes.administration.crud.bulk_load_comments", return_value=False
    )
    fake_inactive_imported_articles = mocker.patch(
        "api.routes.administration.crud.inactive_imported_articles"
    )
    with pytest.raises(HTTPException) as exc:
        await import_data_from_file(mocker.AsyncMock())
    fake_inactive_imported_articles.assert_awaited_once()
    assert exc.value.status_code == 422
    assert exc.value.detail == "can not process import data"
