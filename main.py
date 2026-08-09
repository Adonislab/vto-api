import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import try_on, measurements

app = FastAPI(
    title="Virtual Try-On API",
    description="API modulaire d'essayage virtuel et d'estimation anatomique"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(try_on.router)
app.include_router(measurements.router)

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "API VTO opérationnelle"}