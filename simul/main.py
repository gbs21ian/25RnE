import pygame
import sys
import threading
from simulation import Simulation
from utils import draw_text, save_csv
from stats_popup import StatsPopup

MAIN_WIDTH, MAIN_HEIGHT = 800, 640
BG_COLOR = (230, 230, 240)
FONT_NAME = "arial"

def run_stats_popup(sim):
    popup = StatsPopup(sim)
    popup.run()

def main():
    pygame.init()
    screen = pygame.display.set_mode((MAIN_WIDTH, MAIN_HEIGHT))
    pygame.display.set_caption("California Traffic Simulation (Braess Paradox)")
    sim = Simulation(screen)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(FONT_NAME, 18)
    running = True
    show_result = False

    # 통계창(StatsPopup)을 별도의 쓰레드로 실행
    stats_thread = threading.Thread(target=run_stats_popup, args=(sim,), daemon=True)
    stats_thread.start()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    sim.stop()
                    show_result = True
                    save_csv("results.csv", sim.get_results_csv())

        screen.fill(BG_COLOR)
        sim.draw_grid_background()
        sim.update()
        sim.render()

        pygame.display.flip()
        clock.tick(25)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()