from dotenv import load_dotenv

load_dotenv()

import logfire
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.chat import router

logfire.configure()
logfire.instrument_pydantic_ai()

app = FastAPI(title="Duvo Chat API")

logfire.instrument_fastapi(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
