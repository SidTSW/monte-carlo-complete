import pygame
import random
import math

# ==============================================================
# Monte Carlo Transport Lab — GRAND GUIDED VERSION
# Shows how statistical laws emerge from random motion
# ==============================================================

pygame.init()

# -------------------- Screen --------------------
WIDTH, HEIGHT = 1400, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Monte Carlo Transport Lab — From Randomness to Law")
clock = pygame.time.Clock()
FPS = 60

# -------------------- Colors --------------------
BG = (8, 8, 14)
CYAN = (0, 255, 220)
RED = (255, 90, 90)
BLUE = (90, 170, 255)
TEXT = (235, 235, 235)
MUTED = (140, 140, 160)

# -------------------- Fonts --------------------
font = pygame.font.SysFont("consolas", 15)
big_font = pygame.font.SysFont("consolas", 28)
mid_font = pygame.font.SysFont("consolas", 20)

# -------------------- Physics --------------------
SPEED = 3
MEAN_FREE_PATH = 80
ABSORB_PROB = 0.25

# -------------------- Detector --------------------
DETECTOR = pygame.Rect(520, 150, 24, 450)
detector_hits = 0
detector_signal = 0.0

# -------------------- Heatmap --------------------
GRID = 8
grid_w = WIDTH // GRID
grid_h = HEIGHT // GRID
heatmap = [[0 for _ in range(grid_h)] for _ in range(grid_w)]

# -------------------- State --------------------
running = True
paused = False
guided_stage = 0
particles_to_emit = 1
emitted = 0
started = False

# -------------------- Prediction tracking --------------------
prob_history = []

# -------------------- Glow helper --------------------
def draw_glow_circle(x, y, color, r):
    # Stronger neon glow using multi-layer additive alpha
    glow = pygame.Surface((r*12, r*12), pygame.SRCALPHA)
    cx = cy = r*6

    # Outer soft bloom
    for rr, a in [(r*5, 10), (r*4, 18), (r*3, 30)]:
        pygame.draw.circle(glow, (*color, a), (cx, cy), rr)

    # Inner intense glow
    for rr, a in [(r*2, 80), (r, 180)]:
        pygame.draw.circle(glow, (*color, a), (cx, cy), rr)

    screen.blit(glow, (x-cx, y-cy))
    pygame.draw.circle(screen, color, (int(x), int(y)), r)

# -------------------- Particle --------------------
class Particle:
    def __init__(self):
        self.x = 250
        self.y = HEIGHT // 2
        self.angle = random.uniform(0, 2 * math.pi)
        self.dist_left = -MEAN_FREE_PATH * math.log(random.random())
        self.alive = True

    def update(self):
        global detector_hits, detector_signal
        if not self.alive:
            return

        vx = SPEED * math.cos(self.angle)
        vy = SPEED * math.sin(self.angle)
        self.x += vx
        self.y += vy
        self.dist_left -= math.hypot(vx, vy)

        gx = int(self.x // GRID)
        gy = int(self.y // GRID)
        if 0 <= gx < grid_w and 0 <= gy < grid_h:
            heatmap[gx][gy] += 1

        if DETECTOR.collidepoint(self.x, self.y):
            detector_hits += 1
            detector_signal = 1.0
            self.alive = False
            return

        if self.dist_left <= 0:
            if random.random() < ABSORB_PROB:
                self.alive = False
            else:
                self.angle = random.uniform(0, 2 * math.pi)
                self.dist_left = -MEAN_FREE_PATH * math.log(random.random())

        if not (0 <= self.x <= WIDTH and 0 <= self.y <= HEIGHT):
            self.alive = False

    def draw(self):
        if self.alive:
            draw_glow_circle(self.x, self.y, CYAN, 2)

particles = []

# -------------------- Helper --------------------
def reset_sim():
    global particles, detector_hits, detector_signal, emitted, prob_history
    particles = []
    detector_hits = 0
    detector_signal = 0.0
    emitted = 0
    prob_history.clear()
    for i in range(grid_w):
        for j in range(grid_h):
            heatmap[i][j] = 0

reset_sim()

# -------------------- Guided stages --------------------
stages = [
    ("Stage 1: One particle", "One particle tells us nothing."),
    ("Stage 2: Few particles", "Small samples are noisy."),
    ("Stage 3: Many particles", "Patterns begin to emerge."),
    ("Stage 4: Large ensemble", "Statistics converge to laws."),
]

# -------------------- Main loop --------------------
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_n:
                guided_stage = min(guided_stage + 1, len(stages)-1)
                reset_sim()
                particles_to_emit = [1, 20, 200, 800][guided_stage]
                started = False
            if event.key == pygame.K_b:
                guided_stage = max(guided_stage - 1, 0)
                reset_sim()
                particles_to_emit = [1, 20, 200, 800][guided_stage]
                started = False
            if event.key == pygame.K_s:
                started = True
            if event.key == pygame.K_r:
                reset_sim()
        if event.type == pygame.MOUSEBUTTONDOWN and guided_stage == 0:
            start_button = pygame.Rect(200, 350, 150, 50)
            if start_button.collidepoint(event.pos):
                started = True

    screen.fill(BG)

    # ---------------- World panel ----------------
    pygame.draw.rect(screen, BLUE, (0, 0, 560, HEIGHT), 1)
    screen.blit(mid_font.render("PHYSICAL WORLD", True, TEXT), (20, 20))

    # Draw start button on stage 0 before started
    if guided_stage == 0 and not started:
        start_button = pygame.Rect(200, 350, 150, 50)
        pygame.draw.rect(screen, CYAN, start_button, 2)
        screen.blit(mid_font.render("START", True, CYAN), (215, 360))

    if not paused and emitted < particles_to_emit and (guided_stage > 0 or started):
        particles.append(Particle())
        emitted += 1

    for p in particles:
        p.update()
        p.draw()

    pygame.draw.rect(screen, RED, DETECTOR, 2)
    glow_r = int(6 + 30 * detector_signal)
    draw_glow_circle(DETECTOR.centerx, DETECTOR.centery, RED, glow_r)
    detector_signal *= 0.95

    # Heatmap overlay
    for i in range(0, grid_w):
        for j in range(0, grid_h):
            val = heatmap[i][j]
            if val > 0:
                intensity = min(100, val // 8)
                cell = pygame.Surface((GRID, GRID), pygame.SRCALPHA)
                cell.fill((intensity, 30, 30, 40))
                screen.blit(cell, (i*GRID, j*GRID))

    # ---------------- Prediction panel ----------------
    pygame.draw.rect(screen, BLUE, (580, 0, 420, HEIGHT), 1)
    screen.blit(mid_font.render("STATISTICS & PREDICTION", True, TEXT), (600, 20))

    prob = 0.0
    if emitted > 0:
        prob = detector_hits / emitted
        prob_history.append(prob)

    screen.blit(font.render(f"Detected / Emitted = {detector_hits} / {emitted}", True, TEXT), (600, 60))
    screen.blit(font.render(f"Detection probability ≈ {prob:.3f}", True, TEXT), (600, 80))

    # Convergence graph
    if len(prob_history) > 2:
        graph_x, graph_y = 600, 140
        graph_w, graph_h = 360, 200
        pygame.draw.rect(screen, (40,40,60), (graph_x, graph_y, graph_w, graph_h))
        pygame.draw.rect(screen, MUTED, (graph_x, graph_y, graph_w, graph_h), 1)
        max_pts = min(len(prob_history), graph_w)
        for i in range(1, max_pts):
            x1 = graph_x + i - 1
            y1 = graph_y + graph_h - prob_history[i-1] * graph_h
            x2 = graph_x + i
            y2 = graph_y + graph_h - prob_history[i] * graph_h
            pygame.draw.line(screen, CYAN, (x1, y1), (x2, y2), 2)

    # ---------------- Explanation panel ----------------
    pygame.draw.rect(screen, BLUE, (1020, 0, 380, HEIGHT), 1)
    screen.blit(mid_font.render("GUIDED EXPLANATION", True, TEXT), (1040, 20))

    title, text = stages[guided_stage]
    screen.blit(big_font.render(title, True, TEXT), (1040, 70))
    screen.blit(font.render(text, True, MUTED), (1040, 110))

    explain = [
        "Each particle moves randomly.",
        "Individual paths are unpredictable.",
        "But the fraction reaching the detector",
        "stabilizes.",
        "Physics predicts probabilities, not paths.",
    ]

    for i, line in enumerate(explain):
        screen.blit(font.render(line, True, MUTED), (1040, 160 + i*20))

    # Footer
    screen.blit(font.render("B: Previous | N: Next stage | SPACE: Pause | R: Reset", True, MUTED), (20, HEIGHT-30))
    screen.blit(font.render("Random motion → Predictable statistics", True, TEXT), (500, HEIGHT-30))

    pygame.display.flip()

pygame.quit()
