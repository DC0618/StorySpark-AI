import re, random
from typing import List, Dict, Tuple
from dataclasses import dataclass
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.sentiment import SentimentIntensityAnalyzer

@dataclass
class StoryRecord:
    id: str
    title: str
    body: str
    tags: List[str]

def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()

ROLE_TO_THEMES = {
    "Manager": ["Leadership moment", "Cross-team unblock", "Coaching & growth", "Handling deadline pressure"],
    "HR": ["Recognition done right", "Onboarding delight", "DEI in action", "Wellbeing support"],
    "Customer Success": ["Escalation turned win", "Proactive adoption push", "Renewal rescue", "Voice of customer"],
    "Engineering": ["Incident response", "Tech debt paydown", "Performance boost", "Quality-first decision"],
    "Sales": ["Creative prospecting", "Objection handling", "Collaborative close", "Post-sale handoff"],
    "New Hire": ["First win", "Mentor shoutout", "Learning moment", "Culture surprise"]
}

THEME_TO_INCIDENTS = {
    "Leadership moment": ["Stepped up to align teams during ambiguity", "Made a call to unblock delivery", "Shielded team from scope creep"],
    "Cross-team unblock": ["Coordinated eng + ops to fix a blocker", "Paired with CS to reproduce a tricky bug"],
    "Coaching & growth": ["Gave actionable feedback that changed approach", "Paired program to level up skills"],
    "Handling deadline pressure": ["Re-scoped with stakeholders to keep quality", "Negotiated timeline transparently"],
    "Recognition done right": ["Publicly credited behind-the-scenes work", "Tied recognition to values"],
    "Onboarding delight": ["Created a checklist/guide that saved new hires hours", "Buddy system that worked"],
    "DEI in action": ["Amplified quieter voices", "Adjusted process for inclusivity"],
    "Wellbeing support": ["Covered shifts for a teammate in need", "Flagged burnout early"],
    "Escalation turned win": ["Defused frustration and set clear next steps", "Closed loop with a thoughtful follow-up"],
    "Proactive adoption push": ["Shared a template that unlocked usage", "Hosted a mini-workshop for power users"],
    "Renewal rescue": ["Identified risk early and coordinated plan", "Brought in product for roadmap clarity"],
    "Voice of customer": ["Documented customer pain and shared succinctly", "Turned feedback into a small win"],
    "Incident response": ["Owned triage, status, and handoffs", "Wrote a crisp postmortem"],
    "Tech debt paydown": ["Refactored risky module", "Automated flaky checks"],
    "Performance boost": ["Optimized query or cache", "Cut load time by X%"],
    "Quality-first decision": ["Pushed back on risky release", "Added tests around a failure mode"],
    "Creative prospecting": ["Personalized outreach that got a reply", "Leveraged a customer story to open a door"],
    "Objection handling": ["Found the real blocker and addressed it", "Brought proof via pilot"],
    "Collaborative close": ["Co-sold with CS/SE to win trust", "Looped product early to de-risk"],
    "Post-sale handoff": ["Clear transition doc & meeting", "Aligned success plan to value"],
    "First win": ["Shipped a small but meaningful improvement", "Closed first ticket with praise"],
    "Mentor shoutout": ["Thanks to a mentor who unblocked you", "A peer who shared a crucial tip"],
    "Learning moment": ["Admitted a mistake and fixed it", "Asked for help early"],
    "Culture surprise": ["Tradition that made you feel welcome", "An unexpected kindness"]
}

def suggest_incidents(role: str, keywords: List[str]) -> List[str]:
    themes = ROLE_TO_THEMES.get(role, [])[:2] + random.sample(list(THEME_TO_INCIDENTS.keys()), 3)
    ideas = []
    for th in themes:
        opts = THEME_TO_INCIDENTS.get(th, [])
        if not opts: 
            continue
        pick = random.choice(opts)
        if keywords:
            pick = f"{pick} — related to: {', '.join(keywords[:3])}"
        ideas.append(f"{th}: {pick}")
    seen=set(); out=[]
    for i in ideas:
        if i not in seen:
            out.append(i); seen.add(i)
    return out[:6]

def suggest_titles_offline(text: str) -> List[str]:
    base = _clean(text)
    if not base:
        base = "A teammate unblocked a customer under pressure"
    core = base[:60].rstrip(".")
    return [
        f"{core}: From Roadblock to Win",
        "Turning a Detractor into a Promoter",
        "Cross‑Team Collaboration in Action",
        "Small Move, Big Impact",
        "Bias for Action When It Mattered"
    ]

def extract_tags(text: str, candidate_tags: List[str]) -> List[str]:
    text_l = _clean(text).lower()
    hits = []
    for t in candidate_tags:
        tl = t.lower()
        if tl in text_l:
            hits.append(t)
    if any(w in text_l for w in ["customer", "client", "user"]):
        hits.append("Customer Focus")
    if any(w in text_l for w in ["team", "helped", "together", "collaborat"]):
        hits.append("Collaboration")
    if any(w in text_l for w in ["fast", "quick", "hours", "minutes"]):
        hits.append("Bias for Action")
    dedup = []
    for h in hits:
        if h not in dedup:
            dedup.append(h)
    return dedup[:6]

class SemanticIndex:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.docs = []
        self.doc_ids = []
        self.matrix = None

    def fit(self, items: List[Tuple[str, str]]):
        self.doc_ids = [i for i, _ in items]
        self.docs = [t for _, t in items]
        if self.docs:
            self.matrix = self.vectorizer.fit_transform(self.docs)
        else:
            self.matrix = None

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        if self.matrix is None or not self.docs:
            return []
        qv = self.vectorizer.transform([query])
        from sklearn.metrics.pairwise import cosine_similarity
        sims = cosine_similarity(qv, self.matrix)[0]
        import numpy as np
        order = np.argsort(-sims)[:top_k]
        return [(self.doc_ids[i], float(sims[i])) for i in order]

def analyze_sentiment(text: str) -> Dict[str, float]:
    sia = SentimentIntensityAnalyzer()
    return sia.polarity_scores(text or "")
