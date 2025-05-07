from fastapi import FastAPI, Response, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json, uvicorn
from asyncio import sleep
from pydantic import BaseModel, Field, ConfigDict
from agents import clarify_agent
from multiagent import graph
import time
from fastapi import WebSocket
from fastapi.responses import HTMLResponse
import os
from pydantic_ai import Agent, RunContext
from agents.pydantic_models.clarify import Objective
from agents.pydantic_models.state_graph import State
from agents.pydantic_models.curriculum import CurriculumDeps, CurriculumResult
from agents.pydantic_models.supervisor import SupervisorDeps
from agents.pydantic_models.collect_data import CollectDataDeps
from agents.pydantic_models.lecture_note import LectureNoteDeps
from agents.pydantic_models.presentation import Content
from agents.pydantic_models.quiz import QuizInput
from agents.pydantic_models.evaluator import EvaluationInput

from agents.curriculum_gen import table_content, curriculum_gen_agent
from agents.supervisor import supervisor_agent
from agents.collect_data import collect_data_agent
from agents.lecture_note_gen import lecture_note_gen_agent
from agents.quiz_gen import quiz_gen_agent
from agents.presentation_gen import presentation_gen_agent
from agents.evaluator import evaluator_agent

from typing import List, Literal, Dict
from langgraph.graph import StateGraph, START, END
import json
from datetime import datetime


os.environ["GEMINI_API_KEY"] = "AIzaSyD_fOfuu7stUwMxCSkUtQvgMpaPbWyt51c"

class Objective(BaseModel):
    user_query: str
    subject: str
    level: str
    target_audience: str
    entire_course: bool
    chapters: List[str]
    thinking: List[str] = Field(description="Thinking steps of agent")
    websocket: WebSocket

    model_config = ConfigDict(arbitrary_types_allowed=True)

clarify_agent = Agent(
    'google-gla:gemini-2.0-flash',
    deps_type=Objective,
    result_type = str
)

@clarify_agent.system_prompt
def system_prompt(ctx: RunContext) -> str:
     return f"""
        You are in charge of understanding the user query and extracting information from: "{ctx.deps.user_query}".
        Given the current course objective details:
        - Subject: {ctx.deps.subject}
        - Level: {ctx.deps.level}
        - Target Audience: {ctx.deps.target_audience}
        - Entire Course: {ctx.deps.entire_course}
        - Chapters (if applicable): {ctx.deps.chapters}

        Your goal is to identify any missing or unclear information required to fully understand the user's intent.
        If you are unsure about any aspect of the objective based on the initial user query, use the 'get_user_query' tool to ask the user for a clear and concise clarification question.

        Focus on asking ONE specific question at a time to avoid overwhelming the user.
        Make sure the question directly addresses the ambiguity or missing detail.
        Avoid vague or open-ended questions. Be precise about what information you need.
        Do not assume information. Always ask for clarification if there's any doubt.
        Return user's objective clear and concise.
        """
        

@clarify_agent.tool
async def get_user_query(ctx: RunContext, question: str) -> str:
    websocket = ctx.deps.websocket

    await websocket.send_json(
        {
            "role": "agent",
            "content": question,
            "timestamp": str(datetime.now())
        }
    )

    data = await websocket.receive_text()
    answer = json.loads(data)

    return f"User answer: {answer['content']}"


async def clarify_agent_node(state: State):
    deps = Objective(
      user_query = state.get("user_query"),
      subject = "",
      level = "",
      target_audience = "",
      entire_course = False,
      chapters = [],
      thinking = [],
      websocket = state.get("websocket")
    )

    result = await clarify_agent.run(
        "", deps=deps,
        model_settings={'temperature': 0.0}
    )

    print(result)

    state["objective"] = result.data
    state["next_step"] = "curriculum_gen_agent"
    return state


async def curriculum_gen_agent_node(state: State):
    deps = CurriculumDeps(
        objective = state.get("objective"),
        table_content = table_content
    )

    result = await curriculum_gen_agent.run("", deps=deps)
    
    curriculum = {
        "title": result.data.title,
        "overview": result.data.overview,
        "modules": [
            {
                "title": module.title,
                "content": module.content
            } 
            for module in result.data.modules]
    }

    state["results"]["curriculum"] = curriculum
    state["next_step"] = "supervisor_agent"
    return state

async def supervisor_agent_node(state: State):
    deps = SupervisorDeps(
        curriculum = state.get("results").get("curriculum"),
        todo_list = state.get("todo_list")
    )

    result = await supervisor_agent.run("", deps=deps)
    print(result.data)

    next_action = result.data.next_action
    state["next_action"] = next_action

    # Convert todo_list from list to dictionary
    if not state.get("todo_list"):
        state["todo_list"] = {}
        for task in result.data.todo_list.tasks:
            task_dict = {
                "task_id": task.task_id,
                "description": task.description,
                "status": task.status
            }

            state["todo_list"][str(task.task_id)] = task_dict

    print(state.get("todo_list"))
    state["next_step"] = next_action.agent
    state["todo_list"][str(next_action.task_id)]["status"] = "done"

    return state

async def collect_data_agent_node(state: State):
    deps = CollectDataDeps(
        task = state["next_action"]
    )

    result = await collect_data_agent.run("", deps=deps)
    print(result.data)
    ws = state.get("websocket")
    await ws.send_json({
                "role": "agent",
                "content": result.data,
                "timestamp": str(datetime.now())
            })

    state["results"]["data"] = result.data

    return state

async def lecture_note_gen_node(state: State):
    task = state["next_action"]

    deps = LectureNoteDeps(
        task = task,
        data = state.get("results").get("data")
    )

    result = await lecture_note_gen_agent.run("", deps=deps)
    print(result.data, "\n\n\n")

    ws = state.get("websocket")
    await ws.send_json({
                "role": "agent",
                "content": result.data,
                "timestamp": str(datetime.now())
            })


    state["lecture_notes"][task.task_id] = result.data
    return state

async def quiz_gen_node(state: State):
    print("_____QUIZZ_________")
    dep = QuizInput(
        data = state.get("results").get("data")
    )

    result = await quiz_gen_agent.run(" ", deps=dep)

    # saveMessage(result,'QuizzNode')
    state['results']["quiz"] = result.data
    print("QUIZ: ")
    print(result.data)


    next_action = state["next_action"]
    # key = state["todo_list"][str(next_action.task_id)].module_id
    
    # if key not in state['modules_result']:
    #   state['modules_result'][key] = []
    # state['modules_result'][key].append({
    #     'quiz': result.output
    #       })
    return state


async def presentation_gen_node(state: State):
    print("_____SLIDE_________")
    dep = Content(
        title = state.get("user_query"),
        content = state.get('results').get('data'),
        images = [],
        language = "English"
    )

    result = await presentation_gen_agent.run(" ", deps=dep)
    # saveMessage(result,'slideNode')

    state['results']["slide"]=result.data
    print("SLIDE: ")
    print(result.data)

    next_action = state["next_action"]

    # key = state["todo_list"][next_action.task_id].module_id
    # if key not in state['modules_result']:
    #   state['modules_result'][key] = []
    # state['modules_result'][key].append({
    #     'slide': result.output
    #       })
    
    return state


async def evaluator_node(state: State):
    print("_____EVALUATION_________")
    dep = EvaluationInput(
        lecture_note = state.get('results').get('lecture_note'),
        quiz = state.get('results').get('quizz'),
        slide = state.get('results').get('slide')
    )

    result = await evaluator_agent.run(" ", deps=dep)
    # saveMessage(result,'evaluation_agent_node')
    print("EVALUATION: ")
    print(result.data)
    state['results']["evaluation"] = result.data

    next_action = state["next_action"]

    # key=state["todo_list"][next_action.task_id].module_id
    # if key not in state['modules_result']:
    #   state['modules_result'][key] = []
    # state['modules_result'][key].append({
    #     'evaluate': result.output
    #       })
    
    return state


graph_builder = StateGraph(State)

graph_builder.add_node("clarify_agent", clarify_agent_node)
graph_builder.add_node("curriculum_gen_agent", curriculum_gen_agent_node)
graph_builder.add_node("supervisor_agent", supervisor_agent_node)
graph_builder.add_node("collect_data_agent", collect_data_agent_node)
graph_builder.add_node("lecture_note_gen_agent", lecture_note_gen_node)
graph_builder.add_node("quiz_gen_agent", quiz_gen_node)
graph_builder.add_node("presentation_gen_agent", presentation_gen_node)
graph_builder.add_node("evaluator_agent", evaluator_node)


graph_builder.add_edge(START, "clarify_agent")
graph_builder.add_edge("clarify_agent", "curriculum_gen_agent")
graph_builder.add_edge("curriculum_gen_agent", "supervisor_agent")


def conditional_edges(state: State):
    return state.get("next_step")

graph_builder.add_conditional_edges(
    "supervisor_agent",
    conditional_edges,
    {
        "collect_data_agent": "collect_data_agent",
        "lecture_note_gen_agent": "lecture_note_gen_agent",
        "presentation_gen_agent": "presentation_gen_agent",
        "evaluator_agent": "evaluator_agent",
        "quiz_gen_agent": "quiz_gen_agent",
        "end": END
    }
)

graph_builder.add_edge("collect_data_agent", "supervisor_agent")
graph_builder.add_edge("lecture_note_gen_agent", "supervisor_agent")
graph_builder.add_edge("presentation_gen_agent", "supervisor_agent")
graph_builder.add_edge("quiz_gen_agent", "supervisor_agent")
graph_builder.add_edge("evaluator_agent", "supervisor_agent")


graph = graph_builder.compile()



app = FastAPI(
    # docs_url='/api/py/docs', 
    # openapi_url='/api/py/openapi.json'
)

@app.get("/")
async def get():
    return HTMLResponse(html)

user_query = "Can you help me create Introduction to AI course"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept() 
    
    data = await websocket.receive_text()
    user_query = json.loads(data)
    
    init_state = {
        "user_query": user_query["content"],
        "websocket": websocket, 
        "results": {},
        "todo_list": {},
        "lecture_notes": {}
    }

    async for chunk in graph.astream(init_state, stream_mode="values"):
        current_state = dict(chunk)
        del current_state["websocket"]


        # if current_state.get("todo_list"): 
        #     await websocket.send_json({
        #         "role": "agent",
        #         "content": str(current_state["todo_list"]),
        #         "timestamp": str(datetime.now())
        #     })
        # elif current_state["results"].get("curriculum"):
        #     await websocket.send_json({
        #         "role": "agent",
        #         "content": current_state["results"]["curriculum"],
        #         "timestamp": str(datetime.now())
        #     })
        # else:
        await websocket.send_json({
            "role": "agent",
            "content": f"{str(current_state)}",                
            "timestamp": str(datetime.now())
        })

        # notes = [{
        #     "task_id": i,
        #     "content": note
        # } for i, note in enumerate(current_state.get("lecture_notes").values())]

        send_data = {
            "todoList": list(current_state.get("todo_list").values()),
            "curriculum": current_state.get("results").get("curriculum"),
            "lectureNotes": list(current_state.get("lecture_notes").values())
        }

        await websocket.send_json(send_data)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# async def waypoints_generator():
#     with open("sample.txt", "r") as file:
#         content = file.read()
    
#         # Split the content into tokens
#         tokens = [{"data": token} for token in content.split()]

#     for token in tokens:
#         data = json.dumps(token)
#         yield f"event: streamToken\ndata: {data}\n\n"
#         await sleep(0.1)

# @app.get("/api/py/chat")
# async def root():
#     return StreamingResponse(waypoints_generator(), media_type="text/event-stream")

class InputData(BaseModel):
    inputValue: str


@app.post("/api/get_user_query")
def get_user_query(data: InputData):    
    received_value = data.inputValue
    result = f"FastAPI backend received: {received_value}"
    return {"result": result}

@app.post("/api/run_multiagent")
def run_multiagent(data: InputData):
    user_query = data.inputValue

    init_state = {
        "user_query": user_query
    }

    for chunk in graph.stream(init_state, stream_mode="values"):
        print(chunk)
        time.sleep(1)
    

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

# Can you help me make learning material for "Introduction to AI" course at begin level for university student. I want to make a complete course