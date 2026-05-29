# app/services/mock_gateway.py

# Имитация таблицы кластеров (теперь адрес и координаты живут тут)
MOCK_CLUSTERS_DB = {
    1: {
        "id": 1,
        "name": "Площадь Юности",
        "address": "Зеленоград, площадь Юности 2 ст1",
        "latitude": None,  # Сначала координат нет, они заполнятся через геокодер
        "longitude": None
    },
    2: {
        "id": 2,
        "name": "ТЦ Иридиум",
        "address": "Зеленоград, Крюковская площадь 1",
        "latitude": None,
        "longitude": None
    }
}

MOCK_FRANCHISES_DB = {
    1: "Вкусно и Точка",
    2: "Rostics",
    3: "Бургер Кинг"
}

# Имитация таблицы предприятий (чистая связь)
MOCK_ENTERPRISES_DB = [
    {"id": 1, "name": "Rostics на Юности", "franchise_id": 2, "cluster_id": 1},
    {"id": 2, "name": "ВиТ Иридиум", "franchise_id": 1, "cluster_id": 2},
    {"id": 3, "name": "Rostics Иридиум", "franchise_id": 2, "cluster_id": 2},
    {"id": 4, "name": "Бургер Кинг Иридиум", "franchise_id": 3, "cluster_id": 2}
]


async def get_enterprises_from_gateway():
    """
    ЗАПРОС №1 (GET на реальном гейтвее): Получение плоского списка предприятий с данными их кластеров.
    Реальный Gateway будет делать SQL запрос с JOIN таблиц clusters и franchises.
    """
    enriched_enterprises = []
    for ent in MOCK_ENTERPRISES_DB:
        cluster = MOCK_CLUSTERS_DB[ent["cluster_id"]]
        franchise_name = MOCK_FRANCHISES_DB[ent["franchise_id"]]

        enriched_enterprises.append({
            "id": ent["id"],
            "name": ent["name"],
            "franchise_id": ent["franchise_id"],
            "franchise_name": franchise_name,
            "cluster_id": cluster["id"],
            "cluster_name": cluster["name"],
            "cluster_address": cluster["address"],
            "cluster_latitude": cluster["latitude"],
            "cluster_longitude": cluster["longitude"]
        })
    return enriched_enterprises


async def save_cluster_coordinates_to_gateway(cluster_id: int, latitude: float, longitude: float):
    """
    ЗАПРОС №2 (POST/PUT на реальном гейтвее): Обновление координат конкретного кластера в БД.
    """
    if cluster_id in MOCK_CLUSTERS_DB:
        MOCK_CLUSTERS_DB[cluster_id]["latitude"] = latitude
        MOCK_CLUSTERS_DB[cluster_id]["longitude"] = longitude
        print(f"[Gateway] Координаты кластера {cluster_id} успешно сохранены в БД: {latitude}, {longitude}")
        return {"status": "success"}
    return {"status": "error", "message": "Cluster not found"}