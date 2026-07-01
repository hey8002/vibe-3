import { useEffect, useState } from "react";
import { checkBackendHealth, checkDatabaseHealth } from "../shared/api/health";
import type { HealthCheckResult, PageKey } from "../shared/types";
import { ChatbotPage } from "../pages/ChatbotPage";
import { ExcelPage } from "../pages/ExcelPage";
import { HomePage } from "../pages/HomePage";
import { NewsPage } from "../pages/NewsPage";
import { SchedulePage } from "../pages/SchedulePage";

const pages: Array<{ key: PageKey; label: string }> = [
  { key: "home", label: "연동 확인" },
  { key: "schedule", label: "팀원 스케줄" },
  { key: "excel", label: "엑셀 자동화" },
  { key: "chatbot", label: "민원 챗봇" },
  { key: "news", label: "뉴스 수집" },
];

export default function App() {
  const [activePage, setActivePage] = useState<PageKey>("home");
  const [backendHealth, setBackendHealth] = useState<HealthCheckResult>({
    status: "checking",
  });
  const [databaseHealth, setDatabaseHealth] = useState<HealthCheckResult>({
    status: "checking",
  });

  async function refreshHealthChecks() {
    setBackendHealth({ status: "checking" });
    setDatabaseHealth({ status: "checking" });

    const [backend, database] = await Promise.all([
      checkBackendHealth(),
      checkDatabaseHealth(),
    ]);

    setBackendHealth(backend);
    setDatabaseHealth(database);
  }

  useEffect(() => {
    void refreshHealthChecks();
  }, []);

  return (
    <div className="shell">
      <aside className="sidebar">
        <p className="eyebrow">Admin Super App</p>
        <h1>공공직군 행정업무 슈퍼앱</h1>
        <nav className="nav">
          {pages.map((page) => (
            <button
              className={activePage === page.key ? "active" : ""}
              key={page.key}
              onClick={() => setActivePage(page.key)}
              type="button"
            >
              {page.label}
            </button>
          ))}
        </nav>
      </aside>

      <main className="content">
        {activePage === "home" && (
          <HomePage
            backendHealth={backendHealth}
            databaseHealth={databaseHealth}
            onRefresh={refreshHealthChecks}
          />
        )}
        {activePage === "schedule" && <SchedulePage />}
        {activePage === "excel" && <ExcelPage />}
        {activePage === "chatbot" && <ChatbotPage />}
        {activePage === "news" && <NewsPage />}
      </main>
    </div>
  );
}
