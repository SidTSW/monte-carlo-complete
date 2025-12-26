# Monte Carlo 2: Lennard-Jones Molecular Dynamics

## Overview

This is an interactive **2D molecular dynamics simulation** using **Metropolis Monte Carlo sampling**. Watch 100 particles interact via van der Waals forces and reach thermal equilibrium in real time—without solving a single differential equation.

Instead of classical dynamics (F=ma), this uses statistical mechanics: randomly propose particle moves and accept them based on energy change using the **Boltzmann distribution**. The system naturally finds the canonical ensemble (NVT: fixed number, volume, temperature).

## Key Physics

### Lennard-Jones Potential
$$E_{LJ} = 4\epsilon\left[\left(\frac{\sigma}{r}\right)^{12} - \left(\frac{\sigma}{r}\right)^6\right]$$

- **r⁻¹² term**: Steep repulsion (particles can't overlap)
- **r⁻⁶ term**: Van der Waals attraction
- **Default**: epsilon = 1.0, sigma = 1.0, cutoff = 2.5σ

### Metropolis Monte Carlo Algorithm
1. Select a random particle
2. Propose a random displacement (uniform in ±max_disp)
3. Compute energy change ΔE
4. **Accept** if: ΔE ≤ 0  OR  rand() < exp(−ΔE / k_B T)
5. Update position and total energy if accepted

This efficiently samples configurations where P(state) ∝ exp(−E / k_B T).

### Periodic Boundary Conditions
- Particles wrap around box edges (toroidal topology)
- Prevents artificial surface effects
- Minimum image convention for distance calculations

## How to Run

```bash
python "monte carlo 2.py"
```

**Requirements**: pygame, numpy

## Controls

| Key | Action |
|-----|--------|
| **SPACE** | Pause / Resume simulation |
| **R** | Reset system to initial grid configuration |
| **+** | Increase maximum displacement (larger steps) |
| **−** | Decrease maximum displacement (smaller steps) |
| **ESC** | Quit |

## What to Observe

### Equilibration Phase (first 1000 steps)
- Particles start on a regular grid
- Move randomly and scatter
- Potential energy drops as system relaxes

### Equilibrium Phase (after ~5000 steps)
- Potential energy plateaus and fluctuates
- Particles cluster due to attractive forces
- **Acceptance ratio** stabilizes (~40-60% typical)

### Parameter Tuning
- **Too large max_disp**: Most moves rejected, slow exploration
- **Too small max_disp**: Moves accepted but local exploration
- **Optimal**: ~50% acceptance ratio = good balance

## Adjustable Parameters

Edit the top of the script to change:

```python
N = 100                    # number of particles
density = 0.8              # number density (affects box size)
epsilon = 1.0              # LJ interaction strength
sigma = 1.0                # LJ length scale
rcut = 2.5 * sigma         # cutoff distance
temperature = 1.0          # target temperature (in units of k_B)
max_disp = 0.1             # maximum displacement per trial move
```

**Interesting experiments**:
- **Lower temperature** (T = 0.1): Particles form solid-like clusters
- **Higher temperature** (T = 5.0): More fluid-like, random motion
- **Higher density** (density = 1.5): More interactions, higher energy
- **Larger N** (N = 200): Richer phase behavior (but slower)

## Physical Insights

1. **Equilibration**: Why does the system settle into a specific energy? Because entropy + energy balance—low-energy states are visited frequently at low T, high-energy states at high T.

2. **Acceptance rate**: A good acceptance ratio means you're sampling efficiently. Too rigid or too loose = wasted computation.

3. **Phase behavior**: At low T, particles lock into crystal-like arrangements; at high T, they behave like a gas. This transition exists in real materials!

4. **Computational efficiency**: This method is ~O(N²) per step (all pairwise distances), but for N ≤ 200 it's practical. Larger systems need neighbor lists.

## Real-World Applications

- **Drug discovery**: Sampling protein conformations
- **Materials science**: Computing equation of state, phase diagrams
- **Crystal structure prediction**: Finding low-energy atomic arrangements
- **Statistical mechanics**: Validating theory via simulation

## References

- Metropolis et al. (1953) - Original Monte Carlo algorithm
- Allen & Tildesley (1987) - *Computer Simulation of Liquids*
- Frenkel & Smit (2002) - *Understanding Molecular Simulation*

---

**Enjoy equilibrating your particles!** 🔬
