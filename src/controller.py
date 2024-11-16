from .pdf_layout_analysis import analyze_pdf, analyze_pdf_fast
from starlette.concurrency import run_in_threadpool

async def analyze_pdf_controller(file_content: bytes, fast: bool, extraction_format: str):
    
    if fast:
        return await run_in_threadpool(analyze_pdf_fast, file_content, "", extraction_format)
    return await run_in_threadpool(analyze_pdf, file_content, "", extraction_format)