from typing import TypedDict, Annotated, List, Dict, Any
import operator
from pydantic import BaseModel, Field
from app.models.base import BaseDBModel

class AgentState(TypedDict):
    messages: Annotated[List[Dict[str, Any]], operator.add]
    tools_called: Annotated[List[str], operator.add]
    findings: List[str]
    final_answer: str

class AgentRun(BaseDBModel):
    user_id: str
    agent_type: str
    status: str = "running"
    state_snapshot: dict = {}
    result: str = ""
    error: str = ""
