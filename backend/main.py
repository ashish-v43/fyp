"""Arkspace API: ephemeral document retrieval backed by Groq."""

from __future__ import annotations

import io
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any

import uvicorn
from docx import Document as DocxDocument
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.documents import Document
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
from pypdf import PdfReader

load_dotenv()

MAX_UPLOAD_BYTES = 20 * 1024 * 1024
MAX_CONTEXT_CHUNKS = 3
SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx"}

app = FastAPI(title="Arkspace API", version="2.0.0")

vercel_origin = os.getenv("VERCEL_ORIGIN", "https://arkspace.vercel.app").rstrip("/")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        vercel_origin,
    ],
    allow_origin_regex=r"https://[a-zA-Z0-9-]+\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
document_chunks: list[Document] = []


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)


def extract_text(filename: str, content: bytes) -> str:
    """Extract text from supported office and plain-text documents in memory."""
    extension = Path(filename).suffix.lower()
    try:
        if extension == ".txt":
            return content.decode("utf-8-sig")
        if extension == ".pdf":
            reader = PdfReader(io.BytesIO(content))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        if extension == ".docx":
            document = DocxDocument(io.BytesIO(content))
            return "\n".join(paragraph.text for paragraph in document.paragraphs)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read document: {exc}") from exc
    raise HTTPException(
        status_code=415,
        detail="Unsupported file type. Upload a .txt, .pdf, or .docx file.",
    )


def retrieve_chunks(question: str, limit: int = MAX_CONTEXT_CHUNKS) -> list[Document]:
    """Rank in-memory chunks by query-term coverage and frequency."""
    query_terms = set(re.findall(r"[\w'-]+", question.casefold()))
    if not query_terms or not document_chunks:
        return []

    scored: list[tuple[float, int, Document]] = []
    for index, chunk in enumerate(document_chunks):
        terms = re.findall(r"[\w'-]+", chunk.page_content.casefold())
        counts = Counter(terms)
        matched = query_terms.intersection(counts)
        if not matched:
            continue
        coverage = len(matched) / len(query_terms)
        frequency = sum(min(counts[term], 3) for term in matched) / max(len(terms), 1)
        scored.append((coverage + frequency, -index, chunk))

    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [chunk for _, _, chunk in scored[:limit]]


@app.get("/")
async def health() -> dict[str, str]:
    return {"status": "running", "project": "Arkspace"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> dict[str, Any]:
    filename = Path(file.filename or "upload").name
    if Path(filename).suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Upload a .txt, .pdf, or .docx file.")

    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds the 20 MB upload limit.")
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    text = extract_text(filename, content)
    if not text.strip():
        raise HTTPException(status_code=400, detail="No readable text was found in the file.")

    pieces = splitter.create_documents(
        [text], metadatas=[{"filename": filename}]
    )
    document_chunks.extend(pieces)
    return {
        "filename": filename,
        "text_length": len(text),
        "chunks_added": len(pieces),
        "total_chunks": len(document_chunks),
        "message": "Document indexed in memory. Ask a question to retrieve relevant passages.",
    }


@app.post("/ask")
async def ask(request: AskRequest) -> dict[str, Any]:
    context_chunks = retrieve_chunks(request.question.strip())
    if not context_chunks:
        raise HTTPException(
            status_code=404,
            detail="No relevant document passages found. Upload a document or try a question using its terms.",
        )

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="GROQ_API_KEY is not configured on the server.")

    context = "\n\n".join(
        f"[Passage {index}: {chunk.metadata.get('filename', 'document')}]\n{chunk.page_content}"
        for index, chunk in enumerate(context_chunks, start=1)
    )
    prompt = (
        "Answer the user's question using only the document passages below. "
        "If they do not contain the answer, say that the uploaded documents do not provide it. "
        "Keep the answer concise and do not invent facts.\n\n"
        f"Document passages (up to {MAX_CONTEXT_CHUNKS}):\n{context}\n\n"
        f"Question: {request.question.strip()}"
    )

    try:
        llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama3-8b-8192"),
            api_key=api_key,
            temperature=0,
        )
        response = await llm.ainvoke(prompt)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="The Groq request failed.") from exc

    return {
        "answer": response.content,
        "sources": [
            {
                "filename": chunk.metadata.get("filename", "document"),
                "snippet": chunk.page_content,
            }
            for chunk in context_chunks
        ],
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
