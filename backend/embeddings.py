import os

from dotenv import load_dotenv
from google import genai
from langchain_core.embeddings import Embeddings

load_dotenv()


class GeminiEmbeddings(Embeddings):

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")

        self.model = os.getenv(
            "EMBEDDING_MODEL",
            "gemini-embedding-001",
        )

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=self.api_key
        )

    def embed_documents(self, texts):

        response = self.client.models.embed_content(
            model=self.model,
            contents=texts,
        )

        return [
            embedding.values
            for embedding in response.embeddings
        ]

    def embed_query(self, text):

        response = self.client.models.embed_content(
            model=self.model,
            contents=text,
        )

        return response.embeddings[0].values


def get_embeddings():
    return GeminiEmbeddings()