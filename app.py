import csv
import datetime
import json
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

RISK_LEVEL_TO_SCORE = {
    "LOW": 25,
    "MEDIUM": 60,
    "HIGH": 90,
}

ALLOWED_DOMAINS = {"generic", "ecommerce", "retail_banking"}
ALLOWED_RISK_TYPES = {
    "Product / Functional",
    "Environment / Operational",
    "Dependency / External",
    "Quality / Test",
    "Process / Governance",
    "Security / Compliance",
    "Schedule / Capacity",
}
ALLOWED_OWNERS = {
    "Program Manager",
    "Engineering Manager",
    "QA Lead",
    "Product Manager",
    "External Dependency Owner",
    "Release Manager",
}
ALLOWED_READINESS = {"GO", "GO_WITH_RISKS", "NO_GO"}
ALLOWED_URGENCY = {"Monitor", "Act This Sprint", "Immediate Escalation"}

SYSTEM_PROMPT = """
You are an AI release readiness and program risk intelligence engine for delivery leaders.

Your job is to analyze a one-line or short project/release update, identify the issue, assess release impact,
classify the most relevant risk, and recommend the next best action in a way a senior stakeholder can use immediately.

Return ONLY valid JSON with this exact schema:
{
  "domain": "generic | ecommerce | retail_banking",
  "issue_title": "short executive-friendly title",
  "project_name": "string",
  "milestone": "string",
  "release_readiness_status": "GO | GO_WITH_RISKS | NO_GO",
  "blocking_flag": "Yes | No",
  "risk_level": "LOW | MEDIUM | HIGH",
  "risk_score": 0,
  "confidence_score": 0,
  "risk_type": "Product / Functional | Environment / Operational | Dependency / External | Quality / Test | Process / Governance | Security / Compliance | Schedule / Capacity",
  "sub_risk_type": "short subtype",
  "urgency": "Monitor | Act This Sprint | Immediate Escalation",
  "root_cause": "short explanation",
  "business_impact": "short explanation",
  "recommended_action": "specific action",
  "action_owner": "Program Manager | Engineering Manager | QA Lead | Product Manager | External Dependency Owner | Release Manager",
  "explanation": "why this decision was made",
  "evidence_signals": ["signal 1", "signal 2"],
  "escalation_needed": "Yes | No"
}

Rules:
- risk_score and confidence_score must be between 0 and 100
- risk_level must align with risk_score:
  LOW for 0-39
  MEDIUM for 40-74
  HIGH for 75-100
- domain should default to "generic" unless the user explicitly provides enough context to justify "ecommerce" or "retail_banking"
- choose the most likely resolver, not the meeting coordinator
- owner principles:
  - Product / Functional -> Engineering Manager
  - Environment / Operational -> Release Manager
  - Dependency / External -> External Dependency Owner
  - Quality / Test -> QA Lead
  - Process / Governance -> Program Manager
  - Security / Compliance -> Engineering Manager
  - Schedule / Capacity -> Engineering Manager
- only use Product Manager if the issue is clearly about requirements, prioritization, or scope decisions
- release_readiness_status should reflect business readiness:
  GO when no meaningful blocker exists
  GO_WITH_RISKS when release can proceed but needs explicit mitigation
  NO_GO when a blocker makes release unsafe or unreliable
- blocking_flag should be Yes when a blocker can directly prevent or seriously disrupt release readiness
- recommended_action must be concrete and action-oriented
- issue_title must be a short, meaningful headline describing the issue itself, not a generic bucket name
- risk_type must be chosen from the allowed taxonomy only
- evidence_signals must contain 2 to 5 concise phrases
- evidence_signals must be derived ONLY from the actual user input or explicit structured fields
- NEVER invent evidence from generic domain examples, taxonomy hints, or possible scenarios that were not mentioned
- if the input is sparse, keep evidence sparse and specific
"""


def clamp_score(value: Any, default: int) -> int:
    try:
        parsed = int(float(value))
    except (TypeError, ValueError):
        return default
    return max(0, min(parsed, 100))


def fallback_issue_title(text: str) -> str:
    cleaned = " ".join(text.strip().split())
    if not cleaned:
        return "Program risk requiring action"
    trimmed = cleaned[:70].rstrip(" ,.;:")
    return trimmed[:1].upper() + trimmed[1:]


def fallback_evidence_signals(text: str) -> list[str]:
    cleaned = " ".join(text.strip().split())
    if not cleaned:
        return ["Limited structured signals were provided."]
    return [cleaned]


def build_program_payload(input_text: str) -> Dict[str, Any]:
    cleaned = input_text.strip()
    if not cleaned:
        return {}

    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            domain = str(parsed.get("domain", "generic")).strip().lower()
            if domain not in ALLOWED_DOMAINS:
                domain = "generic"
            parsed["domain"] = domain
            parsed["status_summary"] = str(parsed.get("status_summary") or parsed.get("scenario") or cleaned).strip()
            return parsed
    except json.JSONDecodeError:
        pass

    return {
        "domain": "generic",
        "status_summary": cleaned,
        "blockers": [],
    }


def normalize_result(result: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(result)

    domain = str(normalized.get("domain", payload.get("domain", "generic"))).strip().lower()
    if domain not in ALLOWED_DOMAINS:
        domain = "generic"

    normalized["domain"] = domain
    status_summary = str(payload.get("status_summary", "")).strip()
    normalized["issue_title"] = normalized.get("issue_title") or fallback_issue_title(status_summary)
    normalized["project_name"] = normalized.get("project_name") or "Program Delivery Intelligence"
    normalized["milestone"] = normalized.get("milestone") or "Current delivery cycle"

    risk_level = str(normalized.get("risk_level", "MEDIUM")).upper().strip()
    if risk_level not in {"LOW", "MEDIUM", "HIGH"}:
        risk_level = "MEDIUM"

    risk_score = clamp_score(normalized.get("risk_score"), RISK_LEVEL_TO_SCORE[risk_level])
    confidence_score = clamp_score(normalized.get("confidence_score"), 72)

    if risk_score <= 39:
        risk_level = "LOW"
    elif risk_score <= 74:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    risk_type = str(normalized.get("risk_type", "")).strip()
    if risk_type not in ALLOWED_RISK_TYPES:
        risk_type = "Process / Governance"

    release_status = str(normalized.get("release_readiness_status", "GO_WITH_RISKS")).upper().strip()
    if release_status not in ALLOWED_READINESS:
        release_status = "GO_WITH_RISKS"

    blocking_flag = "Yes" if str(normalized.get("blocking_flag", "No")).strip().lower() == "yes" else "No"
    escalation_needed = "Yes" if str(normalized.get("escalation_needed", "No")).strip().lower() == "yes" else "No"

    if risk_level == "HIGH":
        release_status = "NO_GO" if blocking_flag == "Yes" else "GO_WITH_RISKS"
        escalation_needed = "Yes"
    elif risk_level == "MEDIUM" and release_status == "GO":
        release_status = "GO_WITH_RISKS"

    evidence_signals = normalized.get("evidence_signals", [])
    if not isinstance(evidence_signals, list):
        evidence_signals = [str(evidence_signals)]

    normalized["risk_level"] = risk_level
    normalized["risk_score"] = risk_score
    normalized["confidence_score"] = confidence_score
    normalized["risk_type"] = risk_type
    normalized["sub_risk_type"] = normalized.get("sub_risk_type") or "General Delivery Risk"
    normalized["release_readiness_status"] = release_status
    normalized["blocking_flag"] = blocking_flag
    urgency = str(normalized.get("urgency", "Act This Sprint")).strip()
    normalized["urgency"] = urgency if urgency in ALLOWED_URGENCY else "Act This Sprint"
    normalized["root_cause"] = normalized.get("root_cause", "Insufficient evidence provided.")
    normalized["business_impact"] = normalized.get("business_impact", "Potential release disruption.")
    normalized["recommended_action"] = normalized.get("recommended_action", "Review the update and assign an owner.")
    action_owner = str(normalized.get("action_owner", "")).strip()
    normalized["action_owner"] = action_owner if action_owner in ALLOWED_OWNERS else "Program Manager"
    normalized["explanation"] = normalized.get("explanation", "Decision generated from the available delivery and readiness signals.")
    cleaned_evidence = [str(item).strip() for item in evidence_signals if str(item).strip()][:5]
    if not cleaned_evidence:
        cleaned_evidence = fallback_evidence_signals(status_summary)
    normalized["evidence_signals"] = cleaned_evidence
    normalized["escalation_needed"] = escalation_needed

    if not normalized["evidence_signals"]:
        normalized["evidence_signals"] = ["Limited structured signals were provided."]

    return normalized


def risk_analyzer(input_text: str) -> Optional[Dict[str, Any]]:
    payload = build_program_payload(input_text)
    if not payload:
        return None

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Analyze this release/program update and return JSON only.\n"
                    "Evidence signals must only reflect what is actually present in the input.\n"
                    f"{json.dumps(payload, indent=2)}"
                ),
            },
        ],
    )

    output = response.choices[0].message.content.strip()
    if output.startswith("```"):
        output = output.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(output)
    except json.JSONDecodeError:
        print("JSON parsing failed:")
        print(output)
        return None

    return normalize_result(result, payload)


def save_to_csv(input_text: str, result: Dict[str, Any]) -> None:
    if not result:
        return

    file_name = f"results_{datetime.date.today()}.csv"
    file_exists = os.path.isfile(file_name)

    with open(file_name, "a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        if not file_exists:
            writer.writerow(
                [
                    "timestamp",
                    "scenario",
                    "domain",
                    "issue_title",
                    "project_name",
                    "milestone",
                    "release_readiness_status",
                    "blocking_flag",
                    "risk_level",
                    "risk_score",
                    "confidence_score",
                    "risk_type",
                    "sub_risk_type",
                    "urgency",
                    "root_cause",
                    "business_impact",
                    "recommended_action",
                    "action_owner",
                    "explanation",
                    "evidence_signals",
                    "escalation_needed",
                ]
            )

        writer.writerow(
            [
                datetime.datetime.now().isoformat(timespec="seconds"),
                input_text.strip(),
                result["domain"],
                result["issue_title"],
                result["project_name"],
                result["milestone"],
                result["release_readiness_status"],
                result["blocking_flag"],
                result["risk_level"],
                result["risk_score"],
                result["confidence_score"],
                result["risk_type"],
                result["sub_risk_type"],
                result["urgency"],
                result["root_cause"],
                result["business_impact"],
                result["recommended_action"],
                result["action_owner"],
                result["explanation"],
                " | ".join(result["evidence_signals"]),
                result["escalation_needed"],
            ]
        )


def print_result(result: Dict[str, Any]) -> None:
    if not result:
        return

    print("\n--- RELEASE READINESS DECISION ---\n")
    print(f"Domain             : {result['domain']}")
    print(f"Issue Title        : {result['issue_title']}")
    print(f"Project Name       : {result['project_name']}")
    print(f"Milestone          : {result['milestone']}")
    print(f"Release Status     : {result['release_readiness_status']}")
    print(f"Blocking Flag      : {result['blocking_flag']}")
    print(f"Risk Level         : {result['risk_level']}")
    print(f"Risk Score         : {result['risk_score']}/100")
    print(f"Confidence Score   : {result['confidence_score']}/100")
    print(f"Risk Type          : {result['risk_type']}")
    print(f"Sub Risk Type      : {result['sub_risk_type']}")
    print(f"Urgency            : {result['urgency']}")
    print(f"Escalation Needed  : {result['escalation_needed']}")
    print(f"Root Cause         : {result['root_cause']}")
    print(f"Business Impact    : {result['business_impact']}")
    print(f"Recommended Action : {result['recommended_action']}")
    print(f"Action Owner       : {result['action_owner']}")
    print(f"Explanation        : {result['explanation']}")
    print("Evidence Signals   :")
    for signal in result["evidence_signals"]:
        print(f"  - {signal}")


if __name__ == "__main__":
    print("Enter a free-text release/program update or paste a JSON object with structured fields.")
    scenario = input("Program update: ")

    result = risk_analyzer(scenario)
    if result:
        save_to_csv(scenario, result)
        print_result(result)
    else:
        print("Failed to analyze the program update.")
