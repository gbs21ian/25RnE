import csv
import pygame
from collections import deque

def draw_text(screen, text, x, y, font, color):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def save_csv(fname, data):
    with open(fname, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for row in data:
            writer.writerow(row)

def shortest_path(grid, rows, cols, start, goal):
    q = deque()
    q.append((start, [start]))
    visited = set()
    while q:
        curr, path = q.popleft()
        if curr == goal:
            return path
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = curr[0]+dr, curr[1]+dc
            if 0<=nr<rows and 0<=nc<cols and grid[nr][nc] in ('R','C'):
                npos = (nr, nc)
                if npos not in visited:
                    visited.add(npos)
                    q.append((npos, path+[npos]))
    return []