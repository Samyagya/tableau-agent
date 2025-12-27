from fastapi import APIRouter

router = APIRouter()
#health check
@router.get("/health")
def health():
    return {"status": "ok"}
