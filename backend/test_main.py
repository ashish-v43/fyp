from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture(autouse=True)
def empty_document_store():
    main.document_chunks.clear()
    yield
    main.document_chunks.clear()


def test_upload_indexes_text_into_langchain_chunks():
    text = (
        "Project Orion approved a budget of 250000 dollars for the renewal. "
        "The finance team will review the contract next quarter. "
    ) * 60

    with TestClient(main.app) as client:
        response = client.post(
            "/upload",
            files={"file": ("meeting.txt", text.encode("utf-8"), "text/plain")},
        )

    assert response.status_code == 200
    result = response.json()
    assert result["filename"] == "meeting.txt"
    assert result["text_length"] == len(text)
    assert result["chunks_added"] > 1
    assert result["total_chunks"] == result["chunks_added"]
    assert len(main.document_chunks) == result["chunks_added"]
    assert main.splitter._chunk_size == 1000
    assert main.splitter._chunk_overlap == 200
    assert all(len(chunk.page_content) <= 1000 for chunk in main.document_chunks)
    assert all(chunk.metadata["filename"] == "meeting.txt" for chunk in main.document_chunks)


def test_ask_sends_only_retrieved_context_to_mocked_groq(monkeypatch: pytest.MonkeyPatch):
    relevant_text = (
        "Project Orion contract renewal budget approval. "
        "Finance approved the Orion renewal budget at 250000 dollars. "
    ) * 45
    unrelated_text = "UNRELATED_SECRET_SENTINEL " + ("Unrelated gardening notes. " * 20)

    with TestClient(main.app) as client:
        upload_response = client.post(
            "/upload",
            files={"file": ("project-notes.txt", relevant_text.encode(), "text/plain")},
        )
        assert upload_response.status_code == 200
        unrelated_upload_response = client.post(
            "/upload",
            files={"file": ("other-notes.txt", unrelated_text.encode(), "text/plain")},
        )
        assert unrelated_upload_response.status_code == 200

        monkeypatch.setenv("GROQ_API_KEY", "test-key-do-not-use-live-credentials")
        mock_llm = SimpleNamespace(
            ainvoke=AsyncMock(
                return_value=SimpleNamespace(
                    content="The approved budget is 250000 dollars."
                )
            )
        )
        with patch("main.ChatGroq", return_value=mock_llm) as groq_constructor:
            response = client.post(
                "/ask",
                json={"question": "What is the Project Orion contract renewal budget?"},
            )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "The approved budget is 250000 dollars."
    assert 1 <= len(body["sources"]) <= 3
    assert all(source["filename"] == "project-notes.txt" for source in body["sources"])

    groq_constructor.assert_called_once_with(
        model="llama3-8b-8192",
        api_key="test-key-do-not-use-live-credentials",
        temperature=0,
    )
    mock_llm.ainvoke.assert_awaited_once()
    prompt = mock_llm.ainvoke.await_args.args[0]
    assert "Project Orion" in prompt
    assert "250000 dollars" in prompt
    assert "Question: What is the Project Orion contract renewal budget?" in prompt
    assert "UNRELATED_SECRET_SENTINEL" not in prompt
