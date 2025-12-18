import pytest


@pytest.mark.anyio
async def test_read_root(async_client):
    """There are no values in the empty database."""
    response = await async_client.get("/api/v1/categories/categories")

    assert response.status_code == 200
    assert len(response.json()) == 0
