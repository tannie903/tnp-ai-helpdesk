import streamlit as st

st.set_page_config(page_title="TNP AI Helpdesk", page_icon="🎓", layout="wide")

try:
    from main import build_graph
except Exception as e:
    st.error(
        "Couldn't import `build_graph` from main.py. Make sure streamlit_app.py "
        f"sits in the same folder as main.py (repo root).\n\nDetails: {e}"
    )
    st.stop()

try:
    from utils.eligibility import load_companies, get_company_names, check_eligibility
except Exception as e:
    st.error(
        "Couldn't import the eligibility checker. Make sure the file with "
        "load_companies() / get_company_names() / check_eligibility() is "
        f"saved at utils/eligibility.py.\n\nDetails: {e}"
    )
    st.stop()


@st.cache_resource
def get_app():
    return build_graph()


graph_app = get_app()

if "messages" not in st.session_state:
    st.session_state.messages = []  # [{"role": "user"/"assistant", "content": str}]

if "student" not in st.session_state:
    st.session_state.student = {"name": "", "branch": "", "year": "1"}

if "category" not in st.session_state:
    st.session_state.category = None  # set once the user picks a category on the welcome screen

CATEGORY_MAP = {
    "📊 Placement Stats": "placement",
    "📋 Guidelines": "guideline",
    "✅ Eligibility": "eligibility",
    "💬 General": "general",
}

# SIDEBAR
with st.sidebar:
    st.header("👋 Your Details")
    st.session_state.student["name"] = st.text_input(
        "Name", st.session_state.student["name"], placeholder="e.g. Aanya"
    )
    st.session_state.student["branch"] = st.text_input(
        "Branch", st.session_state.student["branch"], placeholder="e.g. IT"
    )
    st.session_state.student["year"] = st.selectbox(
        "Year", ["1", "2", "3", "4"],
        index=["1", "2", "3", "4"].index(st.session_state.student["year"]),
    )

    st.divider()

    st.header("✅ Quick Eligibility Checker")
    st.caption("Instant check against our records — no need to chat for this.")

    companies = get_company_names()
    all_branches = sorted(
        {b for c in load_companies() for b in c["eligible_branches"] if b != "All Branches"}
    )

    with st.form("eligibility_form"):
        sel_company = st.selectbox("Company", companies)
        sel_cgpa = st.number_input("Your CGPA", min_value=0.0, max_value=10.0, step=0.1, value=7.5)
        sel_backlogs = st.number_input("Active backlogs", min_value=0, max_value=10, step=1, value=0)
        sel_branch = st.selectbox("Your branch", all_branches)
        submitted = st.form_submit_button("Check Eligibility")

    if submitted:
        eligible, reasons = check_eligibility(sel_company, sel_cgpa, sel_backlogs, sel_branch)
        if eligible:
            st.success(f"✅ You're ELIGIBLE for {sel_company}")
        else:
            st.error(f"❌ Not eligible for {sel_company} right now")
        for r in reasons:
            st.write(f"- {r}")

    st.divider()

    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()


# MAIN AREA 
st.title("🎓 TNP AI Helpdesk")

name = st.session_state.student["name"]

if st.session_state.category is None:
    greeting = f"Hi {name}! 👋" if name else "Hi! 👋"
    st.subheader(f"{greeting} Welcome to the TNP Chatbot of IGDTUW")
    st.write("What would you like to know?")

    cols = st.columns(4)
    for col, label in zip(cols, CATEGORY_MAP.keys()):
        with col:
            if st.button(label, use_container_width=True):
                st.session_state.category = label
                st.rerun()

else:
    top_left, top_right = st.columns([5, 1])
    with top_left:
        st.caption(f"Category: **{st.session_state.category}**")
    with top_right:
        if st.button("🔄 Change"):
            st.session_state.category = None
            st.rerun()

    # Display past chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_query = st.chat_input("Type your question...")

    if user_query:
        # Display current query immediately on UI
        with st.chat_message("user"):
            st.markdown(user_query)

        # 1. Format prior history into (role, content) tuples
        formatted_history = [
            ("human" if m["role"] == "user" else "ai", m["content"])
            for m in st.session_state.messages
        ]

        # 2. Prepend category for router matching
        full_query = f"{CATEGORY_MAP[st.session_state.category]} {user_query}"

        # 3. Invoke graph with formatted prior history
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    result = graph_app.invoke({
                        "user_query": full_query,
                        "chat_history": formatted_history
                    })
                    response = result.get("response", "Sorry, I couldn't generate a response.")
                except Exception as e:
                    response = f"Something went wrong while generating a response: {e}"
            st.markdown(response)

        # 4. Save both current turn messages to state AFTER execution
        st.session_state.messages.append({"role": "user", "content": user_query})
        st.session_state.messages.append({"role": "assistant", "content": response})