# Release Preparation Checklist — v0.1.0

Follow this checklist to prepare and publish release `v0.1.0`:

- [x] **Portable Root Discovery**: Ensure `RAIZ` is dynamically calculated across all `tools/*.py` scripts without machine paths.
- [x] **Configuration Examples**: Verify `data/config_projeto.example.json` and `data/familias_pecas.example.json` are tracked.
- [x] **Gitignore Update**: Ensure `.mcp.json` and local output directories (`auditoria/`, `memoriais/`) are git-ignored.
- [x] **Native WPF Window**: Confirm `HydroStudioInteractiveWindow` opens cleanly inside Revit without pyRevit console popups.
- [x] **Documentation**: Complete `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, and `CODE_OF_CONDUCT.md`.
- [ ] **Capture Visual Assets**: Capture screenshots listed in `docs/SCREENSHOT_CHECKLIST.md` into `docs/images/`.
- [ ] **Create Git Tag**:
  ```bash
  git tag -a v0.1.0 -m "v0.1.0 - Cold Water MVP"
  git push origin v0.1.0
  ```
- [ ] **Publish GitHub Release**: Copy release notes from `docs/releases/v0.1.0.md` into GitHub Release notes.
