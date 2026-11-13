import json
import logging
from uuid import uuid4
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from execbrief.api.dependencies import get_chat
from execbrief.api.schemas.requests import ChatRequest
from execbrief.api.schemas.responses import ChartPayload

router = APIRouter()

@router.post("/api/chat/stream")
async def chat(body: ChatRequest, use_case=Depends(get_chat)):
    async def stream():
        common = dict(request_id=str(uuid4()), message_id=str(uuid4()))
        sequence = 0
        def encode(event, payload):
            nonlocal sequence
            sequence += 1
            return f"event: {event}\ndata: {json.dumps(dict(**common, sequence=sequence, **payload), allow_nan=False)}\n\n"
        iterator = use_case.execute(body.question, [h.model_dump() for h in body.history])
        try:
            async for event, payload in iterator:
                if event == "chart":
                    payload = ChartPayload.model_validate(payload).model_dump()
                yield encode(event, payload)
        except Exception:
            logging.getLogger(__name__).exception("Mock response failed")
            yield encode("error", dict(code="response_failed", message="Unable to complete response.", retryable=True))
            yield encode("done", dict(outcome="error", sources=[], stream_mode="mock"))
        finally:
            await iterator.aclose()
    return StreamingResponse(stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

