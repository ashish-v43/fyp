from pydantic import BaseModel


class AnalyzeResponse(BaseModel):
    planner: dict
    security: dict
    retrieval: list
    analysis: dict