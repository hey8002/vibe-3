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

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `${response.status} ${response.statusText}`);
  }
  return (await response.json()) as T;
}

export async function listChatbotDocuments(): Promise<ChatbotDocument[]> {
  const response = await fetch(apiUrl("/chatbot/documents"));
  return parseJson<ChatbotDocument[]>(response);
}

export async function uploadChatbotDocument(file: File): Promise<ChatbotUploadResult> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(apiUrl("/chatbot/documents/upload"), {
    method: "POST",
    body: formData,
  });
  return parseJson<ChatbotUploadResult>(response);
}

export async function trainChatbotDocument(documentId: string): Promise<ChatbotTrainResult> {
  const response = await fetch(apiUrl("/chatbot/train"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ document_id: documentId }),
  });
  return parseJson<ChatbotTrainResult>(response);
}

export async function askChatbot(question: string): Promise<ChatbotAnswerResult> {
  const response = await fetch(apiUrl("/chatbot/ask"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  return parseJson<ChatbotAnswerResult>(response);
}
