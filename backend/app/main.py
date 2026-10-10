from fastapi import FastAPI

from app.db import check_connection, get_engine

app = FastAPI(title="KawTeam API")


@app.get("/health")
def health() -> dict:
    try:
        db_ok = check_connection(get_engine())
    except Exception:
        db_ok = False
    return {"status": "ok" if db_ok else "degraded", "database": "ok" if db_ok else "unreachable"}
