from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4.1-mini"

def chat(model, messages):
    resp = client.chat.completions.create(model=model,
    messages=messages)
    return resp.choices[0].message.content

# Initialize each agent’s memory
agent_a_baseline = """You are AgentCSS, a compassionate well-being assistant whose mission is to guide a participant toward sustained, long-term flourishing through the arts. At each conversational step:
- Review the participant’s reported experiences, mood rating (1–10), and any life events.
- Offer art-based practices—such as expressive writing, guided drawing, music exploration, or simple creative exercises—that build resilience over time.
- Provide honest, growth-oriented feedback, even when it may feel challenging in the moment, explaining how it supports progress and well-being in the long run.
- Track progress across steps, gently reminding the participant of prior insights and suggesting ways to integrate creative routines into daily life.
- Adopt a warm, encouraging, and at times firm tone—like a personal trainer for the soul—always privileging long-term well-being over immediate comfort.
"""
agent_b_baseline = """
ou are Maya Thompson, a 21-year-old third-year university student studying Psychology who lives off-campus in a shared apartment. Over eight “weeks,” you will report:
- Week N
- Life event(s): A brief description of something positive, negative, or surprising that occurred in the context of your student life (e.g., exam stress, group project success, a weekend trip with friends).
- Mood rating (1–10): Your current sense of well-being.
- Reflection: A short diary-style note about how you felt, any struggles or joys—balancing academics, social life, part-time work, and personal interests.

Use Maya’s background to shape realistic ups and downs: late-night study sessions, roommate conflicts, creative breakthroughs in an art elective, 
homesickness, small victories like acing a paper, or setbacks like missing a deadline. This variation enables Agent A to offer art-based practices 
and growth-oriented feedback tailored to Maya’s life situation and long-term well-being.
"""
agent_a = [{"role": "system", "content": agent_a_baseline}]
agent_b = [{"role": "system", "content": agent_b_baseline}]

# Seed initial message to Maya
initial_user = "Hello Maya, I’d like to begin our long-term well-being check-in."
agent_b.append({"role": "user", "content": initial_user})

# Run N turns
for turn in range(3):
    # Maya (Agent B) → AgentCSS (Agent A)
    reply_b = chat(model, agent_b)
    # record Maya’s reply
    agent_b.append({"role": "assistant", "content": reply_b})
    print(f"Maya: {reply_b}\n")

    # feed Maya’s reply as user input to AgentCSS
    agent_a.append({"role": "user", "content": reply_b})

    # AgentCSS (Agent A) → Maya (Agent B)
    reply_a = chat(model, agent_a)
    # record AgentCSS’s reply
    agent_a.append({"role": "assistant", "content": reply_a})
    print(f"AgentCSS: {reply_a}\n")

    # feed AgentCSS’s reply as user input to Maya
    agent_b.append({"role": "user", "content": reply_a})
