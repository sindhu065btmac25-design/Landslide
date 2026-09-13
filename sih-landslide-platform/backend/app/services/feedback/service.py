"""Feedback storage. In-memory list here; production build writes to the
`feedback` table and feeds ai/pipelines/retraining (see §19)."""
import uuid
from datetime import datetime, timezone

from app.schemas.domain import FeedbackRecord, FeedbackSubmission

_STORE: list[FeedbackRecord] = []


class FeedbackService:
    def submit(self, payload: FeedbackSubmission) -> FeedbackRecord:
        record = FeedbackRecord(
            id=uuid.uuid4().hex, created_at=datetime.now(timezone.utc), **payload.model_dump()
        )
        _STORE.append(record)
        return record

    def list_all(self) -> list[FeedbackRecord]:
        return list(_STORE)

