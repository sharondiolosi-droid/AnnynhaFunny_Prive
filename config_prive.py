"""
===============================================
AnnynhaFunny_PriveBot - Configura??es
===============================================
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Token do Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN_PRIVE")

# Admin (seu ID) - separados por v?rgula
try:
    ADMIN_CHAT_IDS = [int(x.strip()) for x in os.getenv("ADMIN_CHAT_IDS", "0").split(",") if x.strip()]
except ValueError:
    ADMIN_CHAT_IDS = []

# Banco de dados
DATABASE_PATH = "prive_bot.db"

# Pre?os padr?o
PRECO_FAN = 29.90
PRECO_VIP = 79.90
PRECO_PRIVE = 299.90

# Prefixo dos canais
PREFIXO_FREE = "Hot_Prive_Free"
PREFIXO_FAN = "_Fans"
PREFIXO_VIP = "_VIP"
PREFIXO_PRIVE = "_Prive"

# Drops
DROP_DURATION_HOURS = 48
