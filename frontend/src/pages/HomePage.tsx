import { useState } from "react";
import type { HealthCheckResult } from "../shared/types";
import { testBackendConnection } from "../shared/api/health";

type HomePageProps = {
  backendHealth: HealthCheckResult;
  databaseHealth: HealthCheckResult;
  onRefresh: () => void;
  backendBaseUrl: string;
  onChangeBackendBaseUrl: (value: string) => void;
};

export function HomePage({
  backendHealth,
  databaseHealth,
  onRefresh,
  backendBaseUrl,
  onChangeBackendBaseUrl,
}: HomePageProps) {
  const [testResult, setTestResult] = useState<HealthCheckResult | null>(null);
  const [testing, setTesting] = useState(false);

  async function handleTestConnection() {
    setTesting(true);
    setTestResult(null);
    try {
      const result = await testBackendConnection(backendBaseUrl);
      setTestResult(result);
    } finally {
      setTesting(false);
    }
  }

  return (
    <section className="page">
      <div className="page-header">
        <p className="eyebrow">Integration Check</p>
        <h2>FE-BE, BE-DB 연결 확인</h2>
        <p>
          GitHub Pages나 다른 프런트 환경에서 사용할 백엔드 URL을 직접 입력하고 연결을
          테스트할 수 있습니다.
        </p>
      </div>

      <div className="card-grid">
        <article className="card">
          <h3>백엔드 URL</h3>
          <label>
            백엔드 기본 주소
            <input
              placeholder="https://your-backend.example.com/api"
              value={backendBaseUrl}
              onChange={(event) => onChangeBackendBaseUrl(event.target.value)}
            />
          </label>
          <button disabled={testing} onClick={handleTestConnection} type="button">
            {testing ? "연결 테스트 중..." : "연결 테스트"}
          </button>
        </article>

        <article className="card">
          <h3>테스트 결과</h3>
          <p>{testResult?.message ?? "아직 테스트하지 않았습니다."}</p>
          {testResult?.detail ? <code>{testResult.detail}</code> : null}
        </article>
      </div>

      <div className="status-grid">
        <StatusCard title="FE-BE 연결" result={backendHealth} />
        <StatusCard title="BE-DB 연결" result={databaseHealth} />
      </div>

      <button className="primary-button" onClick={onRefresh} type="button">
        연결 상태 다시 확인
      </button>
    </section>
  );
}

function StatusCard({
  title,
  result,
}: {
  title: string;
  result: HealthCheckResult;
}) {
  const label =
    result.status === "ok" ? "정상" : result.status === "checking" ? "확인 중" : "실패";

  return (
    <article className={`status-card ${result.status}`}>
      <span>{label}</span>
      <h3>{title}</h3>
      <p>{result.message ?? "상태를 확인하고 있습니다."}</p>
      {result.detail && <code>{result.detail}</code>}
    </article>
  );
}
