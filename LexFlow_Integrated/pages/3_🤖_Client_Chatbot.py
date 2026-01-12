import streamlit as st
import frontend_api as api

st.set_page_config(page_title="LexFlow Legal Research", layout="wide", page_icon="⚖️")
st.title("⚖️ LexFlow AI: Research & Intelligence")

# --- PERSISTENT FILE LOADER ---
def render_file_input_persistent(label, key):
    if key not in st.session_state: st.session_state[key] = ""
    
    tab_up, tab_db = st.tabs([f"📤 Upload New", f"🗂️ From Workspace"])
    
    with tab_up:
        files = st.file_uploader(f"Upload ({label})", key=f"u_{key}", accept_multiple_files=True)
        if files:
            import backend.utils.file_handler as fh
            content = "\n\n".join([f"--- {f.name} ---\n{fh.read_file_content(f)}" for f in files])
            if content != st.session_state[key]: st.session_state[key] = content

    with tab_db:
        clients = api.get_all_clients()
        if clients:
            cid = st.selectbox(f"Client ({label})", options=[c[0] for c in clients], format_func=lambda x: next(c[1] for c in clients if c[0]==x), key=f"c_{key}")
            c_files = api.get_client_files(cid)
            if c_files:
                fmap = {f[1]: f[0] for f in c_files}
                sel = st.multiselect(f"Files ({label})", list(fmap.keys()), key=f"s_{key}")
                if st.button(f"📥 Load Content ({label})", key=f"b_{key}"):
                    data = [api.get_doc_content(fmap[f]) for f in sel]
                    st.session_state[key] = "\n\n".join([f"--- {d['filename']} ---\n{d['content']}" for d in data if d])
                    st.rerun()

    if st.session_state[key]: st.success(f"✅ Content Loaded ({len(st.session_state[key])} chars)")
    else: st.warning("⚠️ Please load content first.")
    return st.session_state[key]

# --- SIDEBAR ---
with st.sidebar:
    mode = st.radio("Module", ["🔍 Legal Research", "📰 Weekly Updates", "💬 Chat with Docs", "⚖️ Compare", "📝 Appeal Grounds"])

# --- MODULES ---
if mode == "🔍 Legal Research":
    q = st.text_input("Query")
    if st.button("Search"):
        res = api.research_search(q)
        if res.get('results'):
            for r in res['results']:
                with st.expander(r['title'], expanded=True):
                    st.markdown(f"{r['body']}\n\n[Source]({r['href']})")
        else: st.error("No trusted results found.")

elif mode == "📰 Weekly Updates":
    if st.button("Fetch Updates"): st.markdown(api.research_weekly())

elif mode == "💬 Chat with Docs":
    clients = api.get_all_clients()
    if clients:
        cid = st.selectbox("Client", [c[0] for c in clients], format_func=lambda x: next(c[1] for c in clients if c[0]==x))
        if "messages" not in st.session_state: st.session_state.messages = []
        
        for idx, m in enumerate(st.session_state.messages):
            with st.chat_message(m["role"]): st.markdown(m["content"])
            if m.get("followups"):
                cols = st.columns(len(m["followups"]))
                for f_idx, f in enumerate(m["followups"]):
                    # FIXED KEY ERROR HERE
                    if cols[f_idx].button(f, key=f"hist_{idx}_{f_idx}"):
                        st.session_state.temp_prompt = f
                        st.rerun()

        prompt = st.chat_input("Ask...")
        if "temp_prompt" in st.session_state:
            prompt = st.session_state.temp_prompt
            del st.session_state.temp_prompt

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    res = api.chat_with_docs(prompt, cid)
                    # Handle dict response
                    ans = res['answer'] if isinstance(res, dict) else str(res)
                    follow = res['followups'] if isinstance(res, dict) else []
                    st.markdown(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans, "followups": follow})
                    st.rerun()

elif mode == "⚖️ Compare":
    c1, c2 = st.columns(2)
    with c1: t1 = render_file_input_persistent("Doc A", "cmp_1")
    with c2: t2 = render_file_input_persistent("Doc B", "cmp_2")
    if st.button("Compare"):
        if t1 and t2: st.write(api.compare_texts(t1, t2))
        else: st.error("Load both docs.")

elif mode == "📝 Appeal Grounds":
    t = render_file_input_persistent("Source", "app_1")
    if st.button("Draft"):
        if t: st.write(api.generate_appeal_grounds(t))
        else: st.error("Load doc.")