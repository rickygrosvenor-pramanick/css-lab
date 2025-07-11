import os
import json
import argparse
import re
import anthropic
from dotenv import load_dotenv

# RUN python claude_multi_agent_interview_sim.py --persona data/persona_1.json in the ai-friend-sim directory

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def chat(system, user):
    response = client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=500,
        temperature=0.7,
        system=system,
        messages=[
            {"role": "user", "content": user}
        ]
    )
    return response.content[0].text.strip()

class ScenarioAgent:
    def set_scene(self, major):
        return f"""You have a major job interview tomorrow for a highly competitive {major}-related internship. 
        You've been balancing coursework, job applications, and personal responsibilities. 
        You're anxious about how you'll perform, especially in answering behavioral questions and presenting yourself confidently under pressure."""

class StudentAgent:
    def __init__(self, persona, label):
        self.persona = persona
        self.label = label

    def persona_prompt(self):
        p = self.persona
        return f"""You are {p['name']}, a {p['age']}-year-old first-year undergraduate {p['major']} major with a CGPA of {p['CGPA']:.2f}.
        Traits:
        - Conscientiousness: {p['Conscientiousness']:.2f}
        - Academic Self-Efficacy: {p['Academic Self-Efficacy']:.2f}
        - Achievement Motivation: {p['Grade Goals (Achievement Motivation)']:.2f}
        - Effort Regulation: {p['Effort Regulation (Self-Discipline)']:.2f}
        - Low Test Anxiety: {p['Low Test Anxiety']:.2f}
        - Grit: {p['Grit (Perseverance)']:.2f}

        Background: {p['persona']}

        You're preparing for an important job interview tomorrow. Respond in-character."""

    def respond_to_scenario(self, scenario):
        prompt = f"""Here's the situation you're facing:
        {scenario}

        How are you feeling? What are your thoughts and your current plan to prepare for the interview?"""
        return chat(self.persona_prompt(), prompt)

    def respond_after_advice(self, scenario, advice):
        prompt = f"""You were facing this situation:
        {scenario}

        Then you received this advice:
        {advice}

        How do you feel now? Will this change your preparation? Respond in character and do not format it like an email."""
        return chat(self.persona_prompt(), prompt)

class AdvisorAgent:
    def provide_advice(self, scenario, persona):
        system = "You are a helpful and practical interview coach. Give concise, structured advice based on the student's persona. Do not use email signoffs."
        user = f"""This is the student's scenario:
        {scenario}

        And their background:
        {json.dumps(persona, indent=2)}

        Provide detailed, structured advice without sounding like an email."""
        return chat(system, user)

def simulate_outcome(prep_response, persona):
    system = "You are a neutral evaluator. Based on the persona and preparation, output the following:"
    user = f"""
        Persona:
        {json.dumps(persona)}

        Interview prep behavior:
        \"\"\"
        {prep_response}
        \"\"\"

        Please respond **exactly** in the following format:
        Result: <Offer or No Offer>
        Confidence Score: <0-100>
        Preparation Quality: <0-100>
        Learning Mindset: <0-100>
        Stress Management: <0-100>
        Self-Assessment: <1-2 sentences>
        """
    result = chat(system, user)

    def extract(pattern, cast=str):
        match = re.search(pattern, result)
        return cast(match.group(1).strip()) if match else None

    return {
        "result": extract(r"Result:\s*(Offer|No Offer)"),
        "confidence": extract(r"Confidence Score:\s*(\d+)", int),
        "prep_quality": extract(r"Preparation Quality:\s*(\d+)", int),
        "mindset": extract(r"Learning Mindset:\s*(\d+)", int),
        "stress_mgmt": extract(r"Stress Management:\s*(\d+)", int),
        "assessment": extract(r"Self-Assessment:\s*(.*)")
    }

def load_persona(path):
    with open(path, "r") as f:
        return json.load(f)

def display_outcome(label, outcome):
    print(f"🔹 {label}:")
    print(f"- Result: {outcome['result']}")
    print(f"- Confidence Score: {outcome['confidence']}")
    print(f"- Preparation Quality: {outcome['prep_quality']}")
    print(f"- Learning Mindset: {outcome['mindset']}")
    print(f"- Stress Management: {outcome['stress_mgmt']}")
    print(f"- Self-Assessment: {outcome['assessment']}\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--persona", type=str, required=True, help="Path to persona JSON file")
    args = parser.parse_args()

    persona = load_persona(args.persona)
    major = persona.get("major", "Psychology")

    print("\n=== MULTI-AGENT INTERVIEW SIMULATION ===\n")

    scenario_agent = ScenarioAgent()
    scenario = scenario_agent.set_scene(major)
    print(f"🎭 SCENARIO:\n{scenario}\n")

    agent2 = StudentAgent(persona, "Agent 2 (No Advice)")
    agent3 = StudentAgent(persona, "Agent 3 (With Advice)")

    print("👤 AGENT 2 - Initial Reflection (No Advice):")
    resp2 = agent2.respond_to_scenario(scenario)
    print(resp2 + "\n")

    print("👤 AGENT 3 - Initial Reflection (Will Receive Advice):")
    resp3 = agent3.respond_to_scenario(scenario)
    print(resp3 + "\n")

    advisor = AdvisorAgent()
    print("🤖 ADVISOR - Giving Advice:")
    advice = advisor.provide_advice(scenario, persona)
    print(advice + "\n")

    print("👤 AGENT 3 - Post-Advice Reflection:")
    resp3_after = agent3.respond_after_advice(scenario, advice)
    print(resp3_after + "\n")

    print("📝 INTERVIEW OUTCOME SUMMARY:\n")
    outcome2 = simulate_outcome(resp2, persona)
    display_outcome("Agent 2 (No Advice)", outcome2)

    outcome3 = simulate_outcome(resp3_after, persona)
    display_outcome("Agent 3 (With Advice)", outcome3)

    print("📊 COMPARISON SUMMARY:")
    delta_conf = outcome3["confidence"] - outcome2["confidence"]
    delta_prep = outcome3["prep_quality"] - outcome2["prep_quality"]
    delta_mindset = outcome3["mindset"] - outcome2["mindset"]
    delta_stress = outcome3["stress_mgmt"] - outcome2["stress_mgmt"]

    if outcome3["result"] == "Offer" and outcome2["result"] != "Offer":
        conclusion = "LLM advice helped the student secure an offer."
    elif delta_prep > 0 and delta_mindset > 0 and delta_stress > 0:
        conclusion = (
            f"LLM advice improved preparation (+{delta_prep}), mindset (+{delta_mindset}), and stress handling (+{delta_stress})."
        )
    elif delta_conf > 0:
        conclusion = f"LLM advice improved confidence (+{delta_conf})."
    else:
        conclusion = "LLM advice had limited measurable impact."

    print(f"Conclusion: {conclusion}")

if __name__ == "__main__":
    main()
