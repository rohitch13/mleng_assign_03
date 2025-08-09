# streamlit_app.py
import streamlit as st
import requests
import pandas as pd
from typing import List

API_URL = "http://localhost:8011/score_headlines"

st.set_page_config(page_title="Headline Sentiment Scorer", layout="wide")

st.title("Headline Sentiment Scorer — Streamlit UI")
st.markdown(
    """
    Enter headlines individually, paste multiple lines, or upload a simple text file.
    Click **Score headlines** to call the backend service (FastAPI) running on port **8011**.
    """
)

# Initialize session state
if "headlines" not in st.session_state:
    st.session_state.headlines = []

if 'predictions' not in st.session_state:
    st.session_state.predictions = []

def add_headline_callback():
    val = st.session_state.get("new_headline_input", "").strip()
    if val:
        st.session_state.headlines.append(val)
        # Safe to modify session_state inside callback
        st.session_state["new_headline_input"] = ""

# --- Input column: add / paste / upload
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Add / paste headlines")
    new_h = st.text_input("Add a single headline and press Enter or click Add", key="new_headline_input")
    add_btn = st.button("Add headline", on_click=add_headline_callback)
    paste_area = st.text_area("Or paste multiple headlines (one per line)", height=120)
    paste_btn = st.button("Import pasted lines")

    uploaded_file = st.file_uploader("Or upload a text file (.txt) with one headline per line", type=["txt"])
    if uploaded_file is not None:
        try:
            raw = uploaded_file.read().decode("utf-8")
            lines = [l.strip() for l in raw.splitlines() if l.strip()]
            # Only add headlines not already in the list
            new_lines = [line for line in lines if line not in st.session_state.headlines]
            st.session_state.headlines.extend(new_lines)
            st.success(f"Imported {len(new_lines)} new headlines from file.")
            st.session_state.predictions = []
        except Exception as e:
            st.error(f"Could not read uploaded file: {e}")


    if add_btn and new_h.strip():
        st.session_state.headlines.append(new_h.strip())
        st.session_state.new_headline_input = ""  # clear input
    if paste_btn and paste_area.strip():
        lines = [l.strip() for l in paste_area.splitlines() if l.strip()]
        st.session_state.headlines.extend(lines)
        st.success(f"Imported {len(lines)} headlines from paste.")
        st.rerun()

with col2:
    st.subheader("Controls")
    if st.button("Clear all headlines"):
        st.session_state.headlines = []
    st.markdown("---")
    st.write("Backend endpoint (must run this separately from mleng_assign_02 folder):")
    st.code(API_URL)

# --- Editable headline list
st.subheader("Headline list (editable)")
if not st.session_state.headlines:
    st.info("No headlines yet — add or paste headlines above.")
else:
    # display editable list with remove button
    for i, h in enumerate(list(st.session_state.headlines)):  # list(...) to avoid mutation issues
        cols = st.columns([9, 1])
        with cols[0]:
            new_text = st.text_input(f"headline_{i}", value=h, key=f"headline_input_{i}")
            st.session_state.headlines[i] = new_text
        with cols[1]:
            if st.button("Remove", key=f"remove_{i}"):
                st.session_state.headlines.pop(i)
                st.rerun()

st.markdown("---")

# --- Scoring
st.subheader("Score headlines")
if st.button("Score headlines"):
    headlines = [h for h in st.session_state.headlines if h.strip()]
    if not headlines:
        st.error("No headlines to score. Add headlines first.")
    else:
        with st.spinner("Calling backend and scoring..."):
            try:
                resp = requests.post(API_URL, json={"headlines": headlines}, timeout=30)
                if resp.status_code != 200:
                    st.error(f"Backend returned {resp.status_code}: {resp.text}")
                else:
                    data = resp.json()
                    labels = data.get("labels", [])
                    if not isinstance(labels, list) or len(labels) != len(headlines):
                        st.error("Unexpected response format from backend.")
                    else:
                        df = pd.DataFrame({"headline": headlines, "label": labels})
                        st.success("Scored successfully")
                        # color rows by label (simple)
                        def color_label(val):
                            if isinstance(val, str):
                                v = val.lower()
                                if "optim" in v or "pos" in v or "happy" in v:
                                    return "background-color: #d4edda"
                                if "pess" in v or "neg" in v or "hate" in v:
                                    return "background-color: #f8d7da"
                                if "neutral" in v or "neu" in v:
                                    return "background-color: #fff3cd"
                            return ""
                        st.dataframe(df, use_container_width=True)
                        # also show a grouped summary
                        st.subheader("Summary")
                        st.table(df["label"].value_counts().rename_axis("label").reset_index(name="count"))
            except requests.exceptions.RequestException as exc:
                st.error(f"Request to backend failed: {exc}")

# Footer instructions
st.markdown("---")
st.markdown(
    """
    **Notes**
    - Make sure the FastAPI service is running on `http://localhost:8011`.
    - Start Streamlit with `streamlit run streamlit_app.py --server.port 9011`.
    """
)
