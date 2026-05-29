# app/services/gateway_service.py
import httpx
from typing import List, Dict, Any
import os

GATEWAY_URL= os.getenv("GATEWAY_URL")

GATEWAY_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}


async def get_map_data_from_gateway() -> List[Dict[str, Any]]:
    """
    Получение сырых данных обо всех предприятиях и их кластерах.
    """
    async with httpx.AsyncClient(headers=GATEWAY_HEADERS) as client:
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
    payload = {
        "cluster_latitude": latitude,
        "cluster_longitude": longitude
    }

    async with httpx.AsyncClient(headers=GATEWAY_HEADERS) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 422:
                print(f" СЕРВЕР БД ОТКЛОНИЛ ДАННЫЕ (422). ОТВЕТ: {exc.response.text}")
            else:
                print(f"Ошибка при сохранении координат для кластера {cluster_id}: {exc}")
            return False
        except httpx.HTTPError as exc:
            print(f"Сетевая ошибка при запросе к Gateway: {exc}")
            return False