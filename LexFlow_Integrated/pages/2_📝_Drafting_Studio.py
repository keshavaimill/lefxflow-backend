import streamlit as st
import os
import sys

# --- IMPORT EXPORT ENGINE LOCALLY FOR BYTES CONVERSION ---
# This allows us to convert text to Word/PDF without sending data to the backend
from backend.drafting import export_engine

# --- IMPORT API CLIENT ---
# This connects to your backend server
import frontend_api as api

# --- PAGE SETUP ---
st.set_page_config(page_title="LexFlow Studio", layout="wide", page_icon="⚖️")

# Custom CSS for better text area and buttons
st.markdown("""
<style>
    .stTextArea textarea { font-family: 'Times New Roman', serif; font-size: 16px; }
    .stButton button { width: 100%; }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ LexFlow AI - Drafting Studio")

# ===================== STATE INITIALIZATION =====================
# We use session_state to keep your data safe if you switch tabs
if "draft_content" not in st.session_state: st.session_state["draft_content"] = ""
if "client_name" not in st.session_state: st.session_state["client_name"] = ""
if "opp_party" not in st.session_state: st.session_state["opp_party"] = ""
if "facts" not in st.session_state: st.session_state["facts"] = ""
if "doc_hash" not in st.session_state: st.session_state["doc_hash"] = None

# ===================== 1. CONTEXT SELECTION =====================
st.subheader("1. Context Selection")

tab_upload, tab_client = st.tabs(["📤 Upload New (Analysis)", "🗂️ From Client Workspace (Fast Load)"])

# --- TAB 1: UPLOAD NEW (Runs Analysis) ---
with tab_upload:
    st.caption("Use this for NEW documents that need deep analysis.")
    uploaded_file = st.file_uploader("Upload Legal Document", type=["docx", "pdf", "txt"])
    
    if uploaded_file and st.button("🔍 Analyze New Document"):
        with st.spinner("Processing via API..."):
            # This calls the backend to analyze the file (Uses LLM)
            res = api.analyze_file_drafting(uploaded_file)
            if res:
                analysis = res["analysis"]
                st.session_state["doc_hash"] = res["hash"]
                # Auto-fill fields from analysis
                st.session_state["client_name"] = analysis.get("document_metadata", {}).get("addressed_to", "")
                st.session_state["facts"] = "\n".join(analysis.get("key_points_summary", []))
                st.success("Analyzed & Loaded!")
            else:
                st.error("API Error: Could not analyze file.")

# --- TAB 2: CLIENT WORKSPACE (Cost Optimized) ---
with tab_client:
    st.caption("Select existing files. Uses pre-built indexes (No extra cost).")
    
    # 1. Get Clients
    raw_clients = api.get_all_clients()
    
    if not raw_clients:
        st.info("No clients found in database.")
    else:
        # Create a dictionary for the dropdown: {ID: "Name (ID)"}
        client_options = {c[0]: f"ID: {c[0]} | {c[1]}" for c in raw_clients}
        selected_client_id = st.selectbox("Select Client", options=list(client_options.keys()), format_func=lambda x: client_options[x])
        
        if selected_client_id:
            # 2. Get Files for Selected Client
            files = api.get_client_files(selected_client_id)
            
            if not files:
                st.warning("No files found for this client.")
            else:
                # files format: [(id, filename, type, date), ...]
                # Map Filename -> ID
                file_map = {f[1]: f[0] for f in files}
                all_files_list = list(file_map.keys())

                # 3. Multi-Select Files
                selected_filenames = st.multiselect("Select Documents for Context", options=all_files_list)
                
                # 4. Load Context Button
                if st.button("⚡ Load Selected Context", type="primary"):
                    if not selected_filenames:
                        st.error("Please select at least one document.")
                    else:
                        final_hashes = []
                        combined_facts = []
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Loop through selected files
                        for idx, fname in enumerate(selected_filenames):
                            doc_id = file_map[fname]
                            status_text.write(f"📥 Fetching content for: {fname}...")
                            
                            # API Call: Get Text Content Only (Cheap)
                            data = api.get_doc_content(doc_id)
                            
                            if data:
                                text_content = data['content']
                                d_hash = data['hash']
                                
                                # Store hash to use the EXISTING index (Zero Cost)
                                final_hashes.append(d_hash)
                                
                                # Use raw text for facts (Zero Cost)
                                combined_facts.append(f"--- From {fname} ---\n{text_content[:3000]}...")
                                
                            progress_bar.progress((idx + 1) / len(selected_filenames))
                        
                        # Update UI State
                        st.session_state["doc_hash"] = final_hashes
                        st.session_state["facts"] = "\n\n".join(combined_facts)
                        st.session_state["client_name"] = "Client (See Context)" 
                        
                        status_text.write("✅ All Context Loaded!")
                        st.toast(f"Loaded {len(selected_filenames)} documents.")

# ===================== 2. DRAFTING STUDIO =====================
st.markdown("---")
st.subheader("2. Drafting Studio")

col_left, col_center, col_right = st.columns([1.2, 2.5, 1])

# --- LEFT: SETUP ---
with col_left:
    st.header("Setup")
    template_type = st.selectbox("Type", ["gst_show_cause_reply", "nda", "employment_contract", "lease_deed", "commercial_agreement"])
    
    st.text_input("Client Name", key="client_name")
    st.text_input("Opposite Party", key="opp_party")
    st.text_area("Facts / Instructions", height=300, key="facts", help="Context loaded from files appears here.")
    tone = st.selectbox("Tone", ["Formal", "Persuasive", "Firm"])

    st.markdown("---")
    if st.button("✨ Generate Draft", type="primary"):
        # Prepare Request
        req = {
            "template_type": template_type,
            "client_name": st.session_state["client_name"],
            "opposite_party": st.session_state["opp_party"],
            "facts": st.session_state["facts"],
            "tone": tone,
            "doc_hash": st.session_state.get("doc_hash") # Passes the list of hashes for RAG
        }
        
        with st.spinner("Drafting..."):
            res = api.generate_draft(req)
            st.session_state["draft_content"] = res["content"]
            st.rerun()

    with st.expander("Reset"):
        if st.button("Clear Context"):
            st.session_state["draft_content"] = ""
            st.session_state["facts"] = ""
            st.rerun()

# --- CENTER: EDITOR ---
with col_center:
    st.subheader("Editor")
    draft_val = st.text_area("Content", value=st.session_state["draft_content"], height=800, label_visibility="collapsed")
    if draft_val != st.session_state["draft_content"]: st.session_state["draft_content"] = draft_val

    # Export Buttons
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("Word"): 
            st.download_button("Download .docx", export_engine.export_to_word(st.session_state["draft_content"]), "Draft.docx")
    with c2: 
        if st.button("PDF"): 
             st.download_button("Download .pdf", export_engine.export_to_pdf(st.session_state["draft_content"]), "Draft.pdf")

# --- RIGHT: TOOLS ---
with col_right:
    st.header("Tools")
    
    st.markdown("### ✨ Refine")
    if st.button("Make Stronger"):
        with st.spinner("Refining..."):
            res = api.refine_draft(st.session_state["draft_content"], "Make stronger")
            st.session_state["draft_content"] = res
            st.rerun()
            
    if st.button("Make Polite"):
        with st.spinner("Refining..."):
            res = api.refine_draft(st.session_state["draft_content"], "Make polite")
            st.session_state["draft_content"] = res
            st.rerun()

    st.markdown("### 📚 Research")
    if st.button("Suggest Case Laws"):
        with st.spinner("Searching..."):
            res = api.suggest_cases(st.session_state["draft_content"])
            st.info(res)

    st.markdown("### 📧 Email")
    recip = st.text_input("To:", key="email_to")
    sub = st.text_input("Subject:", value="Legal Draft", key="email_sub")
    if st.button("Send Email"):
        if recip:
            with st.spinner("Sending..."):
                res = api.send_email(recip, sub, st.session_state["draft_content"])
                if res.get("success"): st.success("Sent!")
                else: st.error(res.get("message"))