import requests

from config import settings


class AzureOpenAIService:

    def generate(
        self,
        system_prompt: str,
        user_prompt: str
    ):

        prompt = f"""
        {system_prompt}

        USER INPUT:
        {user_prompt}
        """

        payload = {
            "model": settings.MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(
            f"{settings.OLLAMA_URL}/api/generate",
            json=payload
        )

        response.raise_for_status()

        return response.json()["response"]


llm_service = AzureOpenAIService()