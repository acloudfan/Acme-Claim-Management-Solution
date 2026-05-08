# Executive Portal - Frontend

Business Intelligence Dashboard for ACME Claims

## Overview

The Executive Portal provides a comprehensive dashboard for C-suite executives and insurance operations managers to monitor AI adoption impact on claim processing.

## Features

- **4 Core KPIs**
  - Average Cycle Time
  - Auto-Adjudication Rate
  - Cost per Claim
  - Fraud Detection Rate

- **Interactive Charts** (Recharts)
  - Monthly trends
  - Processing path analysis
  - Cost savings visualization
  - Fraud detection effectiveness

- **Query Interface**
  - 4 preset queries
  - Custom date range filtering
  - Export capabilities (PDF, CSV, PNG)

- **Drill-Down**
  - Claim-level details
  - Timeline view
  - Cost accuracy breakdown

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool
- **React Router 7** - Routing
- **Tailwind CSS 3** - Styling
- **Recharts 2** - Charts library
- **Axios** - HTTP client
- **Lucide React** - Icons

## Setup

### 1. Install Dependencies

```bash
cd src/ui/executive
npm install
```

### 2. Configuration

Edit `public/executive-portal-config.yaml`:

```yaml
api:
  base_url: "http://localhost:8000/api/v1"  # API server URL

portal_links:
  customer_portal_url: "http://localhost:5173"
  adjustor_portal_url: "http://localhost:5174"
  admin_portal_url: "http://localhost:5170"
```

### 3. Start Development Server

```bash
npm run dev
```

Portal will be available at: **http://localhost:5176**

## Project Structure

```
src/ui/executive/
├── public/
│   └── executive-portal-config.yaml   # Portal configuration
├── src/
│   ├── api/                           # API client
│   │   ├── client.js                  # Axios instance
│   │   ├── config.js                  # Config loader
│   │   └── executive.js               # API endpoints
│   ├── components/
│   │   ├── common/                    # Reusable components
│   │   │   ├── Button.jsx
│   │   │   ├── Card.jsx
│   │   │   ├── Badge.jsx
│   │   │   ├── Modal.jsx
│   │   │   └── Spinner.jsx
│   │   └── dashboard/                 # Dashboard-specific (Phase 3)
│   │       ├── KPICard.jsx
│   │       ├── TrendChart.jsx
│   │       ├── QueryInterface.jsx
│   │       ├── FilterSidebar.jsx
│   │       └── DrillDownModal.jsx
│   ├── context/
│   │   └── AuthContext.jsx            # No-auth mode
│   ├── pages/
│   │   ├── LoginPage.jsx              # Minimal login
│   │   ├── DashboardPage.jsx          # Main dashboard
│   │   └── NotFoundPage.jsx
│   ├── utils/
│   │   ├── formatters.js              # Value formatters
│   │   └── constants.js               # App constants
│   ├── App.jsx                        # Main app with routing
│   ├── main.jsx                       # Entry point
│   └── index.css                      # Global styles
├── package.json
├── vite.config.js
├── tailwind.config.js
└── README.md
```

## Available Scripts

### `npm run dev`
Start development server on port 5176

### `npm run build`
Build production bundle

### `npm run preview`
Preview production build

### `npm run lint`
Run ESLint

## API Dependencies

The portal requires the following backend API endpoints:

- **GET /api/v1/executive/kpis** - Fetch KPI data
- **GET /api/v1/executive/trends/{kpi_name}** - Fetch trend data
- **POST /api/v1/executive/query** - Execute queries
- **GET /api/v1/executive/drilldown/{claim_id}** - Claim details
- **GET /api/v1/executive/export/{format}** - Export dashboard

Make sure the API server is running:
```bash
python -m src.api.main
```

## Development Phases

### ✅ Phase 2: Frontend Setup (Current)
- [x] Project structure
- [x] Configuration files
- [x] API client setup
- [x] Common components
- [x] Basic pages (Login, Dashboard, 404)
- [x] Routing
- [x] AuthContext

### 🚧 Phase 3: Core Components (Next)
- [ ] KPICard component
- [ ] TrendChart component (Recharts)
- [ ] QueryInterface component
- [ ] FilterSidebar component
- [ ] DrillDownModal component

### 🚧 Phase 4: Dashboard Integration
- [ ] Wire KPI cards to API
- [ ] Render 4 trend charts
- [ ] Implement time filtering
- [ ] Add query interface
- [ ] Connect drill-down

### 🚧 Phase 5-9: Polish, Testing, Documentation

## Usage

### 1. Access Portal
Navigate to http://localhost:5176

### 2. Login
Click "Enter Portal" (no credentials required)

### 3. View Dashboard
- See 4 KPI cards at top
- View trend charts below
- Use filters sidebar to change time period
- Click on data points to drill down

### 4. Run Queries
- Select preset query from dropdown
- Click "Generate Report"
- View results below dashboard

### 5. Export
- Click export button in sidebar
- Choose format (PDF, CSV, PNG)
- Download file

## Troubleshooting

### Portal won't load
- Check API server is running on port 8000
- Verify `executive-portal-config.yaml` has correct API URL

### API connection errors
- Open browser console (F12)
- Check for CORS errors
- Verify API endpoints return data

### Charts not rendering
- Ensure Recharts is installed: `npm install recharts`
- Check console for React errors

## Integration with Other Portals

The Executive Portal integrates with:

- **Admin Portal (5170)** - Quick Access link in Admin sidebar
- **Customer Portal (5173)** - For claim drill-down
- **Adjustor Portal (5174)** - For human review tracking

## Environment Variables

No environment variables needed. Configuration is in YAML file.

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## License

Proprietary - ACME Claims Inc.

## Support

For issues, contact the development team or file a GitHub issue.
