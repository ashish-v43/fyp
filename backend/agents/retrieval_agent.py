from pathlib import Path

from agents.base_agent import BaseAgent


class RetrievalAgent(BaseAgent):

    def __init__(self):

        self.docs_path = (
            Path(__file__)
            .resolve()
            .parent
            .parent
            / "data"
            / "sample_transcripts"
        )

    async def run(self, query: str):

        print(f"Docs Path: {self.docs_path}")
        print(f"Exists: {self.docs_path.exists()}")

        files = list(
            self.docs_path.glob("*.txt")
        )

        print(f"Files Found: {files}")

        retrieved_context = []

        for file in files:

            content = file.read_text(
                encoding="utf-8"
            )

            query_words = set(
                query.lower().split()
            )

            content_words = set(
                content.lower().split()
            )

            score = len(
                query_words.intersection(
                    content_words
                )
            )

            if score > 0:

                retrieved_context.append(
                    {
                        "document": file.name,
                        "content": content,
                        "score": score
                    }
                )

        retrieved_context.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return retrieved_context[:3]