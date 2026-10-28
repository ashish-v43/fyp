from pathlib import Path

from pypdf import PdfReader
from docx import Document


class DocumentService:

    def extract_text(
        self,
        file_path: str
    ) -> str:

        extension = (
            Path(file_path)
            .suffix
            .lower()
        )

        if extension == ".txt":

            return self._extract_txt(
                file_path
            )

        elif extension == ".pdf":

            return self._extract_pdf(
                file_path
            )

        elif extension == ".docx":

            return self._extract_docx(
                file_path
            )

        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    def _extract_txt(
        self,
        file_path: str
    ):

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            return f.read()

    def _extract_pdf(
        self,
        file_path: str
    ):

        reader = PdfReader(
            file_path
        )

        text = ""

        for page in reader.pages:

            text += (
                page.extract_text()
                or ""
            )

        return text

    def _extract_docx(
        self,
        file_path: str
    ):

        doc = Document(
            file_path
        )

        return "\n".join(
            [
                para.text
                for para in doc.paragraphs
            ]
        )


document_service = DocumentService()