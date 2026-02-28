from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal, Optional

ToolName = Literal[
    "detect_objects",
    "get_3d_pose",
    "check_reachable",
    "move_ptp",
    "gripper",
    "ask_user",
]

class Step(BaseModel):
    tool: ToolName
    args: Dict[str, Any] = Field(default_factory=dict)

class Plan(BaseModel):
    intent: str
    steps: List[Step]
    need_clarification: bool = False
    question: str = ""
    target: Optional[Dict[str, Any]] = None
