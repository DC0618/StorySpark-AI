import sys, os
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import uuid
import streamlit as st
import pandas as pd

import app.core.nlp as nlp
import app.core.storage as storage
import app.core.llm as llm

st.set_page_config(page_title="GoodSeeker · Suggestions v4", layout="wide")
st.title("GoodSeeker · AI Suggestions Demo")
st.caption("Inline incident ideas while writing • Brainstorming tab • Titles • Recs • Personalization • Insights")

with st.sidebar:
    st.header("Settings")
    role = st.selectbox("Your role", ["Manager","HR","Customer Success","Engineering","Sales","New Hire"], index=0)
    candidate_tags = st.text_area(
        "Org Values/Tags (comma-separated)",
        value="Innovation, Accountability, Ownership, Customer Obsession, Inclusion, Integrity, Collaboration, Bias for Action"
    )
    candidate_tags = [t.strip() for t in candidate_tags.split(",") if t.strip()]
    st.divider()
    st.caption("LLM optional: set OPENAI_API_KEY for boosted titles & chatbot.")

tabs = st.tabs(["Write Story (Inline Tips)", "Incident Suggestions", "Title Suggestions", "Chatbot (Beta)", "Personalization", "Insights & Automation"])

# ----- Write Story with inline incident suggestions -----
with tabs[0]:
    st.subheader("Write your story (with live suggestions)")
    title = st.text_input("Title (optional for now)")
    body = st.text_area("Story body", height=220, placeholder="Start typing your story… mention who, what happened, and the outcome.")
    
    # extract simple keywords from body for suggestions
    stop = set("the a an and or if then else with without into onto about above below over under to from for by of in on at is are was were be been being this that it they them we you i our my your".split())
    words = [w.strip(".,!?;:()[]{}\"'").lower() for w in body.split()]
    keywords = [w for w in words if w and w.isalpha() and w not in stop]
    uniq = []
    for w in keywords:
        if w not in uniq:
            uniq.append(w)
    keywords = uniq[:5]
    
    tips = nlp.suggest_incidents(role, keywords) if body.strip() else []
    if tips:
        st.markdown("**Inline suggestions (based on what you wrote):**")
        for t in tips:
            st.write("• ", t)
    
    col1, col2 = st.columns(2)
    with col1:
        use_llm = bool(os.getenv("OPENAI_API_KEY"))
        if st.button("Suggest Titles from Body"):
            titles = []
            if use_llm:
                titles = llm.suggest_titles_llm(body)
            if not titles:
                titles = nlp.suggest_titles_offline(body)
            st.markdown("**Title options:**")
            for t in titles:
                st.write("• ", t)
    with col2:
        if st.button("Save Story"):
            rid = str(uuid.uuid4())
            record = {"id": rid, "title": title or "Untitled", "body": body, "tags": []}
            storage.append_story(record)
            st.success("Saved to your local store.")

# ----- Brainstorming tab -----
with tabs[1]:
    st.subheader("Incident Suggestions (brainstorming)")
    kws = st.text_input("Keywords (comma-separated)", value="customer, escalation, quick fix")
    kws_list = [k.strip() for k in kws.split(",") if k.strip()]
    if st.button("Generate Ideas", type="primary"):
        ideas = nlp.suggest_incidents(role, kws_list)
        for i, idea in enumerate(ideas, start=1):
            st.write(f"{i}. {idea}")

# ----- Title Suggestions tab -----
with tabs[2]:
    st.subheader("AI Title Suggestions")
    rough = st.text_area("Paste rough text / bullets")
    use_llm = bool(os.getenv("OPENAI_API_KEY"))
    if st.button("Suggest Titles"):
        titles = []
        if use_llm:
            titles = llm.suggest_titles_llm(rough)
        if not titles:
            titles = nlp.suggest_titles_offline(rough)
        st.write("**Title options:**")
        for t in titles:
            st.write("• ", t)

# ----- Chatbot recommender -----
with tabs[3]:
    st.subheader("Ask which stories to read")
    stories = storage.get_all()
    query = st.text_input("Your interest", value="customer fast resolution")
    if st.button("Get Recommendations"):
        idx = nlp.SemanticIndex()
        items = [(s["id"], f"{s['title']}. {s['body']}") for s in stories]
        idx.fit(items)
        hits = idx.search(query, top_k=5)
        if hits:
            df = []
            by_id = {s["id"]: s for s in stories}
            for sid, score in hits:
                s = by_id.get(sid, {})
                df.append({"score": round(score, 3), "title": s.get("title",""), "preview": (s.get("body","")[:180]+"...")})
            st.dataframe(pd.DataFrame(df))
        ans = llm.chatbot_answer(query, "\n".join([f"{s['title']}: {s['body'][:200]}" for s in stories[:20]]))
        if ans:
            st.info(ans)

# ----- Personalization -----
with tabs[4]:
    st.subheader("Personalized picks")
    st.caption("Role-based themes + story matches for you")
    st.write("**Themes for your role:**")
    for idea in nlp.suggest_incidents(role, [])[:4]:
        st.write("• ", idea)
    stories = storage.get_all()
    idx = nlp.SemanticIndex()
    items = [(s["id"], f"{s['title']}. {s['body']}") for s in stories]
    idx.fit(items)
    hits = idx.search(role, top_k=5)
    if hits:
        st.write("**Stories you may like:**")
        df = []
        by_id = {s["id"]: s for s in stories}
        for sid, score in hits:
            s = by_id.get(sid, {})
            df.append({"score": round(score, 3), "title": s.get("title",""), "preview": (s.get("body","")[:180]+"...")})
        st.dataframe(pd.DataFrame(df))

# ----- Insights & Automation -----
with tabs[5]:
    st.subheader("Insights & Automation")
    stories = storage.get_all()
    st.write(f"Total stories: **{len(stories)}**")
    if stories:
        df = pd.DataFrame(stories)
        df["len"] = df["body"].str.len()
        st.write("Average story length (chars): ", int(df["len"].mean()))
        tag_counts = {}
        for s in stories:
            for t in s.get("tags", []):
                tag_counts[t] = tag_counts.get(t, 0) + 1
        if tag_counts:
            st.bar_chart(pd.Series(tag_counts))
        st.caption("Automation (simulated): Weekly digest → '3 new Collaboration stories' · '2 Customer Focus wins'")
