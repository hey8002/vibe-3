from __future__ import annotations

from pydantic import BaseModel, Field


class ChatbotUploadResult(BaseModel):
    document_id: str
    filename: str
    file_type: str
    status: str
    message: str


class ChatbotTrainRequest(BaseModel):
    document_id: str


class ChatbotTrainResult(BaseModel):
    document_id: str
    status: str
    chunks_created: int
    embedded_chunks: int
    message: str


class ChatbotMessageRequest(BaseModel):
    question: str = Field(min_length=1)


class ChatbotAnswerResult(BaseModel):
    answer: str
    sources: list[dict[str, object]]
    message: str


class ChatbotDocumentSummary(BaseModel):
    document_id: str
    filename: str
    file_type: str
    status: str
    created_at: str
    chunk_count: int

