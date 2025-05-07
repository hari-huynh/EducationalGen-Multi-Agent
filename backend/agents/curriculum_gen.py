from pydantic_ai import Agent, RunContext
from .pydantic_models.curriculum import CurriculumDeps, CurriculumResult
import os

os.environ["GEMINI_API_KEY"] = "AIzaSyD_fOfuu7stUwMxCSkUtQvgMpaPbWyt51c"

curriculum_gen_agent = Agent(
    'google-gla:gemini-2.0-flash',
    deps_type=CurriculumDeps,
    result_type = CurriculumResult
)

@curriculum_gen_agent.system_prompt
def system_prompt(ctx: RunContext) -> str:
    return f"""
    Base on course objective {ctx.deps.objective} and table of content of book: {ctx.deps.table_content}.
    Select the appropriate content from this to create a detailed curriculum for the course.
    Only return the curriculum.
    """

table_content = """
I ArtificialIntelligence
    1 Introduction 19
    1.1 WhatIsAI? . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19
    1.2 TheFoundationsofArtificialIntelligence. . . . . . . . . . . . . . . . . . 23
    1.3 TheHistoryofArtificialIntelligence . . . . . . . . . . . . . . . . . . . . 35
    1.4 TheStateoftheArt . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 45
    1.5 RisksandBenefitsofAI . . . . . . . . . . . . . . . . . . . . . . . . . . . 49
    Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 52
    BibliographicalandHistoricalNotes . . . . . . . . . . . . . . . . . . . . . . . . 53
    2 IntelligentAgents 54
    2.1 AgentsandEnvironments . . . . . . . . . . . . . . . . . . . . . . . . . . 54
    2.2 GoodBehavior:TheConceptofRationality . . . . . . . . . . . . . . . . 57
    2.3 TheNatureofEnvironments. . . . . . . . . . . . . . . . . . . . . . . . . 60
    2.4 TheStructureofAgents . . . . . . . . . . . . . . . . . . . . . . . . . . . 65
    Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 78
    BibliographicalandHistoricalNotes . . . . . . . . . . . . . . . . . . . . . . . . 78
""" 
