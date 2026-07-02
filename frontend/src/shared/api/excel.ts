import { apiUrl } from "./base";

export type ExcelUploadResult = {
  file_id: string;
  filename: string;
  created_at: string | null;
  sheet_count: number;
  sheets: Array<{
    sheet_name: string;
    row_count: number;
    columns: string[];
    rows: Array<Record<string, unknown>>;
  }>;
};

export type ExcelSplitResponse = {
  message: string;
  labels: string[];
  download_url: string;
};

export type ExcelMergeResponse = {
  message: string;
  download_url: string;
};

export type StoredExcelFile = {
  file_id: string;
  filename: string;
  sheet_count: number;
  row_count: number;
  sheet_names: string[];
  created_at: string;
};

export type StoredExcelFileDetail = StoredExcelFile & {
  sheets: Array<{
    sheet_name: string;
    row_count: number;
    columns: string[];
    rows: Array<Record<string, unknown>>;
  }>;
};

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `${response.status} ${response.statusText}`);
  }
  return (await response.json()) as T;
}

export async function uploadExcelFile(file: File): Promise<ExcelUploadResult> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(apiUrl("/excel/upload"), {
    method: "POST",
    body: formData,
  });

  return parseJson<ExcelUploadResult>(response);
}

export async function splitExcelFile(input: {
  fileId: string;
  column: string;
  sheetName?: string;
  keepBlankValues?: boolean;
}): Promise<ExcelSplitResponse> {
  const response = await fetch(apiUrl("/excel/split"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      file_id: input.fileId,
      column: input.column,
      sheet_name: input.sheetName ?? null,
      keep_blank_values: input.keepBlankValues ?? true,
    }),
  });

  return parseJson<ExcelSplitResponse>(response);
}

export async function mergeExcelFiles(input: {
  fileIds: string[];
  sheetName?: string;
  deduplicate?: boolean;
}): Promise<ExcelMergeResponse> {
  const response = await fetch(apiUrl("/excel/merge"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      file_ids: input.fileIds,
      sheet_name: input.sheetName ?? null,
      deduplicate: input.deduplicate ?? false,
    }),
  });

  return parseJson<ExcelMergeResponse>(response);
}

export async function listStoredExcelFiles(): Promise<StoredExcelFile[]> {
  const response = await fetch(apiUrl("/excel/stored"));
  return parseJson<StoredExcelFile[]>(response);
}

export async function searchStoredExcelFiles(input: {
  filename?: string;
  sheetName?: string;
}): Promise<StoredExcelFile[]> {
  const params = new URLSearchParams();
  if (input.filename) params.set("filename", input.filename);
  if (input.sheetName) params.set("sheet_name", input.sheetName);
  const response = await fetch(apiUrl(`/excel/stored?${params.toString()}`));
  return parseJson<StoredExcelFile[]>(response);
}

export async function getStoredExcelFile(fileId: string): Promise<StoredExcelFileDetail> {
  const response = await fetch(apiUrl(`/excel/stored/${fileId}`));
  return parseJson<StoredExcelFileDetail>(response);
}

export async function deleteStoredExcelFile(fileId: string): Promise<void> {
  const response = await fetch(apiUrl(`/excel/stored/${fileId}`), {
    method: "DELETE",
  });
  await parseJson<{ status: string; message: string }>(response);
}

export async function deleteAllStoredExcelFiles(): Promise<void> {
  const response = await fetch(apiUrl("/excel/stored"), {
    method: "DELETE",
  });
  await parseJson<{ status: string; message: string }>(response);
}
