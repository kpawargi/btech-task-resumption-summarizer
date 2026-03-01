import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from summarizer import generate_summary

# ---------------- PATH SETUP ----------------
BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "data" / "outputs"

st.set_page_config(page_title="Task Resumption Summarizer", layout="centered")

# ---------------- SESSION STATE INIT ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_task" not in st.session_state:
    st.session_state.selected_task = None

if "active_session" not in st.session_state:
    st.session_state.active_session = None


# ==================================================
# HOME PAGE
# ==================================================
if st.session_state.page == "home":

    st.title("🧠 Task Resumption Summarizer")

    if not OUTPUTS_DIR.exists():
        st.error(f"Outputs directory not found: {OUTPUTS_DIR}")
        st.stop()

    task_ids = [p.name for p in OUTPUTS_DIR.iterdir() if p.is_dir()]

    if not task_ids:
        st.warning("No TASK_ID folders found.")
        st.stop()

    selected_task = st.selectbox(
        "Select Task ID",
        task_ids,
        index=None,
        placeholder="Choose a task..."
    )

    if selected_task:
        st.session_state.selected_task = selected_task

        col1, col2 = st.columns(2)

        # -------- RESUME TASK --------
        with col1:
            if st.button("▶ Resume Task", use_container_width=True):

                task_dir = OUTPUTS_DIR / selected_task
                session_dirs = [p for p in task_dir.iterdir() if p.is_dir()]

                if not session_dirs:
                    st.error("No session folders found for this TASK_ID.")
                    st.stop()

                latest_session = max(session_dirs, key=lambda p: p.stat().st_mtime)
                context_file = latest_session / "ContextBundle.json"

                if not context_file.exists():
                    st.error("ContextBundle.json not found.")
                    st.stop()

                with open(context_file, "r", encoding="utf-8") as f:
                    context_bundle = json.load(f)

                context_list = context_bundle.get("context", [])
                summary = generate_summary(context_list)

                summary_file = latest_session / "ResumeSummary.json"
                with open(summary_file, "w", encoding="utf-8") as f:
                    json.dump(
                        {
                            "task_id": selected_task,
                            "session_id": latest_session.name,
                            "summary": summary
                        },
                        f,
                        indent=2
                    )

                st.session_state.active_session = latest_session.name
                st.session_state.generated_summary = summary
                st.session_state.page = "summary"
                st.rerun()

        # -------- CREATE SESSION --------
        with col2:
            if st.button("➕ Create Session", use_container_width=True):

                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                new_session_dir = OUTPUTS_DIR / selected_task / timestamp
                new_session_dir.mkdir(parents=True, exist_ok=True)

                st.session_state.active_session = timestamp
                st.session_state.page = "create_session"
                st.rerun()


# ==================================================
# CREATE SESSION PAGE
# ==================================================
elif st.session_state.page == "create_session":

    st.title("🆕 New Session")
    st.caption(f"Task: {st.session_state.selected_task}")

    diff_text = st.text_area(
        "Enter your .diff output",
        height=300,
        placeholder="Paste git diff output here..."
    )

    if st.button("💾 Save Session"):

        session_dir = (
            OUTPUTS_DIR
            / st.session_state.selected_task
            / st.session_state.active_session
        )

        context_bundle = diff_text
        

        with open(session_dir / "sample.diff", "w", encoding="utf-8") as f:
           f.write(diff_text)

        st.success("Session created successfully!")
        st.session_state.page = "home"
        st.rerun()

    if st.button("⬅ Back"):
        st.session_state.page = "home"
        st.rerun()


# ==================================================
# SUMMARY PAGE
# ==================================================
elif st.session_state.page == "summary":

    st.title("📄 Resume Summary")

    st.text_area(
        "Generated Summary",
        st.session_state.generated_summary,
        height=350
    )

    st.caption(
        f"Task: {st.session_state.selected_task} | "
        f"Session: {st.session_state.active_session}"
    )

    if st.button("⬅ Back to Home"):
        st.session_state.page = "home"
        st.rerun()
