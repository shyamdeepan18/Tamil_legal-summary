"""Summary API routes - placeholder"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/summary/{upload_id}")
async def get_summary(upload_id: str):
    """Get summary for a processed document"""
    # TODO: Implement summary retrieval
    return {"message": "Summary endpoint - to be implemented"}
