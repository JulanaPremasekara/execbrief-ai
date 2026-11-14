"""Compare curl -N arrival timing against isolated real Uvicorn mock servers."""
import os
import subprocess
import sys
import time
import urllib.request

for diagnostic in ("0", "1"):
    env = dict(os.environ, EXECBRIEF_MODE="mock", MOCK_STREAM_DIAGNOSTIC=diagnostic)
    server = subprocess.Popen([sys.executable, "-m", "uvicorn", "execbrief.main:app", "--port", "8017"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                urllib.request.urlopen("http://127.0.0.1:8017/api/health", timeout=.2)
                break
            except Exception:
                time.sleep(.1)
        start = time.monotonic()
        curl = subprocess.Popen(["curl.exe", "-N", "-sS", "--max-time", "30", "-H", "Content-Type: application/json", "--data-binary", "@-", "http://127.0.0.1:8017/api/chat/stream"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        curl.stdin.write('{"question":"How is our company performing?"}')
        curl.stdin.close()
        arrivals = []
        for line in curl.stdout:
            if line.startswith("event:"):
                event = line.strip()[7:]
                arrivals.append((event, time.monotonic()-start))
                if event in ("text_delta", "chart", "done"):
                    print(diagnostic, event, round(arrivals[-1][1], 3), flush=True)
        assert curl.wait() == 0
        assert arrivals[-1][0] == "done"
        if diagnostic == "1":
            assert arrivals[-1][1] - next(t for e,t in arrivals if e == "text_delta") > .3
    finally:
        server.terminate()
        server.wait(timeout=10)
