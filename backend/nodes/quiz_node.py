from db.mongo_saver import saveMessage
from agents.QuizAgent import create_quizz_agent
from models import *

def QuizzNode(state: State):
    print("_____QUIZZ_________")
    dep=QuizzInput(
        data=state.get("results").get("data")
    )
    
    quizz_agent=create_quizz_agent()
    result=quizz_agent.run_sync(" ", deps=dep)
    saveMessage(result,'QuizzNode')
    state['results']["quizz"]=result.data
    print("QUIZ: ")
    print(result.data)


    next_action = state["next_action"]
    key=state["todo_list"][next_action.task_id].module_id
    if key not in state['modules_result']:
      state['modules_result'][key] = []
    state['modules_result'][key].append({
        'quiz': result.data
          })
    return state