# import os
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Configuration
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587
# MAIL_USERNAME = os.getenv("MAIL_USERNAME")
# MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
# MAIL_FROM = os.getenv("MAIL_FROM") or MAIL_USERNAME

# async def send_draft_email(recipient: str, subject: str, content: str):
#     """
#     Sends an email using Gmail SMTP.
#     """
#     if not MAIL_USERNAME or not MAIL_PASSWORD:
#         raise ValueError("Missing 'MAIL_USERNAME' or 'MAIL_PASSWORD' in .env file.")

#     try:
#         # 1. Setup Message
#         msg = MIMEMultipart()
#         msg['From'] = MAIL_FROM
#         msg['To'] = recipient
#         msg['Subject'] = subject
#         msg.attach(MIMEText(content, 'plain'))

#         # 2. Connect to Server
#         server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
#         server.ehlo() # Identify ourselves
#         server.starttls() # Secure the connection
#         server.ehlo() # Re-identify as encrypted

#         # 3. Login
#         server.login(MAIL_USERNAME, MAIL_PASSWORD)

#         # 4. Send
#         server.send_message(msg)
#         server.quit()
        
#         return "Email Sent Successfully!"

#     except smtplib.SMTPAuthenticationError:
#         raise ConnectionError("Login failed. Check your Email/App Password in .env.")
#     except Exception as e:
#         raise ConnectionError(f"Email Error: {str(e)}")












# import os
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Configuration
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587
# MAIL_USERNAME = os.getenv("MAIL_USERNAME")
# MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
# MAIL_FROM = os.getenv("MAIL_FROM") or MAIL_USERNAME

# async def send_draft_email(recipient: str, subject: str, content: str):
#     """
#     Sends an email using Gmail SMTP.
#     """
#     # Fallback simulation if credentials are missing (prevents crash)
#     if not MAIL_USERNAME or not MAIL_PASSWORD:
#         print(f"⚠️  [Simulation] Email to {recipient}: {subject}")
#         return True

#     try:
#         # 1. Setup Message
#         msg = MIMEMultipart()
#         msg['From'] = MAIL_FROM
#         msg['To'] = recipient
#         msg['Subject'] = subject
#         msg.attach(MIMEText(content, 'plain'))

#         # 2. Connect to Server
#         server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
#         server.ehlo() # Identify ourselves
#         server.starttls() # Secure the connection
#         server.ehlo() # Re-identify as encrypted

#         # 3. Login
#         server.login(MAIL_USERNAME, MAIL_PASSWORD)

#         # 4. Send
#         server.send_message(msg)
#         server.quit()
        
#         print(f"✅ Email Sent Successfully to {recipient}")
#         return True

#     except smtplib.SMTPAuthenticationError:
#         print("❌ Login failed. Check your Email/App Password in .env.")
#         return False
#     except Exception as e:
#         print(f"❌ Email Error: {str(e)}")
#         return False








# import os
# from dotenv import load_dotenv
# from openai import OpenAI

# # --- IMPORTS ---
# # We connect this to your existing schema file
# from backend.api_schemas import DraftRequest

# load_dotenv()

# # Initialize Client
# api_key = os.getenv("OPENAI_API_KEY")
# client = OpenAI(api_key=api_key) if api_key else None
# MODEL_NAME = "gpt-4o"

# # ======================================================
# # HELPER FUNCTIONS (Inlined for Stability)
# # ======================================================
# def build_legal_prompt(data: DraftRequest, web_context: str = ""):
#     return f"""
#     Draft a legal document based on the following details:
    
#     Type: {data.doc_type}
#     Topic: {data.topic}
#     Facts/Details: {data.facts if hasattr(data, 'facts') else 'None provided'}
    
#     Context from Documents (RAG):
#     {web_context}
    
#     Requirements:
#     - Professional legal tone (Indian Law context).
#     - Clear structure.
#     """

# def validate_draft(text, template_type):
#     warnings = []
#     if "placeholder" in text.lower():
#         warnings.append("Draft contains placeholders.")
#     if len(text) < 100:
#         warnings.append("Draft seems too short.")
#     return warnings

# # Placeholder for RAG retrieval if you haven't set up the vector store fully yet
# def retrieve_top_k_chunks(query, k, doc_hash):
#     return [] 

# # ======================================================
# # MAIN DRAFT GENERATOR (NOW RAG-AWARE)
# # ======================================================
# async def generate_legal_draft(data: DraftRequest, web_context: str = ""):
#     """
#     Generates legal draft.
#     Uses embeddings ONLY if doc_hash is present.
#     """
#     if not client:
#         return {
#             "content": "AI Simulation: OpenAI API Key missing. Add it to .env to generate real drafts.",
#             "warnings": ["Simulation Mode"]
#         }

#     # -------------------------
#     # 1️⃣ RAG CONTEXT
#     # -------------------------
#     rag_context = web_context

#     # Note: If you implement the vector store logic later, uncomment this:
#     # if getattr(data, "doc_hash", None) and not rag_context:
#     #     chunks = retrieve_top_k_chunks(
#     #         query=(data.facts or "")[:500],
#     #         k=5,
#     #         doc_hash=data.doc_hash
#     #     )
#     #     rag_context = "\n\n".join(chunks)

#     # -------------------------
#     # 2️⃣ PROMPT BUILDING
#     # -------------------------
#     # Mapping 'template_type' to 'doc_type' if needed, or using direct fields
#     prompt = build_legal_prompt(
#         data=data,
#         web_context=rag_context
#     )

#     # -------------------------
#     # 3️⃣ LLM CALL
#     # -------------------------
#     try:
#         response = client.chat.completions.create(
#             model=MODEL_NAME,
#             messages=[
#                 {"role": "system", "content": "You are a Senior Indian Legal Drafting AI."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.2
#         )

#         draft_text = response.choices[0].message.content.strip()

#         # -------------------------
#         # 4️⃣ VALIDATION
#         # -------------------------
#         # Handle optional fields safely
#         t_type = getattr(data, "template_type", "General")
#         warnings = validate_draft(draft_text, t_type)

#         return {
#             "content": draft_text,
#             "warnings": warnings
#         }
#     except Exception as e:
#         return {
#             "content": f"Error generating draft: {str(e)}",
#             "warnings": ["AI Generation Failed"]
#         }


# # ======================================================
# # REFINEMENT TOOL
# # ======================================================
# async def refine_text(text, instruction):
#     """Refines the ENTIRE document."""
#     if not client: return "AI Simulation: Refined text based on instruction."

#     try:
#         response = client.chat.completions.create(
#             model=MODEL_NAME,
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "You are a Senior Legal Editor. "
#                         "Rewrite the legal document according to the instruction. "
#                         "Output only the refined text."
#                     )
#                 },
#                 {
#                     "role": "user",
#                     "content": f"Instruction: {instruction}\n\nDocument Content:\n{text}"
#                 }
#             ],
#             temperature=0.2
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         return str(e)


# # ======================================================
# # CASE LAW SUGGESTION TOOL
# # ======================================================
# async def suggest_case_laws_ai(text):
#     """Suggests RELEVANT SECTIONS and CASE LAWS."""
#     if not client: return "**Simulation:**\n- Section 3 of Example Act\n- State v. Person (2023)"

#     try:
#         response = client.chat.completions.create(
#             model=MODEL_NAME,
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "You are a Legal Researcher. Analyze the text and suggest "
#                         "**Indian Statutory Provisions (Sections/Acts)** and "
#                         "**Case Laws**.\n\n"
#                         "Output Format:\n"
#                         "**Relevant Laws:**\n"
#                         "- Section X of [Act Name]: [Brief Explanation]\n\n"
#                         "**Case Precedents:**\n"
#                         "- Case Name (Year): [One line summary]"
#                     )
#                 },
#                 {
#                     "role": "user",
#                     "content": f"Analyze this draft and find legal grounds:\n{text[:3000]}"
#                 }
#             ],
#             temperature=0.2
#         )
#         return response.choices[0].message.content.strip()
#     except Exception:
#         return "Error fetching legal research."


















# import os
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Configuration
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587
# MAIL_USERNAME = os.getenv("MAIL_USERNAME")
# MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
# MAIL_FROM = os.getenv("MAIL_FROM") or MAIL_USERNAME

# async def send_draft_email(recipient: str, subject: str, content: str):
#     """
#     Sends an email using Gmail SMTP.
#     """
#     # Fallback simulation if credentials are missing (prevents crash)
#     if not MAIL_USERNAME or not MAIL_PASSWORD:
#         print(f"⚠️  [Simulation] Email to {recipient}: {subject}")
#         return True

#     try:
#         # 1. Setup Message
#         msg = MIMEMultipart()
#         msg['From'] = MAIL_FROM
#         msg['To'] = recipient
#         msg['Subject'] = subject
#         msg.attach(MIMEText(content, 'plain'))

#         # 2. Connect to Server
#         server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
#         server.ehlo() # Identify ourselves
#         server.starttls() # Secure the connection
#         server.ehlo() # Re-identify as encrypted

#         # 3. Login
#         server.login(MAIL_USERNAME, MAIL_PASSWORD)

#         # 4. Send
#         server.send_message(msg)
#         server.quit()
        
#         print(f"✅ Email Sent Successfully to {recipient}")
#         return True

#     except smtplib.SMTPAuthenticationError:
#         print("❌ Login failed. Check your Email/App Password in .env.")
#         return False
#     except Exception as e:
#         print(f"❌ Email Error: {str(e)}")
#         return False




















import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM") or MAIL_USERNAME

async def send_draft_email(recipient: str, subject: str, content: str):
    """
    Sends an email using Gmail SMTP.
    If credentials are missing, it falls back to Simulation Mode.
    """
    # Fallback simulation if credentials are missing (prevents crash)
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        print(f"⚠️  [Simulation] Email to {recipient}: {subject}")
        # Simulate successful send
        return True

    try:
        # 1. Setup Message
        msg = MIMEMultipart()
        msg['From'] = MAIL_FROM
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'plain'))

        # 2. Connect to Server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.ehlo() # Identify ourselves
        server.starttls() # Secure the connection
        server.ehlo() # Re-identify as encrypted

        # 3. Login
        server.login(MAIL_USERNAME, MAIL_PASSWORD)

        # 4. Send
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email Sent Successfully to {recipient}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("❌ Login failed. Check your Email/App Password in .env.")
        return False
    except Exception as e:
        print(f"❌ Email Error: {str(e)}")
        return False