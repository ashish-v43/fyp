import json

from agents.base_agent import BaseAgent
from services.azure_openai_service import llm_service


class PlannerAgent(BaseAgent):

    async def run(self, input_data):

        system_prompt = """
        You are a planning agent.

        Analyze the document and identify the workflow.

        Return JSON only.

        Example:

        {
            "workflow": [
                "security_scan",
                "summary_generation",
                "task_extraction"
            ]
        }
        """

        response = llm_service.generate(
            system_prompt,
            input_data
        )

        try:
            return json.loads(response)
        except Exception:
            return {
                "workflow": [
                    "security_scan",
                    "summary_generation",
                    "task_extraction"
                ]
            }