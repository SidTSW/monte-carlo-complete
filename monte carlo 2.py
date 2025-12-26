"""
2D Monte Carlo Simulation (Lennard-Jones potential)
---------------------------------------------------
- N particles in a periodic square box
- Uses Metropolis Monte Carlo sampling
- Visualized with Pygame
- Displays instantaneous potential energy and acceptance ratio

Controls:
    SPACE : pause / resume
    r     : reset system
    +/-   : increase / decrease displacement step size
    ESC   : quit
"""

import pygame
import numpy as np
import math, random, sys

# ---------------------------
# Simulation parameters
# ---------------------------
N = 100                    # number of particles
density = 0.8              # number density
L = math.sqrt(N / density) # box side length
epsilon = 1.0              # LJ epsilon
sigma = 1.0                # LJ sigma
rcut = 2.5 * sigma         # cutoff
kB = 1.0                   # Boltzmann constant
temperature = 1.0          # target temperature
max_disp = 0.1             # maximum displacement per trial move
draw_scale = 50            # pixels per unit length
particle_radius = 4

# ---------------------------
# Pygame setup
# ---------------------------
pygame.init()
WINDOW_SIZE = int(L * draw_scale) + 500
screen = pygame.display.set_mode((WINDOW_SIZE, int(L * draw_scale)))
pygame.display.set_caption("2D Monte Carlo — Lennard-Jones")
font = pygame.font.SysFont("consolas", 16)
clock = pygame.time.Clock()

# Colors
BG = (12, 12, 12)
BOX_COLOR = (200, 200, 200)
PARTICLE_COLOR = (100, 200, 255)
TEXT_COLOR = (230, 230, 230)
PAUSE_COLOR = (255, 130, 130)

# ---------------------------
# Helper functions
# ---------------------------
def wrap(x):
    """Periodic boundary conditions."""
    return x % L

def minimum_image(dx):
    """Apply minimum image convention."""
    return dx - L * np.round(dx / L)

def pair_energy(r2):
    """Compute Lennard-Jones potential for squared distance."""
    if r2 < rcut * rcut:
        inv_r2 = 1.0 / r2
        inv_r6 = inv_r2 ** 3
        inv_r12 = inv_r6 ** 2
        return 4 * epsilon * (inv_r12 - inv_r6)
    return 0.0

def total_potential(positions):
    """Compute total potential energy (O(N^2) naive)."""
    E = 0.0
    for i in range(N - 1):
        for j in range(i + 1, N):
            dx = minimum_image(positions[i, 0] - positions[j, 0])
            dy = minimum_image(positions[i, 1] - positions[j, 1])
            r2 = dx * dx + dy * dy
            if r2 < rcut * rcut:
                E += pair_energy(r2)
    return E

def local_energy_change(i, new_pos, positions):
    """Compute energy change if particle i moves to new_pos."""
    dE = 0.0
    old_pos = positions[i].copy()
    for j in range(N):
        if j == i:
            continue
        # old contribution
        dx = minimum_image(old_pos[0] - positions[j, 0])
        dy = minimum_image(old_pos[1] - positions[j, 1])
        r2 = dx * dx + dy * dy
        if r2 < rcut * rcut:
            dE -= pair_energy(r2)
        # new contribution
        dx = minimum_image(new_pos[0] - positions[j, 0])
        dy = minimum_image(new_pos[1] - positions[j, 1])
        r2 = dx * dx + dy * dy
        if r2 < rcut * rcut:
            dE += pair_energy(r2)
    return dE

# ---------------------------
# Initialization
# ---------------------------
def initialize_positions():
    """Initialize positions roughly on a grid."""
    n_side = int(math.ceil(math.sqrt(N)))
    spacing = L / n_side
    pos = []
    for i in range(n_side):
        for j in range(n_side):
            if len(pos) >= N:
                break
            pos.append([
                (i + 0.5) * spacing + (random.random() - 0.5) * 0.1 * spacing,
                (j + 0.5) * spacing + (random.random() - 0.5) * 0.1 * spacing
            ])
    return np.array(pos[:N])

positions = initialize_positions()
potential_energy = total_potential(positions)
accepted_moves = 0
attempted_moves = 0
paused = False
running = True

# ---------------------------
# Main Loop (Monte Carlo)
# ---------------------------
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_r:
                positions = initialize_positions()
                potential_energy = total_potential(positions)
                accepted_moves = 0
                attempted_moves = 0
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                max_disp *= 1.2
            elif event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE:
                max_disp /= 1.2

    if not paused:
        # Monte Carlo move
        i = np.random.randint(N)
        trial_pos = positions[i] + np.random.uniform(-max_disp, max_disp, 2)
        trial_pos = wrap(trial_pos)
        dE = local_energy_change(i, trial_pos, positions)
        attempted_moves += 1
        if dE <= 0 or np.random.rand() < np.exp(-dE / (kB * temperature)):
            positions[i] = trial_pos
            potential_energy += dE
            accepted_moves += 1

    # Draw
    screen.fill(BG)
    box_px = int(L * draw_scale)
    pygame.draw.rect(screen, BOX_COLOR, (0, 0, box_px, box_px), 1)

    for i in range(N):
        x = int(positions[i, 0] * draw_scale)
        y = int(positions[i, 1] * draw_scale)
        pygame.draw.circle(screen, PARTICLE_COLOR, (x, y), particle_radius)
        # wrap visuals for periodic edges
        if positions[i, 0] * draw_scale > box_px - 10:
            pygame.draw.circle(screen, PARTICLE_COLOR, (x - box_px, y), particle_radius)
        if positions[i, 1] * draw_scale > box_px - 10:
            pygame.draw.circle(screen, PARTICLE_COLOR, (x, y - box_px), particle_radius)

    # Info panel
    info_x = box_px + 10
    acc_ratio = accepted_moves / max(1, attempted_moves)
    lines = [
        f"N particles         : {N}",
        f"Box L               : {L:.3f}",
        f"Density             : {density:.3f}",
        f"Temperature (T)     : {temperature:.2f}",
        f"Max disp (Δ)        : {max_disp:.3f}",
        f"Potential Energy    : {potential_energy:.4f}",
        f"Acceptance Ratio    : {acc_ratio*100:.1f}%",
        "",
        "Controls:",
        "SPACE : pause/resume",
        "r     : reset system",
        "+ / - : increase/decrease step",
        "ESC   : quit"
    ]
    y0 = 8
    for line in lines:
        surf = font.render(line, True, TEXT_COLOR)
        screen.blit(surf, (info_x, y0))
        y0 += 18

    if paused:
        surf = font.render("PAUSED", True, PAUSE_COLOR)
        screen.blit(surf, (info_x, y0 + 8))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
