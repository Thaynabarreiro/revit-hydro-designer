# GitHub Repository Configuration & Roadmap Issues

This guide provides the metadata, description, topics, and initial issue templates to configure your open-source GitHub repository for `revit-hydro-designer`.

---

## 📌 Repository Metadata

### Repository Description
> Open-source pyRevit extension for generating and verifying cold-water plumbing systems from architectural BIM models.

### Repository Topics
Add the following topics in **GitHub → About (Gear Icon)**:
`revit`, `pyrevit`, `revit-api`, `bim`, `mep`, `plumbing`, `civil-engineering`, `building-services`, `automation`, `python`, `claude`, `mcp`

---

## 📋 Recommended Initial GitHub Issues

Create these 7 initial issues on GitHub to establish your project roadmap and invite open-source collaboration:

### Issue 1: Hot Water System Module (AF/AQ Integration)
- **Title**: `[Feature] Implement Hot Water (AQ) Pipe Sizing & Thermal Losses`
- **Body**: Expand `M2` and `M6` to support domestic hot water distribution (NBR 7198), including water heater sizing, thermal expansion, and dual hot/cold pipe routing.

### Issue 2: Sanitary Drainage & Venting Router
- **Title**: `[Feature] Implement Sanitary Drainage (ESG) Gravity Router with Slope Constraints`
- **Body**: Build gravity-flow routing algorithms for sanitary drainage and primary/secondary venting (NBR 8160) enforcing continuous 1.0%–2.0% slopes and shaft drops.

### Issue 3: Stormwater & Rainfall Curve Sizing
- **Title**: `[Feature] Implement Stormwater Drainage (PLUV) with IDF Curve Selection`
- **Body**: Add rainfall intensity curve calculations (NBR 10844 / DTU 60.11) for roof gutters, downspouts, and site stormwater drainage.

### Issue 4: On-Site Wastewater Treatment Sizing
- **Title**: `[Feature] Add Septic Tank, Anaerobic Filter & Soakaway Sizing (NBR 7229 / NBR 13969)`
- **Body**: Implement automated sizing and Revit family placement for on-site wastewater treatment systems (fossa séptica, filtro anaeróbio, sumidouro).

### Issue 5: International Code Module — French DTU 60.11
- **Title**: `[Code Module] Add French DTU 60.11 Simultaneity Sizing Module`
- **Body**: Implement a pluggable DTU 60.11 calculation module replacing weighted fixture units with simultaneity coefficients $y = 0.8 / \sqrt{N - 1}$.

### Issue 6: Automated Fitting & Accessory Placement
- **Title**: `[Enhancement] Auto-place Valves, Water Meters, and Cleanouts`
- **Body**: Enhance network generation (`M6`) to automatically insert stop valves, check valves, water meters, and sanitary cleanout plugs at code-required positions.

### Issue 7: Multi-Story Riser Shaft Router Optimization
- **Title**: `[Optimization] Multi-Story Vertical Shaft Routing for Residential Buildings`
- **Body**: Optimize the spatial routing engine for multi-floor residential buildings to consolidate vertical risers into shared MEP shafts.
