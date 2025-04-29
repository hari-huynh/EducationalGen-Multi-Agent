from db.mongo_saver import saveMessage
from agents.Supervisor import create_supervisor_agent
from models import *
from typing import Dict

def check_and_update_next_action(state: dict) -> dict:
    todo_list: Dict[str, Task] = state.get("todo_list", {})
    next_action: RunTask = state.get("next_action")

    all_done = all(task.status == "done" for task in todo_list.values())

    if all_done:
        next_action.agent = "end"
        next_action.description = "All tasks completed. Ending the workflow."

        state["next_action"] = next_action
    print("Checked")

def supervisor_agent_node(state: State):
    
    deps = SupervisorDeps(
        curriculum=state.get("results").get("curriculum"),
        todo_list=state.get("todo_list")
    )

    supervisor_agent=create_supervisor_agent()
    result = supervisor_agent.run_sync("", deps=deps)
    saveMessage(result, 'supervisor_agent_node')
    # print(result.data)

    next_action = result.data.next_action
    state["next_action"] = next_action

    # Convert todo_list from list to dictionary
    if not state.get("todo_list"):
        state["todo_list"] = {}
        for task in result.data.todo_list.tasks:
            state["todo_list"][task.task_id] = task

    check_and_update_next_action(state)
    state["next_step"] = next_action.agent
    state["todo_list"][next_action.task_id].status = "done"

    return state
