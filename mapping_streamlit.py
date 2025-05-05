import streamlit as st
import pandas as pd

# — (1) load data
qs = pd.read_csv("questions.csv")
fus = pd.read_csv("followups.csv")

# explicit column names
QUESTION_COL         = "Question"
LEANING_COL          = "Political Leaning"
FOLLOWUP_TEXT_COL    = "Statement text content"

# — (2) build a mapping from question → follow-ups
question_to_followups = {}
for _, row in fus.iterrows():
    q_key = row[QUESTION_COL].strip()                       # e.g. "How can I register…"
    f_txt = row[FOLLOWUP_TEXT_COL].strip()                  # now using the correct column
    question_to_followups.setdefault(q_key, []).append(f_txt)

# — (3) build a lookup for question → leaning
question_to_leaning = {
    row[QUESTION_COL].strip(): row[LEANING_COL].strip().capitalize()
    for _, row in qs.iterrows()
}

# — (4) list of unique, sorted questions
questions = sorted(question_to_leaning.keys())

# — (5) Streamlit UI
st.title("❓ Question → Follow-Ups Explorer")

selected_q = st.selectbox("Select a question:", questions)

# show its political leaning
st.markdown(f"**Political Leaning:** {question_to_leaning.get(selected_q, 'Unknown')}")

# show follow-ups (or note none)
followups = question_to_followups.get(selected_q, [])
if followups:
    st.markdown("**Follow-ups:**")
    for fu in followups:
        st.write("•", fu)
else:
    st.write("_No follow-ups found for this question._")
