from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.analyze import router as analyze_router
from api.upload import router as upload_router
from api.report import router as report_router


app = FastAPI(
    title="Arkspace"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    analyze_router
)

app.include_router(
    upload_router
)

app.include_router(
    report_router
)


@app.get("/")
def health():

    return {
        "status": "running",
        "project": "Arkspace"
    }
