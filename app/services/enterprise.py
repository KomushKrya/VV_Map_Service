from typing import List, Dict, Optional
from app.services.geocoder import geocode_address
from app.services.mock_gateway import get_enterprises_from_gateway
import math
from collections import defaultdict

_coordinates_cache = {}

async def get_all_enterprises(with_coordinates: bool = True) -> List[Dict]:
    enterprises = await get_enterprises_from_gateway()

    if not with_coordinates:
        return enterprises

    for enterprise in enterprises:
        coords = await _get_or_geocode_coordinates(
            enterprise["id"],
            enterprise["address"]
        )
        if coords:
            enterprise["coordinates"] = {
                "latitude": coords[0],
                "longitude": coords[1]
            }
        else:
            enterprise["coordinates"] = None

    return [e for e in enterprises if e.get("coordinates")]


async def _get_or_geocode_coordinates(enterprise_id: int, address: str) -> Optional[tuple]:
    if enterprise_id in _coordinates_cache:
        return _coordinates_cache[enterprise_id]

    try:
        lat, lon, precision = await geocode_address(address)
        if lat is not None:
            _coordinates_cache[enterprise_id] = (lat, lon)
            return (lat, lon)
    except Exception as e:
        print(f"Ошибка геокодирования {address}: {e}")

    return None


async def get_enterprise_by_id(enterprise_id: int) -> Optional[Dict]:
    enterprises = await get_all_enterprises(with_coordinates=True)
    for e in enterprises:
        if e["id"] == enterprise_id:
            return e
    return None


async def get_clusters_from_enterprises(enterprises: List[Dict]) -> List[Dict]:
    clusters_dict = {}

    for e in enterprises:
        cluster_id = e["cluster_id"]
        if cluster_id not in clusters_dict:
            clusters_dict[cluster_id] = {
                "id": cluster_id,
                "name": f"Фудкорт {cluster_id}",
                "enterprises": []
            }
        clusters_dict[cluster_id]["enterprises"].append(e)

    clusters = []
    for cluster_id, data in clusters_dict.items():
        enterprises_list = data["enterprises"]
        lat_sum = sum(e["coordinates"]["latitude"] for e in enterprises_list)
        lon_sum = sum(e["coordinates"]["longitude"] for e in enterprises_list)
        count = len(enterprises_list)

        clusters.append({
            "id": cluster_id,
            "name": data["name"],
            "coordinates": {
                "latitude": lat_sum / count,
                "longitude": lon_sum / count
            },
            "enterprise_count": count
        })

    return clusters


def distribute_enterprises_in_clusters(enterprises: List[Dict]) -> List[Dict]:
    cluster_groups = defaultdict(list)
    for enterprise in enterprises:
        cluster_id = enterprise["cluster_id"]
        cluster_groups[cluster_id].append(enterprise)

    result = []
    for cluster_id, group in cluster_groups.items():
        if len(group) == 1:
            result.append(group[0])
        else:
            radius = 0.00008
            center_lat = group[0]["coordinates"]["latitude"]
            center_lon = group[0]["coordinates"]["longitude"]

            for i, enterprise in enumerate(group):
                angle = (i / len(group)) * 2 * math.pi
                delta_lat = radius * math.cos(angle)
                delta_lon = radius * math.sin(angle)

                enterprise["coordinates"] = {
                    "latitude": center_lat + delta_lat,
                    "longitude": center_lon + delta_lon
                }
                result.append(enterprise)

    return result
