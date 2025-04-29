from dataclasses import dataclass
from pydantic import BaseModel, Field
from typing import List,Union, Literal, Optional
from typing import List, Literal, Dict, Any
from typing_extensions import TypedDict


@dataclass
class Message:
    content: str
    role: str = "assistant"

@dataclass
class GraphState:
    """Mô hình trạng thái cho đồ thị."""
    question: str
    retrieval_result: str = ""
    search_result: str = ""
    outline_result: str = ""
    quizz_result: str = ""
    evaluation_result: str = ""
    next_step: str = "retrieve"

class ToolOutput(BaseModel):
    result: str

class ImageData(BaseModel):
    image_url: str
    caption: str
    width: int
    height: int
    
        
@dataclass
class Content:
    title: str
    content: str
    images: List[ImageData]
    language: str

class BulletPoints(BaseModel):
    subject: str
    points: List[str]

class Description(BaseModel):
    text: str
    
class Slide(BaseModel):
    title: str = Field(description="title of slide")
    body_text: Union[BulletPoints | Description]
    reference: str | None = Field(description="Reference link of figures, cite, etc", default=None)
    layout: Literal["cover", "table content", "only text", "text, image 25%", "text and image equal, 50%-50%",
    "image, text 25%", "only image", "text and 4 images", "text and 2 images", "graph", "video", "closing"]
    image_urls: Optional[List[str]]
    page: int    
    
class Presentation(BaseModel):
    title: str
    slides: List[Slide]    
    
class Question(BaseModel):
    question: str = Field(description="Question of multichoice")
    option: List[str] = Field(description="List of multiple")
    answer: str =Field(description="Answer of question from option, not A/B/C/D")
    explain: str = Field(description="Explain the correct answer")
    source: str =Field(description="Extract questions from database or web")
    
class OutputQuizz(BaseModel):
    questions: List[Question]

class QuizzInput(BaseModel):
    data: str    

## ClarifyAgent
@dataclass
class Objective:
    user_query: str
    subject: str
    level: str
    target_audience: str
    entire_course: bool
    chapters: List[str]

@dataclass
class ClarifyDeps:
    user_query: str
    
@dataclass
class ClarifyResult:
    question: str
    
## Curriculum

@dataclass
class CurriculumDeps:
    objective: str
    table_content: str    
    
## Supervisor

from pydantic import BaseModel, Field
from typing import Union

class Task(BaseModel):
    task_id: int = Field(description="Task ID")
    agent: Literal["collect_data_agent", "lecture_note_gen_agent","quiz_gen_agent","slide_gen_agent" , "evaluation_agent", "end"]
    description: str = Field(description="Short description about task include: chapter, ...")
    module_id: str = Field(description="ID or name of the module/topic that this task belongs to")
    status: Literal["pending", "done"]
    

class TODOList(BaseModel):
    tasks: List[Task] = Field(description="List of tasks")

class RunTask(BaseModel):
    task_id: int = Field(description="Task ID")
    agent: Literal["collect_data_agent", "lecture_note_gen_agent", "quiz_gen_agent","slide_gen_agent","evaluation_agent" ,"end"]
    description: str = Field(description="Short description about task include: chapter, ...")

@dataclass
class SupervisorDeps:
    curriculum: str
    todo_list: TODOList

class SupervisorResult(BaseModel):
    todo_list: TODOList = Field(description = "List of tasks")
    next_action:  RunTask
    
## Data collect
@dataclass
class CollectDataDeps:
    task: RunTask
    
    
##lecture note
@dataclass
class LectureNoteDeps:
    task: RunTask
    data: str
    
    
## Evaluate
class LectureNoteEvaluation(BaseModel):
    completeness: int = Field(ge=1, le=5, description="The completeness of the lecture content")
    logical_flow: int = Field(ge=1, le=5, description="The logical flow and structure of the lecture")
    scientific_accuracy: int = Field(ge=1, le=5, description="The scientific accuracy of the lecture content")
    clarity: int = Field(ge=1, le=5, description="The clarity and understandability of the lecture")
    reference_quality: int = Field(ge=1, le=5, description="The quality and validity of cited references")
    comment: Optional[str] = Field(description="General comments on the lecture note")

class QuizEvaluation(BaseModel):
    difficulty: int = Field(ge=1, le=5, description="The difficulty level of the quiz questions")
    question_clarity: int = Field(ge=1, le=5, description="The clarity and comprehensibility of the questions")
    answer_correctness: int = Field(ge=1, le=5, description="The correctness and appropriateness of the answers")
    explanation_quality: int = Field(ge=1, le=5, description="The quality and clarity of the answer explanations")
    topic_variety: int = Field(ge=1, le=5, description="The diversity of topics covered by the quiz")
    comment: Optional[str] = Field(description="General comments on the quiz")

class SlideEvaluation(BaseModel):
    layout_quality: int = Field(ge=1, le=5)
    aesthetic: int = Field(ge=1, le=5)
    visual_support: int = Field(ge=1, le=5)
    information_accuracy: int = Field(ge=1, le=5)
    readability: int = Field(ge=1, le=5)
    comment: Optional[str]

class EvaluationAgent(BaseModel):
    lecture_note_eval: Optional['LectureNoteEvaluation']
    quiz_eval: Optional['QuizEvaluation']
    slide_eval: Optional['SlideEvaluation']

class EvaluationInput(BaseModel):
    lecture_note: Optional[str]
    quiz: Optional[OutputQuizz]
    slide: Optional[Presentation]

## graph


class State(TypedDict):
    user_query: str
    objective: str
    history: str
    thinking: str
    todo_list: Dict[str, Task]
    data: str
    next_action: RunTask
    action: RunTask
    next_step: Literal["supervisor", "get_user_query", "collect_data_agent", "curriculum_agent", "lecture_note_gen_agent","quiz_gen_agent","slide_gen_agent","evaluation_agent","end"]
    results: Dict[str, Any]
    modules_result: Dict[str, List[Dict[str, Any]]]
    