from fastapi import APIRouter
import requests
import json

router = APIRouter()

@router.post("/initialize-earnings-pdf-summary", summary="Start the task of creating a summary of a symbol's earnings report.")
def init_earnings_pdf_summary(symbol: str, word_count: int):
    params = {"ticker" : symbol, "word_count" : word_count}
    req = requests.post("https://agile-anchorage-11058-7b018c820619.herokuapp.com/summarize-earnings-transcript", params=params)
    return {"content" : req.text}

@router.get("/get-pdf-report-status", summary="Check the status of an earnings summary.")
def get_report_status(task_id: str):
    task_obj = {"task_id" : task_id}
    req = requests.get("https://agile-anchorage-11058-7b018c820619.herokuapp.com/check_task_status", params=task_obj)
    return {"content" : req.content}

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
