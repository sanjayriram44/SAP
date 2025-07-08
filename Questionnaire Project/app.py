import streamlit as st
from generate_suggested_questions import generate_suggested_questions
from generate_followups import generate_all_followups
from vector_utils import load_documents, create_or_load_vectorstore, get_rag_context
from extract_subprocesses import extract_subprocesses
from user_choices import USER_CHOICES
from core.models import llm_instance
from process_analysis import generate_process_understanding, revise_process_understanding, generate_process_recommendation, revise_process_recommendation

# Page config
st.set_page_config(page_title="SAP BBP Discovery Assistant", layout="wide")
st.title("📘 SAP BBP Discovery Assistant - Sub-Process Mode")

# Initialize session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
    st.session_state.current_question = ""
    st.session_state.followups = []
    st.session_state.step = "question"
    st.session_state.process_understanding = ""
    st.session_state.process_recommendation = ""

if "subprocess_list" not in st.session_state:
    st.session_state.subprocess_list = extract_subprocesses()
    st.session_state.current_subprocess_index = 0

if "selected_subprocess" not in st.session_state:
    st.session_state.selected_subprocess = st.session_state.subprocess_list[0]

if "rag_context" not in st.session_state or not st.session_state.rag_context:
    with st.spinner("Loading documents and building context..."):
        st.session_state.rag_context = get_rag_context()

# View subprocess list
with st.expander("📄 View All Sub-Processes"):
    for idx, sp in enumerate(st.session_state.subprocess_list, 1):
        st.markdown(f"{idx}. {sp}")

# Step 1: Generate Suggested Question
if st.session_state.step == "question":
    st.session_state.selected_subprocess = st.session_state.subprocess_list[st.session_state.current_subprocess_index]
    with st.spinner("Generating suggested question..."):
        suggested = generate_suggested_questions(
            user_choices=USER_CHOICES,
            sub_process_name=st.session_state.selected_subprocess,
            rag_context=st.session_state.rag_context,
            conversation_history=st.session_state.conversation_history
        )
        if suggested:
            st.session_state.current_question = suggested[0]
            st.session_state.followups = []
            st.session_state.step = "await_answer"
        else:
            st.session_state.current_subprocess_index += 1
            if st.session_state.current_subprocess_index >= len(st.session_state.subprocess_list):
                st.success("✅ All subprocesses completed!")
                st.stop()
            else:
                st.session_state.step = "question"
                st.rerun()

# Step 2: Await Main Answer
if st.session_state.step == "await_answer":
    st.markdown(f"###  Sub-Process: {st.session_state.selected_subprocess}")
    st.subheader("💬 Suggested Question")
    st.markdown(f"**Question:** {st.session_state.current_question}")
    main_answer = st.text_area("Your Answer")

    if st.button("Submit Main Answer"):
        if not main_answer.strip():
            st.warning("⚠️ Please enter an answer before proceeding.")
        else:
            with st.spinner("⏳ Generating follow-up questions..."):
                followups = generate_all_followups(
                    question=st.session_state.current_question,
                    answer=main_answer,
                    rag_context=st.session_state.rag_context,
                    conversation_history=st.session_state.conversation_history
                )
            st.session_state.followups = followups
            st.session_state.temp_main_answer = main_answer
            st.session_state.step = "followups"

            # Auto-update Process Understanding
            st.session_state.conversation_history.append({
                "question": st.session_state.current_question,
                "answer": main_answer,
                "followups": followups
            })
            with st.spinner("🔍 Updating Process Understanding..."):
                convo = st.session_state.conversation_history
                st.session_state.process_understanding = generate_process_understanding(convo)

            st.rerun()

# Step 3: Follow-Up Questions
if st.session_state.step == "followups":
    st.markdown(f"### Sub-Process: {st.session_state.selected_subprocess}")
    st.subheader("💬 Suggested Question")
    st.markdown(f"**Question:** {st.session_state.current_question}")
    st.markdown(f"**Your Answer:** {st.session_state.temp_main_answer}")

    st.subheader("🔍 Follow-Up Questions")
    for i, f in enumerate(st.session_state.followups):
        f["answer"] = st.text_input(f"Follow-up {i+1}: {f['question']}", key=f"fq_{i}")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("✅ Save & Continue"):
            # Finalize answers
            st.session_state.conversation_history[-1]["followups"] = st.session_state.followups
            st.session_state.current_subprocess_index += 1
            if st.session_state.current_subprocess_index >= len(st.session_state.subprocess_list):
                st.success("✅ All subprocesses completed!")
                st.stop()
            else:
                st.session_state.step = "question"
                for i in range(10):
                    if f"fq_{i}" in st.session_state:
                        del st.session_state[f"fq_{i}"]
                st.rerun()

    with col2:
        st.markdown("### 🧾 Process Understanding")
        st.markdown(st.session_state.process_understanding)
        st.markdown("#### ✏️ Add clarification or corrections")
        user_input = st.text_area("Suggest additions or corrections to the Process Understanding")
        if st.button("🔁 Update Process Understanding"):
            updated = revise_process_understanding(
                current_summary=st.session_state.process_understanding,
                user_input=user_input
            )
            st.session_state.process_understanding = updated
            st.rerun()

    with col3:
        if st.button("🛠️ Generate Process Recommendation"):
            with st.spinner("⚙️ Generating detailed recommendation..."):
                st.session_state.process_recommendation = generate_process_recommendation(st.session_state.conversation_history)
                st.rerun()

        if st.session_state.process_recommendation:
            st.markdown("### ✅ Process Recommendation")
            st.markdown(st.session_state.process_recommendation)
            st.markdown("#### ✏️ Add clarifications or corrections")
            rec_input = st.text_area("Suggest additions or corrections to the Recommendation")
            if st.button("🔁 Update Process Recommendation"):
                updated_rec = revise_process_recommendation(
                    current_recommendation=st.session_state.process_recommendation,
                    user_input=rec_input
                )
                st.session_state.process_recommendation = updated_rec
                st.rerun()
