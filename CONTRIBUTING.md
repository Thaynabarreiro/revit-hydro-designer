# Contributing to revit-hydro-designer

Thank you for your interest in contributing to `revit-hydro-designer`! This project aims to build an open-source, code-compliant, and transparent plumbing design engine for Autodesk Revit.

---

## 1. Development Setup & Workflow

### Environment
- **Tested Version**: Autodesk Revit 2027
- **Extension Framework**: [pyRevit v4.8+](https://github.com/pyrevitlabs/pyRevit)
- **Ribbon Engine**: CPython 3.12 (inside pyRevit ribbon buttons)
- **Routes Bridge Engine**: IronPython 2.7 (headless execution via pyRevit Routes REST API)

### Local Configuration
Do NOT commit personal or machine-specific paths (`C:\Users\...`).
1. Copy `data/config_projeto.example.json` → `data/config_projeto.json`
2. Copy `data/familias_pecas.example.json` → `data/familias_pecas.json`
3. Copy `.mcp.example.json` → `.mcp.json` (if developing with AI/MCP tools)

---

## 2. Revit Testing Process

All calculation and routing changes must be validated against a active Revit 2027 project:
1. Open Revit 2027 with a test model containing architectural fixtures.
2. Execute the test suite via the Routes API or directly in pyRevit:
   ```bash
   python tools/run_in_revit.py tools/m1_reader.py "test reader"
   python tools/run_in_revit.py tools/m2_dimensionamento.py "test sizing"
   ```
3. Verify that:
   - All fixtures are detected and classified correctly.
   - Network routing completes without modal hanging dialogs.
   - Pressure verification (`M9`) succeeds with valid positive head margins.

---

## 3. Dual Engine Constraints (CPython 3.12 vs IronPython 2.7)

When writing or modifying scripts in `tools/` and `lib/`:

- **IronPython 2.7 Compatibility**:
  - Do NOT use Python 3.6+ f-strings (`f"{var}"`). Use `.format()` or `%`.
  - Avoid non-BMP unicode characters (such as emojis) directly in IronPython source files; use standard text or read from JSON UTF-8 files using `codecs.open()`.
  - Use `codecs.open(path, "r", encoding="utf-8")` instead of `open(..., encoding="utf-8")`.

- **CPython 3.12 Compatibility**:
  - `unicode` is not a built-in type in Python 3; `lib/hydro.py` handles compatibility shims.

---

## 4. Engineering Rule Changes & Technical References

- **No Silent Assumptions**: Do NOT change calculation formulas, fixture weights, simultaneity factors, or pipe sizing tables without documenting the exact standard clause.
- **Reference Required**: Every pull request altering engineering logic MUST cite the relevant national standard clause (e.g., *NBR 5626:2020 Item 5.3*, *NBR 8160:1999 Tabela 3*, *NBR 10844:1989*, *DTU 60.11*).
- **Keep Data Separate from Code**: All engineering coefficients, fixture weights, and report strings MUST remain in JSON data files (`data/pecas_br.json`, `data/perda_carga_br.json`).
