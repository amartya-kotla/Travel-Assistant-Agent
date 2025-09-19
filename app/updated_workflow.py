from langgraph.graph import StateGraph, END
from typing import List, Optional
from langchain_core.prompts import ChatPromptTemplate
from .utils import llm, extract_json_from_response
from .transport import invoke_transportation
from .activities import invoke_activities
from .summary import invoke_summary
from pydantic import BaseModel

# Defining the Agent State, to maintain Chat History and transport, activity tips

class AgentState(BaseModel):
    chat_history: List[str]
    origin: Optional[str] = None
    destination: Optional[str] = None
    transportation: Optional[str] = None
    activities: Optional[str] = None
    # summary: Optional[str] = None


# In case model has not found the Origin and Destination Locations
def ask_for_locations(state: AgentState):
    # This function just returns a message to the user.
    state.chat_history.append("Please provide your origin and destination. For example, 'I want to travel from New York to London'.")
    # u_i = input("\nHuman: \n")
    # state.chat_history.append(u_i)
    return {"chat_history": state.chat_history} 


# Agent to get the Locations from user input
def get_location(state: AgentState):

    # Use the latest message from chat_history as the prompt to extract locations.
    user_prompt = state.chat_history[-1]
    
    # print(state.chat_history)

    START_PROMPT = """
    You are a simple LLM agent whose task is to identify the Origin Location and the Destination Location
    from the prompt of a user inquiring about travel between these locations.

    Once identified, write the locations down in this JSON format:

    ```
        {{
            "origin" : "<Origin Location>",
            "destination" : "<Destination Location>",
            "nothing" : "true"
        }}
    ```
    If origin or location was not identified you can completely ignore that corresponding field in the JSON format output. The dummy field must always be true.
"""
#     HUMAN_PROMPT = """
#     I want to travel to Japan from Bangalore.
# """
    prompt = ChatPromptTemplate.from_messages(
        [("system", START_PROMPT),
         ("human", user_prompt)]
    )

    response = llm.invoke(prompt.invoke({}))
    result = extract_json_from_response(response.content)
    
    return {"origin" : result.get("origin"), "destination" : result.get("destination")}


# Function called in conditional edges in the state graph, to decide which state to go to next
def get_next(state: AgentState) -> str:
    if state.origin is None or state.destination is None:
        return "Prompt User"
    
    if not state.transportation:
        return "Transport"

    if not state.activities:
        return "Activity"
    
    return "Summary"
    

#Invokes the transportation agent
def get_transport_details(state: AgentState):
    content = invoke_transportation(state.origin, state.destination)
    return {"transportation" : content}

#Invokes the activities agent
def get_activities_details(state: AgentState):
    content = invoke_activities(state.destination)
    return {"activities" : content}

#Invokes the summary agent
def get_summary(state: AgentState):
    content = invoke_summary(state)
    state.chat_history.append(content)
    return {"chat_history" : state.chat_history}


#Workflow Definition
graph = StateGraph(AgentState)

# graph.add_node("Start", start)

# Initializing state
graph.add_node("Location", get_location)

graph.add_node("Prompt User", ask_for_locations)

# Travel Agent
graph.add_node("Transport", get_transport_details)

# Activity Agent
graph.add_node("Activity", get_activities_details)

# Summarizer
graph.add_node("Summary", get_summary)

graph.set_entry_point("Location")

graph.add_conditional_edges(
    "Location",
    get_next,
    {
        "Transport" : "Transport",
        "Prompt User" : "Prompt User",
    }
)

graph.add_conditional_edges(
    "Transport",
    get_next,
    {
        "Activity" :"Activity",
        "Summary" : "Summary"
    }
)

graph.add_conditional_edges(
    "Activity",
    get_next,
    {
        "Summary" : "Summary"
    }
)

graph.add_edge("Prompt User", END)

graph.add_edge("Summary" , END)

workflow = graph.compile()


# -----Test Scenarios, uncomment to try them-------

# # Create an empty state to start the conversation
# initial_state = AgentState(chat_history=[''])
# inputs = initial_state

# # --- Scenario 1: User provides locations upfront ---
# print("--- Scenario 1: User provides locations upfront ---")
# user_input_1 = "I want to travel from Bangalore to Japan."
# inputs["chat_history"].append(f"human: {user_input_1}")

# # Run the workflow
# result_1 = workflow.invoke(inputs)
# pprint.pprint(result_1, indent=2)

# print("\n" + "="*50 + "\n")

# --- Scenario 2: User doesn't provide locations initially ---
# print("--- Scenario 2: User doesn't provide locations initially ---")
# user_input_2_part1 = "I want to travel"
# inputs_2 = AgentState(chat_history=[f"human: {user_input_2_part1}"])

# # Run the first step. This should trigger the 'Ask_Location' node.
# first_run_output = workflow.invoke(inputs_2)
# # pprint.pprint(first_run_output, indent=2)
# print(first_run_output)

# print("\n--- User's turn to provide more info ---")
# user_input_2_part2 = "My origin is Bangalore."
# # Update the state with the new user input
# first_run_output.chat_history.append(f"human: {user_input_2_part2}")

# # Run the workflow again with the updated state
# second_run_output = workflow.invoke(first_run_output)
# pprint.pprint(second_run_output, indent=2)


