import sqlite3
import os
import datetime
import shutil 

# --- PATH CONFIGURATION ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_NAME = os.path.join(DATA_DIR, "lexflow.db")

# =============================
# HELPER & INITIALIZATION
# =============================
def get_db_connection():
    """Helper to get a database connection with Row factory."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # 1. Clients Table
    c.execute('''CREATE TABLE IF NOT EXISTS clients 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, type TEXT, 
                  gstin TEXT, pan TEXT, email TEXT, mobile TEXT, status TEXT)''')
    
    # 2. Documents Table
    c.execute('''CREATE TABLE IF NOT EXISTS documents 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, client_id INTEGER, 
                  filename TEXT, filepath TEXT, doc_type TEXT, upload_date TEXT, 
                  embedding_hash TEXT, FOREIGN KEY(client_id) REFERENCES clients(id))''')
    
    # 3. Communications Table
    c.execute('''CREATE TABLE IF NOT EXISTS communications 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, client_id INTEGER, 
                  platform TEXT, direction TEXT, content TEXT, timestamp TEXT,
                  FOREIGN KEY(client_id) REFERENCES clients(id))''')
    
    # 4. Matters Table
    c.execute('''CREATE TABLE IF NOT EXISTS matters 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, client_id INTEGER, 
                  title TEXT, type TEXT, status TEXT, last_updated TEXT,
                  FOREIGN KEY(client_id) REFERENCES clients(id))''')

    # 5. Deadlines Table
    c.execute('''CREATE TABLE IF NOT EXISTS deadlines 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, client_id INTEGER, 
                  title TEXT, due_date TEXT, status TEXT, type TEXT,
                  FOREIGN KEY(client_id) REFERENCES clients(id))''')

    conn.commit()
    conn.close()
    ensure_embedding_column()
    print(f"✅ Database initialized at: {DB_NAME}")

def ensure_embedding_column():
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE documents ADD COLUMN embedding_hash TEXT")
        conn.commit()
    except Exception:
        pass
    conn.close()

# =============================
# CLIENTS (Unique Logic with Auto-Recovery)
# =============================
def add_client(name, c_type, gstin, pan, email=None, mobile=None, status="active"):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        # Check for duplicate Client (by Name or PAN)
        query = "SELECT id FROM clients WHERE name=?"
        params = [name]
        if pan and len(pan) > 5:
            query += " OR pan=?"
            params.append(pan)
            
        c.execute(query, tuple(params))
        existing = c.fetchone()
        
        if existing:
            print(f"⚠️ Duplicate Prevented: '{name}' already exists (ID: {existing['id']})")
            return True, {"id": str(existing['id']), "name": name, "status": "Existing"}

        c.execute("INSERT INTO clients (name, type, gstin, pan, email, mobile, status) VALUES (?,?,?,?,?,?,?)",
                  (name, c_type, gstin, pan, email, mobile, status))
        conn.commit()
        print(f"✅ New Client Created: {name} (ID: {c.lastrowid})")
        return True, {"id": str(c.lastrowid), "name": name, "status": "Created"}
        
    except sqlite3.OperationalError as e:
        # ✅ AUTO-FIX: If table missing, re-init DB and retry
        if "no such table" in str(e):
            print("⚠️ Tables missing. Re-initializing Database...")
            init_db()
            return add_client(name, c_type, gstin, pan, email, mobile, status)
        return False, str(e)
        
    except Exception as e:
        print(f"❌ Error Adding Client: {e}")
        return False, str(e)
    finally:
        conn.close()

def get_all_clients():
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM clients ORDER BY id DESC")
        rows = c.fetchall()
        return [dict(row) for row in rows]
    except Exception:
        return []

def get_client_details(client_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM clients WHERE id=?", (client_id,))
    res = c.fetchone()
    conn.close()
    return dict(res) if res else {}

def delete_client_fully(client_id):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Delete Folder
    c.execute("SELECT name FROM clients WHERE id=?", (client_id,))
    res = c.fetchone()
    if res:
        safe_name = "".join([x for x in res['name'] if x.isalnum() or x in (" ", "_")]).strip()
        folder = os.path.join(DATA_DIR, "uploads", f"{client_id}_{safe_name.replace(' ', '_')}")
        if os.path.exists(folder):
            try: shutil.rmtree(folder)
            except: pass
            
    # Delete DB Records
    for table in ["communications", "documents", "matters", "deadlines", "clients"]:
        col = "id" if table == "clients" else "client_id"
        c.execute(f"DELETE FROM {table} WHERE {col}=?", (client_id,))
        
    conn.commit()
    conn.close()
    return True

# =============================
# DOCUMENTS (Sync Fix)
# =============================
def save_document(client_id, filename, filepath, doc_type="General"):
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        # Force integer
        client_id_int = int(client_id)
        
        # Check Duplicate
        c.execute("SELECT id FROM documents WHERE client_id=? AND filename=?", (client_id_int, filename))
        existing = c.fetchone()
        
        # Use Standard Date (YYYY-MM-DD) for Frontend
        date_now = datetime.datetime.now().strftime("%Y-%m-%d")
        
        if existing:
            doc_id = existing['id']
            c.execute("UPDATE documents SET filepath=?, doc_type=?, upload_date=? WHERE id=?", 
                      (filepath, doc_type, date_now, doc_id))
            conn.commit()
            return doc_id, False, date_now
        else:
            c.execute("INSERT INTO documents (client_id, filename, filepath, doc_type, upload_date) VALUES (?, ?, ?, ?, ?)",
                      (client_id_int, filename, filepath, doc_type, date_now))
            doc_id = c.lastrowid
            conn.commit()
            return doc_id, True, date_now
            
    except Exception as e:
        print(f"❌ DB Save Error: {e}")
        return None, False, None
    finally:
        conn.close()

def get_client_files(client_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, filename, doc_type, upload_date FROM documents WHERE client_id=?", (int(client_id),))
    rows = c.fetchall()
    
    clean_list = []
    for r in rows:
        clean_list.append({
            "id": r['id'], 
            "filename": r['filename'], 
            "type": r['doc_type'], 
            "date": r['upload_date'], 
            "client_id": int(client_id)
        })
    conn.close()
    return clean_list

def delete_document(doc_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT filepath FROM documents WHERE id=?", (doc_id,))
    res = c.fetchone()
    if res and res['filepath'] and os.path.exists(res['filepath']):
        try: os.remove(res['filepath']) 
        except: pass
    c.execute("DELETE FROM documents WHERE id=?", (doc_id,))
    conn.commit()
    conn.close()
    return True

def get_document_path(doc_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT filepath, filename FROM documents WHERE id=?", (doc_id,))
    res = c.fetchone()
    conn.close()
    return (res['filepath'], res['filename']) if res else (None, None)

def save_embedding_reference(doc_id, doc_hash):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE documents SET embedding_hash=? WHERE id=?", (doc_hash, doc_id))
    conn.commit()
    conn.close()

# =============================
# MATTERS & DEADLINES
# =============================
def get_client_matters(client_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM matters WHERE client_id=? ORDER BY id DESC", (client_id,))
    rows = c.fetchall()
    return [{
        "id": f"MAT-{r['id']}", 
        "title": r['title'], 
        "type": r['type'], 
        "status": r['status'], 
        "last_updated": r['last_updated']
    } for r in rows]

def create_matter(client_id, title, m_type, status="In Progress"):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        date_now = datetime.datetime.now().strftime("%Y-%m-%d")
        c.execute("INSERT INTO matters (client_id, title, type, status, last_updated) VALUES (?, ?, ?, ?, ?)",
                  (client_id, title, m_type, status, date_now))
        conn.commit()
        return True, c.lastrowid
    except Exception: return False, "Error"
    finally: conn.close()

def get_client_deadlines(client_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM deadlines WHERE client_id=? ORDER BY due_date ASC", (client_id,))
    rows = c.fetchall()
    return [{
        "id": r["id"], "title": r["title"], "due_date": r["due_date"],
        "status": r["status"], "type": r["type"]
    } for r in rows]

def add_deadline(client_id, title, due_date, dtype):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        # Prevent duplicate deadlines
        c.execute("SELECT id FROM deadlines WHERE client_id=? AND title=? AND due_date=?", (client_id, title, due_date))
        if c.fetchone():
            return True, "Exists"

        c.execute("INSERT INTO deadlines (client_id, title, due_date, status, type) VALUES (?, ?, ?, ?, ?)",
                  (client_id, title, due_date, "Pending", dtype))
        conn.commit()
        return True, c.lastrowid
    except Exception: return False, "Error"
    finally: conn.close()

# ✅ MARK DEADLINE AS DONE
def mark_deadline_done(deadline_id):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        print(f"✅ DB: Marking deadline {deadline_id} as Done")
        c.execute("UPDATE deadlines SET status='Done' WHERE id=?", (deadline_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ DB Error: {e}")
        return False
    finally:
        conn.close()