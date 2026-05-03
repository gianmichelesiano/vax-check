from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="VaxCheck API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:80", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from vaxcheck.api.routers import patients, records, analysis, catalog

app.include_router(patients.router, prefix="/api")
app.include_router(records.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(catalog.router, prefix="/api")
