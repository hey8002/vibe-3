import { apiUrl } from "./base";

export type ChatbotDocument = {
  document_id: string;
  filename: string;
  file_type: string;
  status: string;
  created_at: string;
  chunk_count: number;
};

export type ChatbotUploadResult = {
  document_id: string;
  filename: string;
  file_type: string;
  status: string;
  message: string;
};

export type ChatbotTrainResult = {
  document_id: string;
  status: string;
  chunks_created: number;
  embedded_chunks: number;
  message: string;
};

export type ChatbotAnswerResult = {
  answer: string;
  sources: Array<Record<string, unknown>>;
  message: string;
};

const requestTimeoutMs = 30000;

async function fetchWithTimeout(input: RequestInfo | URL, init: RequestInit = {}): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), requestTimeoutMs);

  try {
    return await fetch(input, {
      ...init,
      signal: controller.signal,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error("백엔드 서버 응답이 지연되고 있습니다. 서버 실행 상태와 API URL을 확인하세요.");
    }
    throw error;
  } finally {
    window.clearTimeout(timeoutId);
  }
}

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const rawDetail = await response.text();
    let message = rawDetail || `${response.status} ${response.statusText}`;
    try {
      const parsed = JSON.parse(rawDetail) as { detail?: unknown };
      if (parsed.detail) {
        message = String(parsed.detail);
      }
    } catch {
      // Keep the original response body when the server did not return JSON.
    }
    throw new Error(message);
  }
  return (await response.json()) as T;
}

export async function listChatbotDocuments(): Promise<ChatbotDocument[]> {
  const response = await fetchWithTimeout(apiUrl("/chatbot/documents"));
  return parseJson<ChatbotDocument[]>(response);
}

export async function uploadChatbotDocument(file: File): Promise<ChatbotUploadResult> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetchWithTimeout(apiUrl("/chatbot/documents/upload"), {
    method: "POST",
    body: formData,
  });
  return parseJson<ChatbotUploadResult>(response);
}

export async function trainChatbotDocument(documentId: string): Promise<ChatbotTrainResult> {
  const response = await fetchWithTimeout(apiUrl("/chatbot/train"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ document_id: documentId }),
  });
  return parseJson<ChatbotTrainResult>(response);
}

export async function askChatbot(question: string): Promise<ChatbotAnswerResult> {
  const response = await fetchWithTimeout(apiUrl("/chatbot/ask"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  return parseJson<ChatbotAnswerResult>(response);
}
