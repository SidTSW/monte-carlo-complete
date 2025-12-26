import pygame
import random
import math

# ==========================
# Monte Carlo Pi Estimator
# Enhanced + Interactive
# ==========================

pygame.init()

# --------------------------
# Screen & Settings
# --------------------------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Monte Carlo π Estimation — Interactive")

FPS = 120
clock = pygame.time.Clock()

# --------------------------
# Colors
# --------------------------
BLACK = (15, 15, 20)
WHITE = (240, 240, 240)
RED   = (255, 90, 90)
GREEN = (120, 255, 160)
BLUE  = (80, 170, 255)
GRAY  = (120, 120, 120)

# --------------------------
# Fonts
# --------------------------
font = pygame.font.SysFont("consolas", 20)
small_font = pygame.font.SysFont("consolas", 16)
big_font = pygame.font.SysFont("consolas", 28)

# --------------------------
# Simulation Parameters
# --------------------------
radius = 250
square_x = 50
square_y = HEIGHT - radius - 50
center = (square_x, square_y + radius)

points_per_frame = 200   # user adjustable
inside_circle = 0
total_points = 0
paused = False
show_trail = True

# --------------------------
# Helper Functions
# --------------------------
def draw_static():
    pygame.draw.rect(screen, WHITE, (square_x, square_y, radius, radius), 2)
    pygame.draw.circle(screen, BLUE, center, radius, 2)


def draw_ui(pi_estimate):
    pygame.draw.rect(screen, BLACK, (350, 20, 420, 200))

    title = big_font.render("Monte Carlo π Estimation", True, WHITE)
    screen.blit(title, (360, 25))

    screen.blit(font.render(f"π Estimate : {pi_estimate:.8f}", True, WHITE), (360, 70))
    screen.blit(font.render(f"Points     : {total_points}", True, WHITE), (360, 100))
    screen.blit(font.render(f"Inside     : {inside_circle}", True, WHITE), (360, 130))
    screen.blit(font.render(f"Speed      : {points_per_frame}/frame", True, WHITE), (360, 160))

    controls = [
        "SPACE  : Pause / Resume",
        "UP     : Increase speed",
        "DOWN   : Decrease speed",
        "C      : Clear & Reset",
        "T      : Toggle point trail"
    ]

    for i, text in enumerate(controls):
        screen.blit(small_font.render(text, True, GRAY), (360, 210 + i * 18))


# --------------------------
# Main Loop
# --------------------------
running = True
screen.fill(BLACK)
draw_static()

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_UP:
                points_per_frame = min(5000, points_per_frame + 100)
            if event.key == pygame.K_DOWN:
                points_per_frame = max(10, points_per_frame - 100)
            if event.key == pygame.K_c:
                screen.fill(BLACK)
                draw_static()
                inside_circle = 0
                total_points = 0
            if event.key == pygame.K_t:
                show_trail = not show_trail

    if not paused:
        for _ in range(points_per_frame):
            x = random.uniform(square_x, square_x + radius)
            y = random.uniform(square_y, square_y + radius)

            dist = math.dist((x, y), center)
            total_points += 1

            if dist <= radius:
                inside_circle += 1
                if show_trail:
                    pygame.draw.circle(screen, GREEN, (int(x), int(y)), 2)
            else:
                if show_trail:
                    pygame.draw.circle(screen, RED, (int(x), int(y)), 2)

    pi_estimate = 4 * inside_circle / total_points if total_points > 0 else 0

    draw_ui(pi_estimate)
    pygame.display.flip()

pygame.quit()
