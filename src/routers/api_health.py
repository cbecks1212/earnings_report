from fastapi import APIRouter

router = APIRouter(
    tags=["Health"]
)

@router.get("/health-check", summary="Check if API is up")
def check_health():
    return {"status" : "healthy"}