# from pydantic import BaseModel
# from typing import Optional, List, Any

# # --- CLIENT SCHEMAS (Updated for React Integration) ---

# class ClientCreate(BaseModel):
#     name: str          # Matches frontend 'name'
#     type: str          # Matches frontend 'type' (Company, LLP, etc.)
#     gstin: Optional[str] = ""
#     pan: Optional[str] = ""
    
#     # These are not in your React "Create Client" modal, so they must be Optional
#     email: Optional[str] = None 
#     mobile: Optional[str] = None

# class ClientUpdate(BaseModel):
#     client_id: int
#     name: str
#     type: str
#     gstin: Optional[str]
#     pan: Optional[str]
#     email: Optional[str]
#     mobile: Optional[str]

# # --- OTHER SCHEMAS (Keep as is) ---
# class SearchQuery(BaseModel):
#     query: str
#     time_limit: Optional[str] = None

# class ChatRequest(BaseModel):
#     query: str
#     client_id: int

# class CompareRequest(BaseModel):
#     text1: str
#     text2: str

# class AppealRequest(BaseModel):
#     text: str

# class SummaryRequest(BaseModel):
#     client_id: int

# class TimelineRequest(BaseModel):
#     client_id: int

# class ComplianceRequest(BaseModel):
#     client_id: int
#     matter_type: str

# class ReplyDraftRequest(BaseModel):
#     client_id: int
#     client_name: str
#     history: str
#     instruction: str

# class LogMessageRequest(BaseModel):
#     client_id: int
#     platform: str
#     direction: str
#     content: str

# # --- NEW: DRAFTING REQUEST (Added for Drafting Engine) ---
# class DraftRequest(BaseModel):
#     client_id: int
#     client_name: str
#     doc_type: str
#     topic: str
#     facts: Optional[str] = None
#     template_type: Optional[str] = "General"
#     doc_hash: Optional[str] = None  # For AI RAG context

























# from pydantic import BaseModel
# from typing import Optional, List, Any

# # --- CLIENT SCHEMAS ---
# class ClientCreate(BaseModel):
#     name: str
#     type: str
#     gstin: Optional[str] = ""
#     pan: Optional[str] = ""
#     email: Optional[str] = None 
#     mobile: Optional[str] = None

# class ClientUpdate(BaseModel):
#     client_id: int
#     name: str
#     type: str
#     gstin: Optional[str]
#     pan: Optional[str]
#     email: Optional[str]
#     mobile: Optional[str]

# # --- OTHER SCHEMAS ---
# class SearchQuery(BaseModel):
#     query: str
#     time_limit: Optional[str] = None

# class ChatRequest(BaseModel):
#     query: str
#     client_id: int

# class DraftRequest(BaseModel):
#     client_id: int
#     client_name: str
#     doc_type: str
#     topic: str
#     facts: Optional[str] = None
#     template_type: Optional[str] = "General"
#     doc_hash: Optional[str] = None 

# # --- MATTER SCHEMAS ---
# class MatterCreate(BaseModel):
#     client_id: int
#     title: str
#     type: str
#     status: Optional[str] = "In Progress"

# # --- DEADLINE SCHEMAS (CRITICAL FIX) ---
# class DeadlineCreate(BaseModel):
#     client_id: int
#     title: str
#     due_date: str
#     type: str































# from pydantic import BaseModel
# from typing import Optional, List, Any

# # --- CLIENT SCHEMAS ---
# class ClientCreate(BaseModel):
#     name: str
#     type: str
#     gstin: Optional[str] = ""
#     pan: Optional[str] = ""
#     email: Optional[str] = None 
#     mobile: Optional[str] = None

# class ClientUpdate(BaseModel):
#     client_id: int
#     name: str
#     type: str
#     gstin: Optional[str]
#     pan: Optional[str]
#     email: Optional[str]
#     mobile: Optional[str]

# # --- OTHER SCHEMAS ---
# class SearchQuery(BaseModel):
#     query: str
#     time_limit: Optional[str] = None

# class ChatRequest(BaseModel):
#     query: str
#     client_id: int

# class DraftRequest(BaseModel):
#     client_id: int
#     client_name: str
#     doc_type: str
#     topic: str
#     facts: Optional[str] = None
#     template_type: Optional[str] = "General"
#     doc_hash: Optional[str] = None 

# # --- MATTER SCHEMAS ---
# class MatterCreate(BaseModel):
#     client_id: int
#     title: str
#     type: str
#     status: Optional[str] = "In Progress"

# # --- DEADLINE SCHEMAS (REQUIRED) ---
# class DeadlineCreate(BaseModel):
#     client_id: int
#     title: str
#     due_date: str
#     type: str





















from pydantic import BaseModel
from typing import Optional, List, Any

# --- CLIENT SCHEMAS ---
class ClientCreate(BaseModel):
    name: str
    type: str
    gstin: Optional[str] = ""
    pan: Optional[str] = ""
    email: Optional[str] = None 
    mobile: Optional[str] = None

class ClientUpdate(BaseModel):
    client_id: int
    name: str
    type: str
    gstin: Optional[str]
    pan: Optional[str]
    email: Optional[str]
    mobile: Optional[str]

# --- OTHER SCHEMAS ---
class SearchQuery(BaseModel):
    query: str
    time_limit: Optional[str] = None

class ChatRequest(BaseModel):
    query: str
    client_id: int

class DraftRequest(BaseModel):
    client_id: int
    client_name: str
    doc_type: str
    topic: str
    facts: Optional[str] = None
    template_type: Optional[str] = "General"
    doc_hash: Optional[str] = None 

# --- MATTER SCHEMAS ---
class MatterCreate(BaseModel):
    client_id: int
    title: str
    type: str
    status: Optional[str] = "In Progress"

# --- DEADLINE SCHEMAS ---
class DeadlineCreate(BaseModel):
    client_id: int
    title: str
    due_date: str
    type: str