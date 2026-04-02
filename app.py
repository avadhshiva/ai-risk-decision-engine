import os
import json
import csv
import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load env
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

risk_map = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3
}

# 🔹 Format text for better readability
def format_for_display(text):
    if not text:
        return ""
    sentences = text.split(". ")
    return ".\n".join(sentences)


# 🔹 AI Risk Analyzer
def risk_analyzer(input_text):
    prompt = f"""
    Analyze the scenario and return ONLY valid JSON.

    {{
      "risk_level": "LOW | MEDIUM | HIGH",
      "risk_category": "Financial | Operational | Technical | Compliance",
      "impact": "short explanation",
      "mitigation": "short actionable mitigation"
    }}

    Scenario: {input_text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    output = response.choices[0].message.content.strip()

    # Clean markdown if present
    if output.startswith("```"):
        output = output.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(output)
    except:
        print("❌ JSON parsing failed:", output)
        return None

    return result


# 🔹 Save results
def save_to_csv(input_text, result):
    if not result:
        return

    file_name = f"results_{datetime.date.today()}.csv"
    file_exists = os.path.isfile(file_name)

    risk_level = result.get("risk_level", "").upper()
    impact = format_for_display(result.get("impact", ""))
    mitigation = format_for_display(result.get("mitigation", ""))

    score = risk_map.get(risk_level, 0)
    category = result.get("risk_category", "Unknown")

    with open(file_name, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "scenario",
                "risk_level",
                "risk_score",
                "category",
                "impact",
                "mitigation"
            ])

        writer.writerow([
            input_text,
            risk_level,
            score,
            category,
            impact,
            mitigation
        ])


# 🔹 Print result
def print_result(result):
    if not result:
        return

    risk_level = result.get("risk_level", "").upper()
    impact = result.get("impact", "")
    mitigation = result.get("mitigation", "")
    score = risk_map.get(risk_level, 0)
    category = result.get("risk_category", "Unknown")

    print("\n--- RESULT ---\n")
    print(f"Risk Level : {risk_level}")
    print(f"Score      : {score}/3")
    print(f"Category   : {category}")
    print(f"Impact     : {impact}")
    print(f"Mitigation : {mitigation}")


# 🔹 MAIN
if __name__ == "__main__":
    scenario = input("Enter scenario: ")

    result = risk_analyzer(scenario)

    if result:
        save_to_csv(scenario, result)
        print_result(result)
    else:
        print("❌ Failed to analyze")