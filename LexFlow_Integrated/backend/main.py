import sys
import os
import re
import json
import datetime
from datetime import timedelta
from io import BytesIO
from typing import List
import sqlite3
import pypdf

from dotenv import load_dotenv
load_dotenv()

# --- FASTAPI ---
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# --- MODULE IMPORTS ---
from backend import database
from backend.client_ai import CaseManagerAI
from backend.chatbot import logic
from backend.drafting import draft_engine, doc_intelligence
from backend.drafting.schemas import DraftRequest
from backend.api_schemas import *
from backend.ai import routes as ai_routes
from backend.communications import routes as comms_routes

# --------------------------------------------------
# APP INITIALIZATION
# --------------------------------------------------
app = FastAPI(title="LexFlow API", version="1.0")

# --------------------------------------------------
# DIRECTORIES
# --------------------------------------------------
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BACKEND_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")
UPLOAD_ROOT = os.path.join(DATA_DIR, "uploads")
os.makedirs(UPLOAD_ROOT, exist_ok=True)

# --------------------------------------------------
# GLOBALS (LAZY INIT)
# --------------------------------------------------
ai_agent = None

def get_ai_agent():
    global ai_agent
    if ai_agent is None:
        ai_agent = CaseManagerAI()
    return ai_agent

# --------------------------------------------------
# STARTUP (SAFE)
# --------------------------------------------------
@app.on_event("startup")
def startup_event():
    print("🔄 Initializing database...")
    database.init_db()
    print("✅ Startup complete. Server ready.")

# --------------------------------------------------
# CORS
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# ROUTERS
# --------------------------------------------------
app.include_router(ai_routes.router, prefix="/api/ai", tags=["AI"])
app.include_router(comms_routes.router, prefix="/api/communications", tags=["Communications"])

# ==================================================
# UTILS
# ==================================================
def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    try:
        if filename.lower().endswith(".pdf"):
            reader = pypdf.PdfReader(BytesIO(file_bytes))
            return " ".join([p.extract_text() or "" for p in reader.pages])
        return file_bytes.decode("utf-8", errors="ignore")
    except Exception:
        return ""

def parse_date(date_str):
    formats = [
        "%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d",
        "%d %B %Y", "%d %b %Y", "%B %d, %Y",
    ]
    clean = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
    for fmt in formats:
        try:
            return datetime.datetime.strptime(clean, fmt)
        except ValueError:
            continue
    return None

# ==================================================
# CLIENTS
# ==================================================
@app.get("/api/clients")
def get_clients():
    return database.get_all_clients()

@app.post("/api/clients")
def add_client(client: ClientCreate):
    ok, res = database.add_client(
        client.name, client.type, client.gstin,
        client.pan, client.email, client.mobile
    )
    if not ok:
        raise HTTPException(400, str(res))
    return res

# ==================================================
# DOCUMENTS
# ==================================================
@app.post("/api/documents/upload")
async def upload_documents(
    client_id: int = Form(...),
    client_name: str = Form(...),
    doc_type: str = Form(...),
    files: List[UploadFile] = File(...)
):
    results = []
    safe_name = client_name.replace(" ", "_")
    folder = os.path.join(UPLOAD_ROOT, f"{client_id}_{safe_name}")
    os.makedirs(folder, exist_ok=True)

    for file in files:
        try:
            content = await file.read()
            path = os.path.join(folder, file.filename)

            with open(path, "wb") as f:
                f.write(content)

            doc_id, created, date = database.save_document(
                client_id, file.filename, path, doc_type
            )

            results.append({
                "id": doc_id,
                "filename": file.filename,
                "success": True,
                "created": created,
                "date": date,
            })
        except Exception as e:
            results.append({"filename": file.filename, "success": False, "error": str(e)})

    return results

@app.get("/api/documents/{doc_id}/view")
def view_document(doc_id: int):
    path, name = database.get_document_path(doc_id)
    if not path or not os.path.exists(path):
        raise HTTPException(404, "File not found")
    return FileResponse(path, media_type="application/pdf")

# ==================================================
# DRAFTING
# ==================================================
@app.post("/api/drafting/generate")
async def generate_draft(request: DraftRequest):
    try:
        return await draft_engine.generate_legal_draft(request)
    except Exception as e:
        raise HTTPException(500, str(e))

# ==================================================
# CHAT
# ==================================================
@app.post("/api/chat/doc-qa")
def chat(req: ChatRequest):
    return logic.ask_client_bot(req.query, req.client_id)

# ==================================================
# RESEARCH
# ==================================================
class SearchQuery(BaseModel):
    query: str

@app.post("/api/research/search")
def research_search(payload: SearchQuery):
    return {"results": logic.search_legal_documents(payload.query)}
