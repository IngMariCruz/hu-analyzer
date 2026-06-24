"""
Rate-limiting efímero por IP (Story 1.11).

slowapi mantiene los contadores SOLO en memoria (ventana deslizante); la IP nunca
se persiste en la base analítica. Protege el endpoint anónimo del abuso y del
costo del LLM.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
