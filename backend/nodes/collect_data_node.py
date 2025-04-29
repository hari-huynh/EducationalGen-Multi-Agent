from db.mongo_saver import saveMessage
from models import *
from agents.CollectData import create_collect_data_agent
def collect_data_agent_node(state: State):
    deps = CollectDataDeps(
        task=state["next_action"]
    )
    collect_data_agent=create_collect_data_agent()
    result = collect_data_agent.run_sync("", deps=deps)
    saveMessage(result, 'collect_data_agent_node')

    print("_______Data Collect___________")
    print("[DATA COLLECT]: "+ result.data)

    state["results"]["data"] = result.data

    next_action = state["next_action"]
    key = state["todo_list"][next_action.task_id].module_id

    if key not in state['modules_result']:
        state['modules_result'][key] = []
    state['modules_result'][key].append({
        'data': result.data
    })
    return state
