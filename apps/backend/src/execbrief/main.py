from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from execbrief.api.routes import chat, health
from execbrief.core.config import FRONTEND_ORIGIN

app = FastAPI(title="ExecBrief AI")
app.add_middleware(CORSMiddleware, allow_origins=[FRONTEND_ORIGIN],
                   allow_methods=["GET","POST"], allow_headers=["Content-Type"])
app.include_router(chat.router)
app.include_router(health.router)

