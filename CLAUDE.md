# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ServiceDispatch is a Flask-based web application for managing service calls, parts inventory, and field service operations. It integrates with the ServicePower SOAP API and a Lotus Approach legacy database system (dBase IV files).

## Tech Stack

- **Backend**: Flask 3.0+, Python 3.x
- **Frontend**: ES6+ JavaScript, SCSS, Leaflet maps, Chart.js
- **Build Tools**: esbuild, Sass, PostCSS, Jest, Playwright
- **Data**: ServicePower SOAP API, dBase IV files (.DBF) via dbfread, pandas for analytics

## Common Commands

### Python Development
```bash
pip install -r requirements.txt    # Install dependencies
python app.py                       # Start Flask dev server (port 5000)
python test_api.py <user> <pass> <account> [env]  # Test ServicePower API
```

### Frontend Build (run from config/ directory)
```bash
npm run dev          # Watch mode (CSS + JS)
npm run build        # Production build
npm run lint         # Run ESLint + Stylelint
npm run format       # Prettier formatting
npm run test         # Jest with coverage
npm run test:watch   # Jest watch mode
npm run test:e2e     # Playwright E2E tests
```

## Architecture

### Main Application (`app.py`)
- SOAP client for ServicePower API (getCallInfoSearch, updateCallInfoObj)
- XML request/response parsing with namespace `urn:SPDServicerService`
- Session-based credential storage (user_id, password, servicer_account, environment)
- DBF file operations with pandas for parts analytics

### Key API Endpoints
- `POST /api/login` - Authentication
- `POST /api/calls` - Fetch service calls via SOAP
- `POST /api/export/dbf` - Export to DBF format
- `POST /api/parts/history` - Search parts history
- `POST /api/parts/analytics` - Parts usage analytics
- `POST /api/customer/analytics` - Customer database analytics

### ServicePower Environments
- Staging NA: `https://fssstag.servicepower.com/sms/services/SPDService`
- Production NA: `https://fss.servicepower.com/sms/services/SPDService`
- Staging EU: `https://fss-stg.hostedservicepower.eu/sms/services/SPDService`
- Production EU: `https://fss.servicepower.eu/sms/services/SPDService`

### Data Layer
- **Partlog.DBF, CUSTDATA.DBF**: Legacy customer and parts data
- **lotus-sp-tickets.dbf**: Ticket data export
- Shared network drive (Y:\Lotus) for multi-user access

### Frontend Structure
- Templates use Jinja2 inheritance (`templates/base/layout.html`)
- CSS uses BEM methodology with CSS custom properties for theming
- JavaScript uses IIFE pattern with event delegation

## Coding Standards

The project follows `CODING_STANDARDS.md` (comprehensive 1600+ line guide):

- **Python**: PEP 8, 120-char lines, type hints required, snake_case functions
- **CSS**: BEM naming (`.card__header`, `.card--primary`), CSS variables for themes
- **JavaScript**: camelCase functions, PascalCase classes, delegated events
- **API responses**: `{success, data, meta, error}` format
- **Git commits**: Conventional format `type(scope): description`

## Logging

Debug logs written to `servicepower_debug.log` - useful for troubleshooting API calls and authentication issues.
