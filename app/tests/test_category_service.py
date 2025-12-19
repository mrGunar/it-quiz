import pytest

from app.schemas.categories import CategoryCreate, CategoryUpdate


@pytest.mark.anyio
async def test_get_from_empty_database(async_client):
    """There are no values in the empty database."""
    response = await async_client.get("/api/v1/categories/")

    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.anyio
async def test_get_invalid_category_id(async_client):
    """Test get an invalid category id from the empty database."""
    response = await async_client.get("/api/v1/categories/1")

    data = response.json()
    assert response.status_code == 404
    assert len(data) == 1
    assert data["detail"] == "Category with ID 1 not found"


@pytest.mark.anyio
async def test_create_a_category(async_client):
    """Test getting all categories when there is a category in the database."""
    category = CategoryCreate(category="First Category")
    response = await async_client.post(
        "/api/v1/categories/", json=category.model_dump()
    )

    assert response.status_code == 201
    data = response.json()
    assert len(data) == 2
    assert data["id"] == 1, "The first id must be equal to 1"
    assert data["category"] == "First Category"


@pytest.mark.anyio
async def test_create_and_get_category(async_client):
    """Test create a category and get it from the database."""
    category = CategoryCreate(category="First Category")

    _ = await async_client.post("/api/v1/categories/", json=category.model_dump())

    response = await async_client.get("/api/v1/categories/")
    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == 1, "The id of the first category must be equal to 1"
    assert data[0]["category"] == "First Category"


@pytest.mark.anyio
async def test_create_and_update_category(async_client):
    """Test create a category and get it from the database."""
    new_category = CategoryCreate(category="First Category")
    updated_category = CategoryUpdate(category="First Category Updated")

    _ = await async_client.post("/api/v1/categories/", json=new_category.model_dump())

    category_id = 1

    response = await async_client.put(
        f"/api/v1/categories/{category_id}",
        json=updated_category.model_dump(),
    )

    data = response.json()
    assert response.status_code == 200
    assert len(data) == 2
    assert data["id"] == 1, "The id must be equal to 1"
    assert data["category"] == "First Category Updated"


@pytest.mark.anyio
async def test_create_and_delete_category(async_client):
    """Test create a category and delete it from the database."""
    new_category = CategoryCreate(category="First Category")

    _ = await async_client.post("/api/v1/categories/", json=new_category.model_dump())

    category_id = 1
    response = await async_client.delete(
        f"/api/v1/categories/{category_id}",
    )

    assert response.status_code == 204

    response = await async_client.get("/api/v1/categories/")

    assert response.status_code == 200
    assert len(response.json()) == 0
