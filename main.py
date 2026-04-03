from fastapi import FastAPI
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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(map_endpoints.router, prefix="/api/map", tags=["map"])

@app.get("/")
async def root():
    return {"message": "Map Microservice is running", "docs": "/docs"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}