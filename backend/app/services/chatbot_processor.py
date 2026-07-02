from __future__ import annotations

import base64
import io
import os
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.services.chatbot_store import get_chunks

SUPPORTED_EXTENSIONS = {".txt", ".md", ".html", ".htm", ".csv", ".xlsx", ".pdf"}


def detect_file_type(filename: str) -> str:
    return Path(filename).suffix.lower().lstrip(".")


def extract_text(path: Path, file_type: str) -> str:
    if file_type in {"txt", "md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    if file_type in {"html", "htm"}:
        soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
        return soup.get_text("\n", strip=True)
    if file_type == "csv":
        frame = pd.read_csv(path)
        return frame.to_csv(index=False)
    if file_type == "xlsx":
        sheet = pd.read_excel(path, engine="openpyxl")
        return sheet.to_csv(index=False)
    if file_type == "pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("PDF 처리를 위해 pypdf가 필요합니다.") from exc
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    raise ValueError(f"지원하지 않는 파일 형식입니다: {file_type}")


def preprocess_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    filtered = [line for line in lines if line]
    return "\n".join(filtered)


def split_text(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    return splitter.split_text(text)


def build_embeddings() -> OpenAIEmbeddings:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY가 설정되지 않았습니다.")
    return OpenAIEmbeddings(model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"))


def build_llm() -> ChatOpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY가 설정되지 않았습니다.")
    return ChatOpenAI(model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"), temperature=0)


def embed_chunks(chunks: list[str]) -> list[list[float]]:
    embeddings = build_embeddings()
    vectors = embeddings.embed_documents(chunks)
    return [list(vector) for vector in vectors]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right, strict=False))
    left_norm = sum(a * a for a in left) ** 0.5
    right_norm = sum(b * b for b in right) ** 0.5
    if not left_norm or not right_norm:
        return 0.0
    return dot / (left_norm * right_norm)


def retrieve_relevant_chunks(question: str, top_k: int = 4) -> list[dict[str, object]]:
    embeddings = build_embeddings()
    question_vector = embeddings.embed_query(question)
    ranked: list[tuple[float, dict[str, object]]] = []
    for chunk in get_chunks():
        embedding = chunk.get("embedding")
        if not embedding:
            continue
        score = cosine_similarity(question_vector, list(embedding))
        ranked.append((score, chunk))
    ranked.sort(key=lambda item: item[0], reverse=True)
    results: list[dict[str, object]] = []
    for score, chunk in ranked[:top_k]:
        results.append(
            {
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "chunk_index": chunk["chunk_index"],
                "content": chunk["content"],
                "score": round(score, 4),
            }
        )
    return results


def answer_question(question: str, context_chunks: list[dict[str, object]]) -> str:
    llm = build_llm()
    context_text = "\n\n".join(
        f"[문서 {chunk['document_id']} / 청크 {chunk['chunk_index']}] {chunk['content']}"
        for chunk in context_chunks
    )
    prompt = (
        "You are a helpful Korean RAG chatbot. Answer only from the provided context. "
        "If the answer is not in the context, say you cannot find it in the uploaded data.\n\n"
        f"Context:\n{context_text}\n\nQuestion:\n{question}"
    )
    response = llm.invoke(prompt)
    return getattr(response, "content", str(response))

