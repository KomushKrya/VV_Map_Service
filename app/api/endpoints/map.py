from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from app.models.schemas import (
    MapDataResponse, Cluster, Enterprise, Coordinates,
    SelectRequest, SelectResponse, GeocodeRequest, GeocodeResponse
)
from app.config import get_settings, Settings
from app.services import enterprise as enterprise_service
from app.services.geocoder import geocode_address
import math

router = APIRouter()


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


@router.get("/data", response_model=MapDataResponse)
async def get_map_data(
        zoom: int = Query(..., description="Текущий уровень приближения"),
        user_lat: Optional[float] = Query(None, description="Широта пользователя"),
        user_lon: Optional[float] = Query(None, description="Долгота пользователя"),
        north: Optional[float] = Query(None, description="Северная граница"),
        south: Optional[float] = Query(None, description="Южная граница"),
        east: Optional[float] = Query(None, description="Восточная граница"),
        west: Optional[float] = Query(None, description="Западная граница"),
        settings: Settings = Depends(get_settings)
):

    enterprises_data = await enterprise_service.get_all_enterprises(with_coordinates=True)

    if all([north, south, east, west]):
        filtered_enterprises = []
        for e in enterprises_data:
            lat = e["coordinates"]["latitude"]
            lon = e["coordinates"]["longitude"]
            if south <= lat <= north and west <= lon <= east:
                filtered_enterprises.append(e)
        enterprises_data = filtered_enterprises

    if zoom < settings.zoom_threshold:
        clusters = await enterprise_service.get_clusters_from_enterprises(enterprises_data)

        if user_lat is not None and user_lon is not None:
            for cluster in clusters:
                cluster["distance"] = calculate_distance(
                    user_lat, user_lon,
                    cluster["coordinates"]["latitude"],
                    cluster["coordinates"]["longitude"]
                )
            clusters.sort(key=lambda x: x.get("distance", float("inf")))

        return MapDataResponse(
            view_type="clusters",
            clusters=[Cluster(**c) for c in clusters]
        )
    else:
        enterprises = []
        enterprises_data = enterprise_service.distribute_enterprises_in_clusters(enterprises_data)
        for e in enterprises_data:
            enterprise = {
                "id": e["id"],
                "name": e["name"],
                "franchise_id": e["franchise_id"],
                "franchise_name": e["franchise_name"],
                "cluster_id": e["cluster_id"],
                "address": e["address"],
                "coordinates": Coordinates(**e["coordinates"])
            }

            if user_lat is not None and user_lon is not None:
                enterprise["distance"] = calculate_distance(
                    user_lat, user_lon,
                    e["coordinates"]["latitude"],
                    e["coordinates"]["longitude"]
                )
            enterprises.append(enterprise)

        if user_lat is not None and user_lon is not None:
            enterprises.sort(key=lambda x: x.get("distance", float("inf")))

        return MapDataResponse(
            view_type="enterprises",
            enterprises=[Enterprise(**e) for e in enterprises]
        )


@router.post("/select", response_model=SelectResponse)
async def select_enterprise(
        request: SelectRequest,
):
    # Не забываем про await, который мы исправили!
    enterprise = await enterprise_service.get_enterprise_by_id(request.enterprise_id)

    if not enterprise:
        raise HTTPException(status_code=404, detail="Предприятие не найдено")

    # Возвращаем фронтенду ID и адрес КЛАСТЕРА, а не ресторана, как вы и просили
    return SelectResponse(
        enterprise_id=enterprise["id"],
        cluster_id=enterprise["cluster_id"],
        enterprise_name=enterprise["name"],
        franchise_id=enterprise["franchise_id"],
        address=enterprise["cluster_address"],  # <--- Адрес КЛАСТЕРА
        coordinates=Coordinates(
            latitude=enterprise["cluster_latitude"],   # <--- Координаты ЦЕНТРА КЛАСТЕРА
            longitude=enterprise["cluster_longitude"]
        )
    )

@router.post("/geocode", response_model=GeocodeResponse)
async def geocode_address_endpoint(
        request: GeocodeRequest,
        settings: Settings = Depends(get_settings)
):
    try:
        latitude, longitude, precision = await geocode_address(request.address)

        if latitude is None:
            raise HTTPException(
                status_code=404,
                detail=f"Адрес '{request.address}' не найден"
            )

        return GeocodeResponse(
            address=request.address,
            coordinates=Coordinates(latitude=latitude, longitude=longitude),
            precision=precision
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))