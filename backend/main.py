from models import *
from langgraph.graph import StateGraph, START, END
from nodes.clarify_node import clarify_agent_node
from nodes.curriculum_node import curriculum_gen_agent_node
from nodes.supervisor_node import supervisor_agent_node
from nodes.collect_data_node import collect_data_agent_node
from nodes.lecture_node import lecture_note_gen_node
from nodes.quiz_node import QuizzNode
from nodes.slide_node import slideNode
from nodes.evaluate_node import evaluation_agent_node
import nest_asyncio
nest_asyncio.apply()


def conditional_edges(state: State):
    return state.get("next_step")


graph_builder = StateGraph(State)

graph_builder.add_node("clarify_agent", clarify_agent_node)
graph_builder.add_node("curriculum_gen_agent", curriculum_gen_agent_node)
graph_builder.add_node("supervisor_agent", supervisor_agent_node)
graph_builder.add_node("collect_data_agent", collect_data_agent_node)
graph_builder.add_node("lecture_note_gen_agent", lecture_note_gen_node)
graph_builder.add_node("quiz_gen_agent", QuizzNode)
graph_builder.add_node("slide_gen_agent", slideNode)
graph_builder.add_node("evaluation_agent", evaluation_agent_node)

graph_builder.add_edge(START, "clarify_agent")
graph_builder.add_edge("clarify_agent", "curriculum_gen_agent")
graph_builder.add_edge("curriculum_gen_agent", "supervisor_agent")

graph_builder.add_conditional_edges(
    "supervisor_agent",
    conditional_edges,
    {
        "collect_data_agent": "collect_data_agent",
        "lecture_note_gen_agent": "lecture_note_gen_agent",
        "quiz_gen_agent": "quiz_gen_agent",
        "slide_gen_agent": "slide_gen_agent",
        "evaluation_agent": "evaluation_agent",
        "end": END
    }
)

graph_builder.add_edge("collect_data_agent", "supervisor_agent")
graph_builder.add_edge("lecture_note_gen_agent", "supervisor_agent")
graph_builder.add_edge("quiz_gen_agent", "supervisor_agent")
graph_builder.add_edge("slide_gen_agent", "supervisor_agent")
graph_builder.add_edge("evaluation_agent", "supervisor_agent")


graph = graph_builder.compile()


results=graph.invoke({
    "user_query": "Can you help me create a learning material for Introduction to Artificial Intelligence course",
    "results": {},
    "todo_list": {},
    "modules_result": {}
    },
    config={"recursion_limit": 100} )