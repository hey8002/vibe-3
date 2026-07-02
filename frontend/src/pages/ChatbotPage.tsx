import { useEffect, useMemo, useState } from "react";
import {
  askChatbot,
  listChatbotDocuments,
  trainChatbotDocument,
  uploadChatbotDocument,
  type ChatbotAnswerResult,
  type ChatbotDocument,
} from "../shared/api/chatbot";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export function ChatbotPage() {
  const [documents, setDocuments] = useState<ChatbotDocument[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedDocumentId, setSelectedDocumentId] = useState("");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [sources, setSources] = useState<Array<Record<string, unknown>>>([]);
  const [status, setStatus] = useState("학습 데이터를 업로드하세요.");
  const [busy, setBusy] = useState<"idle" | "upload" | "train" | "ask">("idle");

  async function refreshDocuments() {
    const items = await listChatbotDocuments();
    setDocuments(items);
    if (!selectedDocumentId && items.length > 0) {
      setSelectedDocumentId(items[0].document_id);
    }
  }

  useEffect(() => {
    void refreshDocuments();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleUpload() {
    if (!selectedFile) {
      setStatus("업로드할 학습 파일을 선택하세요.");
      return;
    }

    setBusy("upload");
    setStatus("업로드 중...");
    try {
      await uploadChatbotDocument(selectedFile);
      setStatus("업로드 완료. 학습을 실행하세요.");
      await refreshDocuments();
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "업로드 실패");
    } finally {
      setBusy("idle");
    }
  }

  async function handleTrain() {
    if (!selectedDocumentId) {
      setStatus("학습할 문서를 선택하세요.");
      return;
    }

    setBusy("train");
    setStatus("학습 중...");
    try {
      const result = await trainChatbotDocument(selectedDocumentId);
      setStatus(`학습 완료: 청크 ${result.chunks_created}개, 임베딩 ${result.embedded_chunks}개`);
      await refreshDocuments();
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "학습 실패");
    } finally {
      setBusy("idle");
    }
  }

  async function handleAsk() {
    if (!question.trim()) {
      setStatus("질문을 입력하세요.");
      return;
    }

    setBusy("ask");
    setStatus("응답 생성 중...");
    setMessages((current) => [...current, { role: "user", content: question }]);
    try {
      const result: ChatbotAnswerResult = await askChatbot(question);
      setMessages((current) => [...current, { role: "assistant", content: result.answer }]);
      setSources(result.sources);
      setStatus(result.message);
      setQuestion("");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "질문 실패");
    } finally {
      setBusy("idle");
    }
  }

  const selectedDocument = useMemo(
    () => documents.find((item) => item.document_id === selectedDocumentId),
    [documents, selectedDocumentId],
  );

  return (
    <section className="page">
      <div className="page-header">
        <p className="eyebrow">RAG Chatbot</p>
        <h2>생성형 AI + RAG 챗봇</h2>
        <p>학습 파일을 업로드하고, 전처리/임베딩 후 질문 응답을 수행합니다.</p>
      </div>

      <div className="card-grid">
        <article className="card">
          <h3>1. 학습 데이터 업로드</h3>
          <input
            accept=".txt,.md,.html,.htm,.csv,.xlsx,.pdf"
            onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
            type="file"
          />
          <button disabled={busy !== "idle"} onClick={handleUpload} type="button">
            업로드
          </button>
        </article>

        <article className="card">
          <h3>2. 학습 실행</h3>
          <label>
            문서 선택
            <select value={selectedDocumentId} onChange={(event) => setSelectedDocumentId(event.target.value)}>
              <option value="">선택</option>
              {documents.map((item) => (
                <option key={item.document_id} value={item.document_id}>
                  {item.filename} ({item.status})
                </option>
              ))}
            </select>
          </label>
          <button disabled={busy !== "idle"} onClick={handleTrain} type="button">
            학습 및 인덱싱
          </button>
        </article>

        <article className="card">
          <h3>3. 상태</h3>
          <p>{status}</p>
          <p>{selectedDocument ? `선택 문서: ${selectedDocument.filename}` : "선택된 문서가 없습니다."}</p>
        </article>
      </div>

      <div className="card">
        <h3>학습 문서 목록</h3>
        <table>
          <thead>
            <tr>
              <th>파일명</th>
              <th>형식</th>
              <th>상태</th>
              <th>청크 수</th>
              <th>등록 시각</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((item) => (
              <tr key={item.document_id}>
                <td>{item.filename}</td>
                <td>{item.file_type}</td>
                <td>{item.status}</td>
                <td>{item.chunk_count}</td>
                <td>{item.created_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h3>질문하기</h3>
        <textarea
          rows={4}
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="학습한 문서 내용을 바탕으로 질문하세요."
        />
        <button disabled={busy !== "idle"} onClick={handleAsk} type="button">
          질문하기
        </button>
      </div>

      <div className="card">
        <h3>대화 기록</h3>
        <div className="chat-log">
          {messages.map((message, index) => (
            <div key={index} className={`chat-bubble ${message.role}`}>
              <strong>{message.role === "user" ? "사용자" : "AI"}</strong>
              <p>{message.content}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h3>참조 근거</h3>
        <table>
          <thead>
            <tr>
              <th>문서</th>
              <th>청크</th>
              <th>점수</th>
            </tr>
          </thead>
          <tbody>
            {sources.map((source, index) => (
              <tr key={index}>
                <td>{String(source.document_id ?? "")}</td>
                <td>{String(source.chunk_index ?? "")}</td>
                <td>{String(source.score ?? "")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
