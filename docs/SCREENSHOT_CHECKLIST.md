# Screenshot & Demo Capture Checklist

To provide visual documentation for the open-source repository and potential program submission, capture the following screenshots and GIF in your active Revit 2027 session and place them into `docs/images/`:

---

## 📷 Required Visual Assets

- [ ] **1. `docs/images/hydro-tab.png`**:
  - **What to capture**: A clean screenshot of the Revit 2027 ribbon showing the **`Hydro`** tab with all 4 discipline panels (**1 Agua Fria e Quente**, **2 Esgoto e Ventilacao**, **3 Pluvial e Tratamento**, **4 Ferramentas**).
  - **Purpose**: Demonstrates native pyRevit ribbon integration.

- [ ] **2. `docs/images/model-before.png`**:
  - **What to capture**: 3D view of the architectural BIM model containing plumbing fixtures before running network routing (clean architectural link + placed fixtures).
  - **Purpose**: Shows starting state before automated 3D routing.

- [ ] **3. `docs/images/network-after.png`**:
  - **What to capture**: 3D view of the Revit MEP model after running **`Gerar Rede 3D AF/AQ`** (`M6`), showing the modeled cold water pipe network (riser, main spine, branches, wall drops, 90° elbows) connected to all fixtures.
  - **Purpose**: Visual proof of automated 3D pipe network generation.

- [ ] **4. `docs/images/calculation-report.png`**:
  - **What to capture**: A screenshot of the generated calculation report (HTML or PDF) from **`Memorial Hidráulico`** (`M8`), showing NBR 5626 formulas, daily demand, design flow, and Fair-Whipple-Hsiao pressure verification table.
  - **Purpose**: Proves engineering calculation and document generation capability.

- [ ] **5. `docs/images/demo.gif`**:
  - **What to capture**: A short 10-15 second screen recording (saved as animated GIF) showing:
    1. Opening the native **Studio BIM** window from **`Hydro` → `4 Ferramentas` → `Hydro Design Hub (Studio)`**.
    2. Clicking **`Calcula & Dimensiona AF/AQ`**.
    3. Clicking **`Gera Rede 3D Ortogonal no Revit`** and seeing pipes appear in Revit 3D view.
  - **Purpose**: Hero animation for the repository header.
