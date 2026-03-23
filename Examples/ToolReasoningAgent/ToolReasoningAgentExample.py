import os
from laeyerz.agent.ToolReasoningAgent import ToolReasoningAgent


# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# api_key_path = os.environ.get("OPENAI_API_KEY_PATH", os.path.join(BASE_DIR, ".env"))
# print("api_key_path: ", api_key_path)

api_key_path = "../../.env"

agent = ToolReasoningAgent(
    name="AgentSimple", 
    api_key_path=api_key_path,
    model="gpt-5-mini", 
    role="You are a travel planner", 
    instructions = "Given the city and the request, use the tools to provide the best information to the user", 
    tools={}
    )



#--------Setting up Tools ----------------------------------
def get_weather(city):
    return f"The weather in {city} is sunny"

agent.add_tool({
    "name": "get_weather",
    "description": "Get the weather for a given city",
    "parameters": [
        {
            "name": "city",
            "type": "string",
            "description": "The city to get the weather for"
        }
    ],
    "function": get_weather
})


def get_traffic_status(city):
    return f"The traffic status in {city} is good"

agent.add_tool({
    "name": "get_traffic_status",
    "description": "Get the traffic status for a given city",
    "parameters": [
        {
            "name": "city",
            "type": "string",
            "description": "The city to get the traffic status for"
        }
    ],
    "function": get_traffic_status
})



#-------------- Run Agent ------------------------------

agent.run_agent("Tell me the weather in Tokyo")

