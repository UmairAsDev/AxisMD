import json
from typing import List, Dict, Optional

class ClinicalPromptBuilder:
    def __init__(self, base_template: Dict, audio_transcript:str):
        self.base_template = base_template
        self.audio_transcript = audio_transcript

    def build_prompt(self):
        """
        Builds a clinical note generation prompt for the LLM.
        """
        template_dict = self.base_template.copy()
        

        prompt = f"""
        This is dictated by a doctor in the specialty{template_dict.get("specialty")} and subspecialty {template_dict.get("subspecialty")}. 
        to a voice assistant to generate a clinical note. While dictating, there might be 
        transcription errors (wrong drug names, conditions, or procedures).

        Raw transcript:
        \"\"\"{self.audio_transcript}\"\"\"

        Your task:
        1. Correct transcription mistakes using appropriate medical context.
        2. Extract structured information into the JSON schema:
        {json.dumps(template_dict, indent=2)}

        Rules:
        - Only include information explicitly stated or implied in the transcript.
        - Insert findings into the relevant sections (including physical exam objectives).
        - Assign correct ICD codes and CPT codes.
        - If insufficient content, return:
        {{
        "error": "Insufficient or unrelated content"
        }}
        - Format based on requested style: {template_dict.get("output_style")}.
        - Output must be ONLY the JSON object, no extra text.
        """
        return prompt.strip()



# if __name__ == "__main__":
#     schema = {
#         "patientName": "",
#         "patientAge": "",
#         "patientGender": "",
#         "chiefComplaint": "",
#         "historyOfPresentIllness": "",
#         "pastMedicalHistory": "",
#         "medications": "",
#         "allergies": "",
#         "physicalExam": "",
#         "assessmentAndPlan": "",
#         "icdCodes": [],
#         "cptCodes": []
#     }


#     builder = ClinicalPromptBuilder(schema, audio_transcript="Patient is a 45 year")

#     transcript = "Patient is a 45 year old female with chest pain radiating to the left arm. ECG abnormal. Possible stent procedure discussed."

#     prompt = builder.build_prompt()

#     print(prompt)
