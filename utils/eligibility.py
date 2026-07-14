import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "eligibility_criteria.json")

def load_companies():
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
    return data["companies"]


def get_company_names():
    return [c["name"] for c in load_companies()]


def check_eligibility(company_name: str, cgpa: float, active_backlogs: int, branch: str):
#tells if eligible and also gives reasons if not
    companies = load_companies()
    """ALTERNATE CODE:
    company = None
    for c in companies:
        if c["name"]==company_name:
            company=c
            break"""
    company = next((c for c in companies if c["name"] == company_name), None)

    if company is None:
        return False, [f"No eligibility data found for '{company_name}'."]

    reasons = []
    eligible = True

    if cgpa < company["min_cgpa"]:
        eligible = False
        reasons.append(
            f"CGPA {cgpa} is below the required {company['min_cgpa']} for {company_name}."
        )

    if active_backlogs > company["max_active_backlogs"]:
        eligible = False
        reasons.append(
            f"You have {active_backlogs} active backlog(s); "
            f"{company_name} allows a maximum of {company['max_active_backlogs']}."
        )

    branch_ok = "All Branches" in company["eligible_branches"] or branch in company["eligible_branches"]
    if not branch_ok:
        eligible = False
        reasons.append(
            f"{branch} is not in the eligible branch list for {company_name}."
        )

    if eligible:
        reasons.append(f"You meet all criteria for {company_name}. All the best!")
        if company.get("oa_round"):
            reasons.append(f"OA Round: {company['oa_round']}")
        if company.get("interview_rounds"):
            reasons.append(f"Interview Rounds: {company['interview_rounds']}")
        if company.get("other_criteria"):
            reasons.append(f"Other Criteria: {company['other_criteria']}")

    return eligible, reasons
