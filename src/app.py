import sys
import torch
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import PlainTextResponse
from starlette.concurrency import run_in_threadpool
from catch_exceptions import catch_exceptions
from configuration import service_logger
from pdf_layout_analysis.get_xml import get_xml
from pdf_layout_analysis.run_pdf_layout_analysis import analyze_pdf
from pdf_layout_analysis.run_pdf_layout_analysis_fast import analyze_pdf_fast
from text_extraction.get_text_extraction import get_text_extraction
from toc.get_toc import get_toc
from visualization.get_visualization import get_visualization
from controller import analyze_pdf_controller
service_logger.info(f"Is PyTorch using GPU: {torch.cuda.is_available()}")

app = FastAPI()


@app.get("/")
async def info():
    return sys.version + " Using GPU: " + str(torch.cuda.is_available())


@app.get("/error")
async def error():
    raise FileNotFoundError("This is a test error from the error endpoint")


@app.post("/")
@catch_exceptions
async def run(file: UploadFile = File(...), fast: bool = Form(False), extraction_format: str = Form("")):
    file_content = file.file.read() 
    return analyze_pdf_controller(file_content, fast, extraction_format)


@app.post("/save_xml/{xml_file_name}")
@catch_exceptions
async def analyze_and_save_xml(file: UploadFile = File(...), xml_file_name: str | None = None, fast: bool = Form(False)):
    xml_file_name = xml_file_name if xml_file_name.endswith(".xml") else f"{xml_file_name}.xml"
    if fast:
        return await run_in_threadpool(analyze_pdf_fast, file.file.read(), xml_file_name, "")
    return await run_in_threadpool(analyze_pdf, file.file.read(), xml_file_name, "")


@app.get("/get_xml/{xml_file_name}", response_class=PlainTextResponse)
@catch_exceptions
async def get_xml_by_name(xml_file_name: str):
    xml_file_name = xml_file_name if xml_file_name.endswith(".xml") else f"{xml_file_name}.xml"
    return await run_in_threadpool(get_xml, xml_file_name)


@app.post("/toc")
@catch_exceptions
async def get_toc_endpoint(file: UploadFile = File(...), fast: bool = Form(False)):
    return await run_in_threadpool(get_toc, file, fast)


@app.post("/toc_legacy_uwazi_compatible")
@catch_exceptions
async def toc_legacy_uwazi_compatible(file: UploadFile = File(...)):
    toc = await run_in_threadpool(get_toc, file, True)
    toc_compatible = []
    for toc_item in toc:
        toc_compatible.append(toc_item.copy())
        toc_compatible[-1]["bounding_box"]["left"] = int(toc_item["bounding_box"]["left"] / 0.75)
        toc_compatible[-1]["bounding_box"]["top"] = int(toc_item["bounding_box"]["top"] / 0.75)
        toc_compatible[-1]["bounding_box"]["width"] = int(toc_item["bounding_box"]["width"] / 0.75)
        toc_compatible[-1]["bounding_box"]["height"] = int(toc_item["bounding_box"]["height"] / 0.75)
        toc_compatible[-1]["selectionRectangles"] = [toc_compatible[-1]["bounding_box"]]
        del toc_compatible[-1]["bounding_box"]
    return toc_compatible


@app.post("/text")
@catch_exceptions
async def get_text_endpoint(file: UploadFile = File(...), fast: bool = Form(False), types: str = Form("all")):
    return await run_in_threadpool(get_text_extraction, file, fast, types)


@app.post("/visualize")
@catch_exceptions
async def get_visualization_endpoint(file: UploadFile = File(...), fast: bool = Form(False)):
    return await run_in_threadpool(get_visualization, file, fast)
