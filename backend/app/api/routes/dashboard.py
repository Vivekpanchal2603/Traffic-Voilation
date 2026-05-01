from fastapi import APIRouter
from pydantic import BaseModel

from app.services.dashboard_service import (
    get_all_violations,
    delete_violation_by_id
)

router = APIRouter()


class PaidRequest(BaseModel):
    violation_id: str


@router.get("/violations")
def fetch_all_violations():
    return {
        "success": True,
        "data": get_all_violations()
    }


@router.delete("/violations/pay")
def mark_paid(data: PaidRequest):
    deleted = delete_violation_by_id(
        data.violation_id
    )

    return {
        "success": deleted
    }