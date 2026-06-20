# Municipal Corporation Jalandhar Road Signs Project (McjRoadSigns)
### Secure, Trilingual, City-Scale Digital Sign Infrastructure Engine (IRC:67-2022 Aligned)

An enterprise-grade Python backend system built to manage and automate 2,000+ permanent physical road signs across Jalandhar. Physical traffic signs (Regulatory, Cautionary, or Informatory) feature printed unguessable QR codes linked directly to high-performance, mobile-optimized trilingual web platforms.

---

## 🏗️ Core Architecture Overview

The application utilizes a fully decoupled, service-oriented multi-layer pattern:
1. **Redirection Layer (`main.py` & `src/web/public_handlers.py`)**: Intercepts high-speed public citizen QR scans at `/s/<sign_uid>`. Runs light read-only lookups using indexed tokens to serve dynamic layouts in milliseconds.
2. **Administrative Control Layer (`src/web/admin_handlers.py`)**: Implements **"Four-Eyes Principle"** approval states. Content Creators input trilingual textual definitions, while Managers authorize page updates live using secure **Mobile OTP challenges**.
3. **Core Automation Layer (`src/core/`)**: Generates cryptographically unpredictable unique asset parameters, renders damage-resistant vector QR graphics (SVG), and compiles high-res industrial PDF worksheets for manufacturing contractors.
4. **Data Spatial Layer (`database/schema.sql`)**: Normalizes relational properties split across physical sign posts inventory locations on a live **PostgreSQL + PostGIS** world geodetic map map, completely independent from virtual text rendering tables.

---

## 🛠️ Step-by-Step Installation & Local Quickstart

### 1. Environmental Variable Seating
Initialize your operational configuration parameters. Clone your sample root environment file template into an active working file:
```bash
cp .env.example .env
```
Open your newly created `.env` file and generate a secure 64-character master signature key via Python's standard library:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Paste that hex signature output into your `APP_SECRET_KEY` slot and update `BASE_PUBLIC_URL` to match your purchased commercial domain asset location (e.g., `https://mcjroadsigns.in`).

### 2. Multi-Container Orchestration Launch
Launch your containerized cluster (PostGIS database layer + Python API workers queue) using Docker Compose:
```bash
docker compose up --build -d
```
This automated command triggers a multi-stage compilation pipeline:
- Installs necessary low-level spatial dependencies (`gdal-bin`, `libgdal-dev`) on a non-root environment workspace shell.
- Provisions a dedicated internal bridge network layout to block raw internet data access to database port `5432`.
- Spawns persistent volume mounts to protect compiled printable PDFs even across full system resets.

### 3. Database Schema Initialization
Execute the SQL structural blueprints and spatial procedure indices directly onto your active containerized PostGIS engine:
```bash
docker exec -i mcj_gis_db_container psql -U mcj_admin -d mcj_road_signs_db < database/schema.sql
```

---

## 🧪 Automated Testing Suite Verification

Run the built-in system testing configurations inside your runtime workspace shell to verify security parameters, input text sanitizers, and cryptographic tokens validation loops before cutting production runs:

```bash
# Execute structural unit and integration pipelines tests via pytest tool inside app container
docker exec -it mcj_web_app_container pytest -v tests/
```
The assertion test modules evaluate four critical application axes:
- `test_api.py`: Confirms that `src/web/middleware.py` filters successfully catch and scrub XSS code scripts and enforce role boundaries.
- `test_auth.py`: Asserts SHA-256 tokens configuration consistency and unique numeric properties generation layouts.
- `test_pipelines.py`: Validates form dictionaries data handling across PostGIS spatial parameter fields.
- `test_qr.py`: Verifies that custom lookups strip confusing look-alike letters (`0`, `O`, `1`, `I`) to maintain high manual typing accessibility.

---

## 📂 System File Workspace Directory Hierarchy

```text
McjRoadSigns/
├── config/             # Settings mapping, DB routing pool handles, alphanumeric token regex shields
├── database/           # Relational schemas, spatial procedures, version tracking folders
├── src/                
│   ├── auth/           # SHA-256 tokens challenge verification, telecom mobile network SMS adapters
│   ├── core/           # Level-H vector graphics compilers, ReportLab industrial layout PDF sheet tools
│   ├── models/         # SQL database relational query joins and GIS location mapping objects
│   └── web/            # Request interceptors, input text cleaners, Four-Eyes management validation loops
├── static/             # Static UI theme files (styles sheets for desktop admin panels & mobile screens)
├── storage/            # Local server storage locker tracking generated vector SVGs and printable master PDFs
└── templates/          # Dynamic layout views handles (multi-lingual dropdown triggers and corporate footer)
```

---

## 🔒 Production Security Compliance Enforcements

- **Anti-Scraping Shield**: Client IPs are limited to a maximum threshold constraint of 60 hits per minute on routing channels to mitigate high server strain or automated crawler load.
- **XSS HTML Escaping**: Forms inputs are systematically passed through middleware text sanitizers to prevent script execution on user smartphone views.
- **Unprivileged Containment Execution**: The app runtime drops all `root` administrative access commands, executing completely under standard permission limits through user ID `1001` (`mcjuser`).
