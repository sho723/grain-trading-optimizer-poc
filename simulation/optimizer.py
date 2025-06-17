from datetime import datetime, timedelta
from typing import List, Optional
from ..data.models import *

class SimpleOptimizer:
    def __init__(self, berths: List[Berth], vessels: List[MainVessel]):
        self.berths = berths
        self.vessels = vessels
        self.schedules: List[Schedule] = []
        # バース占有状況管理
        self.berth_occupancy = {berth.id: [] for berth in berths}
    
    def optimize(self) -> List[Schedule]:
        """FCFS（先着順）による配船最適化"""
        self.schedules = []
        self.berth_occupancy = {berth.id: [] for berth in self.berths}
        
        # 到着日順にソート
        sorted_vessels = sorted(self.vessels, key=lambda v: v.arrival_date)
        
        for vessel in sorted_vessels:
            best_schedule = self._find_best_berth(vessel)
            if best_schedule:
                self.schedules.append(best_schedule)
                # バース占有情報を更新
                end_date = best_schedule.start_date + timedelta(days=best_schedule.handling_days)
                self.berth_occupancy[best_schedule.berth.id].append({
                    'start': best_schedule.start_date,
                    'end': end_date
                })
        
        return self.schedules
    
    def _find_best_berth(self, vessel: MainVessel) -> Optional[Schedule]:
        """船舶に最適なバースを見つける"""
        best_schedule = None
        min_total_cost = float('inf')
        
        for berth in self.berths:
            # 容量チェック
            if vessel.total_quantity > berth.max_capacity:
                continue
                
            schedule = self._calculate_schedule(vessel, berth)
            if schedule and schedule.total_cost < min_total_cost:
                min_total_cost = schedule.total_cost
                best_schedule = schedule
        
        return best_schedule
    
    def _calculate_schedule(self, vessel: MainVessel, berth: Berth) -> Optional[Schedule]:
        """特定バースでのスケジュール計算"""
        # 荷役日数計算
        handling_days = max(1, (vessel.total_quantity + berth.daily_handling_capacity - 1) // berth.daily_handling_capacity)
        
        # 利用可能開始日を計算
        start_date = self._find_available_start_date(berth, vessel.arrival_date, handling_days)
        
        # コスト計算
        berth_cost = berth.daily_cost * handling_days
        
        # 待機コスト（簡略化: 1日150万円）
        waiting_days = max(0, (start_date - vessel.arrival_date).days)
        waiting_cost = waiting_days * 1500000
        
        total_cost = berth_cost + waiting_cost
        
        return Schedule(
            vessel=vessel,
            berth=berth,
            start_date=start_date,
            handling_days=handling_days,
            total_cost=total_cost
        )
    
    def _find_available_start_date(self, berth: Berth, desired_date: datetime, duration_days: int) -> datetime:
        """バースの利用可能開始日を計算"""
        occupancies = sorted(self.berth_occupancy[berth.id], key=lambda x: x['start'])
        
        candidate_date = max(desired_date, datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
        
        for occupancy in occupancies:
            # 重複チェック
            candidate_end = candidate_date + timedelta(days=duration_days)
            if candidate_date < occupancy['end'] and candidate_end > occupancy['start']:
                candidate_date = occupancy['end']
        
        return candidate_date
