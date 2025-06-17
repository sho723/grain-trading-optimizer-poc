from dataclasses import dataclass
from datetime import datetime
from typing import List
from enum import Enum

class CargoType(Enum):
    CORN = "トウモロコシ"
    MILO = "マイロ"
    FEED_BARLEY = "飼料麦"

@dataclass
class Berth:
    id: str
    name: str
    port_name: str
    max_capacity: int
    daily_handling_capacity: int
    daily_cost: int

@dataclass
class Cargo:
    cargo_type: CargoType
    quantity: int

@dataclass
class MainVessel:
    id: str
    name: str
    capacity: int
    arrival_date: datetime
    origin_port: str
    cargos: List[Cargo]
    total_quantity: int = 0
    
    def __post_init__(self):
        self.total_quantity = sum(cargo.quantity for cargo in self.cargos)

@dataclass
class Schedule:
    vessel: MainVessel
    berth: Berth
    start_date: datetime
    handling_days: int
    total_cost: int
