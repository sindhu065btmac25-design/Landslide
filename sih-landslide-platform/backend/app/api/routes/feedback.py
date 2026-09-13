from fastapi import APIRouter

from schemas.domain import FeedbackRecord, FeedbackSubmission
from services.feedback.service import FeedbackService

router = APIRouter(prefix="/api/v1/feedback", tags=["feedback"])
service = FeedbackService()


@router.post("", response_model=FeedbackRecord)
async def submit_feedback(payload: FeedbackSubmission):
    return service.submit(payload)


@router.get("", response_model=list[FeedbackRecord])
async def list_feedback():
    return service.list_all()
