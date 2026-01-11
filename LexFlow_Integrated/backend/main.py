import sys
import os
import sqlite3
import re
import json
from typing import List, Optional
import datetime
from datetime import timedelta
from io import BytesIO
import pypdf 

# ✅ FORCE LOAD .ENV
from dotenv import load_dotenv
# current_dir = os.path.dirname(os.path.abspath(__file__))
# base_dir = os.path.dirname(current_dir)
# env_path = os.path.join(base_dir, ".env")

# if os.path.exists(env_path):
#     load_dotenv(dotenv_path=env_path)
#     print(f"✅ Loaded .env from: {env_path}")
# else:
#     print("⚠️ .env file not found.")
load_dotenv()

# --- FASTAPI IMPORTS ---
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse 
from pydantic import BaseModel

# --- PATH SETUP ---
sys.path.append(base_dir)

# --- MODULE IMPORTS ---
from backend import database
from backend.client_ai import CaseManagerAI
from backend.chatbot import logic 
from backend.drafting import draft_engine, doc_intelligence
from backend.drafting.schemas import DraftRequest

# ✅ WORKING IMPORTS
from backend.api_schemas import * 
from backend.ai import routes as ai_routes
from backend.communications import routes as comms_routes

# --- INITIALIZE APP ---
app = FastAPI(title="LexFlow API", version="1.0")

# Setup Directories
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BACKEND_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")
UPLOAD_ROOT = os.path.join(DATA_DIR, "uploads")
os.makedirs(UPLOAD_ROOT, exist_ok=True)

# Initialize AI
# ai_agent = CaseManagerAI()
ai_agent = None

@app.on_event("startup")
def startup_event():
    global ai_agent
    print("🔄 Checking Database Schema...")
    database.init_db()

    print("🤖 Initializing AI Agent...")
    ai_agent = CaseManagerAI()   # SAFE HERE

    print("✅ System Ready.")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- STARTUP EVENT ---
@app.on_event("startup")
def startup_event():
    print("🔄 Checking Database Schema...")
    database.init_db()
    print("✅ System Ready.")

# --- REGISTER ROUTERS ---
app.include_router(ai_routes.router, prefix="/api/ai", tags=["AI"]) 
app.include_router(comms_routes.router, prefix="/api/communications", tags=["Communications"]) 

# ==========================================
# 🧠 SMART DATE EXTRACTION LOGIC
# ==========================================
def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    text = ""
    try:
        if filename.lower().endswith(".pdf"):
            pdf_reader = pypdf.PdfReader(BytesIO(file_bytes))
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        else:
            text = file_bytes.decode("utf-8", errors="ignore")
        return re.sub(r'\s+', ' ', text).strip()
    except Exception as e:
        print(f"Error extracting text from {filename}: {e}")
        return ""

def parse_date(date_str):
    formats = [
        "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y",
        "%Y-%m-%d", "%Y/%m/%d",
        "%d %B %Y", "%d %b %Y",
        "%B %d, %Y",
    ]
    clean_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
    
    for fmt in formats:
        try:
            return datetime.datetime.strptime(clean_str, fmt)
        except ValueError:
            continue
    return None

def extract_smart_deadlines(text: str):
    """Smartly identifies Document Date vs. Actual Deadlines."""
    deadlines = []
    text_lower = text.lower()
    
    # 1. FIND ISSUE DATE
    date_pattern = r'\b(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}|\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+\d{4})'
    issue_date_match = re.search(r'(?:date|dated)\s*[:\-]?\s*' + date_pattern, text, re.IGNORECASE)
    
    issue_date = None
    if issue_date_match:
        date_str = issue_date_match.group(1)
        issue_date = parse_date(date_str)

    # 2. FIND RELATIVE DEADLINES
    relative_match = re.search(r'within\s+(\d+)\s+days', text_lower)
    if relative_match and issue_date:
        days = int(relative_match.group(1))
        due_date = issue_date + timedelta(days=days)
        deadlines.append({
            "title": f"Compliance Due (within {days} days)",
            "date": due_date.strftime("%Y-%m-%d"),
            "type": "Calculated"
        })

    # 3. FIND EXPLICIT DEADLINES
    deadline_keywords = ["submit by", "reply by", "due date", "on or before", "until"]
    all_dates = re.finditer(date_pattern, text)
    
    for match in all_dates:
        date_str = match.group(0)
        start_idx = max(0, match.start() - 50)
        context = text[start_idx:match.start()].lower()
        
        parsed_d = parse_date(date_str)
        if not parsed_d: continue

        # Ignore if it is the issue date, unless context suggests otherwise
        if issue_date and parsed_d == issue_date:
            continue

        if any(kw in context for kw in deadline_keywords):
            deadlines.append({
                "title": f"Explicit Deadline",
                "date": parsed_d.strftime("%Y-%m-%d"),
                "type": "Extracted"
            })
        elif issue_date and parsed_d > issue_date:
            # Future dates are usually relevant
            deadlines.append({
                "title": "Potential Hearing/Deadline",
                "date": parsed_d.strftime("%Y-%m-%d"),
                "type": "Inferred"
            })

    unique_deadlines = {}
    for d in deadlines: unique_deadlines[d['date']] = d
    return list(unique_deadlines.values())

# ==========================================
# 1. CLIENT ENDPOINTS
# ==========================================
@app.get("/api/clients", tags=["Clients"])
def get_clients(): return database.get_all_clients()

@app.get("/api/clients/{client_id}")
def get_client(client_id: int): return database.get_client_details(client_id)

@app.post("/api/clients")
def add_client(client: ClientCreate):
    success, res = database.add_client(client.name, client.type, client.gstin, client.pan, client.email, client.mobile)
    if not success: raise HTTPException(400, detail=str(res))
    return res

@app.delete("/api/clients/{client_id}")
def del_client(client_id: int):
    database.delete_client_fully(client_id)
    return {"status": "success"}

# ==========================================
# 2. DOCUMENT ENDPOINTS (FIXED SYNC)
# ==========================================
@app.get("/api/clients/{client_id}/documents", tags=["Documents"])
def list_docs(client_id: int): 
    return database.get_client_files(client_id)

@app.post("/api/documents/upload", tags=["Documents"])
async def upload(
    client_id: int = Form(...), 
    client_name: str = Form(...), 
    doc_type: str = Form(...), 
    files: List[UploadFile] = File(...)
):
    results = []
    
    # 1. Folder Setup
    safe_name = "".join([x for x in client_name if x.isalnum() or x in (' ','_')]).strip()
    client_folder = os.path.join(UPLOAD_ROOT, f"{client_id}_{safe_name.replace(' ', '_')}")
    os.makedirs(client_folder, exist_ok=True)

    for file in files:
        try:
            content = await file.read()
            text = extract_text_from_file(content, file.filename)
            
            # 2. Save to Disk
            file_path = os.path.join(client_folder, file.filename)
            with open(file_path, "wb") as f: 
                f.write(content)
            
            # 3. Save to DB (Get updated ID and Date)
            doc_id, created, upload_date = database.save_document(int(client_id), file.filename, file_path, doc_type)
            
            # 4. Extract Deadlines (Smart Logic)
            extracted_deadlines = extract_smart_deadlines(text)
            for item in extracted_deadlines:
                database.add_deadline(int(client_id), f"{item['title']} - {file.filename}", item['date'], item['type'])
            
            # ✅ 5. AUTO-CREATE MATTER IF DEADLINES FOUND
            if extracted_deadlines or "Notice" in file.filename or "Order" in file.filename:
                matter_title = f"Reply to {file.filename}"
                print(f"🚀 Auto-Creating Matter: {matter_title}")
                database.create_matter(int(client_id), matter_title, "Legal Notice", "In Progress")

            # 6. Return Full Object for Frontend
            results.append({
                "id": doc_id,
                "filename": file.filename,
                "type": doc_type,
                "date": upload_date,
                "client_id": int(client_id),
                "success": True,
                "message": "Uploaded Successfully" if created else "Updated"
            })
            
        except Exception as e:
            print(f"❌ Upload Error: {e}")
            results.append({"filename": file.filename, "success": False, "error": str(e)})
            
    return results

@app.get("/api/documents/{doc_id}/view", tags=["Documents"])
def view_doc(doc_id: int):
    path, fname = database.get_document_path(doc_id)
    if not path or not os.path.exists(path): raise HTTPException(404, "File not found")
    media = "application/pdf" if fname.lower().endswith(".pdf") else "application/octet-stream"
    return FileResponse(path, media_type=media, headers={"Content-Disposition": f"inline; filename={fname}"})

@app.delete("/api/documents/{doc_id}", tags=["Documents"])
def delete_document_endpoint(doc_id: int):
    success = database.delete_document(doc_id)
    if not success: raise HTTPException(404, "Document not found")
    return {"success": True}

# ==========================================
# 3. DRAFTING ENDPOINTS
# ==========================================
@app.post("/api/drafting/generate", tags=["Drafting"])
async def create_draft_endpoint(request: DraftRequest):
    print(f"📝 Generating Draft: {request.template_type} for {request.client_name}")
    try:
        result = await draft_engine.generate_legal_draft(request)
        return result
    except Exception as e:
        print(f"❌ Drafting Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/drafting/autopopulate-matter", tags=["Drafting"])
async def autopopulate_matter(payload: dict = Body(...)):
    doc_id = payload.get("doc_id")
    if not doc_id: raise HTTPException(400, "doc_id required")
    
    path, filename = database.get_document_path(doc_id)
    if not path or not os.path.exists(path): raise HTTPException(404, "Document not found")
    
    try:
        if filename.lower().endswith(".pdf"):
            reader = pypdf.PdfReader(path)
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
        else:
            with open(path, "r", errors="ignore") as f: text = f.read()

        summary_data = await doc_intelligence.analyze_legal_document(text[:15000])
        
        if isinstance(summary_data, dict):
            key_points = "\n- ".join(summary_data.get("key_points_summary", ["No summary available"]))
            issues = "\n- ".join(summary_data.get("legality_assessment", {}).get("identified_issues_or_defects", ["None"]))
            
            formatted_text = f"""**DOCUMENT SUMMARY:**
- {key_points}

**IDENTIFIED LEGAL ISSUES:**
- {issues}

**PARTIES INVOLVED:**
{json.dumps(summary_data.get("document_metadata", {}), indent=2)}"""
        else:
            formatted_text = str(summary_data)

        return {"success": True, "matter_details": formatted_text, "filename": filename}
    except Exception as e:
        print(f"Auto-populate error: {e}")
        return {"success": True, "matter_details": "Error analyzing document.", "filename": filename}

@app.get("/api/drafting/templates", tags=["Drafting"])
def get_drafting_templates():
    return [
        {"id": "notice_138", "name": "Section 138 NI Act Notice", "category": "Notices", "description": "Dishonour of Cheque Notice"},
        {"id": "bail_application", "name": "Bail Application", "category": "Criminal", "description": "Regular Bail under CrPC"},
        {"id": "gst_reply", "name": "GST Show Cause Reply", "category": "Tax", "description": "Reply to DRC-01"},
        {"id": "recovery_suit", "name": "Recovery Suit", "category": "Civil", "description": "Suit for recovery of money"},
        {"id": "consumer_complaint", "name": "Consumer Complaint", "category": "Civil", "description": "Complaint against service deficiency"}
    ]

# ==========================================
# 4. MATTERS & DEADLINES
# ==========================================
@app.get("/api/clients/{client_id}/matters", tags=["Matters"])
def get_matters(client_id: int): return database.get_client_matters(client_id)

@app.post("/api/matters", tags=["Matters"])
def add_matter(m: MatterCreate):
    s, res = database.create_matter(m.client_id, m.title, m.type, m.status)
    if not s: raise HTTPException(500, detail=str(res))
    return {"success": True, "id": res}

@app.get("/api/clients/{client_id}/deadlines", tags=["Deadlines"])
def get_deadlines(client_id: int): return database.get_client_deadlines(client_id)

@app.post("/api/deadlines", tags=["Deadlines"])
def add_deadline(d: DeadlineCreate):
    success, res = database.add_deadline(d.client_id, d.title, d.due_date, d.type)
    if not success: raise HTTPException(500, detail=str(res))
    return {"success": True, "id": res}

# ✅ MARK DEADLINE DONE
@app.post("/api/deadlines/{deadline_id}/complete", tags=["Deadlines"])
def complete_deadline(deadline_id: int):
    print(f"📥 API Request: Mark Deadline {deadline_id} as Done")
    success = database.mark_deadline_done(deadline_id)
    if not success: 
        raise HTTPException(status_code=500, detail="Failed to update status")
    return {"success": True, "message": "Deadline marked as done"}

# ==========================================
# 5. CHAT
# ==========================================
@app.post("/api/chat/doc-qa", tags=["Chatbot"])
def chat(req: ChatRequest): return logic.ask_client_bot(req.query, req.client_id)

# ==========================================
# 6. RESEARCH & ANALYSIS
# ==========================================
class SearchQuery(BaseModel):
    query: str

@app.post("/api/research/search", tags=["Research"])
def search_case_laws(payload: SearchQuery):
    try:
        results = logic.search_legal_documents(payload.query)
        return {"results": results}
    except Exception as e:
        print(f"Search API Error: {e}")
        return {"results": []}

@app.get("/api/research/weekly-updates", tags=["Research"])
def get_weekly_updates():
    try:
        content = logic.generate_weekly_update()
        return {"content": content}
    except Exception as e:
        return {"content": f"System Error: {str(e)}"}

@app.post("/api/research/compare", tags=["Research"])
async def compare_documents(files: List[UploadFile] = File(...)):
    if len(files) < 2: raise HTTPException(400, "Need 2 files")
    try:
        c1 = await files[0].read()
        c2 = await files[1].read()
        t1 = extract_text_from_file(c1, files[0].filename)
        t2 = extract_text_from_file(c2, files[1].filename)
        analysis = logic.compare_judgments_logic(t1, t2)
        return {"content": analysis}
    except Exception as e:
        return {"content": f"Error: {str(e)}"}

@app.post("/api/research/appeal-grounds", tags=["Research"])
async def generate_appeal_grounds(text: str = Form(None), files: List[UploadFile] = File(None)):
    try:
        combined = (text or "") + "\n"
        if files:
            for f in files:
                c = await f.read()
                combined += extract_text_from_file(c, f.filename) + "\n"
        if not combined.strip(): raise HTTPException(400, "No input")
        outline = logic.generate_argument_outline(combined)
        return {"content": outline}
    except Exception as e:
        return {"content": f"Error: {str(e)}"}

# if __name__ == "__main__":
#     import uvicorn
#     # ✅ Matches Frontend API Port (8005)
#     uvicorn.run(app, host="0.0.0.0", port=8005)
