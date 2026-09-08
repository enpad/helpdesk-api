from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.errors import DomainError, domain_error_handler
from app.routes import agents, comments, health, tickets
from app.storage import seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_data.load()
    yield


app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    debug=config.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(DomainError, domain_error_handler)

app.include_router(health.router)
app.include_router(tickets.router)
app.include_router(comments.router)
app.include_router(agents.router)
