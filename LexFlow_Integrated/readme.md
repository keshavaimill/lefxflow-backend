README.md

Markdown
# ⚖️ LexFlow Integrated Suite

**LexFlow** is a unified legal technology platform designed to streamline legal workflows. It combines Client Management, AI-Powered Legal Drafting, and Intelligent Legal Research into a single, cohesive application.

---

## 🏗️ Architecture

This project uses a **Client-Server Architecture**:

* **Backend (API):** Built with **FastAPI**. It handles all business logic, database operations (SQLite), file processing, and AI interactions (OpenAI/DuckDuckGo).
* **Frontend (UI):** Built with **Streamlit**. It acts as a client that consumes the Backend API to display data and interact with the user.

---

## 🚀 Key Features

### 1. 🗂️ Client Workspace
* **Client Database:** Register, update, and manage client profiles.
* **Mandatory Compliance:** Fields for **PAN** and **GSTIN** are now mandatory for compliance tracking.
* **Document Repository:** Upload and organize legal documents (PDF/DOCX) per client.
* **AI Timeline:** Automatically extracts key dates and events from uploaded case files.
* **Communication Log:** Track emails and messages; draft replies using AI.

### 2. 📝 Drafting Studio
* **AI Drafting:** Generate legal documents (Notices, Agreements, Replies) based on custom facts.
* **RAG Context:** Select existing client documents to provide context for the draft without re-uploading.
* **Refinement Tools:** "Make Stronger", "Make Polite", and "Suggest Case Laws" tools.
* **Export:** Download drafts as `.docx` or `.pdf`.

### 3. 🤖 Legal Intelligence & Chatbot
* **Authentic Search:** Searches **ONLY** trusted domains (Indian Kanoon, Taxmann, SC/HC websites) using the `site:` operator.
* **Document Chat:** Ask questions to your uploaded documents (RAG).
* **Judgment Comparison:** Upload two judgments to analyze differences in reasoning and outcome.
* **Appeal Grounds:** Generate structured grounds of appeal from an order.

---

## 📂 Project Structure

```text
LexFlow_Integrated/
├── .env                     # API Keys and Config
├── frontend_api.py          # Bridge: Frontend calls to Backend API
├── Home.py                  # Streamlit Entry Point
├── backend/
│   ├── main.py              # FastAPI Server (Endpoints)
│   ├── database.py          # SQLite Database Handler
│   ├── api_schemas.py       # Pydantic Models (Data Validation)
│   ├── client_ai.py         # AI Agent for Client Summaries
│   ├── chatbot/
│   │   └── logic.py         # Legal Search & Chat Logic
│   ├── drafting/
│   │   ├── draft_engine.py  # AI Drafting Logic
│   │   ├── export_engine.py # PDF/Word Conversion
│   │   └── ...
│   └── utils/
│       ├── chunk_and_index.py # FAISS/Vector Store Logic
│       └── ...
├── data/
│   ├── lexflow.db           # SQLite Database File
│   ├── uploads/             # Stored Documents
│   └── index_data/          # FAISS Indexes
└── pages/
    ├── 1_🗂️_Client_Workspace.py
    ├── 2_📝_Drafting_Studio.py
    └── 3_🤖_Client_Chatbot.py
🛠️ Setup & Installation
1. Prerequisites

Python 3.9+

An OpenAI API Key

2. Install Dependencies

Bash
pip install fastapi uvicorn streamlit python-dotenv openai duckduckgo-search langchain chromadb faiss-cpu python-docx pdfplumber pypdf2 requests
3. Environment Configuration

Create a .env file in the root directory and add your keys:

Ini, TOML
OPENAI_API_KEY=sk-your-key-here
MAIL_USERNAME=your-email@gmail.com  # Optional (for emailing drafts)
MAIL_PASSWORD=your-app-password     # Optional
▶️ How to Run
You need to run the Backend and Frontend in two separate terminals.

Terminal 1: Start the Backend (API)

This starts the FastAPI server on http://localhost:8000.

Bash
uvicorn backend.main:app --reload --port 8000
Wait until you see: Application startup complete.

Terminal 2: Start the Frontend (UI)

This starts the Streamlit interface.

Bash
streamlit run Home.py

📚 API Documentation
Once the backend is running, you can view the automatic interactive API documentation at:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

This is useful for the frontend team to understand how to integrate with the backend endpoints.

⚠️ Notes for Deployment
Database: This project currently uses SQLite (data/lexflow.db). For production deployment on platforms like Vercel (which are serverless), you MUST migrate to a cloud database like PostgreSQL (e.g., Supabase, Neon) to avoid data loss.

File Storage: Similarly, local file uploads (data/uploads) will be lost on serverless platforms. Use AWS S3 or Google Cloud Storage for production.