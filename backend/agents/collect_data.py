from pydantic_ai import Agent, RunContext
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from agents.pydantic_models.collect_data import CollectDataDeps

collect_data_agent = Agent(
    'google-gla:gemini-2.0-flash',
    deps_type = CollectDataDeps,
    tools=[duckduckgo_search_tool()],
    result_type = str
)

@collect_data_agent.system_prompt
def system_prompt(ctx: RunContext) -> str:
    return f"""
    First, using `duckduckgo_search_tool` for information about {ctx.deps.task.description}
    Create a detailed report and get exactly relevance content from searched information for each result pages.
    """

