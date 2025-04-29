from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai import Agent,RunContext
from pydantic_ai.providers.google_gla import GoogleGLAProvider
import os
from models import QuizzInput,OutputQuizz
from dotenv import load_dotenv



def create_quizz_agent() -> Agent:
    
    
    llm3 = GeminiModel(
    'gemini-2.0-flash',
    provider=GoogleGLAProvider(api_key=os.getenv('API_GEMINI_MODEL'))
    )
        
    quizz_agent = Agent(
        llm3,
        deps_type=QuizzInput,
        result_type=OutputQuizz,
    )

    @quizz_agent.system_prompt
    def system_prompt(context: RunContext) -> str:
        return f"""
        Based on the following information:
        - Information: {context.deps.data}

        Create multiple-choice questions ranging from basic to advanced levels suitable for university students.

        **DETAILED REQUIREMENTS:**

        1. **Number and Distribution of Questions:**
          - Create a total of 12 multiple-choice questions:
            * 4 basic questions
            * 5 intermediate questions
            * 3 advanced questions

        2. **Question Levels:**
          - **Basic:** Test the ability to recall and understand basic concepts, definitions, and facts.
          - **Intermediate:** Require the ability to apply knowledge to solve problems, analyze situations, or compare concepts.
          - **Advanced:** Demand critical thinking, synthesis of information from multiple sources, evaluation of viewpoints, or solving complex scenarios.

        3. **Question Structure:**
          - Each question must have a clear stem and 4 answer options (A, B, C, D).
          - There must be only ONE correct answer.
          - The distractors (incorrect options) must be plausible and discriminating.
          - For each question, provide:
            * The question
            * Four answer options
            * The correct answer
            * A brief explanation of why the answer is correct
            * The source of information used (database or web)
        """

    return quizz_agent