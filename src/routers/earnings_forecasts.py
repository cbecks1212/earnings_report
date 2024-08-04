from fastapi import APIRouter, Depends, HTTPException, UploadFile, status, BackgroundTasks
import asyncio
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
ml_utils = MLUtils()

model_cache = {}

def load_ml_model(data, file_name, db):
    sql_data = Models(
        model_name=file_name,
        model=data
    )
    db.add(sql_data)
    db.commit()

async def load_model(binary_data, model_name):
    if model_name in model_cache:
        return model_cache[model_name]
    
    model = await asyncio.to_thread(joblib.load, BytesIO(binary_data))
    model_cache[model_name] = model
    return model

@router.get("/view-models")
def get_model(db: db_dependency):
    results = db.query(Models.model_name).all()
    return {"models": str(results)}

@router.post("/upload-model", status_code=status.HTTP_202_ACCEPTED)
async def upload_model(file: UploadFile, db: db_dependency, task: BackgroundTasks):
    data = await file.read()
    task.add_task(load_ml_model, data, file.filename, db)
    return {"msg": f"Uploading {file.filename} to db"}

@router.post("/forecast-eps")
async def forecast_eps(db: db_dependency, model: EarningsForecast):
    data = model.model_dump()
    ticker = data["symbol"]

    # Load feature data asynchronously
    x = await asyncio.to_thread(ml_utils.load_eps_feature_data, ticker)

    # Query model asynchronously
    model_result = await asyncio.to_thread(lambda: db.query(Models).filter(Models.model_name == 'eps_predictor_v2.pkl').first())
    if not model_result:
        raise HTTPException(status_code=404, detail="Model not found")

    binary_data = model_result.model

    # Load model asynchronously with caching
    loaded_model = await load_model(binary_data, model_result.model_name)
    
    # Make prediction asynchronously
    pred = await asyncio.to_thread(loaded_model.predict, x)
    
    return {"Forecasted EPS": pred[0].item()}
