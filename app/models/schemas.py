from pydantic import BaseModel
from typing import Optional, List

class Coordinates(BaseModel):
    latitude: float
    longitude: float

class Enterprise(BaseModel):
    id: int
    name: str
    franchise_id: int
    franchise_name: Optional[str] = None
    cluster_id: int
    address: str
    coordinates: Coordinates
    distance: Optional[float] = None

class Cluster(BaseModel):
    id: int
    name: str
    address: Optional[str] = None
    coordinates: Coordinates
    enterprise_count: int
    distance: Optional[float] = None

class MapDataResponse(BaseModel):
    view_type: str  # "clusters" or "enterprises"
    clusters: Optional[List[Cluster]] = None
    enterprises: Optional[List[Enterprise]] = None

class SelectRequest(BaseModel):
    enterprise_id: int

class SelectResponse(BaseModel):
    enterprise_id: int
    cluster_id: int
    enterprise_name: str
    franchise_id: int
    address: str
    coordinates: Coordinates

class GeocodeRequest(BaseModel):
    address: str

class GeocodeResponse(BaseModel):
    address: str
    coordinates: Coordinates
    precision: str