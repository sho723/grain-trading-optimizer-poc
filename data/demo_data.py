from datetime import datetime, timedelta
from typing import List
import random
from .models import *

def generate_demo_ports() -> List[Berth]:
    """デモ用バースデータ生成"""
    berths = [
        Berth(
            id="CHIBA_B1",
            name="千葉第1バース",
            port_name="千葉港",
            max_capacity=80000,
            daily_handling_capacity=3000,
            daily_cost=500000
        ),
        Berth(
            id="CHIBA_B2", 
            name="千葉第2バース",
            port_name="千葉港",
            max_capacity=60000,
            daily_handling_capacity=2500,
            daily_cost=400000
        ),
        Berth(
            id="YOKOHAMA_B1",
            name="横浜第1バース", 
            port_name="横浜港",
            max_capacity=70000,
            daily_handling_capacity=2800,
            daily_cost=450000
        ),
        Berth(
            id="KOBE_B1",
            name="神戸第1バース",
            port_name="神戸港", 
            max_capacity=75000,
            daily_handling_capacity=3200,
            daily_cost=480000
        )
    ]
    return berths

def generate_demo_vessels() -> List[MainVessel]:
    """デモ用本船データ生成"""
    vessels = []
    base_date = datetime(2025, 7, 1)  # 固定日付でデモ
    
    vessel_configs = [
        {
            "name": "GRAIN CARRIER 1",
            "origin": "ニューオーリンズ",
            "arrival_offset": 0,
            "cargos": [
                Cargo(CargoType.CORN, 45000),
                Cargo(CargoType.MILO, 12000)
            ]
        },
        {
            "name": "PACIFIC BULK 2", 
            "origin": "サンタフェ",
            "arrival_offset": 3,
            "cargos": [
                Cargo(CargoType.CORN, 40000),
                Cargo(CargoType.FEED_BARLEY, 15000)
            ]
        },
        {
            "name": "OCEAN TRADER 3",
            "origin": "ブエノスアイレス", 
            "arrival_offset": 7,
            "cargos": [
                Cargo(CargoType.CORN, 50000),
                Cargo(CargoType.MILO, 8000)
            ]
        },
        {
            "name": "BULK MASTER 4",
            "origin": "ニューオーリンズ",
            "arrival_offset": 10, 
            "cargos": [
                Cargo(CargoType.FEED_BARLEY, 35000),
                Cargo(CargoType.CORN, 20000)
            ]
        },
        {
            "name": "GRAIN EXPRESS 5",
            "origin": "サンタフェ",
            "arrival_offset": 14,
            "cargos": [
                Cargo(CargoType.CORN, 48000),
                Cargo(CargoType.MILO, 10000)
            ]
        }
    ]
    
    for i, config in enumerate(vessel_configs):
        vessels.append(MainVessel(
            id=f"MV_{i+1:03d}",
            name=config["name"],
            capacity=60000,
            arrival_date=base_date + timedelta(days=config["arrival_offset"]),
            origin_port=config["origin"],
            cargos=config["cargos"]
        ))
    
    return vessels
