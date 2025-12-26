"""
Monte Carlo exoplanet transit probability visualization (Pygame)

- Randomly samples star+planet systems and checks geometric transit condition.
- Visualizes systems as dots (green = transit, red = no-transit).
- Shows running estimate of transit probability and approximate standard error.
- Click a transiting dot to see a simple transit animation + light curve sample.

"""

import pygame
import numpy as np
import math
import random
import sys
from collections import deque

# -----------------------------
# PARAMETERS (easy to tweak)
# -----------------------------
SCREEN_W, SCREEN_H = 1500, 700
PANEL_W = 320  # right-hand info panel
FIELD_W = SCREEN_W - PANEL_W
FIELD_H = SCREEN_H
FPS = 60

# Physical-ish units (normalized)
# We'll measure distances in stellar radii (R_star = 1 unit)
R_star_mean = 1.0   # stellar radius (units)
R_planet_mean = 0.1 # typical planet radius (units) — 0.1 = 0.1 stellar radii ~1 Jupiter around Sun is ~0.1
a_min, a_max = 3.0, 200.0  # semi-major axes in stellar radii (3 to 200 * R_star)

# Monte Carlo control
systems_per_frame = 500  # how many random systems to sample each frame (increase for faster convergence)
MAX_POINTS_DISPLAY = 2000  # how many dots to keep on screen (visual window)

# Colors
BG = (10, 12, 20)
PANEL_BG = (18, 20, 28)
GRID_COLOR = (30, 35, 50)
TEXT_COL = (230, 230, 230)
TRANSIT_COLOR = (100, 255, 130)
NO_TRANSIT_COLOR = (255, 110, 110)
HIGHLIGHT = (255, 220, 80)

# Dot drawing
DOT_MIN = 2
DOT_MAX = 6

# Seed RNG (optional)
np.random.seed(42)
random.seed(42)

# -----------------------------
# Pygame init
# -----------------------------
pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Monte Carlo — Exoplanet Transit Probability")
font = pygame.font.SysFont("consolas", 16)
small_font = pygame.font.SysFont("consolas", 14)
clock = pygame.time.Clock()

# -----------------------------
# Statistics / storage
# -----------------------------
total_samples = 0
transit_count = 0

# Keep a rolling display list of recent systems (for visualization)
# Each entry: (x, y, is_transit, a, R_p, i, timestamp_id)
display_points = deque(maxlen=MAX_POINTS_DISPLAY)
point_id_counter = 0

# For showing a sample transit animation when clicking a transit point
active_transit = None
# structure: dict with keys 'a', 'Rp', 'Rstar', 'phase', 'duration_steps', 'lc' (light curve array), 'progress'

# -----------------------------
# Helper functions (physics)
# -----------------------------
def sample_system():
    """
    Sample random star-planet system parameters:
    - R_star: sampled around R_star_mean (small spread)
    - R_planet: sampled around R_planet_mean (spread)
    - a: semi-major axis sampled log-uniform between a_min and a_max (more realistic)
    - inclination: sampled uniformly in cos(i) between -1 and 1 (random orientations)
    Returns (R_star, R_planet, a, inclination)
    """
    R_star = R_star_mean * (1.0 + 0.05 * np.random.randn())  # small scatter
    # positive radii
    R_star = max(0.5, R_star)

    R_p = R_planet_mean * (1.0 + 0.6 * np.random.randn())
    R_p = max(0.01, R_p)

    # log-uniform sample of a
    log_a = np.random.uniform(np.log(a_min), np.log(a_max))
    a = float(np.exp(log_a))

    # random inclination: cos(i) uniform on [-1,1], i in [0, pi]
    cosi = np.random.uniform(-1.0, 1.0)
    i = math.acos(cosi)  # inclination in radians

    return R_star, R_p, a, i

def has_transit(R_star, R_p, a, i):
    """
    Geometric transit test (approximate).
    For circular orbit, transit possible if |cos i| <= (R_star + R_p)/a.
    This condition assumes planet orbit radius a >> R_star is typical; it's the usual transit probability.
    """
    # guard against division by zero
    if a <= 0:
        return False
    threshold = (R_star + R_p) / a
    return abs(math.cos(i)) <= threshold

def transit_duration_estimate(R_star, a, P_days=365.0):
    """
    Very rough estimate of transit duration (in days).
    Using approximation T ≈ (P/π) * arcsin(R_star / a) for central transit,
    where P is orbital period. We don't compute realistic periods here; this is just to make a plausible animation timescale.
    We'll scale P ~ a^(3/2) (Kepler) with arbitrary normalization so durations are visually varied.
    """
    # approximate orbital period scaling (units arbitrary): P ~ a^(3/2)
    P = (a ** 1.5) * 0.02  # scale down so durations are seconds-level
    # central transit
    if a <= R_star:
        return max(0.1, P * 0.1)
    T = (P / math.pi) * math.asin(min(1.0, R_star / a))
    return max(0.05, T)

def sample_point_screen():
    """Return a random (x, y) within the left field area for plotting a sample system."""
    x = random.uniform(20, FIELD_W - 20)
    y = random.uniform(20, FIELD_H - 20)
    return int(x), int(y)

# -----------------------------
# Light curve generator for a sample transit (very simplified)
# -----------------------------
def make_synthetic_lightcurve(R_star, R_p, a, nsteps=200):
    """
    Generate a toy transit light curve array of length nsteps normalized around 1.
    Very approximate: assume box-shaped transit depth ~ (Rp/Rstar)^2 and smooth ingress/egress.
    """
    depth = (R_p / R_star) ** 2
    # duration shape
    dur_frac = min(0.5, (R_star + R_p) / a)  # fraction of "orbit" spent in transit (toy)
    ingress = max(3, int(nsteps * 0.06))
    flat = max(1, int(nsteps * dur_frac))
    egress = ingress
    # build curve
    curve = np.ones(nsteps)
    start = nsteps // 2 - (flat // 2) - ingress
    # ingress
    for t in range(ingress):
        frac = (t + 1) / ingress
        curve[start + t] = 1.0 - depth * (0.5 * (1 - math.cos(math.pi * frac)))
    # flat bottom
    for t in range(flat):
        curve[start + ingress + t] = 1.0 - depth
    # egress
    for t in range(egress):
        frac = (t + 1) / egress
        curve[start + ingress + flat + t] = 1.0 - depth * (0.5 * (1 + math.cos(math.pi * frac)))
    # small random noise
    curve += np.random.normal(0, 0.0008, size=nsteps)
    return curve.clip(0.0, 1.2)

# -----------------------------
# Main loop
# -----------------------------
running = True
paused = False

# for clickable points: store dict id -> (index in display_points)
point_id_map = {}

while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                running = False
            elif ev.key == pygame.K_SPACE:
                paused = not paused
            elif ev.key == pygame.K_r:
                # reset
                total_samples = 0
                transit_count = 0
                display_points.clear()
                point_id_counter = 0
                point_id_map.clear()
            elif ev.key == pygame.K_UP:
                systems_per_frame = min(100000, int(systems_per_frame * 1.5))
            elif ev.key == pygame.K_DOWN:
                systems_per_frame = max(1, int(systems_per_frame / 1.5))
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            if ev.button == 1:  # left click
                mx, my = ev.pos
                # only clickable inside left field
                if mx < FIELD_W:
                    # find nearest transit point within small radius
                    best = None
                    bestdist = 12
                    for idx, (x, y, is_transit, a, Rp, i, pid) in enumerate(display_points):
                        if not is_transit:
                            continue
                        dx = mx - x
                        dy = my - y
                        d = math.hypot(dx, dy)
                        if d < bestdist:
                            best = (idx, display_points[idx])
                            bestdist = d
                    if best is not None:
                        _, (x, y, is_transit, a, Rp, i, pid) = best
                        # create an active transit animation entry
                        active_transit = {
                            'a': a, 'Rp': Rp, 'Rstar': R_star_mean,
                            'phase': 0.0, 'nsteps': 240,
                            'lc': make_synthetic_lightcurve(R_star_mean, Rp, a, nsteps=240),
                            'progress': 0
                        }

    if not paused:
        # Monte Carlo sampling: sample many systems per frame
        for _ in range(systems_per_frame):
            Rstar, Rp, a, i = sample_system()
            transit = has_transit(Rstar, Rp, a, i)
            total_samples += 1
            if transit:
                transit_count += 1

            # store a display point
            x, y = sample_point_screen()
            # dot size could encode a / Rp ratio (visual)
            dot_size = int(np.interp(Rp / Rstar, [0.01, 0.5], [DOT_MIN, DOT_MAX]))
            pid = point_id_counter
            point_id_counter += 1
            display_points.append((x, y, transit, a, Rp, i, pid))

    # compute estimate and stderr
    p_hat = (transit_count / total_samples) if total_samples > 0 else 0.0
    # standard error for a proportion (binomial) ≈ sqrt(p(1-p)/N)
    stderr = math.sqrt(p_hat * (1 - p_hat) / total_samples) if total_samples > 0 else 0.0

    # ------------------ Drawing ------------------
    screen.fill(BG)

    # left field background grid
    # draw slight grid
    for gx in range(0, FIELD_W, 80):
        pygame.draw.line(screen, GRID_COLOR, (gx, 0), (gx, FIELD_H), 1)
    for gy in range(0, FIELD_H, 80):
        pygame.draw.line(screen, GRID_COLOR, (0, gy), (FIELD_W, gy), 1)

    # draw points
    for (x, y, transit, a, Rp, incl, pid) in display_points:
        color = TRANSIT_COLOR if transit else NO_TRANSIT_COLOR
        size = int(np.interp(min(a, 200), [a_min, a_max], [DOT_MAX, DOT_MIN]))
        pygame.draw.circle(screen, color, (x, y), max(2, size))
        # faint outline
        pygame.draw.circle(screen, (20, 20, 30), (x, y), max(2, size), 1)

    # right panel
    pygame.draw.rect(screen, PANEL_BG, (FIELD_W, 0, PANEL_W, SCREEN_H))

    # texts
    def t(s, yy, f=font):
        surf = f.render(s, True, TEXT_COL)
        screen.blit(surf, (FIELD_W + 12, yy))

    t("Monte Carlo: Exoplanet Transit", 12, font)
    t(f"Samples/frame : {systems_per_frame}", 44)
    t(f"Total samples : {total_samples:,}", 68)
    t(f"Transits found: {transit_count:,}", 92)
    t(f"Transit prob. : {p_hat:.6f}", 116)
    t(f"Std. err.     : {stderr:.6f}", 140)
    t("", 164)
    t("Model (toy):", 180, small_font)
    t(f"R_star mean   : {R_star_mean:.2f} R★", 198, small_font)
    t(f"R_planet mean : {R_planet_mean:.3f} R★", 216, small_font)
    t(f"a range       : {a_min:.1f} - {a_max:.1f} R★", 234, small_font)
    t("", 256)
    t("Click a green dot", 272, small_font)
    t("to view sample", 288, small_font)
    t("transit lightcurve", 304, small_font)
    t("", 330)
    t("Controls:", 350, small_font)
    t("SPACE : pause/resume", 368, small_font)
    t("r     : reset stats", 388, small_font)
    t("UP/DN : + / - samples/frame", 408, small_font)
    t("", 440)
    t(f"Showing last {len(display_points)} systems", 460, small_font)

    # show an active transit light curve if any
    if active_transit is not None:
        lc = active_transit['lc']
        n = len(lc)
        prog = active_transit['progress']
        # draw small light curve box
        box_x = FIELD_W + 16
        box_y = 500
        box_w = PANEL_W - 32
        box_h = 150
        pygame.draw.rect(screen, (8, 10, 16), (box_x, box_y, box_w, box_h))
        # draw curve
        for i in range(n - 1):
            x1 = int(box_x + (i / n) * box_w)
            y1 = int(box_y + box_h * (1.0 - lc[i]))
            x2 = int(box_x + ((i + 1) / n) * box_w)
            y2 = int(box_y + box_h * (1.0 - lc[i + 1]))
            pygame.draw.line(screen, (150, 220, 255), (x1, y1), (x2, y2), 2)
        # progress marker
        pygame.draw.rect(screen, HIGHLIGHT, (box_x + int((prog / n) * box_w), box_y + box_h + 4, 4, 8))
        # increment progress
        active_transit['progress'] += 1
        if active_transit['progress'] >= n:
            # finish after one loop
            active_transit = None

    # footer
    t("Tip: Transit probability ≈ (R⋆+Rp)/a (geometric)", SCREEN_H - 24, small_font)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
