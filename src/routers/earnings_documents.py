from fastapi import APIRouter, Response
from typing import Optional
import requests
import json
from io import BytesIO
from ..models.earnings_summary import EarningsSummarizer
from ..earnings_utilities.earnings_aggregator import EarningsCalculator
from ..earnings_utilities.excel_functions import create_excel_object

router = APIRouter()

@router.post("/initialize-earnings-pdf-summary", summary="Start the task of creating a summary of a symbol's earnings report.")
def init_earnings_pdf_summary(symbol: str, word_count: int):
    params = {"ticker" : symbol, "word_count" : word_count}
    req = requests.post("https://agile-anchorage-11058-7b018c820619.herokuapp.com/summarize-earnings-transcript", params=params)
    return req.content

@router.get("/get-pdf-report-status", summary="Check the status of an earnings summary.")
def get_report_status(task_id: str):
    task_obj = {"task_id" : task_id}
    req = requests.get("https://agile-anchorage-11058-7b018c820619.herokuapp.com/check_task_status", params=task_obj)
    return req.content

@router.post("/download-pdf-earnings-summary", summary="Once the task of creating an earnings summary has finished, this endpoint returns the content as bytes. \n You can take the byte-content and write it to a PDF file in the desired directory.")
def download_earnings_summary(task_id: str):
    task_obj = {"task_id" : task_id}
    status_req = requests.get("https://agile-anchorage-11058-7b018c820619.herokuapp.com/check_task_status", params=task_obj)
    status = json.loads(status_req.content)
    if status == "SUCCESS":
        req = requests.post("https://agile-anchorage-11058-7b018c820619.herokuapp.com/download-earnings-synopsis", params=task_obj)
        dict_ = json.loads(req.content.decode())
        content = dict_["content"]
        return {"content" : content}
    else:
        return {"content" : "Task still in progress"}
    
@router.post("/download-earnings-announcements-excel", summary="Download all upcoming earnings announcements as an Excel file")
def download_announcements_excel(model: Optional[EarningsSummarizer] = None):
    if model is not None:
        data = model.model_dump()
    else:
        data = None

    records = EarningsCalculator().get_earnings_announcements(data)
    buffer = create_excel_object(records)
    buffer.seek(0)
    
    headers = {
        'Content-Disposition': 'attachment; filename="sample.xlsx"'
    }

    return Response(content=buffer.getvalue(), media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers=headers)
