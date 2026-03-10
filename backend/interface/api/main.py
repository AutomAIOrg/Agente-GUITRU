import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .lifecycle.lifespan import lifespan
from .webhooks.whatsapp_webhook import router as whatsapp_webhook

logging.basicConfig(level=logging.INFO)

# Extraer CORS origins de variables de entorno
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000")
origins_list = [origin.strip() for origin in ALLOWED_ORIGINS.split(",")]

# Construcción de la app con FastAPI
app = FastAPI(title="MSR-Agent: GUITRU", lifespan=lifespan)

# Añadir Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Añadir router
app.include_router(whatsapp_webhook)
