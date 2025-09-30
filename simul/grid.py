import pygame
import math

ARROW_COLOR = (60, 60, 200)
ARROW_BG = (200, 200, 250)

def draw_arrow(screen, x, y, angle, size=16, thick=4):
    end_x = x + size * math.cos(angle)
    end_y = y + size * math.sin(angle)
    pygame.draw.line(screen, ARROW_COLOR, (x, y), (end_x, end_y), thick)
    ah = size // 2
    left = (end_x + ah * math.cos(angle + 2.5), end_y + ah * math.sin(angle + 2.5))
    right = (end_x + ah * math.cos(angle - 2.5), end_y + ah * math.sin(angle - 2.5))
    pygame.draw.polygon(screen, ARROW_COLOR, [(end_x, end_y), left, right])

class Grid:
    def __init__(self, road_map_path, capacity_map_path):
        self.map, self.rows, self.cols = self.load_map(road_map_path)
        self.capacity = self.load_capacity(capacity_map_path)
        self.cell_size = 40
        self.bg_color = (230, 230, 240)
        self.road_color = (215, 215, 220)
        self.road_edge_color = (140, 140, 140)
        self.build_color = (180, 140, 80)
        self.round_color = (160, 160, 210)

    def load_map(self, path):
        grid = []
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                grid.append(list(line))
        rows = len(grid)
        cols = max(len(row) for row in grid)
        grid = grid[::-1]
        return grid, rows, cols

    def load_capacity(self, path):
        cap = {}
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"): continue
                parts = line.split(',')
                if len(parts) < 3: continue
                r, c, val = map(int, parts)
                cap[(r, c)] = val
        return cap

    def draw(self, screen, signals, vehicles):
        for r in range(self.rows):
            for c in range(self.cols):
                x, y = c*self.cell_size, r*self.cell_size
                cell = self.map[r][c]
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                if cell == 'B':
                    pygame.draw.rect(screen, self.build_color, rect)
                elif cell == 'R':
                    pygame.draw.rect(screen, self.road_color, rect)
                    pygame.draw.rect(screen, self.road_edge_color, rect, 3)
                    dirs = []
                    for v in vehicles:
                        if (int(v.y), int(v.x)) == (r, c) and not v.arrived:
                            dirs.append(v.get_direction())
                    if dirs:
                        from collections import Counter
                        main_dir = Counter(dirs).most_common(1)[0][0]
                        angle = {'U':-math.pi/2, 'D':math.pi/2, 'L':math.pi, 'R':0}.get(main_dir, 0)
                        draw_arrow(screen, x+self.cell_size//2, y+self.cell_size//2, angle)
                elif cell == 'C':
                    pygame.draw.rect(screen, self.round_color, rect)
                    pygame.draw.rect(screen, (120,120,200), rect, 3)
                if (r, c) in signals:
                    color = signals[(r, c)]
                    col = {'red': (240,60,60), 'green': (80,220,80), 'yellow': (240,220,60)}.get(color, (220,220,220))
                    pygame.draw.circle(screen, col, (x+self.cell_size//2, y+self.cell_size//2), 14)

    def draw_background(self, screen):
        for i in range(self.cols+1):
            x = i*self.cell_size
            pygame.draw.line(screen, (100,100,130), (x,0), (x,self.rows*self.cell_size), 3)
        for j in range(self.rows+1):
            y = j*self.cell_size
            pygame.draw.line(screen, (100,100,130), (0,y), (self.cols*self.cell_size, y), 3)

    def get_average_congestion(self, vehicles):
        cell_count = {}
        for v in vehicles:
            if v.arrived: continue
            rc = (int(v.y), int(v.x))
            cell_count[rc] = cell_count.get(rc, 0) + 1
        ratios = []
        for rc, cnt in cell_count.items():
            cap = self.capacity.get(rc, 1)
            ratios.append(cnt / cap)
        return sum(ratios)/len(ratios) if ratios else 0