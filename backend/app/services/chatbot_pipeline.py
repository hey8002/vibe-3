from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from app.services.chatbot_processor import (
    detect_file_type,
    embed_chunks,
    extract_text,
    preprocess_text,
    split_text,
)
from app.services.chatbot_store import (
    CHATBOT_UPLOAD_DIR,
    get_document,
    save_chat_message,
    save_chunks,
    save_uploaded_document,
    update_chunk_embeddings,
    update_document_status,
)


def upload_document(filename: str, data: bytes) -> dict[str, object]:
    CHATBOT_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    document_id = uuid4().hex
    file_type = detect_file_type(filename)
    if file_type not in {"txt", "md", "html", "htm", "csv", "xlsx", "pdf"}:
        raise ValueError("지원하지 않는 파일 형식입니다.")
    path = CHATBOT_UPLOAD_DIR / f"{document_id}_{Path(filename).name}"
    path.write_bytes(data)
    save_uploaded_document(document_id, filename, file_type, path)
    return {
        "document_id": document_id,
        "filename": filename,
        "file_type": file_type,
        "status": "uploaded",
        "message": "업로드 완료",
    }


def train_document(document_id: str) -> dict[str, object]:
    document = get_document(document_id)
    if document is None:
        raise ValueError("문서를 찾을 수 없습니다.")

    update_document_status(document_id, "processing")
    source_path = Path(document["original_path"])
    file_type = str(document["file_type"])
    text = extract_text(source_path, file_type)
    preprocessed = preprocess_text(text)
    chunks = split_text(preprocessed)
    chunk_payloads = [
        {"content": chunk, "metadata": {"document_id": document_id, "file_type": file_type}}
        for chunk in chunks
    ]
    save_chunks(document_id, chunk_payloads)
    vectors = embed_chunks(chunks)
    update_chunk_embeddings(document_id, vectors)
    update_document_status(document_id, "trained")
    return {
        "document_id": document_id,
        "status": "trained",
        "chunks_created": len(chunks),
        "embedded_chunks": len(vectors),
        "message": "학습 완료",
    }


def ask_rag(question: str) -> dict[str, object]:
    from app.services.chatbot_processor import answer_question, retrieve_relevant_chunks

    sources = retrieve_relevant_chunks(question)
    answer = answer_question(question, sources)
    save_chat_message(question, answer, sources)
    return {
        "answer": answer,
        "sources": sources,
        "message": "응답 생성 완료",
    }
