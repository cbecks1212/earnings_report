from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers.earnings_statistics import router as earnings_summary_router
from src.routers.list_industries import router as industry_router
from src.routers.earnings_documents import router as earnings_doc_router

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(earnings_summary_router)
app.include_router(industry_router)
app.include_router(earnings_doc_router)
