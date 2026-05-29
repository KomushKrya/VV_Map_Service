# app/services/gateway_service.py
import httpx
from typing import List, Dict, Any

GATEWAY_URL = "192.168.0.4:8001"


async def get_map_data_from_gateway() -> List[Dict[str, Any]]:
    """
    Получение сырых данных обо всех предприятиях и их кластерах.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{GATEWAY_URL}/database/map-data")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            print(f"Ошибка при запросе к Gateway GET /database/map-data: {exc}")
            return []


async def save_cluster_coordinates_to_gateway(cluster_id: int, latitude: float, longitude: float) -> bool:
    """
    Сохранение вычисленных/геокодированных координат для конкретного кластера.
    """
    url = f"{GATEWAY_URL}/database/cluster/{cluster_id}/coordinates"

    # Стандартный JSON-body для FastAPI POST-запросов
    payload = {
        "latitude": latitude,
        "longitude": longitude
    }

    async with httpx.AsyncClient() as client:
        try:
            # Если ваша БД-команда ожидает параметры в URL (Query params) вместо JSON-тела,
            # то замените `json=payload` на `params=payload`
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return True
        except httpx.HTTPError as exc:
            print(f"Ошибка при сохранении координат для кластера {cluster_id}: {exc}")
            return False