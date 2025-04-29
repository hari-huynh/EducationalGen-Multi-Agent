from db.mongo_saver import saveMessage
from agents.Curriculum import create_curriculum_gen_agent
from models import *

def curriculum_gen_agent_node(state: State):
    table_content=""
    deps = CurriculumDeps(
        objective=state.get("objective"),
        table_content=table_content
    )
    curriculum_gen_agent=create_curriculum_gen_agent()
    result = curriculum_gen_agent.run_sync("", deps=deps)
    saveMessage(result, 'curriculum_gen_agent_node')
    state["results"]["curriculum"] = result.data
    state["next_step"] = "supervisor_agent"
    return state
