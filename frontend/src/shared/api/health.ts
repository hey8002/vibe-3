import type { HealthCheckResult } from "../types";
import { apiUrl, getApiBaseUrl } from "./base";

type ApiHealthResponse = {
  status: string;
  service?: string;
  database?: string;
  message?: string;
};

export async function checkBackendHealth(): Promise<HealthCheckResult> {
  return requestHealth(apiUrl("/health"), "FastAPI 서버 응답 확인 완료");
}

export async function checkDatabaseHealth(): Promise<HealthCheckResult> {
  return requestHealth(apiUrl("/db/health"), "SQLite 연결 확인 완료");
}

export async function testBackendConnection(baseUrl?: string): Promise<HealthCheckResult> {
  const normalizedBase = baseUrl?.trim() ? baseUrl.trim().replace(/\/$/, "") : getApiBaseUrl();
  const target = `${normalizedBase}/health`;
  return requestHealth(target, "백엔드 연결 확인 완료");
}

async function requestHealth(path: string, successMessage: string): Promise<HealthCheckResult> {
  try {
    const response = await fetch(path);

    if (!response.ok) {
      return {
        status: "error",
        message: "API 응답이 정상 범위가 아닙니다.",
        detail: `${response.status} ${response.statusText}`,
      };
    }

    const data = (await response.json()) as ApiHealthResponse;

    return {
      status: data.status === "ok" ? "ok" : "error",
      message: data.message ?? successMessage,
      detail: data.database ?? data.service,
    };
  } catch (error) {
    return {
      status: "error",
      message: "API 호출에 실패했습니다. BE 서버 실행 상태를 확인하세요.",
      detail: error instanceof Error ? error.message : "unknown error",
    };
  }
}
