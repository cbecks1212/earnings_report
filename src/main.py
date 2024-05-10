from fastapi import FastAPI

from src.routers.earnings_statistics import router as earnings_summary_router

app = FastAPI()

app.include_router(earnings_summary_router)
