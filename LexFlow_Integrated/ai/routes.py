import os
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv() # Ensure Env Vars are loaded

# --- LANGCHAIN IMPORTS ---
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("⚠️ LangChain/OpenAI not installed.")

router = APIRouter()

# --- CONFIGURATION ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ DEFAULT GENERIC PROFILE (Safe for Product Distribution)
DEFAULT_SENDER = {
    "name": "[Your Full Name]",       
    "position": "Legal Associate",
    "company": "LexFlow Legal Services",
    "contact": "[Your Contact Number]"
}

class DraftReplyRequest(BaseModel):
    client_id: int
    client_name: str
    instruction: str
    history: Optional[str] = ""
    type: str = "email"
    sender_name: Optional[str] = None 

@router.post("/draft-reply")
async def draft_reply(request: DraftReplyRequest):
    """Agentic generation of email/message drafts using OpenAI."""
    print(f"📝 Agentic Draft Generation for {request.client_name}...")

    # Use default name if not provided
    sender_name = request.sender_name if request.sender_name else DEFAULT_SENDER["name"]

    if not HAS_OPENAI or not OPENAI_API_KEY:
        return {
            "subject": f"Draft: {request.instruction}",
            "body": "Error: OpenAI API Key missing.",
            "content": "Error: OpenAI API Key missing."
        }

    try:
        llm = ChatOpenAI(
            model="gpt-4o", # or gpt-3.5-turbo
            temperature=0.7,
            api_key=OPENAI_API_KEY
        )

        # ✅ Generic System Prompt
        system_prompt = """You are 'LexFlow', an expert legal AI assistant.
        
        YOUR TASK:
        Draft a professional {type} for a client named '{client_name}'.
        
        SENDER DETAILS (Sign off using this):
        Name: {sender_name}
        Position: {sender_position}
        Company: {sender_company}
        Contact: {sender_contact}
        
        CONTEXT:
        - User Instruction: "{instruction}"
        - Communication History:
        {history}
        
        GUIDELINES:
        - Tone: Professional, authoritative, yet polite.
        - **IMPORTANT**: If the sender name is a placeholder like '[Your Full Name]', leave it EXACTLY as is so the user can fill it. Do NOT invent a fake name.
        - Structure: Subject line followed by the message body.
        - Output Format: Return ONLY a raw JSON object (no markdown) with keys: "subject" and "body".
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "Draft the response now.")
        ])

        chain = prompt | llm | StrOutputParser()
        
        response_text = await chain.ainvoke({
            "type": request.type,
            "client_name": request.client_name,
            "sender_name": sender_name,
            "sender_position": DEFAULT_SENDER['position'],
            "sender_company": DEFAULT_SENDER['company'],
            "sender_contact": DEFAULT_SENDER['contact'],
            "instruction": request.instruction,
            "history": request.history if request.history else "No previous history."
        })

        cleaned_response = response_text.replace("```json", "").replace("```", "").strip()
        
        try:
            data = json.loads(cleaned_response)
            return {
                "subject": data.get("subject", "Legal Correspondence"),
                "body": data.get("body", cleaned_response),
                "content": cleaned_response
            }
        except json.JSONDecodeError:
            return {
                "subject": f"Regarding: {request.instruction[:30]}...",
                "body": response_text,
                "content": response_text
            }

    except Exception as e:
        print(f"❌ OpenAI Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Stub endpoints
@router.post("/summary")
async def get_summary(data: dict): return {"summary": "Client summary feature coming soon."}
@router.post("/timeline")
async def get_timeline(data: dict): return {"timeline": []}
@router.post("/compliance")
async def check_compliance(data: dict): return {"status": "Compliant", "issues": []}