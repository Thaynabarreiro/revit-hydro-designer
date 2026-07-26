# Changelog

All notable changes to `revit-hydro-designer` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.1.0] - 2026-07-26

### Added
- **M0 Model Audit**: Automated checks for pipe types, routing preferences, systems, families, and naming conventions.
- **M1 Reader**: linked architectural model reading, fixture extraction, room spatial association, and proximity clustering.
- **M2-M4 Cold Water Sizing Engine**: Daily demand calculation, 2-day reservoir sizing (60% lower / 40% upper), design flow calculation ($Q = 0.3 \sqrt{\Sigma P}$), water meter selection, and service line sizing per NBR 5626.
- **M5 Fixture Placement**: Placement of cold water MEP fixture families in the active Revit project.
- **M6 Cold Water Network Routing**: Orthogonal main-and-branch pipe routing (riser, main spine, perpendicular branches, wall drops) with 90° fittings and fixture connections.
- **M9 Pressure Verification**: Iterative head-loss calculation using Fair-Whipple-Hsiao formula and equivalent lengths to guarantee positive pressure margins at all fixtures.
- **M8 Calculation Report**: Automated generation of print-ready calculation reports in HTML, PDF, and Word (`.docx`).
- **Native Studio BIM WPF Window**: Integrated light-themed WPF UI directly inside Revit with live tab switching and action buttons.
