# EP Pitch Recognition — Timing Bias by Pitch Type

**A hitter's swing timing is calibrated for fastball velocity by
default. Across the league in 2026, swings arrive "early" against
curveballs and changeups at roughly 13-14x the rate they do against
fastballs — and the magnitude of that mistiming is a real, moderate
predictor of whiff rate.**

> **Correction (see bottom of this section):** an earlier version of
> this README reported a 1.3% fastball early-swing rate across all 7
> pitch types, sourced from a batter-level export with an actual
> minimum of 65 swings per batter-pitch-type combo — not the 100
> stated. Corrected below.

Part of the [Emerson Performance](https://github.com/ejimenezperformance)
analytics portfolio (EP-TSP framework). This is the first project in
this portfolio to isolate pitch recognition specifically — separate
from swing execution (bat speed, squared-up%), which every prior repo
has measured.

*[Versión en español disponible aquí](README.es.md)*

---

## The question

Every swing mechanics metric this portfolio has used (bat speed,
squared-up%, attack angle) measures execution — what happens once the
swing is already underway. None of them ask a more basic question:
does the hitter's timing itself reveal whether he correctly identified
what was coming?

## Finding 1 — Swings default to fastball timing

![Early bias by pitch type](outputs/early_bias_EN.png)

| Pitch Type | Early Swing Rate | Batters qualified (100+ swings) |
|---|---|---|
| Fastball | 3.3% | 325 |
| Curveball | 42.3% | 151 |
| Changeup | 46.4% | 67 |

**Why only 3 of 7 pitch types:** with a real 100-swing-per-batter
minimum enforced against a *single* pitch type in one season, Sinker,
Cutter, Slider, and Sweeper don't have enough qualifying batters to
support a reliable league rate — most hitters simply don't see 100+
of one specific non-fastball, non-breaking pitch type from different
pitchers in a season. Rather than force those 4 categories in with a
looser, undocumented threshold, they're excluded here. The 3 remaining
types still make the core point: hitters are almost never early
against fastballs; against pitches that require recognizing off-speed,
they're early on roughly 4 in 10 swings.

## Finding 2 — Off-speed miss distance predicts whiffs best

![Miss distance vs whiff correlation](outputs/miss_distance_whiff_EN.png)

| Pitch Type | r (miss distance vs. whiff rate) |
|---|---|
| Changeup | **0.458** |
| Slider | 0.390 |
| Curveball | 0.345 |
| Sweeper | 0.256 |
| Fastball | 0.220 |
| Sinker | 0.102 |
| Cutter | 0.059 |

How far a hitter's bat misses the ideal contact point against
changeups and sliders specifically predicts overall whiff rate
meaningfully better than miss distance against fastballs or sinkers
does. This reinforces Finding 1: the pitches that most expose a
fastball-calibrated swing are also the ones where timing precision
carries the most diagnostic weight.

## Finding 3 — High pitches fool the swing plane, low pitches fool the timing

![Zone breakdown](outputs/zone_breakdown_EN.png)

| Zone | Early Swing % | Miss Distance | Whiff % |
|---|---|---|---|
| High | 4.1% | 1.06 | **29.9%** |
| Middle | 19.1% | 1.70 | 15.6% |
| Low | 34.1% | 3.89 | **36.2%** |

At the top of the zone, hitters are almost never early (4.1%) and miss
distance is small (1.06) — yet whiff rate is still nearly double the
middle-zone rate. This whiff isn't primarily a timing problem; it's
more consistent with what `vaa-approach-angle-study` already found —
fastballs that play flatter/higher than expected beat swing plane, not
timing. At the bottom of the zone, both timing (34.1% early) and miss
distance (3.89, more than 3x the high-zone figure) are worse, and whiff
rate is the highest of the three — a compounding problem, not a single
cause. Two zones, two different failure modes, both landing on similar
whiff outcomes.

## Finding 4 — The platoon disadvantage shows up in timing, too

![Platoon matchup](outputs/platoon_EN.png)

| Matchup | Whiff Rate |
|---|---|
| Same side (e.g. RHB vs. RHP) | 26.3% |
| Opposite side (e.g. RHB vs. LHP) | 23.5% |

The classic platoon disadvantage — same-handed matchups being tougher
for hitters — is real in this same-side/opposite-side split, though
more modest in size than Findings 1-3. This directly resolves a
limitation flagged in an earlier version of this repo (lumping
left-handed and right-handed matchups together without testing
platoon effects specifically).

## Why this matters

For a hitting development program, this points toward a specific,
trainable target: recognition and timing adjustment against
off-speed/breaking pitches specifically, not swing mechanics broadly.
A hitter with a mechanically sound swing can still be getting beaten
purely by a timing calibration issue — arriving early because his
internal clock defaults to fastball speed — and that's a different
problem, with a different fix, than a bat-speed or contact-quality
issue this portfolio's other repos have measured.

## Repo structure

```
ep-pitch-recognition/
|-- data/
|   |-- swing_timing_season.csv          (min 65/batter-pitch-type, 7 types — Findings 2-4)
|   |-- swing_timing_season_min100.csv   (verified min 100/batter-pitch-type, 3 types — Finding 1)
|   |-- swing_timing_monthly.csv
|   `-- swing_timing_by_zone.csv
|   `-- swing_timing_by_platoon.csv
|-- scripts/
|   |-- pitch_recognition_analysis.py
|   `-- ep_chart_style.py
`-- outputs/
    |-- early_bias_{EN,ES}.png
    |-- miss_distance_whiff_{EN,ES}.png
    `-- zone_breakdown_{EN,ES}.png
    `-- platoon_{EN,ES}.png
```

## Reproduce the analysis

```bash
git clone https://github.com/ejimenezperformance/ep-pitch-recognition.git
cd ep-pitch-recognition
pip install pandas matplotlib
python scripts/pitch_recognition_analysis.py
```

## Methodology

- **Data source:** Baseball Savant Bat Tracking "Swing Timing" leaderboard,
  batter-level, 2026 season. **Finding 1** uses a verified 100-swing
  minimum per batter-pitch-type combination, which only 3 pitch types
  (Fastball, Curveball, Changeup) have enough qualifying batters to
  support — see the Correction section below. **Findings 2-4** use an
  export across all seven publicly tracked pitch types (Four-Seam,
  Sinker, Cutter, Slider, Changeup, Sweeper, Curveball) whose actual
  minimum is 65 swings per combination, not independently re-verified
  at 100.
- **Early/On Time/Late:** whether the bat's sweet spot arrived at the
  contact point before, at, or after the pitch, based on Statcast's
  bat-tracking data.
- **Miss distance:** how far the bat's sweet spot was from the ball at
  the point of closest approach.
- **Correlation:** simple Pearson r between miss distance and whiff
  rate, computed separately within each pitch type.

## Correction (posted after publication)

An earlier version of Finding 1 reported a 1.3% fastball early-swing
rate across all 7 tracked pitch types. That number came from a
batter-level Baseball Savant export whose *actual* minimum was 65
swings per batter-pitch-type combination — the README documented a
100-swing minimum, but the export that produced the original numbers
did not enforce it. This was flagged by a reader in the comments on
the original post; it checked out on review.

With a verified 100-swing minimum enforced (both in the source export
and again in code), the fastball early-swing rate is **3.3%**, not
1.3%. Curveball and Changeup — the two other pitch types with enough
batter-level volume to clear a real 100-swing minimum — come in at
42.3% and 46.4%. The core finding (swings are overwhelmingly late-only
against fastballs and overwhelmingly early against off-speed/breaking
pitches) holds; the specific fastball number and the "30-45x" headline
ratio do not, and are corrected above. Sinker, Cutter, Slider, and
Sweeper are no longer shown in this chart, for the volume reason
explained in Finding 1.

Findings 2-4 below still use the original min-65 dataset
(`swing_timing_season.csv`) and have not been re-verified against a
confirmed 100-swing threshold. Treat their exact percentages with the
same caveat until re-checked.

## Limitations

- **No production outcome (wOBA/SLG) by pitch type was found.** This
  project set out to also test whether pitch-type-specific timing
  predicts production, not just contact. After an extensive search
  across multiple public leaderboards and tools (Baseball Savant's
  Custom Leaderboard, Pitch Arsenal Stats, Expected Stats, Percentile
  Rankings, Year-to-Year Changes, and FanGraphs' batting splits) — nine
  distinct attempts in total — a batter-side production split by pitch
  type faced, across many players at once, could not be located as a
  simple downloadable export. Whiff rate was used as the sole outcome
  metric instead. This is disclosed as a real, searched-for data
  limitation, not an oversight.
- **A single season (2026, partial through mid-August).**
- **Correlation, not causation** — this doesn't establish that
  training timing against a specific pitch type would directly reduce
  a given hitter's whiff rate.

## Contact

**Emerson Jiménez** — Strength & Conditioning Coach, Baseball Performance
Specialist. [Emerson Performance](https://github.com/ejimenezperformance) ·
[@emersonperformance](https://instagram.com/emersonperformance)

---

*EP-TSP framework and design © Emerson Performance. Statcast/Baseball
Savant data is public domain, non-commercial use.*
