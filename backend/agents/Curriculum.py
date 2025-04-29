from pydantic_ai import Agent, RunContext
from models import CurriculumDeps


def create_curriculum_gen_agent() -> Agent:
    curriculum_gen_agent = Agent(
        'google-gla:gemini-2.0-flash',
        deps_type=CurriculumDeps,
        result_type=str,
        model_settings={"temperature": 0.2}
    )

    @curriculum_gen_agent.system_prompt
    def system_prompt(ctx: RunContext) -> str:
        return f"""
        Base on course objective {ctx.deps.objective} and table of content of book: {ctx.deps.table_content}.
        Select the appropriate content from this to create a detailed curriculum for the course.
        Only return the curriculum in markdown format, do not include any other text.
        """

    return curriculum_gen_agent