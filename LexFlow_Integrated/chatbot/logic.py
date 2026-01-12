import os
from openai import OpenAI

# ✅ CORRECT NEW IMPORT (Fixes the crash)
try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None
    print("⚠️ Warning: 'duckduckgo-search' library not found. Using Offline Mode.")

# --- LOCAL IMPORTS ---
from backend.utils import retrieval, chunk_and_index, file_handler

# Initialize OpenAI
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except:
    client = None

# STRICT DOMAIN WHITELIST
TRUSTED_DOMAINS = [
    "indiankanoon.org", "taxmann.com", "livelaw.in", "barandbench.com", 
    "scconline.com", "itatonline.org", "ibbi.gov.in", "incometaxindia.gov.in", 
    "cbic.gov.in", "mca.gov.in", "sci.gov.in", "casemine.com",
    "manupatra.com", "legalserviceindia.com", "mondaq.com", "supremecourt.gov.in"
]

LEGAL_KEYWORDS = [
    "judgment", "judgement", "supreme court", "high court", "tribunal", 
    "circular", "notification", "precedent", "act", "section", "rule", 
    "order", "bench", "petition", "appeal", "tax", "gst"
]

# ==========================================
# 1. FILE INGESTION LOGIC
# ==========================================
def process_and_embed_client_file(file_path):
    doc_hash = chunk_and_index.build_index_from_file(file_path)
    if doc_hash:
        print(f"✅ File indexed: {doc_hash}")
    return doc_hash

def ingest_new_file(file_path, client_id):
    try:
        with open(file_path, "rb") as f:
            file_obj = type('obj', (object,), {'name': os.path.basename(file_path), 'getvalue': lambda: f.read()})
            text = file_handler.read_file_content(file_obj)
        
        if text:
            doc_hash = chunk_and_index.index_document_text(text, client_id)
            print(f"✅ Success: File embedded with hash {doc_hash}")
            return doc_hash
    except Exception as e:
        print(f"❌ Embedding Error: {e}")
        return None

# ==========================================
# 2. SEARCH ENGINE (Safe Mode)
# ==========================================
def smart_legal_search(query, max_results=5, time_limit=None):
    if not DDGS:
        print("❌ Search Library Missing (Offline Mode)")
        return []

    valid_results = []
    site_filter = " OR ".join([f"site:{d}" for d in TRUSTED_DOMAINS])
    final_query = f"'{query}' ({site_filter})"
    
    try:
        with DDGS() as ddgs:
            # Attempt search
            hits = list(ddgs.text(final_query, region='in-en', timelimit=time_limit, max_results=10))
            for h in hits:
                content_blob = (h.get('title', '') + " " + h.get('body', '') + " " + h.get('href', '')).lower()
                if any(k in content_blob for k in LEGAL_KEYWORDS):
                    valid_results.append(h)
                if len(valid_results) >= max_results: break
            
            # Fallback
            if not valid_results:
                hits = list(ddgs.text(f"{query} India Supreme Court", region='in-en', max_results=3))
                valid_results = hits

    except Exception as e:
        print(f"Search Error: {e}")
        return []

    return valid_results

# ==========================================
# 3. WEEKLY UPDATES (Fix: Never Crushes)
# ==========================================
def generate_weekly_update():
    print("🔄 Logic: Generating Weekly Update...") 

    # 1. Immediate Fallback if library missing
    if not DDGS:
        return """**⚠️ System Notice:**
The search module is currently offline (Library Missing).

To fix this, the administrator must run:
`pip install -U duckduckgo-search`

*Please try again after installation.*"""

    queries = [
        "Latest Supreme Court Judgments India this week",
        "CBDT Circulars Income Tax India latest"
    ]
    raw_text = ""
    
    # 2. Try fetching data (Wrapped to prevent crash)
    try:
        for q in queries:
            hits = smart_legal_search(q, max_results=2, time_limit='w')
            for h in hits:
                raw_text += f"\nSOURCE: {h.get('title', 'Unknown')}\nCONTENT: {h.get('body', '')}\n"
    except Exception as e:
        print(f"Search Loop Error: {e}")
    
    # 3. Handle No Data found
    if not raw_text.strip():
        return "No specific legal updates found this week on trusted portals. Please check the Official Gazette directly."

    # 4. Handle Missing OpenAI
    if not client:
        return f"**Latest Updates (Raw Data - AI Unavailable):**\n\n{raw_text[:800]}..."

    # 5. Generate AI Summary
    try:
        prompt = f"Summarize these legal updates in bullet points:\n{raw_text[:5000]}"
        response = client.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating summary: {e}"

# ==========================================
# 4. CHAT WITH DOCS
# ==========================================
def suggest_followups(answer: str, query: str, max_suggestions: int = 3):
    try:
        if not client: return []
        prompt = f"Suggest 3 follow-up questions for: {query}\nAnswer: {answer[:500]}"
        res = client.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
        )
        return [l.strip("- ").strip() for l in res.choices[0].message.content.split("\n") if l.strip()]
    except:
        return []

def get_client_file_hashes(client_id):
    uploads_dir = os.path.join(os.getcwd(), "data", "uploads")
    index_dir = os.path.join(os.getcwd(), "data", "index_data")
    hashes = []
    if not os.path.exists(uploads_dir): return []
    
    target_folder = None
    for folder in os.listdir(uploads_dir):
        if folder.startswith(f"{client_id}_"):
            target_folder = os.path.join(uploads_dir, folder)
            break
    if not target_folder: return []

    for fname in os.listdir(target_folder):
        fpath = os.path.join(target_folder, fname)
        if os.path.isfile(fpath) and not fname.startswith("."):
            try:
                with open(fpath, "rb") as f:
                    dummy = type('obj', (object,), {'name': fname, 'getvalue': lambda: f.read()})
                    text = file_handler.read_file_content(dummy)
                    d_hash = chunk_and_index._hash_text(text)
                    if os.path.exists(os.path.join(index_dir, d_hash)):
                        hashes.append(d_hash)
            except: continue
    return hashes

def ask_client_bot(query: str, client_id: int):
    client_hashes = get_client_file_hashes(client_id)
    pdf_context = ""
    source_label = ""
    
    if client_hashes:
        chunks = retrieval.retrieve_top_k_chunks(query, k=5, doc_hash=client_hashes)
        if chunks: 
            pdf_context = "\n\n".join(chunks)
            source_label = "Internal Client Documents"

    if not pdf_context:
        hits = smart_legal_search(query, max_results=3)
        if hits:
            pdf_context = "\n".join([f"{h['title']}: {h['body']}" for h in hits])
            source_label = "Trusted Legal Web Sources"
    
    if not pdf_context:
        return {"answer": "I could not find information on this.", "followups": []}

    if not client:
        return {"answer": "AI Client not initialized.", "followups": []}

    res = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[{"role": "system", "content": "You are a Senior Indian Lawyer."},
                  {"role": "user", "content": f"Context ({source_label}):\n{pdf_context}\n\nQuestion: {query}"}]
    )
    ans = res.choices[0].message.content + f"\n\n*Source: {source_label}*"
    return {"answer": ans, "followups": suggest_followups(ans, query)}

# ==========================================
# 5. ANALYSIS TOOLS
# ==========================================
def search_legal_documents(query: str):
    return smart_legal_search(query, max_results=5)

def compare_judgments_logic(text1: str, text2: str):
    if not client: return "AI Client not initialized."
    return client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": f"Compare these: {text1[:5000]} vs {text2[:5000]}"}]).choices[0].message.content

def generate_argument_outline(text: str):
    if not client: return "AI Client not initialized."
    return client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": f"Create outline for: {text[:10000]}"}]).choices[0].message.content