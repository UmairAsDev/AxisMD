import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from langgraph.graph import StateGraph, END
from app.tool_node import audio_recorder_tool, audio_transcribe_tool, prompt_builder_node, llm_node
from typing import Dict



def build_voice_agent_graph():
    """
    Builds a LangGraph pipeline for:
    Audio Recorder -> Transcriber -> Prompt Builder -> LLM -> END
    """
    graph = StateGraph(dict) #type: ignore


    graph.add_node("recorder", audio_recorder_tool)#type: ignore
    graph.add_node("transcriber", audio_transcribe_tool)#type: ignore
    graph.add_node("prompt_builder", prompt_builder_node)
    graph.add_node("llm", llm_node)


    graph.add_edge("recorder", "transcriber")
    graph.add_edge("transcriber", "prompt_builder")
    graph.add_edge("prompt_builder", "llm")
    graph.add_edge("llm", END)


    graph.set_entry_point("recorder")

    return graph.compile()


if __name__ == "__main__":
    agent = build_voice_agent_graph()

    init_state = {
        "user_id": "123",
        "file_name": "demo.wav",
        "base_template": {
            "speciality": "Cardiology",
            "subspecialty": "Interventional Cardiology",
            "output_style": "Comprehensive",
            "objectives": ["vitals", "physical exam findings", "test results"]
        }
    }

    final_state = agent.invoke(init_state)
    print("Final Output:", final_state)
