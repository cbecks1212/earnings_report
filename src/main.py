from fastapi import FastAPI

from src.routers.earnings_statistics import router as earnings_summary_router
from src.routers.list_industries import router as industry_router
from src.routers.earnings_documents import router as earnings_doc_router

app = FastAPI()

app.include_router(earnings_summary_router)
app.include_router(industry_router)
app.include_router(earnings_doc_router)
