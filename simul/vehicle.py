import pygame
import math
from utils import shortest_path

CELL_SIZE_M = 5

class Vehicle:
    def __init__(self, id, start_r, start_c, dir, speed_kmh, target_r, target_c):
        self.id = id
        self.start_r = start_r
        self.start_c = start_c
        self.dir = dir
        self.speed_kmh = speed_kmh
        self.target_r = target_r
        self.target_c = target_c

        self.x = start_c
        self.y = start_r
        self.arrived = False
        self.depart_time = None
        self.arrive_time = None
        self.path = []
        self.used_roads = []
        self.total_distance = 0.0

    def move(self, grid, signal_map, vehicles, sim_time):
        if self.arrived: return
        if self.depart_time is None:
            self.depart_time = sim_time

        if int(self.x)==self.target_c and int(self.y)==self.target_r:
            self.arrived = True
            self.arrive_time = sim_time
            self.path.append((int(self.y), int(self.x)))
            return

        if not self.path or self.path[-1] != (int(self.y), int(self.x)):
            self.path = shortest_path(
                grid.map, grid.rows, grid.cols,
                (int(self.y), int(self.x)),
                (self.target_r, self.target_c)
            )

        if not self.path or len(self.path)<2: return
        next_r, next_c = self.path[1]
        curr_rc = (int(self.y), int(self.x))
        next_rc = (next_r, next_c)
        curr_cap = grid.capacity.get(next_rc, 1)
        curr_cnt = sum(1 for v in vehicles if not v.arrived and (int(v.y), int(v.x))==next_rc)
        if curr_cnt >= curr_cap:
            return
        signal = signal_map.get_state(next_rc)
        if signal == 'red':
            return
        elif signal == 'yellow':
            speed_factor = 0.4
        else:
            speed_factor = 1.0

        speed_ms = self.speed_kmh * 1000 / 3600
        move_dist_m = speed_ms * speed_factor * (1/25)
        move_dist = move_dist_m / CELL_SIZE_M

        dx = next_c - self.x
        dy = next_r - self.y
        dist = math.hypot(dx, dy)
        if dist < 0.01: return
        ratio = min(move_dist/dist, 1.0)
        self.x += dx * ratio
        self.y += dy * ratio
        self.used_roads.append(curr_rc)
        self.total_distance += move_dist_m

    def draw(self, screen):
        cs = 40
        px = int(self.x * cs + cs//2)
        py = int(self.y * cs + cs//2)
        car_width = cs // 2
        car_height = cs // 3
        rect = pygame.Rect(px - car_width//2, py - car_height//2, car_width, car_height)
        pygame.draw.rect(screen, (20,120,255), rect, border_radius=8)
        pygame.draw.rect(screen, (40,40,60), rect, 2, border_radius=8)

    def get_direction(self):
        if not self.path or len(self.path)<2: return 'R'
        curr_r, curr_c = self.path[0]
        next_r, next_c = self.path[1]
        if next_r < curr_r: return 'U'
        if next_r > curr_r: return 'D'
        if next_c < curr_c: return 'L'
        return 'R'