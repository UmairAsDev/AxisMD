
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from recorder import audio_processor
from prompt_template import ClinicalPromptBuilder
import time
import json
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
from tools.settings import settings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def audio_recorder_tool(state: dict):
    """
    Expects: {"user_id": "...", "file_name": "..."}
    Returns: {"file_path": "...", "duration": ...}
    """
    recorder = audio_processor()
    recorder["start"]()
    time.sleep(60)
    recorder["stop"]()
    
    file_name = state.get("file_name", "recording.wav")
    file_path = os.path.join("audio_storage", state.get("user_id", "anonymous"), file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    saved = recorder["save_file"](file_path)
    duration = recorder["get_conversation_time"]()

    return {
        "file_path": saved,
        "duration": duration
    }



def audio_transcribe_tool(state: dict):
    """
    Expects: {"file_path": "..."}
    Returns: {"transcription": "...", "messages": [HumanMessage]}
    """
    file_path = state["file_path"]
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    transcription = client.audio.transcriptions.create(
        file=open(file_path, "rb"),
        model="whisper-1",
        prompt="This is a medical transcription. Correct any errors in medical terms.",
    )

    text = transcription.text
    print("Transcription:", text)

    return {
        "transcription": text,
        "messages": [HumanMessage(content=text)]
    }



def prompt_builder_node(state):
    base_template = state["base_template"]
    audio_transcript = state["transcription"] 
    builder = ClinicalPromptBuilder(base_template, audio_transcript)
    prompt = builder.build_prompt()
    state["prompt"] = prompt
    return state



    

def llm_node(state):
    prompt = state["prompt"] 
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    res = llm.invoke([SystemMessage(content="Return ONLY a JSON object."), HumanMessage(content=prompt)])
    if isinstance(res.content, list):
        text = "".join(str(item) for item in res.content).strip()
    else:
        text = str(res.content).strip()
    try:
        payload = json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end >= 0:
            payload = json.loads(text[start:end+1])
        else:
            raise ValueError("Model did not return valid JSON")
    return {"json_note": payload}



if __name__ == "__main__":

    state = {"user_id": "123", "file_name": "demo.wav", "base_template": {"speciality": "Cardiology", "subspecialty": "Interventional Cardiology", "output_style": "Comprehensive", "objectives": ["vitals", "physical exam findings", "test results"]}}
    out1 = audio_recorder_tool(state)
    out2 = audio_transcribe_tool(out1)
    prompt_state = {"base_template": state["base_template"], "transcription": out2["transcription"]}
    out3 = prompt_builder_node(prompt_state)
    out4 = llm_node(out3)
    print(out4)

