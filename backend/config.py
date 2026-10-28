import os
from dotenv import load_dotenv

load_dotenv()


class Settings:

    OLLAMA_URL = os.getenv(
        "OLLAMA_URL",
        "http://localhost:11434"
    )

    MODEL_NAME = os.getenv(
        "MODEL_NAME",
        "llama3.1"
    )


settings = Settings()