from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ExcelUploadResult(BaseModel):
    file_id: str
    filename: str
    created_at: str | None = None
    sheet_count: int
    sheets: list["ExcelSheetResult"]


class ExcelSheetResult(BaseModel):
    sheet_name: str
    row_count: int
    columns: list[str]
    rows: list[dict[str, object]]


class ExcelStoredWorkbook(BaseModel):
    file_id: str
    filename: str
    sheet_count: int
    row_count: int
    sheet_names: list[str]
    created_at: str
    

class ExcelStoredWorkbookDetail(ExcelStoredWorkbook):
    sheets: list[ExcelSheetResult]


class ExcelSplitRequest(BaseModel):
    file_id: str = Field(..., description="Uploaded file identifier")
    column: str = Field(..., description="Column name used for splitting")
    sheet_name: str | None = Field(default=None, description="Optional sheet name")
    keep_blank_values: bool = Field(default=True)


class ExcelMergeRequest(BaseModel):
    file_ids: list[str] = Field(..., min_length=2)
    sheet_name: str | None = Field(default=None)
    deduplicate: bool = Field(default=False)


class ExcelJobResult(BaseModel):
    job_id: str
    kind: Literal["split", "merge", "upload"]
    output_files: list[str]
    message: str
