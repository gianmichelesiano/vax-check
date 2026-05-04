from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from vaxcheck.persistence.session import init_db

# Carica .env dalla root del progetto
load_dotenv(Path(__file__).resolve().parent.parent.parent.parent / ".env")

app = FastAPI(title="VaxCheck API", version="0.1.0")


@app.on_event("startup")
def _on_startup():
    """Ensure all DB tables + migrations on startup."""
    init_db()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:80", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from vaxcheck.api.routers import patients, records, analysis, catalog, ocr

app.include_router(patients.router, prefix="/api")
app.include_router(records.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(catalog.router, prefix="/api")
app.include_router(ocr.router)
