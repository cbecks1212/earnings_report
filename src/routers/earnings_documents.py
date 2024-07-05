from fastapi import APIRouter, Response, Depends, HTTPException
from starlette import status
from typing import Optional
import requests
import json
from io import BytesIO
import pandas as pd
import openpyxl
import requests
from ..auth.utils import get_current_user
from ..models.earnings_summary import EarningsSummarizer
from ..earnings_utilities.earnings_aggregator import EarningsCalculator
from ..earnings_utilities.excel_functions import create_excel_object, adjust_excel_column_widths
from ..earnings_utilities.common_functions import return_valid_symbol

router = APIRouter(
    tags=["Generate Files"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/initialize-earnings-pdf-summary", summary="Start the task of creating a summary of a symbol's earnings report.")
def init_earnings_pdf_summary(symbol: str, word_count: int):
    is_valid_symbol = return_valid_symbol(symbol)
    if not is_valid_symbol:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{symbol} is not a valid symbol")
    
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
        'Content-Disposition': 'attachment; filename="Earnings_Announcements.xlsx"'
    }

    return Response(content=buffer.getvalue(), media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers=headers)

@router.post("/download-earnings-summary-excel", summary="Download an analysis of the current earning season as an Excel file.")
def download_earnings_summary_excel(model: Optional[EarningsSummarizer] = None):
    if model is not None:
        data = model.model_dump()
    else:
        data = None
    
    summary_data = requests.post("https://practical-hamilton-mqecybx2ra-uc.a.run.app/earnings-summary", json=data).text

    breakout_data = requests.post("https://practical-hamilton-mqecybx2ra-uc.a.run.app/earnings-breakout", json=data).text

    initial_buffer = BytesIO()
    summary_df = pd.DataFrame(json.loads(summary_data))[['Beat', 'Missed']].drop_duplicates()
    breakout_df = pd.DataFrame(json.loads(breakout_data))

    with pd.ExcelWriter(initial_buffer, engine='openpyxl') as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        breakout_df.to_excel(writer, sheet_name="Earnings Breakout", index=False)


    workbook = openpyxl.load_workbook(initial_buffer)
    workbook = adjust_excel_column_widths(workbook)
    final_buffer = BytesIO()
    workbook.save(final_buffer)

    final_buffer.seek(0)
    
    headers = {
        'Content-Disposition': 'attachment; filename="Earnings_Season_Analysis.xlsx"'
    }

    return Response(content=final_buffer.getvalue(), media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers=headers)

