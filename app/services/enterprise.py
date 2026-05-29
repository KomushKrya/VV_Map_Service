# app/services/enterprise.py
from typing import List, Dict, Optional
import math
from collections import defaultdict

from app.services.geocoder import geocode_address
from app.services.gateway_service import get_map_data_from_gateway, save_cluster_coordinates_to_gateway


async def get_all_enterprises(with_coordinates: bool = True) -> List[Dict]:
    """
    Запрашивает данные из БД, при необходимости геокодирует координаты КЛАСТЕРА
    и трансформирует данные в формат предприятий для карты.
    """
    raw_data = await get_map_data_from_gateway()
    enterprises = []

    geocoded_clusters_cache = {}

    for item in raw_data:
        cluster_id = item["cluster_id"]
        lat = item.get("cluster_latitude")
        lon = item.get("cluster_longitude")

        if lat is None or lon is None:
            if cluster_id in geocoded_clusters_cache:
                lat, lon = geocoded_clusters_cache[cluster_id]
            else:
                try:
                    geo_lat, geo_lon, _ = await geocode_address(item["cluster_address"])
                    if geo_lat is not None:
                        print(f"!!! ГЕОКОДЕР СРАБОТАЛ для кластера {item['cluster_name']} -> {geo_lat}, {geo_lon}")

                        await save_cluster_coordinates_to_gateway(cluster_id, geo_lat, geo_lon)

                        geocoded_clusters_cache[cluster_id] = (geo_lat, geo_lon)
                        lat, lon = geo_lat, geo_lon
                except Exception as e:
                    print(f"Ошибка геокодирования для кластера {cluster_id}: {e}")
                    lat, lon = None, None

        if with_coordinates and (lat is None or lon is None):
            continue

        enterprise = {
            "id": item["id"],
            "name": f"{item['franchise_name']} {item['cluster_name']}",
            "franchise_id": item["franchise_id"],
            "franchise_name": item["franchise_name"],
            "cluster_id": cluster_id,
            "cluster_name": item["cluster_name"],
            "address": item["cluster_address"],
            "coordinates": {
                "latitude": lat,
                "longitude": lon
            } if lat and lon else None
        }
        enterprises.append(enterprise)

    return enterprises


async def get_enterprise_by_id(enterprise_id: int) -> Optional[Dict]:
    enterprises = await get_all_enterprises(with_coordinates=True)
    for e in enterprises:
        if e["id"] == enterprise_id:
            return e
    return None


async def get_clusters_from_enterprises(enterprises: List[Dict]) -> List[Dict]:
    """
    Группирует переданные заведения обратно в уникальные кластеры для отображения на карте.
    """
    clusters_dict = {}

    for e in enterprises:
        cluster_id = e["cluster_id"]
        if cluster_id not in clusters_dict:
            clusters_dict[cluster_id] = {
                "id": cluster_id,
                "name": e.get("cluster_name", f"Фудкорт {cluster_id}"),
                "address": e["address"],
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
            "address": data["address"],
            "coordinates": {
                "latitude": lat_sum / count,
                "longitude": lon_sum / count
            },
            "enterprise_count": count
        })

    return clusters


def distribute_enterprises_in_clusters(enterprises: List[Dict]) -> List[Dict]:
    """
    Разносит заведения в одном кластере по кругу, чтобы маркеры на карте не слипались.
    """
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