from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from app.api import agent_tools, approvals, audit, me, missions, profiles, users
from app.config import settings
from app.db import check_connection, get_engine
from app.services.errors import Conflict, DomainError, InvalidInput, NotFound, PermissionDenied, Refused

app = FastAPI(title="KawTeam API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Profile-Id"],
)

_STATUS_FOR_ERROR: list[tuple[type[DomainError], int]] = [
    (NotFound, 404),
    (PermissionDenied, 403),
    (Conflict, 409),
    (Refused, 422),
    (InvalidInput, 422),
]


@app.exception_handler(DomainError)
def _domain_error(_request: Request, exc: DomainError) -> JSONResponse:
    code = next((c for cls, c in _STATUS_FOR_ERROR if isinstance(exc, cls)), 400)
    return JSONResponse(status_code=code, content=jsonable_encoder({"detail": exc.message, **exc.details}))


@app.exception_handler(OperationalError)
def _database_unreachable(_request: Request, _exc: OperationalError) -> JSONResponse:
    # Handled here (inside CORS) so the browser gets a readable 503 instead of a network error.
    return JSONResponse(status_code=503, content={"detail": "Can't reach the database"})


@app.get("/health")
def health() -> dict:
    try:
        db_ok = check_connection(get_engine())
    except Exception:
        db_ok = False
    return {"status": "ok" if db_ok else "degraded", "database": "ok" if db_ok else "unreachable"}


app.include_router(me.router)
app.include_router(profiles.router)
app.include_router(missions.router)
app.include_router(approvals.router)
app.include_router(audit.router)
app.include_router(users.router)
app.include_router(agent_tools.router)
