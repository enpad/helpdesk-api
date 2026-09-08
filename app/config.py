"""Configuración de la aplicación."""

import os

APP_NAME = "Helpdesk API"
APP_VERSION = "2.3.0"

DEBUG = True

HOST = os.getenv("HELPDESK_HOST", "0.0.0.0")
PORT = int(os.getenv("HELPDESK_PORT", "8000"))

API_KEY = os.getenv("HELPDESK_API_KEY", "dev-secret-key-123")

CORS_ORIGINS = ["*"]

DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100
