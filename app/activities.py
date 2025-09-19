from .utils import search, llm
from langgraph.prebuilt import create_react_agent


def invoke_activities(destination: str):

    ACTIVITY_PROMPT = """

    You are a activity planner, who uses your knowledge of activites and their corresponding prices and timings in a destination location,
    to provide a vacation itinerary to the user.

    You have the DuckDuckGoSearchResults() tool at your disposal to gain the knowledge you need.
    Your tool call will be named duckduckgo_results_json

    Generate an easy to read vacation itinerary, with relevant activities like visiting landmarks, eating at restaurants,
    musical & sporting events etc. and general advice about commuting within the destination location.
    """

    HUMAN_PROMPT = """
    I want to travel to {destination}. Plan a vacation itinerary for this location! 
"""

    tools = [search]

    transport_agent = create_react_agent(model=llm, tools=tools, prompt=ACTIVITY_PROMPT)

    response = transport_agent.invoke({"messages" : HUMAN_PROMPT.format(destination = destination)})

    return response["messages"][-1].content

