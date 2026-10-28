import json
import re

from agents.base_agent import BaseAgent
from services.azure_openai_service import llm_service


class AnalystAgent(BaseAgent):

    async def run(
        self,
        transcript: str,
        context: str = ""
    ):

        schema = """
{
    "summary":"",

    "key_decisions":[
        {
            "decision":"",
            "responsible_party":""
        }
    ],

    "risks":[
        {
            "risk":"",
            "severity":"High"
        }
    ],

    "recommendations":[
        {
            "recommendation":"",
            "responsible_party":""
        }
    ]
}
"""

        system_prompt = f"""
You are an enterprise business analyst.

MEETING TRANSCRIPT:
{transcript}

COMPANY KNOWLEDGE BASE:
{context}

Using both the transcript and company knowledge, generate:

1. Executive Summary
   - A concise business summary of the meeting.

2. Key Decisions
   - Extract explicit decisions made during the meeting.
   - Include the responsible party when available.

3. Risks
   - Identify project, compliance, delivery, security, or operational risks.
   - Assign severity as High, Medium, or Low.

4. Recommendations
   - Generate actionable recommendations based on the meeting discussion and company policies.
   - Include the responsible party when available.

IMPORTANT:
- Return ONLY valid JSON.
- Do NOT include markdown.
- Do NOT include explanations.
- Do NOT include code fences.
- Follow the schema exactly.

JSON SCHEMA:

{schema}
"""

        response = llm_service.generate(
            system_prompt,
            transcript
        )

        try:

            json_match = re.search(
                r"\{.*\}",
                response,
                re.DOTALL
            )

            if json_match:

                parsed_response = json.loads(
                    json_match.group()
                )

                return parsed_response

            raise ValueError(
                "No JSON found in response"
            )

        except Exception as e:

            print(
                "ANALYST AGENT JSON PARSE ERROR:",
                str(e)
            )

            print(
                "RAW LLM RESPONSE:",
                response
            )

            return {
                "summary": response,
                "key_decisions": [],
                "risks": [],
                "recommendations": []
            }