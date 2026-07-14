def classify_query(query: str) -> str:
    """Categorizes student queries into the 4 core TNP helpdesk features."""
    q = query.lower()
    if any(k in q for k in ["eligibility", "cgpa", "backlog", "criteria", "percent", "cutoff"]):
        return "Eligibility & Stats"
    elif any(k in q for k in ["company", "schedule", "timeline", "when visit", "recruiter", "dates"]):
        return "Company Schedules"
    elif any(k in q for k in ["interview", "rounds", "coding test", "aptitude", "technical round"]):
        return "Interview & Test Formats"
    elif any(k in q for k in ["guideline", "policy", "rules", "bond", "blacklist", "registration"]):
        return "Company Guidelines"
    else:
        return "General FAQ"