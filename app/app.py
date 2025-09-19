
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .updated_workflow import AgentState, workflow


app = FastAPI()

# initial_state = AgentState(chat_history = ["System: Hi, I am a Travel Assistant Agent!. Please tell me where you want to travel to?", "Hiiiiiiiiiiii", "suupppppppppp", "bazinga"])

#Setting the initial state of the message
initial_state = AgentState(chat_history = ["System: Hi, I am a Travel Assistant Agent!. Please tell me where you want to travel to?"])

templates = Jinja2Templates(directory="app/templates")

#Serving the home page with Jinja
@app.get("/", response_class= HTMLResponse)
async def home(request: Request):

    # need a json state to parse in the HTML Jinja template
    json_state = initial_state.model_dump_json()
    # print(json_state)
    return templates.TemplateResponse(name="index.html", context={"request" : request, "state": initial_state, "json_state" : json_state})

@app.post("/")
async def param(request: Request):
    form_data = await request.form()
    user_prompt = form_data.get("user_prompt")
    form_state = form_data.get("state")
    # print(user_prompt)
    # print(current_state)
    # current_state = json.loads(current_state)
    current_state = AgentState.model_validate_json(form_state)
    current_state.chat_history.append(user_prompt)

    updated_state = workflow.invoke(current_state)
    updated_state = AgentState.model_validate(updated_state)

    json_state = updated_state.model_dump_json()
    return templates.TemplateResponse(name="index.html", context={"request" : request, "state" : updated_state, "json_state" : json_state})


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)