from pydantic_ai import Agent, RunContext
from models import Objective,ClarifyDeps,ClarifyResult

def create_clarify_agent() -> Agent:
    clarify_agent = Agent(
        'google-gla:gemini-2.0-flash',
        deps_type=Objective,
        result_type=str
    )

    @clarify_agent.system_prompt
    def system_prompt(ctx: RunContext) -> str:
        return f"""
        You are in charge of understanding user query and extract information from {ctx.deps.user_query}
        Given the course objective: {ctx.deps}
        If not sure, use 'get_user_query' tool to ask for clarification information for course objective.
        Make sure question is clear and concise.
        """

    @clarify_agent.tool
    def get_user_query(ctx: RunContext, question: str) -> str:
        answer = input(question)
        return f"User answer: {answer}"

    return clarify_agent


if __name__== '__main__':
    deps = Objective(
        user_query="Can you help me create a learning material for Introduction to Artificial Intelligence course",
        subject="",
        level="",
        target_audience="",
        entire_course=False,
        chapters=[]
    )
    clarify_agent=create_clarify_agent()
    result = clarify_agent.run_sync("", deps=deps)
    print(result)
    print(result.output)