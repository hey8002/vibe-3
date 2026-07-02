import { useEffect, useMemo, useState } from "react";
import {
  deleteAllStoredExcelFiles,
  deleteStoredExcelFile,
  getStoredExcelFile,
  mergeExcelFiles,
  searchStoredExcelFiles,
  splitExcelFile,
  uploadExcelFile,
  type ExcelUploadResult,
  type StoredExcelFile,
  type StoredExcelFileDetail,
} from "../shared/api/excel";

export function ExcelPage() {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploadedFiles, setUploadedFiles] = useState<ExcelUploadResult[]>([]);
  const [storedFiles, setStoredFiles] = useState<StoredExcelFile[]>([]);
  const [selectedStoredFileId, setSelectedStoredFileId] = useState("");
  const [selectedSheetName, setSelectedSheetName] = useState("");
  const [storedDetail, setStoredDetail] = useState<StoredExcelFileDetail | null>(null);
  const [column, setColumn] = useState("");
  const [filterName, setFilterName] = useState("");
  const [filterSheet, setFilterSheet] = useState("");
  const [message, setMessage] = useState("엑셀 파일을 업로드하세요.");
  const [busy, setBusy] = useState<"idle" | "upload" | "split" | "merge" | "load">("idle");
  const [downloadUrl, setDownloadUrl] = useState("");

  const workbookColumns = useMemo(() => {
    const sheet = storedDetail?.sheets.find((item) => item.sheet_name === selectedSheetName) ?? storedDetail?.sheets[0];
    return sheet?.columns ?? uploadedFiles[0]?.sheets[0]?.columns ?? [];
  }, [storedDetail, selectedSheetName, uploadedFiles]);

  const activeSheet = useMemo(() => {
    if (!storedDetail) return null;
    return storedDetail.sheets.find((item) => item.sheet_name === selectedSheetName) ?? storedDetail.sheets[0] ?? null;
  }, [storedDetail, selectedSheetName]);

  async function refreshStoredFiles() {
    setBusy("load");
    try {
      const items = await searchStoredExcelFiles({
        filename: filterName || undefined,
        sheetName: filterSheet || undefined,
      });
      setStoredFiles(items);
      if (items.length > 0 && !selectedStoredFileId) {
        setSelectedStoredFileId(items[0].file_id);
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "저장 목록 조회 실패");
    } finally {
      setBusy("idle");
    }
  }

  async function loadStoredDetail(fileId: string) {
    if (!fileId) {
      setStoredDetail(null);
      return;
    }

    setBusy("load");
    try {
      const detail = await getStoredExcelFile(fileId);
      setStoredDetail(detail);
      setSelectedSheetName(detail.sheets[0]?.sheet_name ?? "");
      setColumn(detail.sheets[0]?.columns[0] ?? "");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "저장된 파일 조회 실패");
    } finally {
      setBusy("idle");
    }
  }

  async function handleDeleteStoredFile(fileId: string) {
    setBusy("load");
    try {
      await deleteStoredExcelFile(fileId);
      if (selectedStoredFileId === fileId) {
        setSelectedStoredFileId("");
        setStoredDetail(null);
      }
      setMessage("저장된 파일을 삭제했습니다.");
      await refreshStoredFiles();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "삭제 실패");
    } finally {
      setBusy("idle");
    }
  }

  async function handleDeleteAllStoredFiles() {
    setBusy("load");
    try {
      await deleteAllStoredExcelFiles();
      setStoredFiles([]);
      setStoredDetail(null);
      setSelectedStoredFileId("");
      setMessage("저장된 파일을 모두 삭제했습니다.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "전체 삭제 실패");
    } finally {
      setBusy("idle");
    }
  }

  useEffect(() => {
    void refreshStoredFiles();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterName, filterSheet]);

  useEffect(() => {
    if (selectedStoredFileId) {
      void loadStoredDetail(selectedStoredFileId);
    }
  }, [selectedStoredFileId]);

  async function handleUpload() {
    if (selectedFiles.length === 0) {
      setMessage("업로드할 파일을 먼저 선택하세요.");
      return;
    }

    setBusy("upload");
    setMessage("업로드 중...");
    setDownloadUrl("");

    try {
      const results: ExcelUploadResult[] = [];
      for (const file of selectedFiles) {
        // Keep upload flow simple and explicit so the user sees each workbook registered.
        // eslint-disable-next-line no-await-in-loop
        const result = await uploadExcelFile(file);
        results.push(result);
      }
      setUploadedFiles(results);
      await refreshStoredFiles();
      setMessage(`업로드 완료: ${results.map((item) => item.filename).join(", ")}`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "업로드 실패");
    } finally {
      setBusy("idle");
    }
  }

  async function handleSplit() {
    const target = uploadedFiles[0];
    const sheet = target?.sheets[0];
    if (!target || !sheet) {
      setMessage("먼저 파일을 업로드하세요.");
      return;
    }
    if (!column) {
      setMessage("분리 기준 칼럼을 선택하세요.");
      return;
    }

    setBusy("split");
    setMessage("분리 중...");
    setDownloadUrl("");

    try {
      const result = await splitExcelFile({ fileId: target.file_id, column });
      setMessage(`${result.message} (${result.labels.join(", ")})`);
      setDownloadUrl(result.download_url);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "분리 실패");
    } finally {
      setBusy("idle");
    }
  }

  async function handleMerge() {
    if (uploadedFiles.length < 2) {
      setMessage("업로드된 파일이 2개 이상 필요합니다.");
      return;
    }

    setBusy("merge");
    setMessage("병합 중...");
    setDownloadUrl("");

    try {
      const result = await mergeExcelFiles({ fileIds: uploadedFiles.map((item) => item.file_id) });
      setMessage(result.message);
      setDownloadUrl(result.download_url);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "병합 실패");
    } finally {
      setBusy("idle");
    }
  }

  return (
    <section className="page">
      <div className="page-header">
        <p className="eyebrow">Excel Automation</p>
        <h2>엑셀 업로드 및 DB 조회</h2>
        <p>엑셀 파일을 업로드하면 SQLite에 저장되고, 여러 시트와 저장된 내용을 표로 확인할 수 있습니다.</p>
      </div>

      <div className="card-grid">
        <article className="card">
          <h3>1. 업로드</h3>
          <input
            accept=".xlsx"
            multiple
            onChange={(event) => setSelectedFiles(Array.from(event.target.files ?? []))}
            type="file"
          />
          <button disabled={busy !== "idle"} onClick={handleUpload} type="button">
            업로드 후 DB 저장
          </button>
        </article>

        <article className="card">
          <h3>2. 저장된 파일 필터</h3>
          <label>
            파일명 검색
            <input value={filterName} onChange={(event) => setFilterName(event.target.value)} />
          </label>
          <label>
            시트명 검색
            <input value={filterSheet} onChange={(event) => setFilterSheet(event.target.value)} />
          </label>
        </article>

        <article className="card">
          <h3>3. 병합 / 삭제</h3>
          <p>업로드한 여러 파일을 하나로 합치거나 저장된 파일을 삭제할 수 있습니다.</p>
          <button disabled={busy !== "idle" || uploadedFiles.length < 2} onClick={handleMerge} type="button">
            병합 실행
          </button>
          <button disabled={busy !== "idle" || storedFiles.length === 0} onClick={handleDeleteAllStoredFiles} type="button">
            전체 삭제
          </button>
        </article>
      </div>

      <div className="placeholder-panel">
        <strong>상태</strong>
        <p>{message}</p>
        {downloadUrl ? (
          <a href={downloadUrl} rel="noreferrer" target="_blank">
            결과 다운로드
          </a>
        ) : null}
      </div>

      <div className="card">
        <h3>저장된 엑셀 목록</h3>
        <table>
          <thead>
            <tr>
              <th>파일명</th>
              <th>시트 수</th>
              <th>행 수</th>
              <th>시트명</th>
              <th>저장 시각</th>
              <th>작업</th>
            </tr>
          </thead>
          <tbody>
            {storedFiles.map((item) => (
              <tr key={item.file_id}>
                <td>{item.filename}</td>
                <td>{item.sheet_count}</td>
                <td>{item.row_count}</td>
                <td>{item.sheet_names.join(", ")}</td>
                <td>{item.created_at}</td>
                <td>
                  <button disabled={busy !== "idle"} onClick={() => handleDeleteStoredFile(item.file_id)} type="button">
                    삭제
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h3>저장된 내용</h3>
        {storedDetail ? (
          <>
            <label>
              시트 선택
              <select value={selectedSheetName} onChange={(event) => setSelectedSheetName(event.target.value)}>
                {storedDetail.sheets.map((sheet) => (
                  <option key={sheet.sheet_name} value={sheet.sheet_name}>
                    {sheet.sheet_name} ({sheet.row_count}행)
                  </option>
                ))}
              </select>
            </label>
            {activeSheet ? (
              <table>
                <thead>
                  <tr>
                    {activeSheet.columns.map((columnName) => (
                      <th key={columnName}>{columnName}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {activeSheet.rows.map((row, index) => (
                    <tr key={index}>
                      {activeSheet.columns.map((columnName) => (
                        <td key={columnName}>{String(row[columnName] ?? "")}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : null}
          </>
        ) : (
          <p>저장된 파일을 선택하면 내용이 표시됩니다.</p>
        )}
      </div>

      <div className="card">
        <h3>업로드된 파일</h3>
        <table>
          <thead>
            <tr>
              <th>파일명</th>
              <th>시트 수</th>
            </tr>
          </thead>
          <tbody>
            {uploadedFiles.map((item) => (
              <tr key={item.file_id}>
                <td>{item.filename}</td>
                <td>{item.sheet_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <label>
          분리 기준 칼럼
          <select value={column} onChange={(event) => setColumn(event.target.value)}>
            {workbookColumns.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>
        <button disabled={busy !== "idle" || uploadedFiles.length === 0} onClick={handleSplit} type="button">
          칼럼 기준 분리
        </button>
      </div>
    </section>
  );
}
