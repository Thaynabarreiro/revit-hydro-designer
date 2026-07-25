# Project Plan — Automated Plumbing Design for Revit

Reads an architectural BIM model, sizes the plumbing systems to national code,
models the pipe networks, and issues a calculation report an engineer can sign.

Cold water is implemented end to end. This document describes the full scope,
the architecture that makes the remaining disciplines incremental rather than
rewrites, and the engineering decisions taken so far.

---

## 1. Why the architecture looks like this

Two separations drive everything.

**Code rules are separable from the modelling engine.** Reading the model,
routing pipes and generating reports are country-agnostic. What changes between
jurisdictions is the sizing method — and it genuinely changes, not just its
constants. Brazilian NBR 5626 uses weighted fixture units; French DTU 60.11 uses
a simultaneity coefficient over raw demand. Those are different mathematics, so
the code rules live in a pluggable module and the rest is shared.

**Knowledge lives in data, not in code.** Code tables, family mappings,
classification rules, fitting equivalent lengths and every string in the report
are JSON files. Adding a fixture type, adjusting a rule or translating the report
is editing a file. This is what makes a second discipline cheap.

```
data/pecas_br.json              code table: flow, weight, fixture units, pressure
data/perda_carga_br.json        head-loss formula and equivalent lengths
data/familias_pecas.json        fixture type → family in your template
data/config_projeto.json        per-project inputs
data/textos_memorial_br.json    every string in the report
```

**The engineer stays in the loop.** Each stage reports what it found and what it
assumed before the next runs. This is not ceremony. Two real errors were caught
exactly this way, described in section 6.

---

## 2. Pipeline

```
Architectural model (linked, read-only)
    │
    ├─ M0  Audit          model health, template readiness
    ├─ M1  Reader         rooms, fixtures, proximity clustering   ── engineer reviews
    ├─ M2  Sizing         demand, reservoir, design flow, meter
    ├─ M5  Placement      fixture families into the MEP model     ── engineer adjusts
    ├─ M6  Network        riser, distribution main, branches, drops
    ├─ M9  Head loss      pressure verification, diameter iteration
    └─ M8  Report         formulas, tables, declared limitations
```

The MEP model owns the fixtures; the architectural model is linked for context
only. This matches ISO 19650 practice and reality: architects do not model
plumbing reliably, so the engineer places what the project actually needs.
Fixtures missing from the architectural file are declared in project
configuration rather than requiring that file to be corrected.

---

## 3. Scope by discipline

| # | Discipline | Brazilian code | French code | Status |
|---|---|---|---|---|
| 1 | Cold water | NBR 5626 | DTU 60.11 | **done (BR)** |
| 2 | Water meter and service line | NBR 5626 | DTU 60.11 | **done (BR)** |
| 3 | Storage / reservoir | NBR 5626 | DTU 60.11 | **done (BR)** |
| 4 | Calculation report | — | — | **done (BR)** |
| 5 | Head-loss verification | NBR 5626 | DTU 60.11 | **done (BR)** |
| 6 | Hot water | NBR 7198 | DTU 60.11 + RE2020 | planned |
| 7 | Sanitary drainage and venting | NBR 8160 | EN 12056 | planned |
| 8 | Stormwater | NBR 10844 | EN 12056-3 | planned |
| 9 | On-site sewage treatment | NBR 7229 / 13969 | DTU 64.1 | planned |
| 10 | French code module | — | — | planned |

### 3.1 Hot water — the cheapest next step

Reuses roughly 80% of cold water: same reader, same routing, same report engine.
What changes is the code table, the piping system assignment, the heat source
(instantaneous heater, storage cylinder, solar, heat pump) and pipe insulation.

In France this carries regulatory weight that Brazil does not have: RE2020 pushes
heat pumps and solar over gas, which affects equipment selection rather than
hydraulics.

### 3.2 Sanitary drainage and venting — the largest single piece

The first discipline that is not a variation of cold water:

- Sizing is by **drainage fixture units**, not weighted units.
- Pipes are gravity-driven, so every run needs a **slope**, and the router must
  respect a minimum fall along the whole path to the outfall.
- **Stacks and venting** introduce vertical topology that the horizontal
  distribution logic does not cover.
- Traps, cleanouts and grease interceptors are placement rules, not sizing rules.

The router needs a real extension here: gravity routing is a constrained problem
where cold water was not.

### 3.3 Stormwater

Roof catchment area drives everything. Needs rainfall intensity for the project
location, so the system carries a per-city database with a manual-entry fallback
and a link to the authoritative source.

- Brazil: IDF tables from NBR 10844; national hydrological and meteorological data.
- France: rainfall zones from EN 12056-3; Météo-France public data.

Many French municipalities also cap discharge into the public network and require
rainwater harvesting, which has no residential equivalent in Brazil — a rule that
lives in the French module, not in shared code.

### 3.4 On-site sewage treatment

This is where the two jurisdictions diverge structurally, not numerically.

In Brazil, septic tank + anaerobic filter + soakaway is ordinary for houses
without a public sewer. In France the norm is connection to the public network;
on-site treatment is a rural case, legally requires a soil study, and follows a
different design basis entirely. So the system must ask *"is there a public
sewer?"* before this discipline exists at all.

Two modes, both required:

- **Standard** — assumes a typical percolation rate for a chosen soil class.
  Fast, appropriate for preliminary design.
- **Measured** — the designer enters a percolation rate from a field test.
  Required for detailed design, and legally required for on-site treatment in
  France.

The report must state which mode was used. That is a matter of professional
liability, not of calculation.

### 3.5 French code module

The architecture is ready; this is writing `norms/fr.py` and translating one JSON
file for the report. The substantive difference is the sizing method itself, as
described in section 1.

---

## 4. What is implemented

### Cold water, end to end

Worked example, a single-family house with 11 fixtures:

| Stage | Result |
|---|---|
| Reader | 14 rooms, 9 consumption points found, 3 coincident families clustered |
| Occupancy | 3 bedrooms → 6 occupants, 900 L/day |
| Storage | 1800 L required → 2000 L adopted (2 days' reserve) |
| Design flow | Σ weights 5.50 → 0.704 L/s (2.53 m³/h) |
| Water meter | 3.0 m³/h, DN 20 |
| Network | 27 pipes, 67.13 m, 11/11 fixtures physically connected |
| Diameters | DN 25 branches, DN 32 riser and main |
| Critical fixture | shower, 0.06 m of head to spare |

### Routing

Distribution follows a real main-and-branch topology: a vertical riser, a spine
running along one axis, perpendicular branches, vertical drops. Because the three
directions are mutually perpendicular, every junction is a right angle and Revit
can insert tees and elbows.

Three iterations were needed to get there, and each failure taught something the
next version needed.

**Chaining fixtures by proximity** produced arbitrary angles; Revit refused to
fit most junctions.

**One node per fixture** fixed the angles but left segments between close
fixtures too short for a tee body. Fixtures are now grouped into *bands* along
the spine, one node per band, with a branch serving every fixture in it.

**A single spine cannot run both ways.** Sorting bands by distance from the riser
made the spine double back over itself. It now splits into two runs from the
riser, each monotonic along the axis — which is what a real distribution main
does when there is demand on both sides of the stack.

A fourth fix came from the same pass: the main must sit *above* every outlet.
Showers connect at 3100 mm, so a main fixed at 2900 mm left a 200 mm "drop" with
no room for a fitting. The height is now derived from the highest outlet.

| | chained | one node each | banded, two runs |
|---|---|---|---|
| Fittings created | 6 | 17 | **14 of 16** |
| Fixtures connected | 11/11 | 11/11 | **11/11** |
| Total length | 89.84 m | 78.58 m | **67.13 m** |
| Model warnings | 25 | 5 | **4** |

### Head loss

Fair-Whipple-Hsiao for smooth pipe, `J = K·Q^1.75·D^-4.75`, plus local losses by
equivalent length. Iteration raises **one** diameter per step: the highest-loss
segment on the path of the most deficient fixture. Raising the whole path at once
grossly oversizes — the riser reached DN 110 on a single-family house.

Minimum diameter is a project setting. Many offices refuse DN 20 because it is
fragile on site; raising the floor to DN 25 cut the iterations from 13 to 4 and
increased the critical fixture's margin from 0.02 m to 0.06 m of head.

---

## 5. Verification of the code tables

Flow rates and relative weights were cross-checked against the fixture types
carried in a reference template. All nine checked values agree:

| Fixture | Flow | Weight |
|---|---|---|
| Basin | 0.150 L/s | 0.3 |
| Shower | 0.201 L/s | 0.4 |
| Electric shower | 0.099 L/s | 0.1 |
| WC, cistern | 0.150 L/s | 0.3 |
| WC, flush valve | 1.699 L/s | 32.0 |
| Kitchen sink | 0.249 L/s | 0.7 |
| Washing machine | 0.300 L/s | 1.0 |
| Laundry tub | 0.249 L/s | 0.7 |
| Garden tap | 0.201 L/s | 0.4 |

One divergence is recorded rather than resolved: the reference template requires
2 mH₂O minimum pressure at essentially every fixture, against the 5–10 kPa code
minimum. The stricter value is selectable through `criterio_pressao` and is used
by default. It moves the required reservoir height from 1.02 m to 2.0 m above the
least favourable outlet, so it is not a rounding difference.

---

## 6. Why there is a human review step

Both errors below were found in a real project and would have propagated
silently through an unattended pipeline.

**Fixtures counted more than once.** Architectural models represent a single
basin as several nested families — a bowl, a tap, a shared sub-family. Naively
counting them inflated the total weight from 4.1 to 5.5 and the design flow by
15%, and every downstream diameter would have inherited it. Resolved by
clustering families within 700 mm in the same room into one consumption point.

**A bathroom counted as a bedroom.** A room named *banho suíte* — an ensuite
bathroom — matched a bedroom pattern on the word *suíte*, inflating occupancy
from 6 to 8 and the reservoir from 2000 L to 3000 L. Resolved with an exclusion
pattern, but the deeper lesson stands: classification by room name is treacherous,
and the report must always list what was detected so a person can check it.

---

## 7. Declared limitations

Stated in the generated report as well as here. A tool that overstates its own
scope is worse than no tool.

1. **Two tee fittings still fail**, down from six. Fixtures very close together
   *along a branch* leave the segment between them too short for a tee body —
   the same problem the banding solved along the spine, one level down. The fix
   is the same idea applied to branch members.
2. **The head-loss module assumes a fixed main height** (2900 mm) while the
   router now derives it from the highest outlet. Drops are therefore slightly
   longer in the model than in the calculation. The effect is small but real;
   the router should publish its height for the calculation to read.
3. **Routing ignores obstacles.** Pipes run in straight orthogonal lines without
   checking walls, beams or other services.
4. **Clash detection is not part of the pipeline.**
5. **Paths are hardcoded**, so the project currently runs only on its author's
   machine. First task for anyone else wanting to use it.
6. **The formulas and tables require validation** by the responsible engineer
   against the governing code text before use on a real project. The tool
   computes; the signature and the judgement remain human.

---

## 8. Roadmap

**Phase A — close cold water**
Group spine nodes to fix the remaining tees · correct the reservoir placement
offset · write results back into family parameters so existing tags and schedules
read them · fold the head-loss results into the report.

**Phase B — make it a product**
Ribbon buttons for every stage · a template-inventory check that names missing
families before generating instead of failing midway · parameterised paths.

**Phase C — remaining disciplines**
Hot water, then sanitary drainage and venting, then stormwater, then on-site
sewage treatment.

**Phase D — second jurisdiction**
French code module and translated report.
