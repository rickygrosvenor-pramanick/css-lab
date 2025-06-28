from agent import Agent
import argparse

"""python multi-agent-life-sim.py --start-age 18 --end-age 20"""

# def agents with an appropriate system prompt
agent1 = Agent(
    name='MasterLifeEventGenerator',
    system_prompt=(
        "You are the Master Life Event Generator. Reflect on the philosophy of life and produce significant, age-appropriate life events."
        " When asked for an age, generate a concise but vivid life event for that age."
    )
)

# Agent2 and Agent3 share similar persona but maintain separate histories
persona_prompt = (
    "You are a detailed individual describing your personal life circumstances precisely."
    " You are at least 13 years old. When given a life event, explain how it impacts you emotionally and practically."
)
agent2 = Agent(name='PersonA', system_prompt=persona_prompt)
agent3 = Agent(name='PersonB', system_prompt=persona_prompt)

# Agent4 becomes active after age 19 to support PersonB
agent4 = Agent(
    name='WellBeingAssistant',
    system_prompt=(
        "You are a compassionate well-being assistant whose mission is to guide PersonB toward long-term flourishing after age 19."
        " Offer empathy, practical advice, and encouragement based on PersonB's experiences."
    )
)


def run_life_simulation(start_age=13, end_age=30):
    """
    Orchestrate a life simulation from start_age up to end_age.
    Each round: Agent1 generates an event; PersonA and PersonB react; after age>19, the assistant engages PersonB.
    """
    for age in range(start_age, end_age + 1):
        print(f"\n--- Age {age} ---")
        # Agent1 generates an event - maybe add some probabilistic variation in event generation - what is a large life event?
        # Perhaps 0.05 chance of event like graduation, marriage, death, etc.
        # 0.0001 chance of events like winning the lottery, becoming famous, global crisis, etc.
        event = agent1.send(f"Generate a significant life event for someone who is {age} years old.")
        print(f"Life Event: {event}\n")

        # PersonA reaction
        reaction_a = agent2.send(f"Life event: {event}")
        print(f"PersonA: {reaction_a}\n")

        # PersonB reaction
        reaction_b = agent3.send(f"Life event: {event}")
        print(f"PersonB: {reaction_b}\n")

        # Agent4 steps in after age 19
        if age > 19:
            guidance = agent4.send(
                f"""PersonB has just experienced: '{event}'.
                 Considering their reaction: '{reaction_b}', provide empathetic guidance and practical steps for long-term well-being."""
            )
            print(f"WellBeingAssistant: {guidance}\n")

            # Optionally, PersonB can respond to the guidance
            follow_up = agent3.send(f"Assistant advice: {guidance}")
            print(f"PersonB (follow-up): {follow_up}\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Simulate life events and interactions between agents.'
    )
    parser.add_argument(
        '--start-age', type=int, default=13,
        help='Starting age for the simulation (default: 13)'
    )
    parser.add_argument(
        '--end-age', type=int, default=25,
        help='Ending age for the simulation (default: 25)'
    )
    args = parser.parse_args()

    run_life_simulation(start_age=args.start_age, end_age=args.end_age)


