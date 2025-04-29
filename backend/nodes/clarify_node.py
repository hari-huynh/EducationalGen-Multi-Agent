from langchain_core.messages import HumanMessage, SystemMessage
from db.mongo_saver import saveMessage
from agents.ClarifyAgent import create_clarify_agent
from models import *

def clarify_agent_node(state: State):
    print("__________Clarify__________")
    deps = Objective(
        user_query=state.get("user_query"),
        subject="",
        level="",
        target_audience="",
        entire_course=False,
        chapters=[]
    )
    clarify_agent=create_clarify_agent()
    result = clarify_agent.run_sync("", deps=deps)
    saveMessage(result, 'clarify_agent_node')
    
    state["objective"] = result.data
    state["next_step"] = "curriculum_gen_agent"
    return state
