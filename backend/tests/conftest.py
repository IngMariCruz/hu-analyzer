"""
Configuración de pruebas: define variables de entorno mínimas antes de
importar la app, para que `Settings()` no falle sin un `.env` real.
"""

import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("LLM_MODEL", "gpt-4o-mini")
