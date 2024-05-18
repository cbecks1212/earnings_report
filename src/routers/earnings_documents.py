from fastapi import APIRouter
import requests
import base64

router = APIRouter()

@router.post("/initialize-earnings-pdf-summary")
def init_earnings_pdf_summary(symbol: str):
    params = {"ticker" : symbol}
    req = requests.post("https://agile-anchorage-11058-7b018c820619.herokuapp.com/summarize-earnings-transcript", params=params)
    return {"content" : req.text}

@router.post("/download-earnings-summary")
def download_earnings_summary(task_id: str):
    task_obj = {"task_id" : task_id}
    req = requests.post("https://agile-anchorage-11058-7b018c820619.herokuapp.com/download-earnings-synopsis", params=task_obj)
    return req.content

@router.get("/get-report-status")
def get_report_status(task_id: str):
    task_obj = {"task_id" : task_id}
    req = requests.get("https://agile-anchorage-11058-7b018c820619.herokuapp.com/check_task_status", params=task_obj)
    return {"content" : req.content}
