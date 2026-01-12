import os
from dotenv import load_dotenv
from openai import OpenAI
from backend.api_schemas import DraftRequest

load_dotenv()

# Initialize Client
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None
MODEL_NAME = "gpt-4o"

# ======================================================
# HELPER FUNCTIONS
# ======================================================
def build_legal_prompt(data: DraftRequest, web_context: str = ""):
    return f"""
    Draft a legal document based on the following details:
    Type: {data.doc_type}
    Topic: {data.topic}
    Facts/Details: {data.facts if hasattr(data, 'facts') else 'None provided'}
    Context: {web_context}
    """

def validate_draft(text, template_type):
    warnings = []
    if "placeholder" in text.lower(): warnings.append("Draft contains placeholders.")
    return warnings

# ======================================================
# MAIN DRAFT GENERATOR
# ======================================================
async def generate_legal_draft(data: DraftRequest, web_context: str = ""):
    if not client:
        return {"content": "AI Simulation: API Key missing.", "warnings": ["Simulation Mode"]}

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a Senior Indian Legal Drafting AI."},
                {"role": "user", "content": build_legal_prompt(data, web_context)}
            ],
            temperature=0.2
        )
        draft_text = response.choices[0].message.content.strip()
        warnings = validate_draft(draft_text, getattr(data, "template_type", "General"))
        return {"content": draft_text, "warnings": warnings}
    except Exception as e:
        return {"content": f"Error: {str(e)}", "warnings": ["AI Generation Failed"]}

async def refine_text(text, instruction):
    if not client: return "Simulation Refined Text"
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a Senior Legal Editor. Rewrite the text."},
                {"role": "user", "content": f"Instruction: {instruction}\n\nContent:\n{text}"}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return str(e)

async def suggest_case_laws_ai(text):
    if not client: return "- Simulation Case Law (2024)"
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Suggest Indian Case Laws."},
                {"role": "user", "content": f"Analyze:\n{text[:3000]}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except:
        return "Error fetching research."