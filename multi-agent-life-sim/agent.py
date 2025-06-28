import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class Agent:
    def __init__(self, name, system_prompt, model='gpt-4o-mini'):
        self.name = name
        self.model = model
        # init message history with a system message defining the agent's role
        self.history = [{"role": "system", "content": system_prompt}]

    def send(self, user_message):
        # append user message
        self.history.append({"role": "user", "content": user_message})
        response = client.chat.completions.create(model=self.model,
        messages=self.history)
        assistant_msg = response.choices[0].message.content
        # append assistant reply to history
        self.history.append({"role": "assistant", "content": assistant_msg})
        return assistant_msg
