from db.mongo_saver import saveMessage
from agents.Evaluate import create_evaluation_agent
from models import *

def evaluation_agent_node(state: State):
    print("_____EVALUATION_________")
    dep=EvaluationInput(
        lecture_note=state.get('results').get('lecture_note'),
        quiz=state.get('results').get('quizz'),
        slide=state.get('results').get('slide')
    )
    evaluation_agent=create_evaluation_agent()
    result=evaluation_agent.run_sync(" ", deps=dep)
    saveMessage(result,'evaluation_agent_node')
    print("EVALUATION: ")
    print(result.data)
    state['results']["evaluation"]=result.data

    next_action = state["next_action"]
    key=state["todo_list"][next_action.task_id].module_id
    if key not in state['modules_result']:
      state['modules_result'][key] = []
    state['modules_result'][key].append({
        'evaluate': result.data
          })
    return state