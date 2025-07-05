import os
import json
import random
from openai import OpenAI
import argparse
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# LLM does poorly with generating unique personas with high variance in CGPA, so we sample CGPA from a distribution and set that as grounding for persona generation.
def sample_cgpa():
    """
    Sample a CGPA based on the given distribution:
      - 20% between 3.6 and 4.0
      - 34% between 3.1 and 3.5
      - 33% between 2.6 and 3.0
      - 13% below 2.5
    Returns a float rounded to two decimal places.
    """
    bins = [
        (3.6, 4.0, 0.20),
        (3.1, 3.5, 0.34),
        (2.6, 3.0, 0.33),
        (0.0, 2.5, 0.13)
    ]
    r = random.random()
    cumulative = 0.0
    for low, high, weight in bins:
        cumulative += weight
        if r <= cumulative:
            return round(random.uniform(low, high), 2)
    # Fallback, should not normally reach here
    return round(random.uniform(0.0, 4.0), 2)

def generate_persona(traits, cgpa):
    # Prompt LLM to generate name, major, trait scores, age, and CGPA, retrying until valid JSON
    prompt = (
        "You are helping to create university student personas. "
        f"The student's CGPA is {cgpa:.2f}. "
        "Generate the following fields in JSON: 'name' (student full name), 'major' (academic major), "
        "'age' (years), 'CGPA' (0.0–4.0), and for each of these traits—Conscientiousness, Academic Self-Efficacy, "
        "Grade Goals (Achievement Motivation), Effort Regulation (Self-Discipline), Low Test Anxiety, and Grit (Perseverance)—"  
        "a score between 0 and 1. Then write a short student persona (3–5 sentences). "
        "Provide the entire output as a single JSON object with keys exactly matching these field names and 'persona'."
    )

    while True:
        response = client.chat.completions.create(
            model="gpt-4.1-2025-04-14",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=400,
            n=1
        )
        content = response.choices[0].message.content.strip()
        try:
            data = json.loads(content)
            # Ensure all expected keys are present
            expected_keys = set(traits + ['name', 'major', 'age', 'CGPA', 'persona'])
            if expected_keys.issubset(data.keys()):
                return data
        except json.JSONDecodeError:
            pass  # Retry on invalid JSON
        # Loop retries until valid JSON with expected fields


def main():
    parser = argparse.ArgumentParser(
        description="Generate university student personas with unique name-major combinations."
    )
    parser.add_argument(
        "--num", type=int, default=5,
        help="Number of personas to generate."
    )
    parser.add_argument(
        "--out_dir", type=str, default="data",
        help="Directory to write persona files."
    )
    args = parser.parse_args()

    traits = [
        "Conscientiousness",
        "Academic Self-Efficacy",
        "Grade Goals (Achievement Motivation)",
        "Effort Regulation (Self-Discipline)",
        "Low Test Anxiety",
        "Grit (Perseverance)"
    ]

    os.makedirs(args.out_dir, exist_ok=True)

    # avoid making the same person many times
    seen = set()
    count = 0
    attempts = 0
    while count < args.num:
        attempts += 1
        if attempts > args.num * 10:
            raise RuntimeError("Too many duplicate or invalid persona generations. Consider reviewing prompts or increasing variety.")
        cgpa = sample_cgpa()
        persona_data = generate_persona(traits, cgpa)
        name = persona_data.get('name')
        major = persona_data.get('major')
        key = (name, major)
        if not name or not major or key in seen:
            continue  # skip duplicates or invalid
        # Unique persona found
        seen.add(key)
        count += 1
        filename = os.path.join(args.out_dir, f"persona_{count}.json")
        with open(filename, "w") as f:
            json.dump(persona_data, f, indent=2)
        print(f"Generated {filename}")

if __name__ == "__main__":
    main()