from dataclasses import dataclass
from agents.pydantic_models.supervisor import RunTask

@dataclass
class CollectDataDeps:
    task: RunTask