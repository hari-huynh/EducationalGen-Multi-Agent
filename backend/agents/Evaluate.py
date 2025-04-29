from pydantic_ai import Agent, RunContext
from models import Objective,ClarifyDeps,ClarifyResult

from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider
import os
from dotenv import load_dotenv
from models import EvaluationInput,EvaluationAgent
load_dotenv()



def create_evaluation_agent() -> Agent:
    
    llm2 = GroqModel(
    'llama-3.3-70b-versatile', 
    provider=GroqProvider(api_key=os.getenv('API_KEY_GROQ'))
    )
    evaluation_agent = Agent(
        llm2,
        deps_type=EvaluationInput,
        result_type=EvaluationAgent,
    )

    @evaluation_agent.system_prompt
    def system_prompt(context: RunContext):
        return f"""
            lecture_note: {context.deps.lecture_note}
            quiz {context.deps.quiz}
            slide {context.deps.slide}
            You are an evaluation agent responsible for critically assessing the quality of AI-generated educational content, including lecture notes, quizzes, and presentation slides.

                Your tasks are:
                - Analyze the provided content carefully.
                - Evaluate each type of content based on specific scoring criteria.
                - Rate each criterion on a scale from 1 (very poor) to 5 (excellent).
                - Provide concise, constructive comments for each evaluation.

                Evaluation Criteria:
                - Lecture Note: completeness, logical flow, scientific accuracy, clarity, reference quality.
                - Quiz: difficulty, question clarity, answer correctness, explanation quality, topic variety.
                - Slide: layout quality, aesthetics, visual support, information accuracy, readability.

                Output Format:
                - Return structured results following the Pydantic models: LectureNoteEvaluation, QuizEvaluation, SlideEvaluation.
                - If any content is missing, you can omit the corresponding evaluation.

                Important:
                - Be objective and critical.
                - Do not generate new content.
                - Only evaluate the input content.

                Think step-by-step and ensure your scoring is consistent and well justified.

        """
    
    
    return evaluation_agent