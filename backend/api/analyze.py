from fastapi import APIRouter

from orchestrator import AgentOrchestrator

from models.request_models import AnalyzeRequest


router = APIRouter()

orchestrator = AgentOrchestrator()


@router.post("/analyze")
async def analyze(
    request: AnalyzeRequest
):

    result = await orchestrator.execute(
        request.text
    )

    return result