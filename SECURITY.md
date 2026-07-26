# Security Policy

## ⚠️ Important Security Warning: pyRevit Routes Server

The `revit-hydro-designer` bridge relies on pyRevit's Routes REST server (`http://localhost:48884/revit_mcp/execute_code/`).

> [!CAUTION]
> **No Authentication Warning**
> The pyRevit Routes REST API has **NO authentication or token mechanism**. Any process capable of sending HTTP POST requests to the listening port can execute arbitrary Python code directly inside your running Autodesk Revit process with full user privileges.

### Security Binding Requirements:
1. **Bind to Localhost Only**: Ensure pyRevit Routes server is strictly configured to listen on `127.0.0.1`.
2. **Never Bind to `0.0.0.0`**: Do NOT expose the Routes server to the local area network (LAN) or public internet.
3. **Firewall Protection**: Maintain strict local firewall rules blocking external inbound connections to port `48884`.

---

## Reporting a Vulnerability

If you discover a security vulnerability in this repository, please report it responsibly by contacting the maintainer via GitHub issues or private email. Do NOT disclose security issues publicly until a fix is made available.
