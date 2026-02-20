from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.chat import router
from app.routes.downloads import router as downloads_router
from app.routes.evaluations import router as evaluations_router

app = FastAPI(title="Duvo Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(downloads_router)
app.include_router(evaluations_router)
