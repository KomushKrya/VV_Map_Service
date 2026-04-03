import httpx
from typing import Tuple
from app.config import get_settings

settings = get_settings()

async def geocode_address(address: str) -> Tuple[float, float, str]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://geocode-maps.yandex.ru/1.x/",
                params={
                    "apikey": settings.yandex_api_key,
                    "geocode": address,
                    "format": "json"
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()

            geo_object = data["response"]["GeoObjectCollection"]["featureMember"]

            if not geo_object:
                return None, None, "not_found"

            point = geo_object[0]["GeoObject"]["Point"]["pos"]
            longitude, latitude = map(float, point.split())
            precision = "exact"

            return latitude, longitude, precision

        except httpx.TimeoutException:
            raise Exception("Таймаут при обращении к Яндекс.Геокодеру")
        except httpx.HTTPStatusError as e:
            raise Exception(f"Ошибка HTTP при геокодировании: {e}")
        except Exception as e:
            raise Exception(f"Ошибка при геокодировании адреса '{address}': {e}")