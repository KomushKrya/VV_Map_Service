
MOCK_ENTERPRISES_FROM_DB = [
    {
        "id": 1,
        "name": "Rostics на Юности",
        "franchise_id": 2,
        "franchise_name": "Rostics",
        "cluster_id": 1,
        "address": "Зеленоград, площадь Юности 2 ст1"
    },
    {
        "id": 2,
        "name": "ВиТ Иридиум",
        "franchise_id": 1,
        "franchise_name": "Вкусно и Точка",
        "cluster_id": 2,
        "address": "Крюковская площадь 1"
    },
    {
        "id": 3,
        "name": "Rostics Иридиум",
        "franchise_id": 2,
        "franchise_name": "Rostics",
        "cluster_id": 2,
        "address": "Крюковская площадь 1"
    },
    {
        "id": 4,
        "name": "Бургер Кинг Иридиум",
        "franchise_id": 3,
        "franchise_name": "Бургер Кинг",
        "cluster_id": 2,
        "address": "Крюковская площадь 1"
    }
]

async def get_enterprises_from_gateway():
    return MOCK_ENTERPRISES_FROM_DB