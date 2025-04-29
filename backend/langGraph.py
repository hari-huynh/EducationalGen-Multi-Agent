from langgraph.graph import StateGraph
from typing import TypedDict
from langchain_groq import ChatGroq
import os
from langchain.prompts import ChatPromptTemplate
from tools import *

groq_api_key='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'
os.environ["GROQ_API_KEY"]=groq_api_key
llm=ChatGroq(groq_api_key=groq_api_key,model_name="Gemma2-9b-It")

supervisor_prompt = ChatPromptTemplate.from_template("""
You are an AI Controller supervising the generation of educational content.

Given the current STATE:
- Curriculum Generated: {curriculum}
- Lecture Notes Generated: {lecture_notes}
- Presentation Generated: {presentation}
- Quiz Generated: {quiz}
- Evaluation Result: {evaluation_result}

You must decide the next action to take, based on these rules:
- If the curriculum is missing, choose "generate_curriculum".
- If any of lecture notes, presentation, or quiz are missing, choose "generate_content".
- If all content is generated, but no evaluation yet, choose "evaluate".
- If evaluation failed, choose "redo_content".
- If evaluation succeeded, choose "done".

ONLY RESPOND with one of these exact actions:
- generate_curriculum
- generate_content
- evaluate
- redo_content
- done
""")

# 1. Định nghĩa State
class LearningState(TypedDict):
    user_query: str
    curriculum: str
    lecture_notes: str
    presentation: str
    quiz: str
    evaluation: str
    action: str

# 2. Các node (function placeholders)
def user_query_node(state):
    print("Nhận câu hỏi người dùng...")
    return {"user_query": "Tôi muốn học về Machine Learning"}

def supervisor_agent(state):
    """Supervisor Agent powered by LLM."""
    # Format prompt
    prompt = supervisor_prompt.format_messages(
        curriculum="Yes" if state.get("curriculum") else "No",
        lecture_notes="Yes" if state.get("lecture_notes") else "No",
        presentation="Yes" if state.get("presentation") else "No",
        quiz="Yes" if state.get("quiz") else "No",
        evaluation_result=state.get("evaluation_result", "Not evaluated yet"),
    )
    print(prompt)
    # Call LLM
    response = llm(prompt)
    print("OK")
    action = response.content.strip().lower()
    print(f"[Supervisor Decision]: {action}")
    # state['action']=action
    return {'action':action}
    # print("Supervisor Agent đang lập kế hoạch...")
    
    # return {"action": "generate_curriculum"}

def curriculum_gen_agent(state):
    print("Tạo curriculum...")
    question=state.get('user_query')
    
    # result1=retrieve(question)
    # result2=tavily_search(question)
    
    combined_context = question #result1.result + "\n\n" + result2.result
    curriculum_prompt_template = ChatPromptTemplate.from_template("""
                            You are a professional curriculum designer.
                            Using the following information:
                            {context}
                            Design a comprehensive curriculum

                            Please include:
                            - Main topics
                            - Subtopics if necessary
                            - Logical order
                            - Suggested duration for each part
                            - Important notes if needed

                            Format your answer clearly and organized.
                            """)
    
    prompt = curriculum_prompt_template.format_messages(
    context=combined_context    )
    response = llm.invoke(prompt)
    curriculum = response.content.strip()
    state["curriculum"] = curriculum
    return state

def lecture_note_gen_agent(state):
    print("Tạo lecture notes...")
    return {"lecture_notes": "Lecture Notes về Machine Learning"}

def presentation_gen_agent(state):
    print("Tạo presentation...")
    return {"presentation": "Slides về Machine Learning"}

def quiz_gen_agent(state):
    print("Tạo bộ quiz...")
    return {"quiz": "Quiz Machine Learning"}

def evaluation_agent(state):
    print("Đánh giá kết quả...")
    # Giả lập: nếu quiz chứa từ "Machine Learning" thì OK, ngược lại NOT_OK
    if "Machine Learning" in state.get("quiz", ""):
        return {"evaluation": "OK"}
    else:
        return {"evaluation": "NOT_OK"}
    
    

# 3. Hàm điều kiện Supervisor
def supervisor_decision(state):
    
    return state['action']

def after_curriculum_decision(state):
    return "supervisor_agent"

# 4. Hàm quyết định sau Evaluation
def evaluation_decision(state):
    if state.get("evaluation") == "OK":
        return "END"
    else:
        return "supervisor_agent"  

# 5. Tạo Graph
graph = StateGraph(LearningState)


## Add node
graph.add_node("user_query_node", user_query_node)
graph.add_node("supervisor_agent", supervisor_agent)
graph.add_node("curriculum_gen_agent", curriculum_gen_agent)
graph.add_node("lecture_note_gen_agent", lecture_note_gen_agent)
graph.add_node("presentation_gen_agent", presentation_gen_agent)
graph.add_node("quiz_gen_agent", quiz_gen_agent)
graph.add_node("evaluation_agent", evaluation_agent)

## Add Edge
graph.add_edge("user_query_node", "supervisor_agent")
graph.add_edge("supervisor_agent", "curriculum_gen_agent")
graph.add_conditional_edges("supervisor_agent", supervisor_decision)
graph.add_conditional_edges("curriculum_gen_agent", after_curriculum_decision)
graph.add_edge('supervisor_agent','lecture_note_gen_agent')
graph.add_edge('supervisor_agent','presentation_gen_agent')
graph.add_edge('supervisor_agent','quiz_gen_agent')




graph.add_edge("lecture_note_gen_agent", "evaluation_agent")
graph.add_edge("presentation_gen_agent", "evaluation_agent")
graph.add_edge("quiz_gen_agent", "evaluation_agent")


graph.add_conditional_edges("evaluation_agent", evaluation_decision)


## Run
graph.set_entry_point("user_query_node")

runnable = graph.compile()
# result = runnable.invoke({})
# print(result)
