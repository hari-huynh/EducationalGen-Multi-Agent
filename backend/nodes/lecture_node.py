from db.mongo_saver import saveMessage
from agents.LectureNote import create_lecture_note_gen_agent
from models import *

def lecture_note_gen_node(state: State):
    deps = LectureNoteDeps(
        task = state["next_action"],
        data = state.get("results").get("data")
    )
    lecture_note_gent_agent=create_lecture_note_gen_agent()
    result = lecture_note_gent_agent.run_sync("", deps=deps)
    saveMessage(result,'lecture_note_gen_node')


    print("[NOTE]: " +result.data, "\n\n\n")
    state['results']["lecture_note"]=result.data


    next_action = state["next_action"]
    key=state["todo_list"][next_action.task_id].module_id
    if key not in state['modules_result']:
      state['modules_result'][key] = []
    state['modules_result'][key].append({
        'lecture_note': result.data
          })


    return state