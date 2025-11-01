import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from ..models.azure_openai_models import get_azure_openai_model
from ..tools.tools import find_bike_rentals
from ..prompts.system_prompt import agent_system_prompt

load_dotenv()

MODEL = os.getenv("MODEL", "gpt-4o-mini")

model = get_azure_openai_model(MODEL)
system_prompt = agent_system_prompt()

agent = create_agent(model, tools=[find_bike_rentals], system_prompt=system_prompt)

result = agent.invoke({"messages": [{"role": "user", "content": "I need a bike store in Gracia, Barcelona."}]})

print(f"Agent Response: {result['messages']}")
