# import streamlit as st
# import os
# import sys
# import time
# import urllib.parse
# import pandas as pd

# # Add root to sys path for imports if needed
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# # --- IMPORT API CLIENT ---
# import frontend_api as api

# # --- PAGE SETUP ---
# st.set_page_config(page_title="Client Workspace", layout="wide")
# st.title("🟪 Client & Matter Workspace")

# COUNTRY_CODES = ["+91 (India)", "+1 (USA)", "+44 (UK)", "+971 (UAE)", "+61 (Aus)"]

# # --- UTILS ---
# def parse_email_draft(raw_text):
#     lines = raw_text.split('\n')
#     subject = "Legal Update"
#     body_lines = []
#     found_subject = False
#     for line in lines:
#         if line.strip().lower().startswith("subject:"):
#             subject = line.split(":", 1)[1].strip()
#             found_subject = True
#         elif found_subject:
#             body_lines.append(line)
#     if not found_subject: return "Legal Update", raw_text.strip()
#     return subject, "\n".join(body_lines).strip()

# # --- SIDEBAR ---
# with st.sidebar:
#     st.header("📂 Client Manager")
    
#     with st.expander("➕ Register New Client", expanded=False):
#         with st.form("new_client"):
#             st.caption("Required Fields*")
#             fn = st.text_input("First Name*")
#             mn = st.text_input("Middle Name")
#             ln = st.text_input("Last Name")
#             st.markdown("---")
#             em = st.text_input("Email ID*")
#             c1, c2 = st.columns([1.2, 2])
#             with c1: code = st.selectbox("Code*", COUNTRY_CODES, index=0)
#             with c2: mob = st.text_input("Mobile Number*", placeholder="9876543210")
            
#             if st.form_submit_button("Register Client", type="primary"):
#                 if fn and em and mob:
#                     clean_code = code.split(" ")[0]
#                     succ, msg = api.add_client(fn, mn, ln, em, clean_code + mob)
#                     if succ: 
#                         st.success("Registered!")
#                         time.sleep(1)
#                         st.rerun()
#                     else: st.error(msg)
#                 else: st.error("Fill mandatory fields!")

#     raw_clients = api.get_all_clients()
#     if not raw_clients:
#         st.warning("No clients found.")
#         st.stop()
        
#     client_options = {c[0]: f"ID: {c[0]} | {c[1]}" for c in raw_clients}
#     selected_id = st.selectbox("Select Client", options=list(client_options.keys()), format_func=lambda x: client_options[x])
    
#     client_data = api.get_client_details(selected_id)
#     client_first_name = client_data.get('first', 'Client')
#     client_full_name = client_data.get('name', 'Unknown')

#     with st.expander("✏️ Edit Client Details", expanded=False):
#         with st.form("edit_client"):
#             st.write(f"Editing: **{client_full_name}**")
#             new_fn = st.text_input("First Name", value=client_data.get('first', ''))
#             new_mn = st.text_input("Middle Name", value=client_data.get('middle', ''))
#             new_ln = st.text_input("Last Name", value=client_data.get('last', ''))
#             new_em = st.text_input("Email", value=client_data.get('email', ''))
#             ce_code, ce_num = st.columns([1.2, 2])
#             with ce_code: edit_code = st.selectbox("New Code", COUNTRY_CODES, index=0)
#             with ce_num: new_mob = st.text_input("New Number", value=client_data.get('mobile', ''), help="Clear box to type new number")
            
#             if st.form_submit_button("Update Details"):
#                 clean_edit = edit_code.split(" ")[0]
#                 final_mob = new_mob if new_mob.startswith("+") else clean_edit + new_mob
#                 succ, msg = api.update_client(selected_id, new_fn, new_mn, new_ln, new_em, final_mob)
#                 if succ:
#                     st.success(msg)
#                     time.sleep(1)
#                     st.rerun()
#                 else: st.error(msg)

#     st.markdown("---")
#     with st.expander("Delete Client"):
#         if st.button("🗑️ Delete Client", type="primary"):
#             api.delete_client(selected_id)
#             st.rerun()

# # --- DASHBOARD ---
# st.markdown(f"### 📊 Dashboard: {client_full_name} (ID: {selected_id})")
# st.caption(f"📞 {client_data.get('mobile','')} | ✉️ {client_data.get('email','')}")

# if st.button("🔄 Update Summary"):
#     with st.spinner("Analyzing..."):
#         st.info(api.get_summary(selected_id))

# tab_files, tab_timeline, tab_checklist, tab_comms = st.tabs(["📂 Files", "⏳ Timeline", "✅ Checklist", "💬 Communications"])

# with tab_files:
#     st.subheader("Repository")
#     c1, c2 = st.columns([1, 2])
#     dtype = c1.selectbox("Doc Type", ["Notice", "Order", "Reply", "GSTR-1", "GSTR-3B", "Invoice", "Agreement", "Other"])
#     files_up = c2.file_uploader("Upload", type=['pdf', 'docx', 'xlsx', 'txt'], accept_multiple_files=True)
#     if files_up and st.button("Upload & Verify"):
#         progress = st.progress(0)
#         status = st.empty()
#         status.write("Uploading to API...")
#         succ, msg = api.upload_document(selected_id, client_full_name, dtype, files_up)
#         if succ: st.toast("✅ Upload Complete")
#         else: st.error("❌ Upload Failed")
#         time.sleep(1)
#         st.rerun()

#     files = api.get_client_files(selected_id)
#     if files:
#         st.divider()
#         for f in files:
#             did, fname, ftype, fdate = f
#             c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
#             c1.write(f"📄 {fname}")
#             c2.write(f"🏷️ **{ftype}**")
#             c3.write(fdate)
#             if c4.button("🗑️", key=f"d_{did}"):
#                 api.delete_document(did)
#                 st.rerun()
#     else: st.info("No files.")

# with tab_timeline:
#     st.subheader("Case Progression")
#     if st.button("Trace Timeline"):
#         with st.spinner("Analyzing..."):
#             raw = api.get_timeline(selected_id)
#             for line in raw.split('\n'):
#                 if "|" in line:
#                     parts = line.split("|")
#                     c1, c2 = st.columns([1, 4])
#                     c1.markdown(f"**{parts[0].strip()}**")
#                     c2.write(parts[1].strip())
#                     st.divider()
#                 elif line.strip(): st.caption(line)

# with tab_checklist:
#     st.subheader("Gap Analysis")
#     matter = st.selectbox("Matter", ["GST Adjudication", "Income Tax Scrutiny", "Corporate Agreement"])
#     if st.button("Check Compliance"):
#         miss, pres = api.check_compliance(selected_id, matter)
#         c1, c2 = st.columns(2)
#         with c1:
#             st.success("✅ Available")
#             for p in pres: st.write(f"✔️ {p.upper()}")
#         with c2:
#             st.error("❌ Missing")
#             for m in miss: st.write(f"⚠️ {m.upper()}")

# with tab_comms:
#     st.subheader("Threads")
#     msgs = api.get_comms(selected_id)
#     if msgs:
#         for m in msgs:
#             mid, plat, direc, cont, ts = m
#             col_msg, col_del = st.columns([5, 0.5])
#             with col_msg:
#                 role = "user" if direc == "Inbound" else "assistant"
#                 avatar = "👤" if direc == "Inbound" else "⚖️"
#                 with st.chat_message(role, avatar=avatar):
#                     st.markdown(f"**{plat} ({direc})** • {ts}")
#                     st.write(cont)
#             with col_del:
#                 if st.button("🗑️", key=f"del_m_{mid}"):
#                     api.delete_comm(mid)
#                     st.rerun()
    
#     st.markdown("---")
#     st.write("#### 📝 Action Center")
#     if "draft_subject" not in st.session_state: st.session_state.draft_subject = "Legal Update"
#     if "draft_body" not in st.session_state: st.session_state.draft_body = ""

#     plat = st.selectbox("Platform", ["Email", "WhatsApp"], label_visibility="collapsed")
#     input_context = st.text_area("Client Message / Instructions", placeholder="Paste incoming message OR instructions...", height=100)
    
#     c_log, c_draft = st.columns([1, 1])
#     with c_log:
#         if st.button("📥 Log Incoming", use_container_width=True):
#             if input_context:
#                 api.log_comm(selected_id, plat, "Inbound", input_context)
#                 st.rerun()
#     with c_draft:
#         if st.button("✨ Generate Reply", type="primary", use_container_width=True):
#             if input_context:
#                 hist = "\n".join([f"{m[2]}: {m[3]}" for m in msgs])
#                 with st.spinner("Drafting..."):
#                     raw = api.draft_reply(selected_id, client_first_name, hist, f"Reply to: {input_context}")
#                     sub, body = parse_email_draft(raw)
#                     st.session_state.draft_subject = sub
#                     st.session_state.draft_body = body
#                     st.rerun()

#     if st.session_state.draft_body:
#         st.markdown("### 📤 Review & Send")
#         final_subj = st.text_input("Subject", value=st.session_state.draft_subject)
#         final_body = st.text_area("Body", value=st.session_state.draft_body, height=200)
        
#         c_send, c_log_out = st.columns([1, 1])
#         with c_send:
#             if plat == "Email":
#                 if st.button("📨 Send Email Now", type="primary", use_container_width=True):
#                     res = api.send_email(client_data['email'], final_subj, final_body)
#                     if res.get("success"):
#                         st.success(res['message'])
#                         full_log = f"Subject: {final_subj}\n\n{final_body}"
#                         api.log_comm(selected_id, "Email", "Outbound", full_log)
#                         st.session_state.draft_body = ""
#                         time.sleep(1)
#                         st.rerun()
#                     else: st.error(res['message'])
#             elif plat == "WhatsApp":
#                 if st.button("🟢 Open WhatsApp"):
#                     if client_data['mobile']:
#                         ph = client_data['mobile'].replace("+", "").replace(" ", "").replace("-", "")
#                         txt = urllib.parse.quote(final_body)
#                         url = f"https://wa.me/{ph}?text={txt}"
#                         st.markdown(f'<a href="{url}" target="_blank">Click to Launch</a>', unsafe_allow_html=True)
#                         api.log_comm(selected_id, "WhatsApp", "Outbound", final_body)
#                     else: st.error("No mobile!")
        
#         with c_log_out:
#             if st.button("💾 Log as Sent (Manual)", use_container_width=True):
#                 final_c = f"Subject: {final_subj}\n\n{final_body}" if plat == "Email" else final_body
#                 api.log_comm(selected_id, plat, "Outbound", final_c)
#                 st.session_state.draft_body = ""
#                 st.rerun()


























import streamlit as st
import os
import sys
import time
import urllib.parse
import frontend_api as api

# --- PAGE SETUP ---
st.set_page_config(page_title="Client Workspace", layout="wide")
st.title("🟪 Client & Matter Workspace")

COUNTRY_CODES = ["+91 (India)", "+1 (USA)", "+44 (UK)", "+971 (UAE)", "+61 (Aus)"]

# --- SIDEBAR ---
with st.sidebar:
    st.header("📂 Client Manager")
    
    # 1. NEW CLIENT REGISTRATION
    with st.expander("➕ Register New Client", expanded=False):
        with st.form("new_client"):
            st.caption("Required Fields*")
            fn = st.text_input("First Name*")
            mn = st.text_input("Middle Name")
            ln = st.text_input("Last Name")
            st.markdown("---")
            em = st.text_input("Email ID*")
            
            c1, c2 = st.columns([1.2, 2])
            with c1: code = st.selectbox("Code*", COUNTRY_CODES, index=0)
            with c2: mob = st.text_input("Mobile Number*", placeholder="9876543210")
            
            # NEW MANDATORY FIELDS
            st.markdown("---")
            pan = st.text_input("PAN Number*", placeholder="ABCDE1234F", max_chars=10)
            gstin = st.text_input("GSTIN*", placeholder="27ABCDE1234F1Z5", max_chars=15)
            
            if st.form_submit_button("Register Client", type="primary"):
                # VALIDATION CHECK
                if fn and em and mob and pan and gstin:
                    clean_code = code.split(" ")[0]
                    succ, msg = api.add_client(fn, mn, ln, em, clean_code + mob, pan, gstin)
                    if succ: 
                        st.success("Registered!")
                        time.sleep(1)
                        st.rerun()
                    else: st.error(msg)
                else: st.error("Please fill ALL mandatory fields (Name, Email, Mobile, PAN, GSTIN).")

    raw_clients = api.get_all_clients()
    if not raw_clients:
        st.warning("No clients found.")
        st.stop()
        
    client_options = {c[0]: f"ID: {c[0]} | {c[1]}" for c in raw_clients}
    selected_id = st.selectbox("Select Client", options=list(client_options.keys()), format_func=lambda x: client_options[x])
    
    # Get Details
    client_data = api.get_client_details(selected_id)
    client_first_name = client_data.get('first', 'Client')
    client_full_name = client_data.get('name', 'Unknown')

    # 2. EDIT CLIENT
    with st.expander("✏️ Edit Client Details", expanded=False):
        with st.form("edit_client"):
            st.write(f"Editing: **{client_full_name}**")
            new_fn = st.text_input("First Name", value=client_data.get('first', ''))
            new_mn = st.text_input("Middle Name", value=client_data.get('middle', ''))
            new_ln = st.text_input("Last Name", value=client_data.get('last', ''))
            new_em = st.text_input("Email", value=client_data.get('email', ''))
            
            ce_code, ce_num = st.columns([1.2, 2])
            with ce_code: edit_code = st.selectbox("New Code", COUNTRY_CODES, index=0)
            with ce_num: new_mob = st.text_input("New Number", value=client_data.get('mobile', ''), help="Clear box to type new number")
            
            # EDIT NEW FIELDS
            new_pan = st.text_input("PAN", value=client_data.get('pan', ''))
            new_gstin = st.text_input("GSTIN", value=client_data.get('gstin', ''))
            
            if st.form_submit_button("Update Details"):
                if new_pan and new_gstin:
                    clean_edit = edit_code.split(" ")[0]
                    final_mob = new_mob if new_mob.startswith("+") else clean_edit + new_mob
                    succ, msg = api.update_client(selected_id, new_fn, new_mn, new_ln, new_em, final_mob, new_pan, new_gstin)
                    if succ:
                        st.success(msg)
                        time.sleep(1)
                        st.rerun()
                    else: st.error(msg)
                else:
                    st.error("PAN and GSTIN cannot be empty.")

    st.markdown("---")
    with st.expander("Delete Client"):
        if st.button("🗑️ Delete Client", type="primary"):
            api.delete_client(selected_id)
            st.rerun()

# --- DASHBOARD HEADER ---
st.markdown(f"### 📊 Dashboard: {client_full_name} (ID: {selected_id})")
# Display PAN/GSTIN in Header
c_info1, c_info2, c_info3 = st.columns(3)
with c_info1: st.caption(f"📞 {client_data.get('mobile','')}")
with c_info2: st.caption(f"🆔 PAN: **{client_data.get('pan','N/A')}**")
with c_info3: st.caption(f"🏢 GSTIN: **{client_data.get('gstin','N/A')}**")

# ... (Rest of the file remains exactly the same from "if st.button("🔄 Update Summary"):" onwards) ...
if st.button("🔄 Update Summary"):
    with st.spinner("Analyzing..."):
        st.info(api.get_summary(selected_id))

tab_files, tab_timeline, tab_checklist, tab_comms = st.tabs(["📂 Files", "⏳ Timeline", "✅ Checklist", "💬 Communications"])

with tab_files:
    st.subheader("Repository")
    c1, c2 = st.columns([1, 2])
    dtype = c1.selectbox("Doc Type", ["Notice", "Order", "Reply", "GSTR-1", "GSTR-3B", "Invoice", "Agreement", "Other"])
    files_up = c2.file_uploader("Upload", type=['pdf', 'docx', 'xlsx', 'txt'], accept_multiple_files=True)
    if files_up and st.button("Upload & Verify"):
        progress = st.progress(0)
        status = st.empty()
        status.write("Uploading to API...")
        succ, msg = api.upload_document(selected_id, client_full_name, dtype, files_up)
        if succ: st.toast("✅ Upload Complete")
        else: st.error("❌ Upload Failed")
        time.sleep(1)
        st.rerun()

    files = api.get_client_files(selected_id)
    if files:
        st.divider()
        for f in files:
            did, fname, ftype, fdate = f
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
            c1.write(f"📄 {fname}")
            c2.write(f"🏷️ **{ftype}**")
            c3.write(fdate)
            if c4.button("🗑️", key=f"d_{did}"):
                api.delete_document(did)
                st.rerun()
    else: st.info("No files.")

with tab_timeline:
    st.subheader("Case Progression")
    if st.button("Trace Timeline"):
        with st.spinner("Analyzing..."):
            raw = api.get_timeline(selected_id)
            for line in raw.split('\n'):
                if "|" in line:
                    parts = line.split("|")
                    c1, c2 = st.columns([1, 4])
                    c1.markdown(f"**{parts[0].strip()}**")
                    c2.write(parts[1].strip())
                    st.divider()
                elif line.strip(): st.caption(line)

with tab_checklist:
    st.subheader("Gap Analysis")
    matter = st.selectbox("Matter", ["GST Adjudication", "Income Tax Scrutiny", "Corporate Agreement"])
    if st.button("Check Compliance"):
        miss, pres = api.check_compliance(selected_id, matter)
        c1, c2 = st.columns(2)
        with c1:
            st.success("✅ Available")
            for p in pres: st.write(f"✔️ {p.upper()}")
        with c2:
            st.error("❌ Missing")
            for m in miss: st.write(f"⚠️ {m.upper()}")

with tab_comms:
    st.subheader("Threads")
    msgs = api.get_comms(selected_id)
    if msgs:
        for m in msgs:
            mid, plat, direc, cont, ts = m
            col_msg, col_del = st.columns([5, 0.5])
            with col_msg:
                role = "user" if direc == "Inbound" else "assistant"
                avatar = "👤" if direc == "Inbound" else "⚖️"
                with st.chat_message(role, avatar=avatar):
                    st.markdown(f"**{plat} ({direc})** • {ts}")
                    st.write(cont)
            with col_del:
                if st.button("🗑️", key=f"del_m_{mid}"):
                    api.delete_comm(mid)
                    st.rerun()
    
    st.markdown("---")
    st.write("#### 📝 Action Center")
    if "draft_subject" not in st.session_state: st.session_state.draft_subject = "Legal Update"
    if "draft_body" not in st.session_state: st.session_state.draft_body = ""

    plat = st.selectbox("Platform", ["Email", "WhatsApp"], label_visibility="collapsed")
    input_context = st.text_area("Client Message / Instructions", placeholder="Paste incoming message OR instructions...", height=100)
    
    c_log, c_draft = st.columns([1, 1])
    with c_log:
        if st.button("📥 Log Incoming", use_container_width=True):
            if input_context:
                api.log_comm(selected_id, plat, "Inbound", input_context)
                st.rerun()
    with c_draft:
        if st.button("✨ Generate Reply", type="primary", use_container_width=True):
            if input_context:
                # Assuming client_first_name is available from above context
                hist = "\n".join([f"{m[2]}: {m[3]}" for m in msgs])
                with st.spinner("Drafting..."):
                    raw = api.draft_reply(selected_id, client_first_name, hist, f"Reply to: {input_context}")
                    
                    # Define parsing helper locally if not imported
                    def parse_email_draft(raw_text):
                        lines = raw_text.split('\n')
                        subject = "Legal Update"
                        body_lines = []
                        found_subject = False
                        for line in lines:
                            if line.strip().lower().startswith("subject:"):
                                subject = line.split(":", 1)[1].strip()
                                found_subject = True
                            elif found_subject:
                                body_lines.append(line)
                        if not found_subject: return "Legal Update", raw_text.strip()
                        return subject, "\n".join(body_lines).strip()

                    sub, body = parse_email_draft(raw)
                    st.session_state.draft_subject = sub
                    st.session_state.draft_body = body
                    st.rerun()

    if st.session_state.draft_body:
        st.markdown("### 📤 Review & Send")
        final_subj = st.text_input("Subject", value=st.session_state.draft_subject)
        final_body = st.text_area("Body", value=st.session_state.draft_body, height=200)
        
        c_send, c_log_out = st.columns([1, 1])
        with c_send:
            if plat == "Email":
                if st.button("📨 Send Email Now", type="primary", use_container_width=True):
                    res = api.send_email(client_data.get('email',''), final_subj, final_body)
                    if res.get("success"):
                        st.success(res['message'])
                        full_log = f"Subject: {final_subj}\n\n{final_body}"
                        api.log_comm(selected_id, "Email", "Outbound", full_log)
                        st.session_state.draft_body = ""
                        time.sleep(1)
                        st.rerun()
                    else: st.error(res['message'])
            elif plat == "WhatsApp":
                if st.button("🟢 Open WhatsApp"):
                    if client_data.get('mobile'):
                        ph = client_data['mobile'].replace("+", "").replace(" ", "").replace("-", "")
                        txt = urllib.parse.quote(final_body)
                        url = f"https://wa.me/{ph}?text={txt}"
                        st.markdown(f'<a href="{url}" target="_blank">Click to Launch</a>', unsafe_allow_html=True)
                        api.log_comm(selected_id, "WhatsApp", "Outbound", final_body)
                    else: st.error("No mobile!")
        
        with c_log_out:
            if st.button("💾 Log as Sent (Manual)", use_container_width=True):
                final_c = f"Subject: {final_subj}\n\n{final_body}" if plat == "Email" else final_body
                api.log_comm(selected_id, plat, "Outbound", final_c)
                st.session_state.draft_body = ""
                st.rerun()