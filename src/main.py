from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from src.routers.earnings_statistics import router as earnings_summary_router
from src.routers.list_industries import router as industry_router
from src.routers.earnings_documents import router as earnings_doc_router
from src.routers.auth import router as auth_router

from.auth.utils import get_current_user
from .database import tables
from .database.database import ENGINE

app = FastAPI()
tables.Base.metadata.create_all(bind=ENGINE)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(earnings_summary_router)
app.include_router(industry_router)
app.include_router(earnings_doc_router)
