from fastapi import APIRouter
router = APIRouter()

@router.get("/api/health")
def health():
    from execbrief.core.runtime import execution_mode
    return {"status": "ok", "mode": execution_mode()}

