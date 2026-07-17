"""
Policies & Guidelines quick-reference page (Person 3's file).

This is deliberately NOT routed through the chat/RAG pipeline. The content
here (documents checklist, offer-tier table, debarment rules, OA/interview
structure by company type) is exact, structured policy — same reasoning as
the eligibility checker: a table lookup is more reliable and faster than
waiting on an LLM to summarize a paragraph correctly.

The full source PDFs (TNP_Helpdesk_Guidelines, TNP_Supplementary_Policy_FAQs)
are also saved as plain text in data/documents/ for Person 1+2 to feed into
the RAG pipeline — that's where the FAQ-style and open-ended questions
("what if I miss an OA", "can I sit for another company") get answered.
This page only covers the parts worth showing as a fixed reference.
"""

import streamlit as st

st.set_page_config(page_title="Policies & Guidelines", page_icon="📋", layout="wide")

st.title("📋 Placement Policies & Guidelines")
st.caption("Quick reference — for anything not covered here, ask the chatbot.")

# ---------- Documents checklist ----------
st.subheader("📄 Documents to Carry for Every Drive")
st.markdown(
    """
- Valid college ID card
- At least 2 printed copies of your updated resume
- Government photo ID (Aadhaar / PAN / Passport)
- Printed copies of semester-wise mark sheets
- Passport-size photograph (only if the specific company asks — check the portal)
"""
)

st.divider()

# ---------- Offer tier table ----------
st.subheader("🏆 Offer Tiers & Further Applications")
st.markdown("Companies are grouped by CTC into three tiers, which decide whether you can keep applying after accepting an offer.")

tier_data = [
    {"Tier": "Mass Recruiter", "CTC Range": "Below 8 LPA", "Can Apply Further?": "Yes — to Core and Dream tier companies"},
    {"Tier": "Core", "CTC Range": "8 – 20 LPA", "Can Apply Further?": "Yes — to Dream tier companies only"},
    {"Tier": "Dream", "CTC Range": "Above 20 LPA", "Can Apply Further?": "No further applications permitted"},
]
st.table(tier_data)

st.divider()

# ---------- Debarment policy ----------
st.subheader("⚠️ Debarment Policy")
st.warning(
    "You will be debarred from all further campus placement activity for the "
    "rest of the season if you:\n\n"
    "1. Accept an offer and then withdraw without a valid, documented reason\n"
    "2. Are absent from a shortlisted interview without prior intimation to the TNP office\n"
    "3. Engage in malpractice during an OA or interview (impersonation, unauthorized resources, etc.)"
)

st.divider()

# ---------- OA structure by company type ----------
st.subheader("💻 Online Assessment Structure by Company Type")
oa_data = [
    {"Company Type": "Product (e.g. AWS, Microsoft, Adobe)", "OA Focus": "2-3 medium-hard DSA questions — graphs, trees, DP, sliding window"},
    {"Company Type": "Analytics / Consulting (e.g. Deloitte, PwC, Moody's)", "OA Focus": "Aptitude-heavy, SQL basics, case-based MCQs"},
    {"Company Type": "Core (e.g. STMicro, Honeywell)", "OA Focus": "OS, DBMS, Networking + 1 easy coding question"},
    {"Company Type": "Startups / Small Companies", "OA Focus": "Easy coding, practical tasks, real-world problem solving"},
]
st.table(oa_data)

st.subheader("🎤 Interview Structure by Company Type")
interview_data = [
    {"Company Type": "Product", "Focus": "Deep DSA, optimization, follow-ups, sometimes system design"},
    {"Company Type": "Consulting / Analytics", "Focus": "SQL queries, case discussions, resume-based questions"},
    {"Company Type": "Core", "Focus": "Deep OS/DBMS/networking or electronics (for ECE)"},
    {"Company Type": "Startups", "Focus": "Project-based discussion, practical implementation ability"},
]
st.table(interview_data)

st.caption("HR round (all types): 'Tell me about yourself', 'Why this company?', strengths/weaknesses, situational questions.")

st.divider()

# ---------- Do's and Don'ts ----------
col1, col2 = st.columns(2)
with col1:
    st.subheader("✅ Do's")
    st.markdown("- Carry resumes\n- Dress formally\n- Be punctual\n- Attend the PPT if you plan to sit for that company\n- Check the portal daily during placement season")
with col2:
    st.subheader("❌ Don'ts")
    st.markdown("- Don't miss the OA after registering\n- Don't leave interviews midway\n- Don't put fake information on your resume\n- Don't wait for email — the portal is the source of truth")
