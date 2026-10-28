import json
import re

from agents.base_agent import BaseAgent
from services.azure_openai_service import llm_service


class TaskAgent(BaseAgent):

    async def run(
        self,
        transcript: str
    ):

        system_prompt = """
You are a project management AI.

Extract actionable tasks.

Return ONLY JSON.

Format:

{
    "tasks":[
        {
            "owner":"",
            "task":"",
            "priority":"",
            "deadline":""
        }
    ]
}
"""

        response = llm_service.generate(
            system_prompt,
            transcript
        )

        try:

            json_match = re.search(
                r'\{.*\}',
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
                "tasks": []
            }