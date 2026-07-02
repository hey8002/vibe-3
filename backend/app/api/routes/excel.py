from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.schemas.excel import (
    ExcelMergeRequest,
    ExcelSplitRequest,
    ExcelStoredWorkbook,
    ExcelStoredWorkbookDetail,
    ExcelSheetResult,
    ExcelUploadResult,
)
from app.services.excel_processor import (
    OUTPUT_DIR,
    UPLOAD_DIR,
    UploadedExcel,
    inspect_workbook_bytes,
    merge_workbooks,
    read_workbook_metadata,
    split_workbook,
    upload_workbook,
    zip_files,
)
from app.services.excel_store import (
    delete_all_excel_workbooks,
    delete_excel_workbook,
    get_excel_workbook,
    list_excel_workbooks,
    store_excel_workbook,
)

router = APIRouter(prefix="/excel", tags=["excel"])

_uploaded_files: dict[str, UploadedExcel] = {}


@router.get("/jobs")
def list_excel_jobs() -> dict[str, list[dict[str, str]]]:
    return {"items": []}


@router.get("/stored", response_model=list[ExcelStoredWorkbook])
def list_stored_excel_files(filename: str | None = None, sheet_name: str | None = None) -> list[dict[str, object]]:
    return list_excel_workbooks(filename=filename, sheet_name=sheet_name)


@router.get("/stored/{file_id}", response_model=ExcelStoredWorkbookDetail)
def get_stored_excel_file(file_id: str) -> dict[str, object]:
    stored = get_excel_workbook(file_id)
    if stored is None:
        raise HTTPException(status_code=404, detail="Stored file not found")
    return stored


@router.delete("/stored/{file_id}")
def remove_stored_excel_file(file_id: str) -> dict[str, str]:
    deleted = delete_excel_workbook(file_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Stored file not found")
    return {"status": "ok", "message": "Stored file deleted"}


@router.delete("/stored")
def remove_all_stored_excel_files() -> dict[str, str]:
    delete_all_excel_workbooks()
    return {"status": "ok", "message": "All stored files deleted"}


@router.post("/upload", response_model=ExcelUploadResult)
async def upload_excel(file: UploadFile = File(...)) -> ExcelUploadResult:
    data = await file.read()
    try:
        uploaded = upload_workbook(file.filename or "upload.xlsx", data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    _uploaded_files[uploaded.file_id] = uploaded
    rows, columns = read_workbook_metadata(uploaded.path)
    stored = store_excel_workbook(uploaded.file_id, uploaded.path, uploaded.filename)
    first_sheet = stored["sheets"][0] if stored["sheets"] else {"sheet_name": None, "columns": [], "rows": [], "row_count": 0}
    return ExcelUploadResult(
        file_id=stored["file_id"],
        filename=uploaded.filename,
        created_at=stored["created_at"],
        sheet_count=len(stored["sheets"]),
        sheets=[
            ExcelSheetResult(
                sheet_name=sheet["sheet_name"],
                row_count=sheet["row_count"],
                columns=sheet["columns"],
                rows=sheet["rows"],
            )
            for sheet in stored["sheets"]
        ],
    )


@router.post("/split")
def split_excel(payload: ExcelSplitRequest):
    uploaded = _uploaded_files.get(payload.file_id)
    if uploaded is None:
        raise HTTPException(status_code=404, detail="Uploaded file not found")

    try:
        output_paths, labels = split_workbook(
            uploaded.path,
            column=payload.column,
            sheet_name=payload.sheet_name,
            keep_blank_values=payload.keep_blank_values,
        )
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    archive = zip_files(output_paths, f"{uploaded.path.stem}_split")
    return {
        "message": "split completed",
        "labels": labels,
        "download_url": f"/api/excel/download/{archive.name}",
    }


@router.post("/merge")
def merge_excel(payload: ExcelMergeRequest):
    resolved: list[Path] = []
    for file_id in payload.file_ids:
        uploaded = _uploaded_files.get(file_id)
        if uploaded is None:
            raise HTTPException(status_code=404, detail=f"Uploaded file not found: {file_id}")
        resolved.append(uploaded.path)

    try:
        output_path = merge_workbooks(resolved, sheet_name=payload.sheet_name, deduplicate=payload.deduplicate)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "message": "merge completed",
        "download_url": f"/api/excel/download/{output_path.name}",
    }


@router.get("/download/{filename}")
def download_excel(filename: str):
    path = OUTPUT_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=path.name)
