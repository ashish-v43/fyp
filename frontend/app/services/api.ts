import axios from "axios";

const baseURL =
  process.env.NEXT_PUBLIC_API_URL?.trim() || "http://localhost:8000";

const api = axios.create({
  baseURL: baseURL.replace(/\/$/, ""),
  timeout: 60_000,
});

export type UploadResponse = {
  filename: string;
  text_length: number;
  chunks_added: number;
  total_chunks: number;
  message: string;
};

export type AskResponse = {
  answer: string;
  sources: Array<{ filename: string; snippet: string }>;
};

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await api.post<UploadResponse>("/upload", formData);
  return response.data;
}

export async function askQuestion(question: string): Promise<AskResponse> {
  const response = await api.post<AskResponse>("/ask", { question });
  return response.data;
}

export default api;
