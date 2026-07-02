import { apiUrl } from "./base";

export type NewsArticle = {
  title: string;
  published_date: string;
  source_url: string;
  department?: string | null;
  summary?: string | null;
  content?: string | null;
  collected_at: string;
};

export type NewsCollectResult = {
  target_date: string;
  collected: number;
  skipped: number;
  failed: number;
  items: NewsArticle[];
};

export type NewsJob = {
  id: number;
  target_date: string;
  collected: number;
  skipped: number;
  failed: number;
  created_at: string;
};

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `${response.status} ${response.statusText}`);
  }
  return (await response.json()) as T;
}

export async function collectNews(targetDate?: string): Promise<NewsCollectResult> {
  const response = await fetch(apiUrl("/news/collect"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ target_date: targetDate ?? null }),
  });
  return parseJson<NewsCollectResult>(response);
}

export async function listNews(date?: string): Promise<{ items: NewsArticle[] }> {
  const params = new URLSearchParams();
  if (date) params.set("date", date);
  const response = await fetch(apiUrl(`/news${params.toString() ? `?${params.toString()}` : ""}`));
  return parseJson<{ items: NewsArticle[] }>(response);
}

export async function listNewsJobs(): Promise<{ items: NewsJob[] }> {
  const response = await fetch(apiUrl("/news/jobs"));
  return parseJson<{ items: NewsJob[] }>(response);
}
