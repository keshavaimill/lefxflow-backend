# import requests
# import json

# API_URL = "http://localhost:8000"

# # ==========================================
# # 1. CLIENTS
# # ==========================================
# def get_all_clients():
#     try:
#         resp = requests.get(f"{API_URL}/clients")
#         if resp.status_code == 200:
#             return [(c['id'], c['full_name']) for c in resp.json()]
#     except: return []
#     return []

# def get_client_details(client_id):
#     try:
#         resp = requests.get(f"{API_URL}/clients/{client_id}")
#         if resp.status_code == 200: return resp.json()
#     except: pass
#     return {}

# def add_client(fn, mn, ln, em, mob):
#     payload = {"first_name": fn, "middle_name": mn, "last_name": ln, "email": em, "mobile": mob}
#     resp = requests.post(f"{API_URL}/clients", json=payload)
#     if resp.status_code == 200: return True, "Client Added"
#     return False, resp.text

# def update_client(cid, fn, mn, ln, em, mob):
#     payload = {"client_id": cid, "first_name": fn, "middle_name": mn, "last_name": ln, "email": em, "mobile": mob}
#     resp = requests.put(f"{API_URL}/clients/update", json=payload)
#     if resp.status_code == 200: return True, "Updated"
#     return False, resp.text

# def delete_client(cid):
#     requests.delete(f"{API_URL}/clients/{cid}")

# # ==========================================
# # 2. DOCUMENTS
# # ==========================================
# def get_client_files(client_id):
#     try:
#         resp = requests.get(f"{API_URL}/documents/{client_id}")
#         if resp.status_code == 200:
#             return [(d['id'], d['filename'], d['type'], d['date']) for d in resp.json()]
#     except: pass
#     return []

# def upload_document(client_id, client_name, doc_type, files):
#     files_payload = [('files', (f.name, f.getvalue(), f.type)) for f in files]
#     data = {'client_id': client_id, 'client_name': client_name, 'doc_type': doc_type}
#     resp = requests.post(f"{API_URL}/documents/upload", data=data, files=files_payload)
#     if resp.status_code == 200: return True, "Uploaded"
#     return False, "Failed"

# def delete_document(doc_id):
#     requests.delete(f"{API_URL}/documents/{doc_id}")

# def get_doc_content(doc_id):
#     """Fetches text content for a specific file ID (Used in Drafting & Chatbot)"""
#     try:
#         resp = requests.get(f"{API_URL}/documents/{doc_id}/content")
#         if resp.status_code == 200:
#             return resp.json()
#     except: pass
#     return None

# # ==========================================
# # 3. AI AGENT (Workspace Features)
# # ==========================================
# def get_summary(client_id):
#     resp = requests.post(f"{API_URL}/ai/summary", json={"client_id": client_id})
#     return resp.json()['content'] if resp.status_code == 200 else "Error"

# def get_timeline(client_id):
#     resp = requests.post(f"{API_URL}/ai/timeline", json={"client_id": client_id})
#     return resp.json()['content'] if resp.status_code == 200 else "Error"

# def check_compliance(client_id, matter):
#     resp = requests.post(f"{API_URL}/ai/compliance", json={"client_id": client_id, "matter_type": matter})
#     if resp.status_code == 200: return resp.json()['missing'], resp.json()['present']
#     return [], []

# def draft_reply(cid, cname, hist, instr):
#     payload = {"client_id": cid, "client_name": cname, "history": hist, "instruction": instr}
#     resp = requests.post(f"{API_URL}/ai/draft_reply", json=payload)
#     return resp.json()['content'] if resp.status_code == 200 else "Error"

# # ==========================================
# # 4. COMMUNICATIONS
# # ==========================================
# def get_comms(client_id):
#     try:
#         resp = requests.get(f"{API_URL}/communications/{client_id}")
#         if resp.status_code == 200:
#             return [(c['id'], c['platform'], c['direction'], c['content'], c['timestamp']) for c in resp.json()]
#     except: pass
#     return []

# def log_comm(cid, plat, direct, content):
#     requests.post(f"{API_URL}/communications/log", json={"client_id": cid, "platform": plat, "direction": direct, "content": content})

# def delete_comm(mid):
#     requests.delete(f"{API_URL}/communications/{mid}")

# def send_email(recip, sub, cont):
#     payload = {"recipient": recip, "subject": sub, "content": cont}
#     resp = requests.post(f"{API_URL}/communications/send_email", json=payload)
#     return resp.json()

# # ==========================================
# # 5. DRAFTING STUDIO
# # ==========================================
# def analyze_file_drafting(file_obj):
#     files = {'file': (file_obj.name, file_obj.getvalue(), file_obj.type)}
#     resp = requests.post(f"{API_URL}/drafting/analyze_file", files=files)
#     if resp.status_code == 200: return resp.json()
#     return None

# def generate_draft(req_dict):
#     resp = requests.post(f"{API_URL}/drafting/generate", json=req_dict)
#     return resp.json() if resp.status_code == 200 else {"content": "Error"}

# def refine_draft(text, instr):
#     resp = requests.post(f"{API_URL}/drafting/refine", json={"selected_text": text, "instruction": instr})
#     return resp.json()['content'] if resp.status_code == 200 else "Error"

# def suggest_cases(text):
#     resp = requests.post(f"{API_URL}/drafting/suggest_cases", json={"text": text})
#     return resp.json()['content'] if resp.status_code == 200 else "Error"

# # ==========================================
# # 6. CHATBOT & RESEARCH (Updated Names)
# # ==========================================

# def research_search(query):
#     """Returns full JSON object (type + results)"""
#     resp = requests.post(f"{API_URL}/research/search", json={"query": query})
#     if resp.status_code == 200:
#         return resp.json()
#     return {"type": "error", "results": []}

# def research_weekly():
#     """Returns text content string"""
#     resp = requests.get(f"{API_URL}/research/weekly")
#     if resp.status_code == 200:
#         return resp.json()['content']
#     return "Error fetching updates."

# def chat_with_docs(query, client_id):
#     """Chat with client docs"""
#     resp = requests.post(f"{API_URL}/chat/ask_client_docs", json={"query": query, "client_id": client_id})
#     if resp.status_code == 200:
#         return resp.json()['answer']
#     return "Error generating response."

# def compare_texts(text1, text2):
#     """Compare two text blocks"""
#     payload = {"text1": text1, "text2": text2}
#     resp = requests.post(f"{API_URL}/research/compare", json=payload)
#     if resp.status_code == 200:
#         return resp.json()['analysis']
#     return "Error comparing documents."

# def generate_appeal_grounds(text):
#     """Generate appeal grounds from text"""
#     resp = requests.post(f"{API_URL}/research/appeal_grounds", json={"text": text})
#     if resp.status_code == 200:
#         return resp.json()['outline']
#     return "Error generating grounds."



















import requests
import json

API_URL = "http://localhost:8005"

# ==========================================
# 1. CLIENTS
# ==========================================
def get_all_clients():
    try:
        resp = requests.get(f"{API_URL}/api/clients")
        if resp.status_code == 200:
            return [(c['id'], c['full_name']) for c in resp.json()]
    except: return []
    return []

def get_client_details(client_id):
    try:
        resp = requests.get(f"{API_URL}/api/clients/{client_id}")
        if resp.status_code == 200: return resp.json()
    except: pass
    return {}

def add_client(fn, mn, ln, em, mob, pan, gstin):
    """Adds a client with mandatory PAN and GSTIN."""
    payload = {
        "first_name": fn, "middle_name": mn, "last_name": ln, 
        "email": em, "mobile": mob, "pan": pan, "gstin": gstin
    }
    resp = requests.post(f"{API_URL}/api/clients", json=payload)
    if resp.status_code == 200: return True, "Client Added"
    return False, resp.text

def update_client(cid, fn, mn, ln, em, mob, pan, gstin):
    """Updates client details including PAN and GSTIN."""
    payload = {
        "client_id": cid, "first_name": fn, "middle_name": mn, 
        "last_name": ln, "email": em, "mobile": mob, "pan": pan, "gstin": gstin
    }
    resp = requests.put(f"{API_URL}/api/clients/{cid}", json=payload)
    if resp.status_code == 200: return True, "Updated"
    return False, resp.text

def delete_client(cid):
    requests.delete(f"{API_URL}/api/clients/{cid}")

# ==========================================
# 2. DOCUMENTS
# ==========================================
def get_client_files(client_id):
    try:
        resp = requests.get(f"{API_URL}/api/clients/{client_id}/documents")
        if resp.status_code == 200:
            return [(d['id'], d['filename'], d['type'], d['date']) for d in resp.json()]
    except: pass
    return []

def upload_document(client_id, client_name, doc_type, files):
    files_payload = [('files', (f.name, f.getvalue(), f.type)) for f in files]
    data = {'client_id': client_id, 'client_name': client_name, 'doc_type': doc_type}
    resp = requests.post(f"{API_URL}/api/documents/upload", data=data, files=files_payload)
    if resp.status_code == 200: return True, "Uploaded"
    return False, "Failed"

def delete_document(doc_id):
    requests.delete(f"{API_URL}/api/documents/{doc_id}")

def get_doc_content(doc_id):
    """Fetches text content for a specific file ID (Used in Drafting & Chatbot)"""
    try:
        resp = requests.get(f"{API_URL}/api/documents/{doc_id}/content")
        if resp.status_code == 200:
            return resp.json()
    except: pass
    return None

# ==========================================
# 3. AI AGENT (Workspace Features)
# ==========================================
def get_summary(client_id):
    resp = requests.post(f"{API_URL}/api/ai/summary", json={"client_id": client_id})
    return resp.json()['content'] if resp.status_code == 200 else "Error"

def get_timeline(client_id):
    resp = requests.post(f"{API_URL}/api/ai/timeline", json={"client_id": client_id})
    return resp.json()['content'] if resp.status_code == 200 else "Error"

def check_compliance(client_id, matter):
    resp = requests.post(f"{API_URL}/api/ai/compliance", json={"client_id": client_id, "matter_type": matter})
    if resp.status_code == 200: return resp.json()['missing'], resp.json()['present']
    return [], []

def draft_reply(cid, cname, hist, instr):
    payload = {"client_id": cid, "client_name": cname, "history": hist, "instruction": instr}
    resp = requests.post(f"{API_URL}/api/ai/draft-reply", json=payload)
    return resp.json()['content'] if resp.status_code == 200 else "Error"

# ==========================================
# 4. COMMUNICATIONS
# ==========================================
def get_comms(client_id):
    try:
        resp = requests.get(f"{API_URL}/api/communications/{client_id}")
        if resp.status_code == 200:
            return [(c['id'], c['platform'], c['direction'], c['content'], c['timestamp']) for c in resp.json()]
    except: pass
    return []

def log_comm(cid, plat, direct, content):
    requests.post(f"{API_URL}/api/communications/log", json={"client_id": cid, "platform": plat, "direction": direct, "content": content})

def delete_comm(mid):
    requests.delete(f"{API_URL}/api/communications/{mid}")  # Note: Endpoint usually isn't exposed in main.py, check if needed. Assuming delete isn't critical for frontend logic or add to main.py if needed.

def send_email(recip, sub, cont):
    payload = {"recipient": recip, "subject": sub, "content": cont}
    resp = requests.post(f"{API_URL}/api/communications/send-email", json=payload)
    return resp.json()

# ==========================================
# 5. DRAFTING STUDIO
# ==========================================
def analyze_file_drafting(file_obj):
    files = {'file': (file_obj.name, file_obj.getvalue(), file_obj.type)}
    resp = requests.post(f"{API_URL}/api/drafting/analyze", files=files)
    if resp.status_code == 200: return resp.json()
    return None

def generate_draft(req_dict):
    resp = requests.post(f"{API_URL}/api/drafting/generate", json=req_dict)
    return resp.json() if resp.status_code == 200 else {"content": "Error"}

def refine_draft(text, instr):
    resp = requests.post(f"{API_URL}/api/drafting/refine", json={"selected_text": text, "instruction": instr})
    return resp.json()['content'] if resp.status_code == 200 else "Error"

def suggest_cases(text):
    resp = requests.post(f"{API_URL}/api/drafting/suggest-cases", json={"text": text})
    return resp.json()['content'] if resp.status_code == 200 else "Error"

# ==========================================
# 6. CHATBOT & RESEARCH (Updated Names)
# ==========================================

def research_search(query):
    """Returns full JSON object (type + results)"""
    resp = requests.post(f"{API_URL}/api/research/search", json={"query": query})
    if resp.status_code == 200:
        return resp.json()
    return {"type": "error", "results": []}

def research_weekly():
    """Returns text content string"""
    resp = requests.get(f"{API_URL}/api/research/weekly-updates")
    if resp.status_code == 200:
        return resp.json()['content']
    return "Error fetching updates."

def chat_with_docs(query, client_id):
    """Chat with client docs"""
    resp = requests.post(f"{API_URL}/api/chat/doc-qa", json={"query": query, "client_id": client_id})
    if resp.status_code == 200:
        return resp.json()['answer']
    return "Error generating response."

def compare_texts(text1, text2):
    """Compare two text blocks"""
    payload = {"text1": text1, "text2": text2}
    resp = requests.post(f"{API_URL}/api/research/compare", json=payload)
    if resp.status_code == 200:
        return resp.json()['analysis']
    return "Error comparing documents."

def generate_appeal_grounds(text):
    """Generate appeal grounds from text"""
    resp = requests.post(f"{API_URL}/api/research/appeal-grounds", json={"text": text})
    if resp.status_code == 200:
        return resp.json()['outline']
    return "Error generating grounds."