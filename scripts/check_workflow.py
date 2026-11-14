"""Opt-in live SSE smoke check. Prints no credentials, provider bodies or business data."""
import os
from fastapi.testclient import TestClient
from execbrief.core import data_config
from execbrief.main import app
import json

def main():
    os.environ["EXECBRIEF_MODE"] = "live"
    try:
        response = TestClient(app).post("/api/chat/stream", json={
            "question": "How is our company performing over the last six months?"})
        response.raise_for_status()
        events = [(frame.splitlines()[0][7:], json.loads(frame.splitlines()[1][6:]))
                  for frame in response.text.strip().split("\n\n")]
        assert events[-1][0] == "done" and events[-1][1]["outcome"] == "completed"
        assert any(event == "text_delta" for event, _ in events)
        assert [p["sequence"] for _,p in events] == list(range(1,len(events)+1))
        print("Live executive question completed through FastAPI SSE. Review chart selection and evidence quality in the UI.")
        return 0
    except Exception:
        print("Live workflow failed. Run database and hosted-model checks; configure secrets locally.")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
