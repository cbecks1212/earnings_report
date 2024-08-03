from fastapi import APIRouter, Depends, HTTPException, UploadFile, status, BackgroundTasks
import pandas as pd
import numpy as np
import joblib
from io import BytesIO
from typing import Annotated
from sqlalchemy.orm import Session
from ..auth.utils import get_current_user
from ..database.utils import get_db
from ..database.tables import Models
from ..models.earnings_forecasts import EarningsForecast
from ..earnings_utilities.earnings_forecasts_utils import MLUtils


router = APIRouter(
    tags=["Forecasts"],
    dependencies=[Depends(get_current_user)]
)

db_dependency = Annotated[Session, Depends(get_db)]

def load_ml_model(data, file_name, db):
    sql_data = Models(
        model_name = file_name,
        model = data
    )

    db.add(sql_data)
    db.commit()


@router.get("/view-models")
def get_model(db: db_dependency):
    results = db.query(Models.model_name).all()
    return {"models" : str(results)}

@router.post("/upload-model", status_code=status.HTTP_202_ACCEPTED)
async def upload_model(file: UploadFile, db: db_dependency, task: BackgroundTasks):
    """data = await file.read()
    print(type(data))
    sql_data = Models(
        model_name = file.filename,
        model = data
    )

    db.add(sql_data)
    db.commit()
    print("Model Successfully Uploaded")"""

    data = await file.read()

    task.add_task(load_ml_model, data, file.filename, db)
    return {"msg" : f"Uploading {file.filename} to db"}

@router.post("/forecast-eps")
async def forecast_eps(db: db_dependency, model: EarningsForecast):
    data = model.model_dump()
    ticker = data["symbol"]
    x = MLUtils().load_eps_feature_data(ticker)
    model_result = db.query(Models).filter(Models.model_name == 'eps_predictor_v2.pkl').first()
    binary_data = model_result.model
    model = MLUtils().load_model(binary_data)
    #model = joblib.load(BytesIO(binary_data))
    pred = model.predict(x)[0]
    return {"Forecasted EPS" : pred}


    