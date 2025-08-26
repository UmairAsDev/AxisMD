# app/graph/state.py
from typing import TypedDict, Optional, List
from langchain_core.messages import BaseMessage

class ClinicalState(TypedDict):
    session_id: str
    messages: List[BaseMessage]
    audio_path: Optional[str]
    transcript_text: Optional[str]
    prompt_text: Optional[str]
    json_note: Optional[dict]
