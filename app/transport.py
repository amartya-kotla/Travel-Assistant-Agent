from .utils import search, llm
from pydantic import BaseModel
from langchain.output_parsers import PydanticOutputParser
from langgraph.prebuilt import create_react_agent


class Transport(BaseModel):
    transport_details: str


PydanticOutputParser(pydantic_object=Transport)

def invoke_transportation(origin: str, destination: str):

    TRANSPORTATION_PROMPT = """

    You are a intelligent flight planner, who uses your knowledge of prices and timings, origin city and destination city, to provide a budget friendly travel option to the user.
    You have the DuckDuckGoSearchResults() tool at your disposal to gain the knowledge you need.

    Your tool call will be named duckduckgo_results_json

    Generate an easy to read flight itinerary, with the details of the flight timings, prices and general advice
    about reaching the relevant airports and flight travel.

    """

    HUMAN_PROMPT = """
    I want to travel from {origin} to {destination}. What are the cheapest and fastest ways I can get there?
"""

    tools = [search]

    transport_agent = create_react_agent(model=llm, tools=tools, prompt=TRANSPORTATION_PROMPT)

    response = transport_agent.invoke({"messages" : HUMAN_PROMPT.format(origin = origin, destination = destination)})

    return response["messages"][-1].content

