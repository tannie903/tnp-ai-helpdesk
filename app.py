

import streamlit as st
from utils.eligibility import check_eligibility, get_company_names
from utils.rag_chain import get_answer


st.set_page_config(
    page_title="TNP Helpdesk",
    page_icon="🎓",
    layout="wide",
)

# SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hi! I'm the TNP Helpdesk bot, I'm here to answer your queries."
            ),
        }
    ]



with st.sidebar:
    st.title("🎓 TNP Helpdesk")
    st.caption("Training & Placement Cell Assistant")
    st.divider()

    #Eligibility Checker
    st.subheader("Eligibility Checker")
    with st.form("eligibility_form"):
        company = st.selectbox("Company", options=get_company_names())
        cgpa = st.number_input("Your CGPA", min_value=0.0, max_value=10.0, value=8.0, step=0.2)
        active_backlogs = st.number_input("Active backlogs", min_value=0, max_value=20, value=0, step=1)
        branch = st.selectbox("Branch", options=["CSE", "IT", "ECE", "MAE", "AI_DS", "Architecture_Planning"])
        submitted = st.form_submit_button("Check Eligibility")

    if submitted:
        eligible, reasons = check_eligibility(company, cgpa, active_backlogs, branch)
        if eligible:
            st.success("You're eligible!")
        else:
            st.error("Not eligible for this one.")
        for r in reasons:
            st.write(f"- {r}")

    st.divider()

    st.subheader("📌 Quick Links")
    st.page_link("app.py", label="💬 Chat", icon="💬")
    st.page_link("data/2_Policies.py", label="📋 Policies & Guidelines", icon="📋")

    st.divider()
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = st.session_state.messages[:1]
        st.rerun()

#CHAT
st.header("💬 Ask the TNP Helpdesk")

quick_questions = {
    "📈 Placement stats": "What are the latest placement statistics?",
    "🏢 Companies visiting": "Which companies are coming to campus this year?",
    "📝 OA & interview format": "What does the OA and interview process look like for product companies vs core companies?",
    "🎯 Offer tiers & debarment": "What are the offer tier rules, and what can get me debarred?",
    "📄 Documents to carry": "What documents do I need to carry for a placement drive?",
}

quick_question = None
cols = st.columns(len(quick_questions))
for col, (label, question) in zip(cols, quick_questions.items()):
    with col:
        if st.button(label):
            quick_question = question

# Render existing chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Get new input
user_input = st.chat_input("Ask about placements, companies, or interview prep...")
if quick_question:
    user_input = quick_question

if user_input:
    # Show user message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get bot response 
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = get_answer(user_input)
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

