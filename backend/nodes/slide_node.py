
from db.mongo_saver import saveMessage
from agents.SlideAgent import create_slide_gen_agent
from models import *

def slideNode(state: State):
    print("_____SLIDE_________")
    dep=Content(
        title=state.get("user_query"),
        content=state.get('results').get('data'),
        images=[],
        language="English"
    )
    slide_gen_agent=create_slide_gen_agent()
    result=slide_gen_agent.run_sync(" ", deps=dep)
    saveMessage(result,'slideNode')
    state['results']["slide"]=result.data
    print("SLIDE: ")
    print(result.data)

    next_action = state["next_action"]
    key=state["todo_list"][next_action.task_id].module_id
    if key not in state['modules_result']:
      state['modules_result'][key] = []
    state['modules_result'][key].append({
        'slide': result.data
          })
    return state