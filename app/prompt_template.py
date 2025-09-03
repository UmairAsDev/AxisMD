import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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
        if Objectives:
        Objectives = {template_dict.get("objectives")}
         else:
        -Objectives must include vitals, physical exam findings, and results from relevant tests and procedures..
        - Format based on requested style: {template_dict.get("output_style")}.
        if the style is:
        - Comprehensive:
          1- Visit Summary: create a consice summary of the visit.
          2- Subjective: include all relevant patient-reported information.
          3- Chief Complaint: this include age and sex of the patient.
          4- History of Present Illness: Add all the symptoms and diagnosis of the patient that should be brief.
          5- Pertinent PMHx: include relevant past medical, surgical, family, and social history.
          6- Objective: include vitals, physical exam findings, and results from relevant tests and procedures.
          7- Assessment: Add complete assesment of the patient.
             - Plan: #TIA:[Management Plan, Patient Education, Monitoring and Follow-up] #Condition:[Management Plan, Patient Education, Monitoring and Follow-up:]
                #Condition:[Management Plan, Patient Education, Monitoring and Follow-up]
           
        - Focused:
          Visit Summary:
          Subjective:
          Chief Complaint:
          History of Present Illness:
          Pertinent PMHx:
          Objective:
          Assessment:
          Plan: #TIA:[Management Plan, Patient Education, Monitoring and Follow-up] #HCondition
          :[Management Plan, Patient Education, Monitoring and Follow-up]
        
        -Categorized:
        - if the style is Categorized:
          Visit Summary: create a consice summary of the visit.
          Subjective: include all relevant patient-reported information.
          Chief Complaint: this include age and sex of the patient.
          History of Present Illness: Add all the symptoms and diagnosis of the patient that should be brief.
          Pertinent PMHx: include relevant past medical, surgical, family, and social history.
          Objective: include vitals, physical exam findings, and results from relevant tests and procedures.
          Assessment & Plan: Add complete assesment of the patient.
        
        - Output must be ONLY the JSON object, no extra text.
        The #Condition in the plan section should be replaced with the actual condition diagnosed.
        Must include ICD and CPT codes and procedure codes based on the provided transcript.
        """
        return prompt.strip()


