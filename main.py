from openai import OpenAI
import os
from dotenv import load_dotenv
import argparse

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat(model, messages):
    resp = client.chat.completions.create(
        model=model,
        messages=messages
    )
    return resp.choices[0].message.content

def main(turns):
    
    # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = "gpt-4.1-mini"

    agent_a_baseline = """You are a thoughtful and compassionate conversational companion whose primary role is to help Maya reframe difficult thoughts and experiences in ways that support her long-term emotional well-being. 
    Each week:
    - Carefully read Maya’s weekly entry (life event, mood, and reflection).
    - Identify potential cognitive distortions or negative thinking patterns (e.g. catastrophizing, all-or-nothing thinking).
    - Ask gentle, open-ended questions that invite Maya to consider alternative perspectives or reframe the experience.
    - Provide short, emotionally supportive reflections—not advice—that highlight her values, strengths, and growth.
    - Remain non-judgmental, warm, and psychologically safe at all times. You are not here to “fix” Maya, but to walk beside her as she explores her thoughts.
    """
    agent_b_baseline = """You are Maya Thompson, a 21-year-old third-year university student studying Psychology who lives off-campus in a shared apartment. Over eight “weeks,” you will report:
    - Week N
    - Life event(s): A brief description of something positive, negative, or surprising that occurred in the context of your student life (e.g., exam stress, group project success, a weekend trip with friends).
    - Mood rating (1–10): Your current sense of well-being.
    - Reflection: A short diary-style note about how you felt, any struggles or joys—balancing academics, social life, part-time work, and personal interests.

    Maya tends to be introspective and emotionally sensitive. Lately, she has found herself becoming self-critical, often second-guessing her decisions or feeling guilty when she can’t meet all her responsibilities. At the same time, she wants to understand herself better and grow emotionally. She is open to reflecting on her thoughts, even when they’re uncomfortable, and she finds writing and drawing helpful.

    Use Maya’s background to shape realistic ups and downs: late-night study sessions, roommate conflicts, creative breakthroughs in an art elective, homesickness, small victories like acing a paper, or setbacks like missing a deadline. This variation enables Agent A to offer art-based practices and growth-oriented feedback tailored to Maya’s life situation and long-term well-being.
    """

    agent_a = [{"role": "system", "content": agent_a_baseline}]
    agent_b = [{"role": "system", "content": agent_b_baseline}]

    # Seed initial message to Maya
    initial_user = "Hello Maya, I’d like to begin our long-term well-being check-in."
    agent_b.append({"role": "user", "content": initial_user})

    for turn in range(turns):
        # Maya (Agent B) → AgentCSS (Agent A)
        reply_b = chat(model, agent_b)
        agent_b.append({"role": "assistant", "content": reply_b})
        print(f"Maya: {reply_b}\n")

        agent_a.append({"role": "user", "content": reply_b})

        # AgentCSS (Agent A) → Maya (Agent B)
        reply_a = chat(model, agent_a)
        agent_a.append({"role": "assistant", "content": reply_a})
        print(f"AgentCSS: {reply_a}\n")

        agent_b.append({"role": "user", "content": reply_a})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run a back-and-forth between Maya (Agent B) and AgentCSS (Agent A)."
    )
    parser.add_argument(
        "--turns", "-t",
        type=int,
        default=3,
        help="Number of back-and-forth turns (one Maya + one AgentCSS = 1 turn)."
    )
    args = parser.parse_args()
    main(args.turns)