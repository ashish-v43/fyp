import json
import re

from agents.base_agent import BaseAgent
from services.azure_openai_service import llm_service


class InsightAgent(BaseAgent):

    async def run(
        self,
        transcript: str,
        analysis: dict,
        tasks: dict
    ):

        system_prompt = f"""
You are a workplace intelligence and productivity analyst.

Transcript:
{transcript}

Analysis:
{analysis}

Tasks:
{tasks}

Identify:

1. Bottlenecks
2. Team observations
3. Risks to delivery
4. Productivity insights

Return ONLY JSON.

{{
    "bottlenecks": [
        {{
            "issue": "",
            "impact": ""
        }}
    ],
    "team_observations": [
        {{
            "observation": ""
        }}
    ],
    "risks_to_delivery": [
        {{
            "risk": "",
            "severity": ""
        }}
    ],
    "productivity_insights": [
        {{
            "insight": ""
        }}
    ]
}}
"""

        response = llm_service.generate(
            system_prompt,
            transcript
        )

        print("INSIGHT RESPONSE:")
        print(response)

        try:

            json_match = re.search(
                r'\{[\s\S]*\}',
                response,
                re.DOTALL
            )

            if json_match:
                return json.loads(
                    json_match.group()
                )

            raise ValueError()

        except Exception:

            return {
                "bottlenecks": [],
                "team_observations": [],
                "risks_to_delivery": [],
                "productivity_insights": []
            }