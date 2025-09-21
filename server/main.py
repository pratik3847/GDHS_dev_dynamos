from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.orchestrator.orchestrator import build_orchestrator_graph
from backend.utils.pdf_generator import generate_pdf_from_analysis

# -------------------------------
# Initialize FastAPI and Orchestrator
# -------------------------------
app = FastAPI(title="GDHS Multi-Agent API", version="1.0")

# CORS for local dev frontends (Vite default 5173, 5174; React 3000)
app.add_middleware(
    CORSMiddleware,
    # Allow all origins in development; tighten for production
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_orchestrator_graph()

# -------------------------------
# Request & Response Models
# -------------------------------
class PatientInput(BaseModel):
    symptoms: str
    age: int | None = None
    gender: str | None = None
    medicalHistory: str | None = None
    currentMedications: str | None = None
    urgency: str | None = None

class PdfInput(BaseModel):
    patient_info: dict | None = None
    symptom_analysis: dict | None = None
    literature: dict | None = None
    case_matcher: dict | None = None
    treatment: dict | None = None
    summary: dict | None = None

# -------------------------------
# Root Endpoint
# -------------------------------
@app.get("/")
def root():
    return {"message": "GDHS Multi-Agent API is running 🚀"}

# -------------------------------
# Run Full Orchestrator
# -------------------------------
@app.post("/analyze")
def analyze_patient(input_data: PatientInput):
    try:
        # Pass the structured data directly to the graph
        input_state = input_data.dict()
        final_state = graph.invoke(input_state)
        return final_state
    except Exception as e:
        # Provide a structured error for the frontend (avoid opaque Network Error)
        return JSONResponse(status_code=500, content={"error": str(e)})

# -------------------------------
# Generate PDF Endpoint
# -------------------------------
@app.post("/generate-pdf")
async def generate_pdf(analysis_data: PdfInput):
    try:
        # Only include sections that are present
        payload = {k: v for k, v in analysis_data.dict().items() if v is not None}
        if not payload:
            return JSONResponse(status_code=400, content={"error": "No analysis sections provided for PDF."})

        pdf_bytes = generate_pdf_from_analysis(payload)
        if isinstance(pdf_bytes, bytearray):
            pdf_bytes = bytes(pdf_bytes)
        return Response(
            content=pdf_bytes,
            media_type='application/pdf',
            headers={'Content-Disposition': 'attachment; filename="analysis_report.pdf"'}
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# -------------------------------
# Individual Agents (Optional)
# -------------------------------
@app.post("/symptom-analyzer")
def run_symptom_agent(input_data: PatientInput):
    final_state = graph.invoke(input_data.dict())
    return final_state.get("symptom_analysis", {})

@app.post("/literature")
def run_literature_agent(input_data: PatientInput):
    final_state = graph.invoke(input_data.dict())
    return final_state.get("literature", {})

@app.post("/case-matcher")
def run_case_matcher(input_data: PatientInput):
    final_state = graph.invoke(input_data.dict())
    return final_state.get("case_matcher", {})

@app.post("/treatment")
def run_treatment_agent(input_data: PatientInput):
    final_state = graph.invoke(input_data.dict())
    return final_state.get("treatment", {})

@app.post("/summary")
def run_summary_agent(input_data: PatientInput):
    final_state = graph.invoke(input_data.dict())
    return final_state.get("summary", {})
