# GDHS_dev_dynamos

## 🩺 GDHS Dev Dynamos – Multi‑Agent Medical AI

Built for the Global Digital Health Summit Hackathon 🏆. This repository contains a full‑stack, multi‑agent medical reasoning system:

- Backend: FastAPI + LangChain/LangGraph orchestrating specialized agents (symptom analysis, literature, case matching, treatments, final summary)
- Frontend: Vite + React + TypeScript UI for case entry, stepwise results, and downloadable PDF report

The system is privacy‑aware (no PHI persisted by default) and works with or without external API keys (LLM optional, graceful fallbacks enabled).

---

## 🚀 Key Features

- Symptom Analyzer Agent
  - Takes symptoms + demographics (age, gender), history, meds, urgency
  - Returns differentials, risk level, and rationale (ICD‑10 hints when available)
- Literature Agent
  - Searches PubMed (NCBI eutils) and summarizes top articles
  - Summaries use the LLM when available; deterministic fallback when not
- Case Matcher Agent
  - Optional BioPortal ontology lookups for concept mapping (graceful if no key)
- Treatment Agent
  - Looks up options via RxNorm and composes patient‑aware suggestions
- Summarizer Agent
  - Produces a concise, patient‑contextual summary across agents
- PDF Report Generator
  - Nicely formatted PDF including patient info and all agent sections
- Frontend Integration
  - Real API calls to the FastAPI backend (no mocks)
  - Results panel + one‑click PDF download

---

## 🧭 Architecture Overview

- Orchestrator: LangGraph StateGraph, linear flow:
  1) symptom_analyzer → 2) literature_agent → 3) case_matcher → 4) treatment_agent → 5) summarizer_agent
- LLM: OpenRouter (e.g., gpt‑4o‑mini) via ChatOpenAI when OPENROUTER_API_KEY is set; otherwise deterministic fallbacks ensure stability.
- External APIs (all optional):
  - PubMed (NCBI eutils) for literature
  - BioPortal for ontology concepts
  - RxNorm for treatments

---

## 📦 Repository Structure

Top‑level highlights:

- `backend/` – agent implementations and utilities
  - `agents/` – symptom_analyzer.py, literature_agent.py, case_matcher.py, treatment_agent.py, summarizer_agent.py
  - `orchestrator/` – `orchestrator.py` builds the LangGraph pipeline
  - `utils/` – LLM client and helpers
- `server/` – FastAPI app entrypoint (`main.py`) with endpoints
- `frontend/` – Vite + React + TypeScript app (moved here for monorepo)
- `requirements.txt` – backend dependencies
- `README.md` – this guide

---

## 🔑 Environment Variables

Backend (optional keys enable richer results; app runs without them):

- `OPENROUTER_API_KEY` – to use LLM for higher‑quality analyses and summaries
- `BIOPORTAL_API_KEY` – unlocks ontology case matching

Frontend (only if using Supabase auth integration – otherwise ignore):

- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_PROJECT_ID`
- `VITE_SUPABASE_PUBLISHABLE_KEY`

Note: Do not commit secrets. `.env` files are git‑ignored.

---

## ▶️ Run Locally (Windows PowerShell)

Prereqs:
- Python 3.10+ (tested with 3.13)
- Node.js 18+

1) Backend – FastAPI

```powershell
# from repo root
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn server.main:app --reload
```

FastAPI dev server: http://localhost:8000

2) Frontend – React (in another terminal)

```powershell
Set-Location .\frontend
npm install
npm run dev
```

Vite dev server: typically http://localhost:5173 (or as shown in terminal)

---

## 🧩 API Endpoints (FastAPI)

Health check:
- GET `/` → `{ "message": "GDHS Multi-Agent API is running ..." }`

Analyze a patient case:
- POST `/analyze`

Request body (example):
```json
{
  "symptoms": "Chest pain radiating to left arm, shortness of breath",
  "age": 58,
  "gender": "male",
  "medicalHistory": "hypertension, hyperlipidemia",
  "currentMedications": "atorvastatin 20 mg",
  "urgency": "high"
}
```

Response (shape):
```json
{
  "symptom_analysis": { "top_differentials": [], "risk_level": "", "rationale": "", "disclaimer": "" },
  "literature": { "query": "", "articles": [], "patient_context": {}, "disclaimer": "" },
  "case_matcher": { "matched_cases": [], "patient_context": {}, "disclaimer": "" },
  "treatment": { "treatments": [], "patient_context": {}, "disclaimer": "" },
  "summary": "",
  "summary_disclaimer": ""
}
```

Generate a PDF report:
- POST `/generate-pdf` – accepts any combination of sections plus optional `patient_info` and returns `application/pdf`.

Example body:
```json
{
  "patient_info": { "age": 58, "gender": "male", "history": "HTN, HLD", "medications": "atorvastatin", "urgency": "high" },
  "symptom_analysis": { "top_differentials": ["ACS", "GERD"], "risk_level": "high" },
  "literature": { "articles": [{ "pmid": "12345", "title": "Study" }] },
  "treatment": { "treatments": ["Aspirin 325 mg", "Nitroglycerin"] },
  "summary": "Findings suggest ACS; initiate MONA and cardiology consult."
}
```

Per‑agent debug endpoints (optional): `/symptom-analyzer`, `/literature`, `/case-matcher`, `/treatment`, `/summary` – each returns its piece after running the full graph.

---

## 🧪 Quick Test Cases

Use these with POST `/analyze` to validate personalization:

1) Possible ACS (cardiac)
```json
{
  "symptoms": "Crushing chest pain radiating to left arm, diaphoresis, dyspnea",
  "age": 62,
  "gender": "male",
  "medicalHistory": "hypertension, smoker, family history of CAD",
  "currentMedications": "amlodipine",
  "urgency": "high"
}
```

2) Pregnancy UTI
```json
{
  "symptoms": "Dysuria, urinary frequency, suprapubic pain",
  "age": 28,
  "gender": "female",
  "medicalHistory": "10 weeks pregnant, no known drug allergies",
  "currentMedications": "prenatal vitamins",
  "urgency": "moderate"
}
```

Expected: clearly different differentials, literature focus, treatments, and summary tone.

---

## 🖥️ Frontend Notes

- Location: `frontend/`
- API base URL: configured in `src/services/api.ts` (defaults to `http://localhost:8000`)
- PDF: Download button posts to `/generate-pdf` and streams a Blob to the browser
- Supabase: optional; if not used, the auth interceptor is harmless

Run dev server:
```powershell
Set-Location .\frontend
npm install
npm run dev
```

---

## ⚙️ Implementation Details

- Robust error handling and CORS (dev) in `server/main.py`
- Agents accept patient context for personalization and include safe fallbacks when keys are missing
- PDF generator uses fpdf2 with safe wrapping to avoid common layout errors
- Deterministic paths are returned when LLM is unavailable to prevent 500s

---

## 🧰 Troubleshooting

- Network Error from frontend: confirm backend at http://localhost:8000 and CORS is enabled (dev config allows all origins)
- 500 on `/analyze`: verify prompt JSON is well‑formed and environment keys (if any) are correct; fallbacks should keep it running
- PDF errors: very long tokens/lines are chunked; if you still hit issues, try reducing the payload size per section

---

## � Deployment Tips

- Backend: package with Uvicorn/Gunicorn; set OPENROUTER_API_KEY/BIOPORTAL_API_KEY as needed
- Frontend: `npm run build` then host `dist/` behind a static server or CDN
- Consider enabling HTTPS and configuring CORS appropriately for production

---

## 📜 License

For hackathon/demo purposes. Add a license if open‑sourcing.

---

## 🙌 Acknowledgements

- LangChain, LangGraph, OpenRouter, PubMed/NCBI, BioPortal, RxNorm, FastAPI, Vite, React, TypeScript

