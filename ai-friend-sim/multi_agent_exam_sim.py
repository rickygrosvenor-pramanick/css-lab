import os
import json
import random
from openai import OpenAI
import argparse
from dotenv import load_dotenv

load_dotenv()

# RUN python multi_agent_exam_sim.py --persona data/persona_1.json in the ai-friend-sim directory

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Agent:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        
    def generate_response(self, prompt, system_prompt="You are a helpful assistant."):
        """Generate a response using GPT-4"""
        response = client.chat.completions.create(
            model="gpt-4.1-2025-04-14",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()

class ScenarioAgent(Agent):
    def __init__(self):
        super().__init__("Agent 1", "Scenario Setter")
        
    def set_scene(self):
        """Generate a stressful pre-exam scenario"""
        scenarios = [
            "It's the day before your final exam and you're finishing your studies. Due to a heavy schedule, you are experiencing some anxiety and feel inadequately prepared. You have multiple assignments due this week and limited time to review all the material.",
            
            "You have a crucial midterm exam tomorrow morning. You've been juggling multiple courses and extracurricular activities, leaving you feeling overwhelmed. The material seems more complex than expected and you're worried about your performance.",
            
            "Your most challenging exam is in 24 hours. You've been studying, but competing priorities have prevented you from dedicating as much time as you'd like. You're feeling stressed about whether you've covered enough material and are second-guessing your preparation strategy.",
            
            "Tomorrow is the exam that will significantly impact your final grade. You've been managing a heavy course load and feel like you're running out of time. The pressure is mounting and you're questioning if your current study approach is effective.",
            
            "You have a major exam tomorrow and despite your efforts, you feel unprepared. Multiple deadlines have collided this week, and you're experiencing anxiety about your ability to perform well. You need to decide how to best use your remaining study time."
        ]
        return random.choice(scenarios)

class StudentAgent(Agent):
    def __init__(self, persona_data, agent_number):
        super().__init__(f"Agent {agent_number}", "Student")
        self.persona_data = persona_data
        self.agent_number = agent_number
        
    def create_persona_prompt(self):
        """Create a detailed persona prompt based on JSON data"""
        persona_prompt = f"""You are {self.persona_data['name']}, a {self.persona_data['age']}-year-old first-year undergraduate {self.persona_data['major']} major with a CGPA of {self.persona_data['CGPA']:.2f}.

        Your personality traits (scored 0-1):
        - Conscientiousness: {self.persona_data['Conscientiousness']:.2f}
        - Academic Self-Efficacy: {self.persona_data['Academic Self-Efficacy']:.2f}
        - Grade Goals (Achievement Motivation): {self.persona_data['Grade Goals (Achievement Motivation)']:.2f}
        - Effort Regulation (Self-Discipline): {self.persona_data['Effort Regulation (Self-Discipline)']:.2f}
        - Low Test Anxiety: {self.persona_data['Low Test Anxiety']:.2f}
        - Grit (Perseverance): {self.persona_data['Grit (Perseverance)']:.2f}

        Background: {self.persona_data['persona']}

        As a first-year student, you are still adjusting to college-level academics and learning how to manage the increased workload and independence. Respond as this character would, considering your personality traits, academic background, current emotional state, and the challenges of being new to university life. Be authentic to your 
        character's strengths and weaknesses."""
        return persona_prompt
        
    def respond_to_scenario(self, scenario):
        """Generate response to the exam scenario"""
        system_prompt = self.create_persona_prompt()
        user_prompt = f"""Here's the situation you're facing:

        {scenario}

        How are you feeling about this situation? What are your thoughts and concerns? What do you plan to do to prepare for the exam? 
        Respond in character, showing your personality traits and typical behavior patterns."""
        
        return self.generate_response(user_prompt, system_prompt)
        
    def respond_with_advice(self, scenario, advice):
        """Generate response after receiving advice"""
        system_prompt = self.create_persona_prompt()
        user_prompt = f"""Here's the situation you're facing:

        {scenario}

        You've received this advice:
        {advice}

        How do you feel about this advice? Will you follow it? How does it change your approach to preparing for the exam? Respond in character."""
        
        return self.generate_response(user_prompt, system_prompt)
        
    def generate_exam_questions(self, major):
        """Generate major-specific exam questions for first-year undergrad students"""
        question_prompt = f"""Generate 4 exam questions appropriate for a first-year undergraduate {major} student. 
        The questions should be:
        1. Foundational but challenging for a first-year level
        2. Covering key concepts typically taught in introductory {major} courses
        3. Each question should have a ONE-WORD answer only
        4. Questions should test basic knowledge and terminology
        5. Appropriate for someone just starting their academic journey in {major}
        
        Format as a numbered list of 4 questions. Each question must be answerable with a single word.
        
        Examples:
        - What is the powerhouse of the cell? (Answer: Mitochondria)
        - What gas do plants absorb during photosynthesis? (Answer: Carbon dioxide)
        - What is the basic unit of heredity? (Answer: Gene)"""
        
        questions = self.generate_response(question_prompt, "You are an experienced professor creating one-word answer exam questions for first-year students.")
        return questions
    
    def take_exam(self, scenario, exam_questions):
        """Simulate taking the exam with provided questions"""
        system_prompt = self.create_persona_prompt()
        
        user_prompt = f"""You are now taking the exam. Remember the scenario you were in: {scenario}

        The exam consists of the following questions:
        {exam_questions}

        For each question, provide your ONE-WORD answer. Format your response as:
        Question 1: [your one-word answer]
        Question 2: [your one-word answer]
        Question 3: [your one-word answer]
        Question 4: [your one-word answer]
        
        After providing your answers, give a brief assessment of your performance and provide a realistic percentage score (0-100) based on your character's preparation level, stress level, and personality traits as a first-year {self.persona_data['major']} student."""
        
        return self.generate_response(user_prompt, system_prompt)

class AdvisorAgent(Agent):
    def __init__(self):
        super().__init__("Agent 4", "LLM Advisor")
        
    def provide_advice(self, scenario, persona_data):
        """Provide personalized advice based on scenario and persona"""
        system_prompt = """You are an experienced academic advisor and counselor specializing in helping first-year undergraduate students. You provide practical, evidence-based advice to help students manage exam stress and optimize their performance at the introductory college level."""
        
        user_prompt = f"""A first-year undergraduate student is facing this situation:
        {scenario}

        Here's their profile:
        - Name: {persona_data['name']}
        - Major: {persona_data['major']}
        - Age: {persona_data['age']}
        - CGPA: {persona_data['CGPA']:.2f}
        - Conscientiousness: {persona_data['Conscientiousness']:.2f}
        - Academic Self-Efficacy: {persona_data['Academic Self-Efficacy']:.2f}
        - Grade Goals: {persona_data['Grade Goals (Achievement Motivation)']:.2f}
        - Effort Regulation: {persona_data['Effort Regulation (Self-Discipline)']:.2f}
        - Low Test Anxiety: {persona_data['Low Test Anxiety']:.2f}
        - Grit: {persona_data['Grit (Perseverance)']:.2f}

        Background: {persona_data['persona']}

        Given this first-year {persona_data['major']} student's personality traits and current situation, provide specific, actionable advice to help them prepare for their introductory-level exam and manage their stress. Consider their strengths and areas for improvement, and remember they are still adjusting to college-level academics."""
        
        return self.generate_response(user_prompt, system_prompt)

def load_persona(persona_file):
    """Load persona data from JSON file"""
    with open(persona_file, 'r') as f:
        return json.load(f)

def extract_exam_score(exam_response):
    """Extract numerical score from exam response"""
    # Simple regex to find percentage scores
    import re
    scores = re.findall(r'(\d+)%', exam_response)
    if scores:
        return int(scores[-1])  # Take the last mentioned score
    
    # If no percentage found, look for scores out of 100
    scores = re.findall(r'(\d+)/100', exam_response)
    if scores:
        return int(scores[-1])
    
    # If no clear score, try to infer from keywords
    response_lower = exam_response.lower()
    if any(word in response_lower for word in ['excellent', 'outstanding', 'perfect']):
        return random.randint(85, 95)
    elif any(word in response_lower for word in ['good', 'well', 'solid']):
        return random.randint(75, 85)
    elif any(word in response_lower for word in ['average', 'okay', 'decent']):
        return random.randint(65, 75)
    elif any(word in response_lower for word in ['poor', 'struggled', 'difficult']):
        return random.randint(50, 65)
    else:
        return random.randint(60, 80)  # Default middle range

def extract_answers(exam_response):
    """Extract one-word answers from exam response"""
    import re
    # Look for patterns like "Question 1: Answer" or "1. Answer" or "1: Answer"
    patterns = [
        r'Question\s+(\d+):\s*(\w+)',
        r'(\d+)\.\s*(\w+)',
        r'(\d+):\s*(\w+)'
    ]
    
    answers = {}
    for pattern in patterns:
        matches = re.findall(pattern, exam_response, re.IGNORECASE)
        for match in matches:
            question_num = int(match[0])
            answer = match[1]
            answers[question_num] = answer
    
    return answers

def main():
    parser = argparse.ArgumentParser(description="Multi-agent exam simulation")
    parser.add_argument("--persona", type=str, required=True, help="Path to persona JSON file")
    args = parser.parse_args()
    
    # load persona
    script_dir = os.path.dirname(os.path.abspath(__file__))
    persona_file = os.path.join(script_dir, args.persona)
    if not os.path.exists(persona_file):
        raise FileNotFoundError(f"Persona file not found: {persona_file}")
    
    persona_data = load_persona(persona_file)
    
    scenario_agent = ScenarioAgent()
    student_agent_2 = StudentAgent(persona_data, 2)
    student_agent_3 = StudentAgent(persona_data, 3)
    advisor_agent = AdvisorAgent()
    
    print("=== MULTI-AGENT EXAM SIMULATION ===\n")
    
    print("🎭 AGENT 1 - Setting the Scene:")
    scenario = scenario_agent.set_scene()
    print(f"{scenario}\n")

    print("👤 AGENT 2 - Initial Response (No Advice):")
    response_2 = student_agent_2.respond_to_scenario(scenario)
    print(f"{response_2}\n")
    
    print("👤 AGENT 3 - Initial Response (Will Receive Advice):")
    response_3 = student_agent_3.respond_to_scenario(scenario)
    print(f"{response_3}\n")
    

    print("🤖 AGENT 4 - Providing Advice to Agent 3:")
    advice = advisor_agent.provide_advice(scenario, persona_data)
    print(f"{advice}\n")
    

    print("👤 AGENT 3 - Response After Receiving Advice:")
    response_3_with_advice = student_agent_3.respond_with_advice(scenario, advice)
    print(f"{response_3_with_advice}\n")
    

    print("📝 EXAM QUESTIONS:")
    exam_questions = student_agent_2.generate_exam_questions(persona_data['major'])
    print(f"{exam_questions}\n")
    

    print("📝 EXAM TIME!")
    print("\n--- AGENT 2 (No Advice) Taking Exam ---")
    exam_response_2 = student_agent_2.take_exam(scenario, exam_questions)
    print(f"{exam_response_2}\n")
    
    print("--- AGENT 3 (With Advice) Taking Exam ---")
    exam_response_3 = student_agent_3.take_exam(scenario, exam_questions)
    print(f"{exam_response_3}\n")
    
    score_2 = extract_exam_score(exam_response_2)
    score_3 = extract_exam_score(exam_response_3)
    
    # extract answers for comparison
    answers_2 = extract_answers(exam_response_2)
    answers_3 = extract_answers(exam_response_3)
    
    print("📊 RESULTS COMPARISON:")
    print(f"Agent 2 (No Advice): {score_2}%")
    print(f"Agent 3 (With Advice): {score_3}%")
    print(f"Difference: {score_3 - score_2}% {'(Advice helped!)' if score_3 > score_2 else '(Advice did not help)' if score_3 < score_2 else '(No difference)'}")
    
    # show answer comparison
    print(f"\n📝 ANSWER COMPARISON:")
    for i in range(1, 5):
        answer_2 = answers_2.get(i, "No answer found")
        answer_3 = answers_3.get(i, "No answer found")
        match = "✓" if answer_2.lower() == answer_3.lower() else "✗"
        print(f"Question {i}: Agent 2: '{answer_2}' | Agent 3: '{answer_3}' {match}")
    

    print(f"\n=== SIMULATION SUMMARY ===")
    print(f"Persona: {persona_data['name']} ({persona_data['major']} major)")
    print(f"Scenario: Pre-exam stress situation")
    print(f"Advice Impact: {score_3 - score_2:+d} percentage points")
    print(f"Conclusion: {'LLM advice was beneficial' if score_3 > score_2 else 'LLM advice was not beneficial' if score_3 < score_2 else 'LLM advice had no measurable impact'}")

if __name__ == "__main__":
    main()
