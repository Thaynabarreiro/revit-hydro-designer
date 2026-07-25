# revit-hydro-designer

Automated plumbing design for Autodesk Revit — reads an architectural BIM model,
sizes the cold-water system to code, models the pipe network, verifies pressure,
and issues a calculation report ready for an engineer's signature.

Built with [pyRevit](https://github.com/pyrevitlabs/pyRevit) and driven through
the pyRevit Routes REST API, so any MCP-capable AI assistant can develop against
a live Revit session.

> **Status: work in progress.** Cold water is implemented end to end, including
> head-loss verification. Hot water, sanitary drainage and venting, stormwater
> and on-site sewage treatment are planned, as is a second national code module.
> See [the project plan](PROJECT-PLAN.md) for the full scope and for every
> engineering decision taken so far.

---

## Why this exists

Residential plumbing design is highly repetitive: read the fixtures, apply the
code tables, size the pipes, draw the network, write the report. The judgement
that matters — where the shafts go, what the client actually wants, whether a
result is sane — is a small fraction of the hours spent.

Tools that automate this for Revit exist, but they are closed and paid. There is
no open-source equivalent, which means a practising engineer cannot inspect the
rules being applied on their behalf, adapt them to a different national code, or
keep working when a licence ends. This is an attempt at one that is readable and
adaptable.

It automates the repetitive part and, deliberately, **stops at every point where
judgement is required** so the engineer can review and correct.

---

## What works today

| Stage | What it does | Status |
|---|---|---|
| **M0** Audit | Model health check: pipe types and routing preferences, systems, families, parameters, naming conventions, warnings, orphan views | ✅ |
| **M1** Reader | Reads fixtures and rooms from the linked architectural model, clusters coincident families into single consumption points, classifies each by code | ✅ |
| **M2–M4** Sizing | Occupancy, daily demand, reservoir volume, design flow (weighted-fixture-unit method), water meter selection, service-line diameter | ✅ |
| **M5** Placement | Places the matching plumbing families in the MEP model at the correct level | ✅ |
| **M6** Network | Models the network with a real main-and-branch topology — riser, spine, perpendicular branches, drops — with every fixture physically connected | ✅ |
| **M9** Head loss | Pressure verification by Fair-Whipple-Hsiao plus equivalent lengths, iterating diameters until every fixture clears | ✅ |
| **M8** Report | Print-ready calculation report (HTML → PDF) with formulas, tables and declared limitations | ✅ |

Worked example — a single-family house with 11 fixtures:

```
14 rooms · 9 consumption points found · 3 coincident families clustered
3 bedrooms -> 6 occupants -> 900 L/day -> 2000 L storage (2 days reserve)
sum of weights 5.50 -> design flow 0.704 L/s -> 3.0 m3/h meter, DN 20 service
34 pipes · 78.58 m · 11/11 fixtures connected · DN 25 branches, DN 32 riser
critical fixture clears by 0.06 m of head
```

Everything downstream — hot water, drainage and venting, stormwater, on-site
sewage treatment — reuses the same architecture. Hot water reuses roughly 80% of
what already exists. Drainage is the one that needs a genuinely new router,
because gravity flow is a constrained problem where pressurised flow was not.

---

## Design principles

**Knowledge lives in JSON, not in code.** Code tables, family mappings,
classification rules, fitting equivalent lengths and every string in the report
are data files. Adding a fixture type, adjusting a rule or translating the report
is editing a file, not editing Python.

```
data/pecas_br.json            code table: flow, weight, fixture units, pressure
data/perda_carga_br.json      head-loss formula and equivalent lengths
data/familias_pecas.json      fixture type -> family in your template
data/config_projeto.json      per-project inputs
data/textos_memorial_br.json  every string in the report
```

Files ending in `.example.json` are the templates to copy; the real ones are
git-ignored because they describe a specific building and a specific office
template.

**The calculation engine is separable from the modelling engine.** Reading the
model, routing and reporting are country-agnostic; the code rules are a pluggable
module. Brazilian NBR 5626 is implemented; French DTU 60.11 is the next target,
and it is genuinely different — NBR uses weighted fixture units, DTU uses a
simultaneity coefficient over raw demand.

**Project decisions are settings, not assumptions.** Occupancy, per-capita
demand, days of reserve, maximum velocity and minimum diameter all live in
project configuration. Many offices refuse DN 20 as too fragile on site; raising
the floor to DN 25 is one field, and it visibly changes the result — on the
worked example it cut the sizing iterations from 13 to 4.

**The engineer stays in the loop.** Each stage reports what it found and what it
assumed before the next stage runs. This is not ceremony: two real errors were
caught exactly this way — architectural models double-counting a single basin
modelled as several nested families, and a room named *banho suíte* (ensuite
**bathroom**) counted as a bedroom, inflating occupancy by a third.

**Limitations are declared, not hidden.** The generated report states in writing
what was not verified. An automated tool that overstates its own scope is worse
than no tool.

---

## How it works

```mermaid
flowchart TD
    ARQ[Architectural model<br/>linked, read-only]
    CFG[/config_projeto.json<br/>city · code · occupancy · reserve days/]
    TAB[/pecas_br.json<br/>code table: flow, fixture units, pressure/]
    MAP[/familias_pecas.json<br/>fixture type to Revit family/]

    ARQ --> M1
    M1[M1 · Reader<br/>rooms, fixtures, proximity clustering]
    TAB --> M1
    M1 --> REV1{Engineer<br/>reviews}
    REV1 --> M2

    CFG --> M2
    M2[M2-M4 · Sizing<br/>demand · reservoir · flow · meter]
    M2 --> M5

    MAP --> M5
    M5[M5 · Placement<br/>plumbing families in the MEP model]
    M5 --> REV2{Engineer<br/>adds / removes / moves}
    REV2 --> M6

    M6[M6 · Network<br/>riser · spine · branches · drops]
    M6 --> M9
    M9[M9 · Head loss<br/>pressure check, diameter iteration]
    M9 --> M8

    TXT[/textos_memorial_br.json<br/>every string - swap file to localise/]
    TXT --> M8
    M8[M8 · Report<br/>formulas, tables, declared limitations]
    M8 --> PDF[Signed calculation report]

    M6 -.-> MODEL[(MEP model<br/>owns the fixtures)]

    style REV1 fill:#fff6e5,stroke:#d08700
    style REV2 fill:#fff6e5,stroke:#d08700
    style PDF fill:#e8f4ea,stroke:#2e7d4f
```

The amber diamonds are deliberate stops. Automation without a review point is a
trap: both real bugs found so far would have passed silently without them.

The MEP model owns the fixtures; the architectural model is linked for context
only. This matches both ISO 19650 practice and reality: architects do not model
plumbing reliably, so the engineer places what the project actually needs.
Fixtures missing from the architectural file are declared in project
configuration rather than requiring that file to be corrected.

---

## Requirements

- Autodesk Revit (developed against 2027; the API calls used are version-tolerant)
- [pyRevit](https://github.com/pyrevitlabs/pyRevit)
- A Revit template containing plumbing families with configured routing preferences

## Installation

1. Clone this repository.
2. Copy `data/config_projeto.example.json` to `data/config_projeto.json` and
   `data/familias_pecas.example.json` to `data/familias_pecas.json`, then edit
   them for your project and your template.
3. In Revit: **pyRevit → Settings → Custom Extension Directories** → add the
   folder *containing* `revit-hydro-designer.extension`.
4. **Save Settings and Reload.** A **Hydro** tab appears.

## Development against a live Revit session

`tools/run_in_revit.sh` posts a Python file to the pyRevit Routes API
(`http://localhost:48884`), which executes it inside the running Revit process
and returns stdout. This makes the write → run → read-the-real-error → fix loop
possible without leaving the editor.

```bash
./tools/run_in_revit.sh tools/m1_reader.py "read fixtures"
```

Enable **Routes Server** in pyRevit settings first, and bind it to `127.0.0.1`.
The Routes API is a draft feature with no authentication — do not expose it.

---

## Notes for contributors

Two environments, two sets of rules:

| | pyRevit buttons | Routes bridge |
|---|---|---|
| Engine | CPython 3.12 | IronPython 2.7 |
| f-strings | yes | no |
| Accented literals | safe | **corrupted** — read them from JSON |

Revit API traps found the hard way and worth knowing:

- `element.Name` is ambiguous on `PipeType`, `PipingSystemType` and
  `FamilySymbol`. Use `Element.Name.__get__(el)`.
- `ElementId(int)` is ambiguous too — it collides with the `BuiltInParameter` and
  `BuiltInCategory` overloads. Use `ElementId(System.Int64(i))`.
- `RoutingPreferenceRuleGroupType` members are plural: `Elbows`, `Junctions`,
  `Crosses`, `Transitions`, `Unions`, `MechanicalJoints`, `Caps`.
- `ElementId.Value` returns a long, which IronPython's `json` cannot serialise.
- Deleting a pipe cascades to its fittings, so a batch `doc.Delete` fails
  wholesale on an id that is already gone. Delete one at a time, checking for
  `None` first.
- Fixture weight is an *instance* parameter on specific families and a *type*
  parameter on generic ones. Check both.
- `Pipe.Create` from a `Connector` asks Revit to resolve the joint immediately;
  when it cannot, it opens a modal dialog and hangs a headless script forever.
  Create by coordinate and join afterwards with `ConnectTo`.
- Fittings need right angles. A layout that chains fixtures by proximity produces
  arbitrary angles that Revit refuses to fit.

**Known limitation:** the buttons inject the project root, but running a tool
directly through the bridge still falls back to a literal path.

---

## Licence

MIT — see [LICENSE](LICENSE).
