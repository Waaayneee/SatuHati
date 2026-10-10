import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from psycopg.errors import UndefinedTable
from sqlalchemy.exc import OperationalError, ProgrammingError
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.api import agent_tools, approvals, audit, me, missions, profiles, users
from app.config import settings
from app.db import check_connection, get_engine, tables_ready
from app.services.errors import Conflict, DomainError, InvalidInput, NotFound, PermissionDenied, Refused

logger = logging.getLogger("kawteam")

app = FastAPI(title="KawTeam API")


class _ErrorsAsJson:
    """Last-resort handler that sits inside CORS. Any unhandled error becomes a JSON 500 that
    still carries CORS headers, so the browser shows a message instead of "Failed to fetch"."""

    def __init__(self, inner: ASGIApp) -> None:
        self.inner = inner

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.inner(scope, receive, send)
            return
        started = False

        async def tracking_send(message: Message) -> None:
            nonlocal started
            if message["type"] == "http.response.start":
                started = True
            await send(message)

        try:
            await self.inner(scope, receive, tracking_send)
        except Exception:
            logger.exception("Unhandled error on %s %s", scope.get("method"), scope.get("path"))
            if started:
                raise
            response = JSONResponse(status_code=500, content={"detail": "Something went wrong on the server"})
            await response(scope, receive, send)


# Added before CORS so CORS wraps it (the last middleware added is the outermost).
app.add_middleware(_ErrorsAsJson)
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


@app.exception_handler(ProgrammingError)
def _database_error(_request: Request, exc: ProgrammingError) -> JSONResponse:
    if isinstance(exc.orig, UndefinedTable):
        # Reachable database without the KawTeam tables: migrations have not run.
        return JSONResponse(status_code=503, content={"detail": "The database has no KawTeam tables yet"})
    logger.error("Database error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Something went wrong on the server"})


@app.get("/health")
def health() -> dict:
    try:
        engine = get_engine()
        db_ok = check_connection(engine)
        tables_ok = db_ok and tables_ready(engine)
    except Exception:
        db_ok = tables_ok = False
    if not db_ok:
        database = "unreachable"
    elif not tables_ok:
        database = "no_tables"
    else:
        database = "ok"
    return {"status": "ok" if database == "ok" else "degraded", "database": database}


app.include_router(me.router)
app.include_router(profiles.router)
app.include_router(missions.router)
app.include_router(approvals.router)
app.include_router(audit.router)
app.include_router(users.router)
app.include_router(agent_tools.router)
