# NagarikAI Platform - Frontend

React web application for the NagarikAI Platform with three main features:

1. **Beneficiary Discovery** - Identify eligible but unenrolled citizens
2. **Grievance Portal** - Submit and track grievances with automatic routing
3. **Operator Assistant** - Validate applications before submission

## Tech Stack

- React 18
- TypeScript
- Vite
- React Router
- CSS3 (no external UI library for minimal setup)

## Getting Started

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

The app will be available at http://localhost:3000

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── pages/
│   │   ├── BeneficiaryDiscovery.tsx
│   │   ├── GrievancePortal.tsx
│   │   └── OperatorAssistant.tsx
│   ├── App.tsx
│   ├── App.css
│   ├── main.tsx
│   └── index.css
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## API Integration

The frontend expects the backend API to be running on `http://localhost:8000`. The Vite dev server is configured to proxy `/api` requests to the backend.

### API Endpoints Used

- `POST /api/beneficiary/discover` - Discover beneficiaries
- `POST /api/grievance/submit` - Submit grievance
- `POST /api/application/validate` - Validate application

## Features

### Beneficiary Discovery
- Input death record details
- View discovered beneficiaries with confidence scores
- Color-coded confidence levels (high/medium/low)

### Grievance Portal
- Submit grievances in Hindi or English
- View automatic classification and routing
- See predicted resolution timeline

### Operator Assistant
- Enter application details
- Real-time validation with risk scoring
- View validation issues with severity levels
- Get corrective guidance in Hindi and English

## Development Notes

- The app uses React Router for navigation between the three main sections
- All API calls are made using the Fetch API
- Error handling displays alerts (can be enhanced with toast notifications)
- Styling is done with vanilla CSS for simplicity and minimal dependencies
