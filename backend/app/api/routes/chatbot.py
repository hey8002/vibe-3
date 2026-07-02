from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.chatbot import (
    ChatbotAnswerResult,
    ChatbotDocumentSummary,
    ChatbotMessageRequest,
    ChatbotTrainRequest,
    ChatbotTrainResult,
    ChatbotUploadResult,
)
from app.services.chatbot_pipeline import ask_rag, train_document, upload_document
from app.services.chatbot_store import list_documents

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


@router.get("/manuals")
def list_manuals() -> dict[str, list[dict[str, str]]]:
    return {"items": []}


@router.get("/documents", response_model=list[ChatbotDocumentSummary])
def documents() -> list[dict[str, object]]:
    return list_documents()


@router.post("/documents/upload", response_model=ChatbotUploadResult)
async def upload_chatbot_document(file: UploadFile = File(...)) -> ChatbotUploadResult:
    data = await file.read()
    try:
        return ChatbotUploadResult(**upload_document(file.filename or "upload.txt", data))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/train", response_model=ChatbotTrainResult)
def train_chatbot_document(payload: ChatbotTrainRequest) -> ChatbotTrainResult:
    try:
        return ChatbotTrainResult(**train_document(payload.document_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/ask", response_model=ChatbotAnswerResult)
def ask_chatbot(payload: ChatbotMessageRequest) -> ChatbotAnswerResult:
    try:
        return ChatbotAnswerResult(**ask_rag(payload.question))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
