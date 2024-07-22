from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
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

@router.get("/view-models")
def get_model(db: db_dependency):
    results = db.query(Models.model_name).all()
    return {"models" : str(results)}

@router.post("/upload-model", status_code=status.HTTP_201_CREATED)
async def upload_model(file: UploadFile, db: db_dependency):
    data = await file.read()
    print(type(data))
    sql_data = Models(
        model_name = file.filename,
        model = data
    )

    db.add(sql_data)
    db.commit()

@router.post("/forecast-eps")
async def forecast_eps(db: db_dependency, model: EarningsForecast):
    data = model.model_dump()
    ticker = data["symbol"]
    x = MLUtils().load_eps_feature_data(ticker)
    model_result = db.query(Models).filter(Models.model_name == 'eps_predictor_v1.pkl').first()
    binary_data = model_result.model
    model = MLUtils().load_model(binary_data)
    #model = joblib.load(BytesIO(binary_data))
    pred = model.predict(x)[0]
    return {"Forecasted EPS" : pred}


    