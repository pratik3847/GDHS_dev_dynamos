## Meds AI Insight – Frontend

This is the React/Vite frontend for Meds AI Insight. It connects to the FastAPI backend and renders multi‑agent analysis results with a clean UI.

### Tech Stack
- React + TypeScript (Vite)
- shadcn-ui + Tailwind CSS
- Zustand (state) and Axios (API)

### Local Development
1. Install dependencies:
	- Node.js 18+
	- npm install
2. Start dev server:
	- npm run dev
3. Backend URL is configured in `src/services/api.ts` (default: http://localhost:8000)

### Features
- Patient Case input and workflow runner
- Real-time results from FastAPI orchestrator
- PDF report download with patient info and per‑agent sections

### Troubleshooting
- If you see Network Error:
  - Ensure backend is running at http://localhost:8000 and CORS is enabled
  - Check the browser Network tab for request details
  - Verify env and API keys on the backend if agents error
