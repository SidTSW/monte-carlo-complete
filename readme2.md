# Monte Carlo 3: Exoplanet Transit Probability

## Overview

This simulation uses **Monte Carlo statistical sampling** to estimate the probability of exoplanet transits. Randomly generate thousands of star-planet systems, check which ones produce a geometric transit, and watch the probability estimate **converge to the true value** as samples accumulate.

This is exactly how modern astronomy discovers exoplanets: by sampling orbital configurations and counting transits, we can infer how many planets exist across the galaxy.

## Key Physics

### Transit Condition
A planet transits (passes in front of its star) if the orbital plane is sufficiently aligned with our line of sight.

**Geometric criterion** (circular orbits):
$$\text{Transit occurs if } |\cos(i)| \leq \frac{R_\star + R_p}{a}$$

Where:
- **i** = orbital inclination (angle of orbit relative to sky plane)
- **R★** = stellar radius
- **R_p** = planetary radius  
- **a** = orbital semi-major axis

**Intuition**: Larger stars/planets → higher probability. Wider orbits → lower probability (planet appears smaller in sky).

### Statistical Convergence
As you sample N random systems, your probability estimate converges to the true value:

$$p(\text{transit}) = \langle \text{# transits} \rangle / N$$

Standard error decreases as:
$$\sigma = \sqrt{\frac{p(1-p)}{N}} \propto \frac{1}{\sqrt{N}}$$

Watch this happen live on the screen as the standard error shrinks with more samples.

### Random Sampling Strategy
- **Stellar radius**: Small normal variation around mean (0.05 × normal scatter)
- **Planetary radius**: Realistic scatter (0.6 × normal scatter)
- **Semi-major axis**: **Log-uniform** distribution (more small orbits than large—realistic!)
- **Inclination**: **Uniform in cos(i)** (isotropic random orientations)

## How to Run

```bash
python "monte carlo 3.py"
```

**Requirements**: pygame, numpy

## Controls

| Key | Action |
|-----|--------|
| **SPACE** | Pause / Resume sampling |
| **R** | Reset statistics (start over) |
| **UP arrow** | Increase sampling rate (×1.5 systems/frame) |
| **DOWN arrow** | Decrease sampling rate (÷1.5 systems/frame) |
| **LEFT CLICK** on green dot | Show sample transit light curve |
| **ESC** | Quit |

## What to Observe

### Live Statistics (Right Panel)
- **Total samples**: Running count of generated systems
- **Transits found**: How many of those had transits
- **Transit probability**: The estimate p̂ = transits / samples
- **Std. error**: How confident we are (shrinks as √N)

### Visualization (Left Panel)
- **Green dots**: Systems with transits
- **Red dots**: Systems without transits
- Dots scatter randomly across the field
- Only last 2000 systems displayed (older dots fade)

### Convergence Behavior
- **Early (0–1000 samples)**: Noisy, fluctuating estimate
- **Mid (1000–10,000 samples)**: Trend becomes clearer
- **Late (100,000+ samples)**: Estimate plateaus, error is tiny

The noise vanishes as you watch—this is the **Law of Large Numbers** in action.

### Interactive Light Curves
Click any **green dot** to see a sample transit:
- Shows a simulated light curve (star brightness over time)
- Realistic ingress/egress (smooth entry/exit)
- Box-shaped transit bottom (transit depth ∝ (R_p / R★)²)
- Small observational noise added

This mirrors real Kepler/TESS photometry.

## Adjustable Parameters

Edit the top of the script:

```python
R_star_mean = 1.0          # stellar radius (units)
R_planet_mean = 0.1        # planetary radius (units)
a_min, a_max = 3.0, 200.0  # semi-major axis range (in stellar radii)
systems_per_frame = 500    # sampling speed (increase for faster convergence)
MAX_POINTS_DISPLAY = 2000  # how many dots to show
```

**Interesting experiments**:
- **Larger R_planet_mean** (0.2): Higher transit probability (bigger planets easier to see)
- **Wider a range** (1–500): Lower average probability (wider orbits)
- **Smaller a_min** (0.5): Higher probability (closer planets more likely to transit)
- **Increase systems_per_frame** (5000): Converge much faster (watch the error shrink!)

## Physical Insights

1. **Why random sampling works**: The true probability is a property of the population; sampling is just asking nature repeatedly and averaging.

2. **Statistical power**: The error √N is universal—to halve the error, you need 4× more samples. This is why discovering rare planets requires patient observation.

3. **Log-uniform a**: Realistic planetary systems have more close-in planets than distant ones. This is what the Kepler mission actually found!

4. **Inclination isotropy**: Random orientations mean some systems align (transit) and others don't—purely geometric.

## Real-World Connection

**Kepler Space Telescope (2009–2018)**:
- Observed ~150,000 stars continuously
- Found ~2,600 confirmed exoplanets (and ~1,000s of candidates)
- Used this exact principle: statistical sampling of orbital geometries
- Estimated that the Milky Way has ~100 billion planets

**Modern surveys** (TESS, future telescopes):
- Expand the sample further
- Improve detection statistics
- Discover rarer planet types (Earth-sized, habitable zone)

## References

- Borucki et al. (2010) - Kepler Mission results
- Fressin et al. (2013) - Occurrence rates from Kepler
- Howard et al. (2010) - Statistical planet occurrence
- Any intro exoplanet textbook - Transit photometry

---

**Watch chaos converge to certainty!** 🪐✨
