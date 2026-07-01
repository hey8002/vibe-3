import type { HealthCheckResult } from "../shared/types";

type HomePageProps = {
  backendHealth: HealthCheckResult;
  databaseHealth: HealthCheckResult;
  onRefresh: () => void;
};

export function HomePage({
  backendHealth,
  databaseHealth,
  onRefresh,
}: HomePageProps) {
  return (
    <section className="page">
      <div className="page-header">
        <p className="eyebrow">Integration Check</p>
        <h2>FE-BE, BE-DB 연동 확인</h2>
        <p>
          Vite 개발 서버에서 FastAPI API를 호출하고, FastAPI가 SQLite에
          연결되는지 확인하는 초기 점검 화면입니다.
        </p>
      </div>

      <div className="status-grid">
        <StatusCard title="FE-BE 연동" result={backendHealth} />
        <StatusCard title="BE-DB 연동" result={databaseHealth} />
      </div>

      <button className="primary-button" onClick={onRefresh} type="button">
        연동 상태 다시 확인
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
    result.status === "ok"
      ? "정상"
      : result.status === "checking"
        ? "확인 중"
        : "실패";

  return (
    <article className={`status-card ${result.status}`}>
      <span>{label}</span>
      <h3>{title}</h3>
      <p>{result.message ?? "상태를 확인하고 있습니다."}</p>
      {result.detail && <code>{result.detail}</code>}
    </article>
  );
}
