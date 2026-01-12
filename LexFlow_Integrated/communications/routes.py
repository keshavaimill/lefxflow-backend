import os
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

router = APIRouter()

# --- MODELS ---
class EmailRequest(BaseModel):
    clientId: int
    to: str
    subject: str
    body: str

class LogRequest(BaseModel):
    client_id: int
    platform: str
    direction: str
    content: str

# Helper: Connect to DB
def get_db_connection():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(current_dir)) 
    db_path = os.path.join(base_dir, "backend", "data", "lexflow.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Helper: Manual .env Reader (The Fix)
def manual_get_env_var(env_path, key):
    """Manually reads the .env file text to find a variable."""
    try:
        with open(env_path, "r") as f:
            for line in f:
                # Remove comments and whitespace
                line = line.strip()
                if not line or line.startswith("#"): continue
                
                # Check for key=value
                if "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() == key:
                        return v.strip().replace('"', '').replace("'", "") # Clean quotes
    except Exception as e:
        print(f"⚠️ Manual read failed: {e}")
    return None

# --- ROUTES ---

@router.get("/{client_id}")
async def get_logs(client_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='communications'")
        if not cursor.fetchone(): return []
        cursor.execute("SELECT * FROM communications WHERE client_id = ? ORDER BY created_at DESC", (client_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Database Error: {e}")
        return []

@router.post("/send-email")
async def send_email(request: EmailRequest):
    print(f"📧 Processing email for: {request.to}")

    # 1. FIND THE FILE
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir))) # Adjust to find project root
    # Try multiple common locations just in case
    possible_paths = [
        os.path.join(root_dir, ".env"),                                      # Project Root
        os.path.join(os.path.dirname(os.path.dirname(current_dir)), ".env"), # backend/../.env
        os.path.join(current_dir, ".env")                                    # Same folder
    ]
    
    env_path = None
    for p in possible_paths:
        if os.path.exists(p):
            env_path = p
            break
            
    if not env_path:
        print("❌ CRITICAL: Could not find ANY .env file.")
        return {"success": True, "message": "Failed: .env file missing entirely"}

    print(f"📂 Found .env at: {env_path}")

    # 2. ATTEMPT READ (Manual Fallback)
    # Try standard loading first
    load_dotenv(env_path, override=True)
    
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")

    # If standard load failed, use MANUAL parsing
    if not smtp_email:
        print("⚠️ Standard load failed. Trying manual file read...")
        smtp_email = manual_get_env_var(env_path, "SMTP_EMAIL")
    
    if not smtp_password:
        smtp_password = manual_get_env_var(env_path, "SMTP_PASSWORD")

    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    status_msg = "Email logged (Simulation Mode)"

    # 3. VERIFY CREDENTIALS
    if not smtp_email or not smtp_password:
        print("❌ ERROR: Credentials still missing after manual read.")
        print(f"   Please open {env_path} and ensure it has SMTP_EMAIL=... and SMTP_PASSWORD=...")
        status_msg = "Failed: Credentials missing in .env"
    else:
        # 4. SEND EMAIL
        print(f"✅ Credentials Loaded! Sending as: {smtp_email}")
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_email
            msg['To'] = request.to
            msg['Subject'] = request.subject
            msg.attach(MIMEText(request.body, 'plain'))

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_email, smtp_password)
            text = msg.as_string()
            server.sendmail(smtp_email, request.to, text)
            server.quit()
            
            status_msg = "Email sent successfully via SMTP"
            print("✅ Email Sent Successfully!")
        except Exception as e:
            print(f"❌ SMTP Connection Error: {e}")
            status_msg = f"Failed: {str(e)}"

    # 5. LOG TO DB
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO communications (client_id, platform, direction, content, subject)
            VALUES (?, ?, ?, ?, ?)
            """,
            (request.clientId, "Email", "Outbound", f"Subject: {request.subject}\n\n{request.body}", request.subject)
        )
        conn.commit()
        conn.close()
        return {"success": True, "message": status_msg}
    except Exception as e:
        print(f"❌ DB Log Error: {e}")
        return {"success": True, "message": status_msg + " (Log Failed)"}

@router.post("/log")
async def log_communication(request: LogRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO communications (client_id, platform, direction, content) VALUES (?, ?, ?, ?)",
            (request.client_id, request.platform, request.direction, request.content)
        )
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        print(f"❌ DB Error: {e}")
        return {"success": False, "error": str(e)}