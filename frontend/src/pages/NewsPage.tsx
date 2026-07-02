import { useEffect, useState } from "react";
import { collectNews, listNews, listNewsJobs, type NewsArticle, type NewsJob } from "../shared/api/news";

export function NewsPage() {
  const [targetDate, setTargetDate] = useState("");
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [jobs, setJobs] = useState<NewsJob[]>([]);
  const [message, setMessage] = useState("날짜를 선택하고 수집을 실행하세요.");
  const [busy, setBusy] = useState(false);

  async function refresh() {
    const [newsResponse, jobsResponse] = await Promise.all([listNews(), listNewsJobs()]);
    setArticles(newsResponse.items);
    setJobs(jobsResponse.items);
  }

  useEffect(() => {
    void refresh();
  }, []);

  async function handleCollect() {
    setBusy(true);
    setMessage("수집 중...");
    try {
      const result = await collectNews(targetDate || undefined);
      setMessage(`수집 완료: ${result.collected}건, 중복 ${result.skipped}건`);
      await refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "수집 실패");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="page">
      <div className="page-header">
        <p className="eyebrow">News Collector</p>
        <h2>정책브리핑 기사 수집</h2>
        <p>매일 오전 9시 전날 기사 자동 수집과 날짜 지정 수동 수집을 지원합니다.</p>
      </div>

      <div className="card-grid">
        <article className="card">
          <h3>수동 수집</h3>
          <label>
            날짜 선택
            <input type="date" value={targetDate} onChange={(event) => setTargetDate(event.target.value)} />
          </label>
          <button disabled={busy} onClick={handleCollect} type="button">
            수집 실행
          </button>
        </article>

        <article className="card">
          <h3>수집 상태</h3>
          <p>{message}</p>
        </article>
      </div>

      <div className="card">
        <h3>수집된 기사</h3>
        <table>
          <thead>
            <tr>
              <th>제목</th>
              <th>발행일</th>
              <th>부처</th>
              <th>링크</th>
            </tr>
          </thead>
          <tbody>
            {articles.map((article) => (
              <tr key={article.source_url}>
                <td>{article.title}</td>
                <td>{article.published_date}</td>
                <td>{article.department ?? "-"}</td>
                <td>
                  <a href={article.source_url} rel="noreferrer" target="_blank">
                    원문
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h3>수집 작업 로그</h3>
        <table>
          <thead>
            <tr>
              <th>날짜</th>
              <th>수집</th>
              <th>중복</th>
              <th>실패</th>
              <th>시각</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((job) => (
              <tr key={job.id}>
                <td>{job.target_date}</td>
                <td>{job.collected}</td>
                <td>{job.skipped}</td>
                <td>{job.failed}</td>
                <td>{job.created_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
