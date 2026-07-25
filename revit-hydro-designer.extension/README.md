# revit-hydro-designer.extension

pyRevit extension for automated plumbing design.
See the [project plan](../PROJECT-PLAN.md) for the full scope.

## Installation

1. Open Revit.
2. **pyRevit** tab -> **Settings**.
3. Under *Custom Extension Directories*, click **+** and add the folder
   **containing** this `.extension` directory (not the `.extension` itself).
4. **Save Settings and Reload.** A **Hydro** tab appears.

These buttons run on pyRevit's CPython 3.12 engine, where accented literals are
safe. That is not true of the scripts in `../tools/`, which reach Revit through
the Routes bridge — see the contributor notes in the root README.

## Buttons

### 1 Configurar — *Projeto* panel

Form for the inputs that change per project: name, city (used for rainfall data),
national code, occupancy, per-capita demand, days of reserve, reservoir type.
Writes `data/config_projeto.json`.

### Auditoria M0 — *Auditoria* panel

Audits the open model and writes a Markdown report.

| Section | Question it answers |
|---|---|
| Pipe types and routing preferences | Can the template generate a network automatically? |
| Available diameters | Which sizes the calculation may choose from |
| Piping systems | Are cold water, hot water, drainage and stormwater defined? |
| Families by category | Which fixtures the template actually carries |
| Populated parameters | Which parameters the generator should fill |
| Naming | Level, sheet and view naming patterns |
| Health check | Warnings, in-place families, imported CAD, orphan views |

## Planned buttons

`2 Levantar` (survey — the human review step), `3 Dimensionar` (size),
`4 Colocar peças` (place fixtures), `5 Gerar rede` (generate network),
`6 Memorial` (report). Their logic already exists in `../tools/`; what is missing
is the ribbon wrapper and the review dialogs.
