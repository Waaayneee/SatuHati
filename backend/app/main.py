from fastapi import FastAPI

app = FastAPI(title="KawTeam API")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
