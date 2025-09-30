from grid import Grid
from vehicle import Vehicle
from sig_nal import SignalMap
import time

BASE_PATH = r"C:\Users\clemd\OneDrive\문서\GBSH\2025\2025.ver1\R&E\2025 홍창욱T\simul"

class Simulation:
    def __init__(self, screen):
        self.screen = screen
        self.grid = Grid(
            f"{BASE_PATH}\\road_map.txt",
            f"{BASE_PATH}\\capacity_map.txt"
        )
        self.signal_map = SignalMap(f"{BASE_PATH}\\signal_patterns.txt")
        self.vehicles = []
        self.results = []
        self.finished = False
        self.start_time = time.time()
        self.load_vehicles(f"{BASE_PATH}\\vehicle_data.txt")

    def load_vehicles(self, path):
        self.vehicles.clear()
        with open(path, 'r', encoding='utf-8') as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(',')
                if len(parts) < 6: continue
                r, c, d, spd, tr, tc = parts[:6]
                self.vehicles.append(
                    Vehicle(idx, int(r), int(c), d, float(spd), int(tr), int(tc))
                )

    def update(self):
        if self.finished: return
        now = time.time()
        for v in self.vehicles:
            if not v.arrived:
                v.move(self.grid, self.signal_map, self.vehicles, now-self.start_time)
        if all(v.arrived for v in self.vehicles):
            self.stop()

    def stop(self):
        self.finished = True
        self.results = [
            {
                "id": v.id,
                "start": (v.start_r, v.start_c),
                "target": (v.target_r, v.target_c),
                "depart": v.depart_time,
                "arrive": v.arrive_time,
                "total": v.arrive_time - v.depart_time if v.arrived else None,
                "distance": v.total_distance,
                "avg_speed_kmh": (v.total_distance/(v.arrive_time-v.depart_time)) * 3.6 if v.arrived and (v.arrive_time-v.depart_time)>0 else 0,
                "path": v.path,
                "used_roads": v.used_roads
            }
            for v in self.vehicles
        ]

    def render(self):
        self.grid.draw(self.screen, self.signal_map.get_states(), self.vehicles)
        for v in self.vehicles:
            v.draw(self.screen)

    def draw_grid_background(self):
        self.grid.draw_background(self.screen)

    def get_live_stats(self):
        arrived = sum(v.arrived for v in self.vehicles)
        total = len(self.vehicles)
        times = [v.arrive_time-v.depart_time for v in self.vehicles if v.arrived]
        avg_time = sum(times)/len(times) if times else 0
        max_time = max(times) if times else 0
        min_time = min(times) if times else 0
        avg_speed = sum((v.total_distance/(v.arrive_time-v.depart_time))*3.6
                        for v in self.vehicles if v.arrived and (v.arrive_time-v.depart_time)>0) / arrived if arrived else 0
        avg_congestion = self.grid.get_average_congestion(self.vehicles)
        return [
            "[실시간 교통 통계]",
            f"도착 차량: {arrived}/{total}",
            f"평균 이동시간: {avg_time:.2f}s",
            f"평균 속도: {avg_speed:.2f} km/h",
            f"최소: {min_time:.2f}s | 최대: {max_time:.2f}s",
            f"평균 혼잡도: {avg_congestion:.2f}",
            "(스페이스바로 결과표/저장)",
            ""
        ]

    def get_results_table(self):
        lines = []
        lines.append("ID | Start | Target | Start | Arrive | Time | Distance(m) | AvgSpeed(km/h)")
        for r in self.results:
            lines.append(
                f"{r['id']} | {r['start']} | {r['target']} | {r['depart']:.1f} | {r['arrive']:.1f} | {r['total']:.1f} | {r['distance']:.1f} | {r['avg_speed_kmh']:.1f}"
            )
        return lines

    def get_results_csv(self):
        header = ["vehicle_id","start_r","start_c","target_r","target_c","depart_time","arrive_time","total_time","distance_m","avg_speed_kmh","path","used_roads"]
        rows = []
        for r in self.results:
            rows.append([
                r["id"], r["start"][0], r["start"][1], r["target"][0], r["target"][1],
                f"{r['depart']:.2f}", f"{r['arrive']:.2f}", f"{r['total']:.2f}",
                f"{r['distance']:.2f}", f"{r['avg_speed_kmh']:.2f}",
                ";".join(f"{x}" for x in r["path"]),
                ";".join(f"{x}" for x in r["used_roads"])
            ])
        return [header] + rows