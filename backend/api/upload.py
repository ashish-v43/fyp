from pathlib import Path

from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File

from services.document_service import (
    document_service
)

from orchestrator import (
    AgentOrchestrator
)

router = APIRouter()

orchestrator = AgentOrchestrator()

UPLOAD_DIR = Path(
    "uploads"
)

UPLOAD_DIR.mkdir(
    exist_ok=True
)


@router.post(
    "/upload"
)
async def upload_file(
    file: UploadFile = File(...)
):

    file_path = (
        UPLOAD_DIR
        / file.filename
    )

    with open(
        file_path,
        "wb"
    ) as f:

        content = await file.read()

        f.write(
            content
        )

    extracted_text = (
        document_service
        .extract_text(
            str(file_path)
        )
    )

    result = (
        await orchestrator.execute(
            extracted_text
        )
    )

    return {
        "filename":
            file.filename,
        "text_length":
            len(
                extracted_text
            ),
        "result":
            result
    }