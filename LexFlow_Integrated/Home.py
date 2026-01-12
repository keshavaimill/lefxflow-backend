import streamlit as st
import os

st.set_page_config(page_title="LexFlow Integrated", page_icon="⚖️", layout="wide")

# --- CSS STYLING ---
st.markdown("""
    <style>
    .main-header { font-size: 3rem; color: #4F8BF9; text-align: center; margin-bottom: 1rem; }
    .sub-text { text-align: center; color: #666; font-size: 1.2rem; margin-bottom: 2rem; }
    .card { background-color: #f9f9f9; padding: 20px; border-radius: 10px; border: 1px solid #ddd; text-align: center; height: 100%; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">⚖️ LexFlow Integrated Suite</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Unified Legal Technology Platform for Management & Drafting</div>', unsafe_allow_html=True)
st.divider()

col1, col2 = st.columns(2)
with col1:
    st.markdown("""<div class="card"><h3>🗂️ Client Workspace</h3><p>Manage client databases, track case timelines, and organize documents.</p></div>""", unsafe_allow_html=True)
    st.write("")
    if st.button("🚀 Launch Client Workspace", use_container_width=True):
        st.switch_page("pages/1_🗂️_Client_Workspace.py")

with col2:
    st.markdown("""<div class="card"><h3>📝 Drafting Studio</h3><p>AI-powered legal drafting with RAG context, case law research, and auto-email.</p></div>""", unsafe_allow_html=True)
    st.write("")
    if st.button("🚀 Launch Drafting Studio", use_container_width=True):
        st.switch_page("pages/2_📝_Drafting_Studio.py")

st.divider()
st.caption("© 2025 LexFlow AI | Integrated System v1.0")