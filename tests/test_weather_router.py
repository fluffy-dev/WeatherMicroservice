import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_weather_endpoint(client: AsyncClient):
    """Test POST /weather/ endpoint."""
    payload = {
        "city": "ApiCity",
        "country": "AP",
        "temperature": 15.0,
        "humidity": 45,
        "pressure": 1015
    }
    response = await client.post("/weather/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["city"] == "ApiCity"
    assert "id" in data
    assert "fetched_at" in data


@pytest.mark.asyncio
async def test_create_weather_validation_error(client: AsyncClient):
    """Test validation failure (e.g., invalid humidity > 100)."""
    payload = {
        "city": "BadDataCity",
        "country": "BD",
        "temperature": 15.0,
        "humidity": 150,  # Invalid
        "pressure": 1015
    }
    response = await client.post("/weather/", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_weather_not_found(client: AsyncClient):
    """Test GET /weather/{city} for non-existent city."""
    response = await client.get("/weather/NonExistentCity")
    assert response.status_code == 404
    assert response.json()["detail"] == "Weather data for city 'NonExistentCity' not found."


@pytest.mark.asyncio
async def test_full_weather_lifecycle(client: AsyncClient):
    """Test POST -> GET -> PATCH -> DELETE flow via API."""

    # 1. POST
    payload = {
        "city": "LifecycleCity",
        "country": "LC",
        "temperature": 10.0,
        "humidity": 50,
        "pressure": 1000
    }
    post_resp = await client.post("/weather/", json=payload)
    assert post_resp.status_code == 201
    record_id = post_resp.json()["id"]

    # 2. GET
    get_resp = await client.get("/weather/LifecycleCity")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == record_id

    # 3. PATCH
    patch_payload = {"temperature": 99.9}
    patch_resp = await client.patch(f"/weather/{record_id}", json=patch_payload)
    assert patch_resp.status_code == 200
    assert patch_resp.json()["temperature"] == 99.9
    # Check if other fields are preserved
    assert patch_resp.json()["humidity"] == 50

    # 4. DELETE
    del_resp = await client.delete(f"/weather/{record_id}")
    assert del_resp.status_code == 204

    # 5. GET Again (Should be 404)
    final_get = await client.get("/weather/LifecycleCity")
    assert final_get.status_code == 404