# app/main.py
from fastapi import FastAPI
from fastapi.routing import APIRoute
from app.api.endpoints import map as map_endpoints
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Map Microservice",
    description="Сервис для работы с картой ресторанов",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем основные роуты карты
app.include_router(map_endpoints.router, prefix="/api/map", tags=["map"])


# --- ЭНДПОИНТ ДЛЯ API GATEWAY ---
@app.get("/routes")
async def get_routes():
    """
    Динамически собирает все эндпоинты микросервиса карты
    и отдаёт их в формате, требуемом API Gateway.
    """
    routes_list = []

    for route in app.routes:
        # Проверяем, что это обычный эндпоинт, а не служебный (документация или сам /routes)
        if isinstance(route, APIRoute):
            if route.path in ["/docs", "/redoc", "/openapi.json", "/routes", "/", "/health"]:
                continue

            for method in route.methods:
                routes_list.append({
                    "method": method.upper(),
                    "path": route.path
                })

    return {"routes": routes_list}


@app.get("/")
async def root():
    return {"message": "Map Microservice is running", "docs": "/docs"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}