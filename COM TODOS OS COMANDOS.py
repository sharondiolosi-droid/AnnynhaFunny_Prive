Remove-Item bot_prive.py -Force -ErrorAction SilentlyContinue
Remove-Item config_prive.py -Force -ErrorAction SilentlyContinue
Remove-Item database_prive.py -Force -ErrorAction SilentlyContinue
Remove-Item requirements.txt -Force -ErrorAction SilentlyContinue
Remove-Item Dockerfile -Force -ErrorAction SilentlyContinue
Remove-Item railway.json -Force -ErrorAction SilentlyContinue
Remove-Item railway.toml -Force -ErrorAction SilentlyContinue

@'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "bot_prive.py"]
'@ | Out-File -FilePath Dockerfile -Encoding ascii

@'
python-telegram-bot==21.7
python-dotenv==1.0.1
qrcode==7.4.2
Pillow==10.1.0
'@ | Out-File -FilePath requirements.txt -Encoding ascii

@'
__pycache__/
*.pyc
*.pyo
*.pyd
*.db
*.sqlite
*.sqlite3
.env
.env.local
.env.*.local
.vscode/
.idea/
*.swp
*.swo
*.log
'@ | Out-File -FilePath .gitignore -Encoding ascii

@'
{
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "numReplicas": 1,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
'@ | Out-File -FilePath railway.json -Encoding ascii

@'
"""
===============================================
AnnynhaFunny_PriveBot - Bot Principal
===============================================
Bot que gerencia várias modelos com canais Free, FAN, VIP e PRIVE
===============================================
"""

import logging
import asyncio
import time
import os
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from telegram.constants import ParseMode
from dotenv import load_dotenv

from config_prive import *
from database_prive import *

load_dotenv()

# ── Logging ──
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════════
# COMANDOS PRINCIPAIS
# ════════════════════════════════════════════════════════════════

async def start(update, context):
    """Início do bot."""
    user = update.effective_user

    welcome = (
        "🔥 *AnnynhaFunny_PriveBot*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Olá, *{user.first_name}*! 👋\n\n"
        "💋 Conteúdo exclusivo das melhores modelos!\n\n"
        "👀 *Quem está no nosso catálogo?*\n"
    )

    modelos = get_modelos()
    if modelos:
        for m in modelos:
            welcome += f"\n💖 @{m['username']}\n"
            welcome += f"   ├ Free: {m['canal_free']}\n"
            welcome += f"   ├ FAN: {m['canal_fan']} - R$ {m['preco_fan']:.2f}\n"
            welcome += f"   ├ VIP: {m['canal_vip']} - R$ {m['preco_vip']:.2f}\n"
            welcome += f"   └ PRIVE: {m['canal_prive']} - R$ {m['preco_prive']:.2f}\n"
    else:
        welcome += "\n📢 *Em breve novas modelos!*\n"

    welcome += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
    welcome += "🔞 Conteúdo exclusivo para maiores de 18 anos."

    keyboard = [
        [InlineKeyboardButton("🎭 Ver Modelos", callback_data="modelos")],
        [InlineKeyboardButton("💎 Planos e Preços", callback_data="planos")],
        [InlineKeyboardButton("❓ Dúvidas", callback_data="faq")],
        [InlineKeyboardButton("📞 Suporte", callback_data="suporte")],
    ]

    await update.message.reply_text(welcome, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))

async def ver_modelos(update, context):
    """Lista todas as modelos."""
    modelos = get_modelos()

    if not modelos:
        await update.callback_query.edit_message_text(
            "📢 Nenhuma modelo cadastrada ainda.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Voltar", callback_data="menu")]])
        )
        return

    text = "🎭 *NOSSAS MODELOS*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    keyboard = []

    for m in modelos:
        text += f"💖 *{m['nome_completo']}*\n"
        text += f"   🔗 @{m['username']}\n"
        text += f"   📂 Free: {m['canal_free']}\n"
        text += f"   💰 FAN: R$ {m['preco_fan']:.2f}\n"
        text += f"   💰 VIP: R$ {m['preco_vip']:.2f}\n"
        text += f"   💰 PRIVE: R$ {m['preco_prive']:.2f}\n\n"

        keyboard.append([InlineKeyboardButton(f"🔥 Ver {m['nome_completo']}", callback_data=f"modelo_{m['id']}")])

    keyboard.append([InlineKeyboardButton("🏠 Menu Principal", callback_data="menu")])

    await update.callback_query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))

async def ver_planos(update, context):
    """Exibe planos e preços."""
    modelos = get_modelos()

    text = "💎 *PLANOS E PREÇOS*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"

    for m in modelos:
        text += f"💖 *{m['nome_completo']}* (@{m['username']})\n"
        text += f"   📂 Free: *GRÁTIS*\n"
        text += f"   🔥 FAN: *R$ {m['preco_fan']:.2f}*\n"
        text += f"   👑 VIP: *R$ {m['preco_vip']:.2f}*\n"
        text += f"   💎 PRIVE: *R$ {m['preco_prive']:.2f}*\n\n"

    text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "💳 *Formas de pagamento:*\n"
    text += "✅ PIX (aprovado em minutos)\n"
    text += "✅ Cartão de Crédito\n\n"
    text += "🔞 Conteúdo exclusivo para maiores de 18 anos."

    await update.callback_query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Voltar", callback_data="menu")]]))

# ════════════════════════════════════════════════════════════════
# COMANDOS ADMIN
# ════════════════════════════════════════════════════════════════

async def add_modelo(update, context):
    """Adiciona uma nova modelo."""
    if update.effective_user.id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("❌ Acesso negado.")
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "📝 *Como usar:*\n"
            "/add_modelo @username\n\n"
            "Exemplo: /add_modelo @bia\n\n"
            "Depois preencha as informações solicitadas.",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    username = args[0].replace("@", "")

    if get_modelo_by_username(username):
        await update.message.reply_text(f"❌ Modelo @{username} já está cadastrada!")
        return

    context.user_data["nova_modelo"] = {"username": username}

    await update.message.reply_text(
        f"📝 *Cadastro da @{username}*\n\n"
        "Digite o *nome completo* da modelo:",
        parse_mode=ParseMode.MARKDOWN
    )

    context.user_data["estado"] = "ADD_MODELO_NOME"

async def handle_add_modelo(update, context):
    """Processa o cadastro da modelo."""
    user_id = update.effective_user.id
    user_data = context.user_data
    text = update.message.text

    if user_data.get("estado") == "ADD_MODELO_NOME":
        user_data["nova_modelo"]["nome"] = text
        user_data["estado"] = "ADD_MODELO_PRECO_FAN"
        await update.message.reply_text(
            f"✅ Nome salvo: *{text}*\n\n"
            "Digite o *preço FAN* (ex: 29.90):",
            parse_mode=ParseMode.MARKDOWN
        )

    elif user_data.get("estado") == "ADD_MODELO_PRECO_FAN":
        try:
            preco_fan = float(text.replace(",", "."))
            user_data["nova_modelo"]["preco_fan"] = preco_fan
            user_data["estado"] = "ADD_MODELO_PRECO_VIP"
            await update.message.reply_text(
                f"✅ Preço FAN: R$ {preco_fan:.2f}\n\n"
                "Digite o *preço VIP* (ex: 79.90):",
                parse_mode=ParseMode.MARKDOWN
            )
        except ValueError:
            await update.message.reply_text("❌ Valor inválido. Digite um número (ex: 29.90):")

    elif user_data.get("estado") == "ADD_MODELO_PRECO_VIP":
        try:
            preco_vip = float(text.replace(",", "."))
            user_data["nova_modelo"]["preco_vip"] = preco_vip
            user_data["estado"] = "ADD_MODELO_PRECO_PRIVE"
            await update.message.reply_text(
                f"✅ Preço VIP: R$ {preco_vip:.2f}\n\n"
                "Digite o *preço PRIVE* (ex: 299.90):",
                parse_mode=ParseMode.MARKDOWN
            )
        except ValueError:
            await update.message.reply_text("❌ Valor inválido. Digite um número (ex: 79.90):")

    elif user_data.get("estado") == "ADD_MODELO_PRECO_PRIVE":
        try:
            preco_prive = float(text.replace(",", "."))
            data = user_data["nova_modelo"]
            data["preco_prive"] = preco_prive

            resultado = add_modelo(
                username=data["username"],
                nome_completo=data["nome"],
                preco_fan=data["preco_fan"],
                preco_vip=data["preco_vip"],
                preco_prive=preco_prive
            )

            user_data["estado"] = None

            await update.message.reply_text(
                f"✅ *MODELO CADASTRADA COM SUCESSO!*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"💖 *{resultado['nome']}*\n"
                f"🔗 @{resultado['username']}\n\n"
                f"📂 *CANAIS:*\n"
                f"   Free: {resultado['canal_free']}\n"
                f"   FAN: {resultado['canal_fan']} - R$ {data['preco_fan']:.2f}\n"
                f"   VIP: {resultado['canal_vip']} - R$ {data['preco_vip']:.2f}\n"
                f"   PRIVE: {resultado['canal_prive']} - R$ {preco_prive:.2f}\n\n"
                "📌 *Próximos passos:*\n"
                "1. Adicione o bot como admin nos canais\n"
                "2. Use /drop @modelo VIP para postar conteúdo\n"
                "3. Divulgue os canais! 🚀",
                parse_mode=ParseMode.MARKDOWN
            )

        except ValueError:
            await update.message.reply_text("❌ Valor inválido. Digite um número (ex: 299.90):")

async def drop(update, context):
    """Posta um drop em um canal específico."""
    if update.effective_user.id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("❌ Acesso negado.")
        return

    args = context.args
    if not args or len(args) < 2:
        await update.message.reply_text(
            "📝 *Como usar:*\n"
            "/drop @modelo VIP\n\n"
            "Exemplo: /drop @bia VIP\n"
            "/drop @sheron FAN\n\n"
            "Opções: FAN, VIP, PRIVE",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    username = args[0].replace("@", "")
    canal_tipo = args[1].upper()

    if canal_tipo not in ["FAN", "VIP", "PRIVE"]:
        await update.message.reply_text("❌ Canal inválido. Use: FAN, VIP ou PRIVE")
        return

    modelo = get_modelo_by_username(username)
    if not modelo:
        await update.message.reply_text(f"❌ Modelo @{username} não encontrada!")
        return

    context.user_data["drop"] = {
        "modelo_id": modelo["id"],
        "canal_tipo": canal_tipo,
        "canal": modelo[f"canal_{canal_tipo.lower()}"]
    }

    await update.message.reply_text(
        f"📤 *Enviando drop para {modelo['nome_completo']} ({canal_tipo})*\n\n"
        "Envie a *foto ou vídeo* que deseja postar:",
        parse_mode=ParseMode.MARKDOWN
    )

    context.user_data["estado"] = "DROP_MIDIA"

async def handle_drop(update, context):
    """Processa o envio do drop."""
    user_id = update.effective_user.id
    user_data = context.user_data

    if user_data.get("estado") != "DROP_MIDIA":
        return

    drop_info = user_data.get("drop")
    if not drop_info:
        await update.message.reply_text("❌ Erro: Drop não iniciado.")
        return

    file_id = None
    tipo_midia = None

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        tipo_midia = "photo"
    elif update.message.video:
        file_id = update.message.video.file_id
        tipo_midia = "video"
    elif update.message.document:
        file_id = update.message.document.file_id
        tipo_midia = "document"
    else:
        await update.message.reply_text("❌ Envie uma foto, vídeo ou documento.")
        return

    caption = update.message.caption or ""

    if not caption:
        caption = "🔥 *DROP EXCLUSIVO!*\n\nNão compartilhe! 🔞"
    else:
        caption += "\n\n🔥 *Não compartilhe! 🔞"

    caption += f"\n\n⏳ *Disponível por {DROP_DURATION_HOURS}h*"

    add_drop(
        modelo_id=drop_info["modelo_id"],
        canal_tipo=drop_info["canal_tipo"],
        file_id=file_id,
        tipo_midia=tipo_midia,
        caption=caption
    )

    try:
        canal = drop_info["canal"]

        if tipo_midia == "photo":
            await context.bot.send_photo(
                chat_id=canal,
                photo=file_id,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN
            )
        elif tipo_midia == "video":
            await context.bot.send_video(
                chat_id=canal,
                video=file_id,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await context.bot.send_document(
                chat_id=canal,
                document=file_id,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN
            )

        user_data["estado"] = None
        user_data["drop"] = None

        await update.message.reply_text(
            f"✅ *DROP ENVIADO COM SUCESSO!*\n\n"
            f"📤 Canal: {canal}\n"
            f"⏳ Válido por {DROP_DURATION_HOURS}h",
            parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao enviar: {e}")

async def drop_all(update, context):
    """Posta em todas as VIPs simultaneamente."""
    if update.effective_user.id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("❌ Acesso negado.")
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "📝 /drop_all VIP - Posta em todas VIPs\n"
            "/drop_all FAN - Posta em todas FANs",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    canal_tipo = args[0].upper()
    if canal_tipo not in ["FAN", "VIP", "PRIVE"]:
        await update.message.reply_text("❌ Use: FAN, VIP ou PRIVE")
        return

    modelos = get_modelos()
    if not modelos:
        await update.message.reply_text("❌ Nenhuma modelo cadastrada.")
        return

    context.user_data["drop_all"] = {
        "modelos": modelos,
        "canal_tipo": canal_tipo
    }

    await update.message.reply_text(
        f"📤 *Drop ALL ({canal_tipo})*\n\n"
        f"Será enviado para {len(modelos)} modelo(s).\n\n"
        "Envie a *foto ou vídeo* que deseja postar em TODOS os canais:",
        parse_mode=ParseMode.MARKDOWN
    )

    context.user_data["estado"] = "DROP_ALL_MIDIA"

async def handle_drop_all(update, context):
    """Processa o drop_all."""
    user_id = update.effective_user.id
    user_data = context.user_data

    if user_data.get("estado") != "DROP_ALL_MIDIA":
        return

    drop_info = user_data.get("drop_all")
    if not drop_info:
        await update.message.reply_text("❌ Erro.")
        return

    file_id = None
    tipo_midia = None

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        tipo_midia = "photo"
    elif update.message.video:
        file_id = update.message.video.file_id
        tipo_midia = "video"
    else:
        await update.message.reply_text("❌ Envie uma foto ou vídeo.")
        return

    caption = update.message.caption or "🔥 *DROP COLETIVO!*\n\nNão compartilhe! 🔞"
    caption += f"\n\n⏳ *Disponível por {DROP_DURATION_HOURS}h*"

    modelos = drop_info["modelos"]
    canal_tipo = drop_info["canal_tipo"]

    enviados = 0
    for modelo in modelos:
        try:
            canal = modelo[f"canal_{canal_tipo.lower()}"]

            if tipo_midia == "photo":
                await context.bot.send_photo(
                    chat_id=canal,
                    photo=file_id,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await context.bot.send_video(
                    chat_id=canal,
                    video=file_id,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN
                )
            enviados += 1
        except Exception as e:
            logger.error(f"Erro ao enviar para {modelo['username']}: {e}")

    user_data["estado"] = None
    user_data["drop_all"] = None

    await update.message.reply_text(
        f"✅ *DROP ALL ENVIADO!*\n\n"
        f"📤 {enviados}/{len(modelos)} canais receberam o conteúdo.\n"
        f"📂 Canal: {canal_tipo}\n"
        f"⏳ Válido por {DROP_DURATION_HOURS}h",
        parse_mode=ParseMode.MARKDOWN
    )

async def relatorio(update, context):
    """Mostra relatório de vendas por modelo."""
    if update.effective_user.id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("❌ Acesso negado.")
        return

    modelos = get_modelos()
    if not modelos:
        await update.message.reply_text("📊 Nenhuma modelo cadastrada.")
        return

    text = "📊 *RELATÓRIO DE VENDAS*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"

    for m in modelos:
        text += f"💖 *{m['nome_completo']}*\n"
        text += f"   🔗 @{m['username']}\n"
        text += f"   📂 Free: {m['canal_free']}\n"
        text += f"   💰 FAN: R$ {m['preco_fan']:.2f}\n"
        text += f"   💰 VIP: R$ {m['preco_vip']:.2f}\n"
        text += f"   💰 PRIVE: R$ {m['preco_prive']:.2f}\n\n"

    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def listar_modelos(update, context):
    """Lista todas as modelos (admin)."""
    if update.effective_user.id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("❌ Acesso negado.")
        return

    modelos = get_modelos()
    if not modelos:
        await update.message.reply_text("📋 Nenhuma modelo cadastrada.")
        return

    text = "📋 *MODELOS CADASTRADAS*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for m in modelos:
        text += f"{m['id']}. 💖 *{m['nome_completo']}*\n"
        text += f"   🔗 @{m['username']}\n"
        text += f"   📂 Free: {m['canal_free']}\n"
        text += f"   💰 FAN: R$ {m['preco_fan']:.2f}\n"
        text += f"   💰 VIP: R$ {m['preco_vip']:.2f}\n"
        text += f"   💰 PRIVE: R$ {m['preco_prive']:.2f}\n"
        text += f"   📅 Criada: {m['criado_em'][:10]}\n\n"

    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ════════════════════════════════════════════════════════════════
# HANDLER PRINCIPAL
# ════════════════════════════════════════════════════════════════

async def button(update, context):
    """Gerenciador de botões."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "menu":
        await start(update, context)
    elif data == "modelos":
        await ver_modelos(update, context)
    elif data == "planos":
        await ver_planos(update, context)
    elif data == "faq":
        await query.edit_message_text(
            "❓ *PERGUNTAS FREQUENTES*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔹 *Como acessar o conteúdo?*\n"
            "Assine o plano desejado e receba acesso aos canais.\n\n"
            "🔹 *Quais formas de pagamento?*\n"
            "✅ PIX\n"
            "✅ Cartão de Crédito\n\n"
            "🔹 *Posso cancelar?*\n"
            "Sim, a qualquer momento.\n\n"
            "🔹 *O conteúdo é exclusivo?*\n"
            "Sim, conteúdo 100% original.\n\n"
            "🔞 Conteúdo para maiores de 18 anos.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Voltar", callback_data="menu")]])
        )
    elif data == "suporte":
        await query.edit_message_text(
            "📞 *SUPORTE*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📱 WhatsApp: +5511940462611\n"
            "📧 Email: suporte@annynhafunny.com\n\n"
            "💚 Atendimento humanizado!",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Voltar", callback_data="menu")]])
        )

# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════

async def main_async():
    print("=" * 60)
    print("🔥 AnnynhaFunny_PriveBot - Iniciando...")
    print("=" * 60)

    init_db()
    print("✅ Banco de dados: prive_bot.db")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Comandos do bot
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", start))

    # Comandos Admin
    app.add_handler(CommandHandler("add_modelo", add_modelo))
    app.add_handler(CommandHandler("drop", drop))
    app.add_handler(CommandHandler("drop_all", drop_all))
    app.add_handler(CommandHandler("relatorio", relatorio))
    app.add_handler(CommandHandler("modelos", listar_modelos))

    # Handlers
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, handle_drop))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, handle_drop_all))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_add_modelo))

    print("🚀 Bot rodando!")
    print("=" * 60)

    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)

    await asyncio.Event().wait()

def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n🛑 Bot finalizado.")

if __name__ == "__main__":
    main()
'@ | Out-File -FilePath bot_prive.py -Encoding ascii

@'
"""
===============================================
AnnynhaFunny_PriveBot - Configurações
===============================================
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Token do Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN_PRIVE")

# Admin (seu ID) - separados por vírgula
try:
    ADMIN_CHAT_IDS = [int(x.strip()) for x in os.getenv("ADMIN_CHAT_IDS", "0").split(",") if x.strip()]
except ValueError:
    ADMIN_CHAT_IDS = []

# Banco de dados
DATABASE_PATH = "prive_bot.db"

# Preços padrão
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
'@ | Out-File -FilePath config_prive.py -Encoding ascii

@'
"""
===============================================
AnnynhaFunny_PriveBot - Banco de Dados
===============================================
"""

import sqlite3
import json
from datetime import datetime, timedelta

DATABASE_PATH = "prive_bot.db"

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS modelos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            nome_completo TEXT NOT NULL,
            canal_free TEXT NOT NULL,
            canal_fan TEXT NOT NULL,
            canal_vip TEXT NOT NULL,
            canal_prive TEXT NOT NULL,
            preco_fan REAL DEFAULT 29.90,
            preco_vip REAL DEFAULT 79.90,
            preco_prive REAL DEFAULT 299.90,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ativo BOOLEAN DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS drops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modelo_id INTEGER NOT NULL,
            canal_tipo TEXT NOT NULL,
            mensagem_id INTEGER,
            file_id TEXT,
            tipo_midia TEXT,
            caption TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expira_em TIMESTAMP,
            FOREIGN KEY (modelo_id) REFERENCES modelos(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assinantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            modelo_id INTEGER NOT NULL,
            plano TEXT NOT NULL,
            ativo BOOLEAN DEFAULT 1,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expira_em TIMESTAMP,
            FOREIGN KEY (modelo_id) REFERENCES modelos(id)
        )
    """)

    conn.commit()
    conn.close()

# ────────────────────────────────────────────
# MODELOS
# ────────────────────────────────────────────

def add_modelo(username, nome_completo, preco_fan=29.90, preco_vip=79.90, preco_prive=299.90):
    conn = get_connection()
    cursor = conn.cursor()

    canal_free = f"@{username}{PREFIXO_FREE}"
    canal_fan = f"@{username}{PREFIXO_FAN}"
    canal_vip = f"@{username}{PREFIXO_VIP}"
    canal_prive = f"@{username}{PREFIXO_PRIVE}"

    cursor.execute("""
        INSERT INTO modelos (username, nome_completo, canal_free, canal_fan, canal_vip, canal_prive,
                            preco_fan, preco_vip, preco_prive)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, nome_completo, canal_free, canal_fan, canal_vip, canal_prive,
          preco_fan, preco_vip, preco_prive))

    conn.commit()
    modelo_id = cursor.lastrowid
    conn.close()

    return {
        "id": modelo_id,
        "username": username,
        "nome": nome_completo,
        "canal_free": canal_free,
        "canal_fan": canal_fan,
        "canal_vip": canal_vip,
        "canal_prive": canal_prive
    }

def get_modelos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM modelos WHERE ativo = 1 ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_modelo_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM modelos WHERE username = ? AND ativo = 1", (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_modelo_by_id(modelo_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM modelos WHERE id = ? AND ativo = 1", (modelo_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# ────────────────────────────────────────────
# DROPS
# ────────────────────────────────────────────

def add_drop(modelo_id, canal_tipo, file_id, tipo_midia, caption="", expira_horas=48):
    conn = get_connection()
    cursor = conn.cursor()

    expira_em = datetime.now() + timedelta(hours=expira_horas)

    cursor.execute("""
        INSERT INTO drops (modelo_id, canal_tipo, file_id, tipo_midia, caption, expira_em)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (modelo_id, canal_tipo, file_id, tipo_midia, caption, expira_em.isoformat()))

    conn.commit()
    drop_id = cursor.lastrowid
    conn.close()
    return drop_id

def get_drops(modelo_id, canal_tipo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM drops
        WHERE modelo_id = ? AND canal_tipo = ?
        ORDER BY criado_em DESC LIMIT 10
    """, (modelo_id, canal_tipo))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ────────────────────────────────────────────
# ASSINANTES
# ────────────────────────────────────────────

def add_assinante(telegram_id, modelo_id, plano, expira_dias=30):
    conn = get_connection()
    cursor = conn.cursor()

    expira_em = datetime.now() + timedelta(days=expira_dias)

    cursor.execute("""
        INSERT INTO assinantes (telegram_id, modelo_id, plano, expira_em)
        VALUES (?, ?, ?, ?)
    """, (telegram_id, modelo_id, plano, expira_em.isoformat()))

    conn.commit()
    assinante_id = cursor.lastrowid
    conn.close()
    return assinante_id

def get_assinantes(modelo_id, plano=None):
    conn = get_connection()
    cursor = conn.cursor()

    if plano:
        cursor.execute("""
            SELECT * FROM assinantes
            WHERE modelo_id = ? AND plano = ? AND ativo = 1
        """, (modelo_id, plano))
    else:
        cursor.execute("""
            SELECT * FROM assinantes
            WHERE modelo_id = ? AND ativo = 1
        """, (modelo_id,))

    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_assinante(telegram_id, modelo_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM assinantes
        WHERE telegram_id = ? AND modelo_id = ? AND ativo = 1
    """, (telegram_id, modelo_id))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def renovar_assinante(assinante_id, dias=30):
    conn = get_connection()
    cursor = conn.cursor()

    nova_expira = datetime.now() + timedelta(days=dias)

    cursor.execute("""
        UPDATE assinantes
        SET expira_em = ?, ativo = 1
        WHERE id = ?
    """, (nova_expira.isoformat(), assinante_id))

    conn.commit()
    conn.close()

def cancelar_assinante(assinante_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE assinantes SET ativo = 0 WHERE id = ?
    """, (assinante_id,))

    conn.commit()
    conn.close()
'@ | Out-File -FilePath database_prive.py -Encoding ascii

cat Dockerfile | Select-Object -First 1
# DEVE mostrar: FROM python:3.11-slim

cat bot_prive.py | Select-Object -First 1
# DEVE mostrar: """

cat requirements.txt | Select-Object -First 1
# DEVE mostrar: python-telegram-bot==21.7

cat railway.json | Select-Object -First 1
# DEVE mostrar: {

git add .
git commit -m "Versao completa com todos os arquivos corrigidos"
git push -u origin main --force

# Ler o arquivo atual
$content = Get-Content bot_prive.py -Raw

# Adicionar a função suporte antes do main_async
$newContent = $content -replace '(async def main_async\(\):)', @'
async def suporte(update, context):
    text = (
        "📞 *SUPORTE AnnynhaFunny_PriveBot*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📱 *WhatsApp:* +5511940462611\n"
        "📧 *Email:* suporte@annynhafunny.com\n"
        "💬 *Telegram:* @AnynhaFunny_PriveBot\n\n"
        "🕐 *Horário de atendimento:*\n"
        "Segunda a Sexta: 09:00 - 18:00\n"
        "Sábado: 09:00 - 14:00\n\n"
        "💚 *Atendimento humanizado e rápido!*"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

$1
'@

# Adicionar o handler no main_async
$newContent = $newContent -replace '(app.add_handler\(CommandHandler\("modelos", listar_modelos\)\))', '$1
    app.add_handler(CommandHandler("suporte", suporte))'

# Salvar o arquivo
$newContent | Out-File -FilePath bot_prive.py -Encoding ascii

Write-Host "✅ Comando /suporte adicionado!"

git add bot_prive.py
git commit -m "Adiciona comando /suporte"
git push -u origin main

@'
"""
===============================================
AnnynhaFunny_PriveBot - Bot Principal
===============================================
"""

import logging
import asyncio
import os
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from telegram.constants import ParseMode
from dotenv import load_dotenv

from config_prive import *
from database_prive import *

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════════
# COMANDOS PRINCIPAIS
# ════════════════════════════════════════════════════════════════

async def start(update, context):
    """Início do bot."""
    user = update.effective_user
    
    welcome = (
        "🔥 *AnnynhaFunny_PriveBot*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Olá, *{user.first_name}*! 👋\n\n"
        "💋 Conteúdo exclusivo das melhores modelos!\n\n"
        "👀 *Quem está no nosso catálogo?*\n"
    )
    
    modelos = get_modelos()
    if modelos:
        for m in modelos:
            welcome += f"\n💖 @{m['username']}\n"
            welcome += f"   ├ Free: {m['canal_free']}\n"
            welcome += f"   ├ FAN: {m['canal_fan']} - R$ {m['preco_fan']:.2f}\n"
            welcome += f"   ├ VIP: {m['canal_vip']} - R$ {m['preco_vip']:.2f}\n"
            welcome += f"   └ PRIVE: {m['canal_prive']} - R$ {m['preco_prive']:.2f}\n"
    else:
        welcome += "\n📢 *Em breve novas modelos!*\n"
    
    welcome += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
    welcome += "🔞 Conteúdo exclusivo para maiores de 18 anos."
    
    keyboard = [
        [InlineKeyboardButton("🎭 Ver Modelos", callback_data="modelos")],
        [InlineKeyboardButton("💎 Planos e Preços", callback_data="planos")],
        [InlineKeyboardButton("❓ Dúvidas", callback_data="faq")],
        [InlineKeyboardButton("📞 Suporte", callback_data="suporte")],
    ]
    
    await update.message.reply_text(welcome, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))

async def ver_modelos(update, context):
    """Lista todas as modelos."""
    modelos = get_modelos()
    
    if not modelos:
        await update.callback_query.edit_message_text(
            "📢 Nenhuma modelo cadastrada ainda.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Voltar", callback_data="menu")]])
        )
        return
    
    text = "🎭 *NOSSAS MODELOS*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    keyboard = []
    
    for m in modelos:
        text += f"💖 *{m['nome_completo']}*\n"
        text += f"   🔗 @{m['username']}\n"
        text += f"   📂 Free: {m['canal_free']}\n"
        text += f"   💰 FAN: R$ {m['preco_fan']:.2f}\n"
        text += f"   💰 VIP: R$ {m['preco_vip']:.2f}\n"
        text += f"   💰 PRIVE: R$ {m['preco_prive']:.2f}\n\n"
        
        keyboard.append([InlineKeyboardButton(f"🔥 Ver {m['nome_completo']}", callback_data=f"modelo_{m['id']}")])
    
    keyboard.append([InlineKeyboardButton("🏠 Menu Principal", callback_data="menu")])
    
    await update.callback_query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))

async def ver_planos(update, context):
    """Exibe planos e preços."""
    modelos = get_modelos()
    
    text = "💎 *PLANOS E PREÇOS*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for m in modelos:
        text += f"💖 *{m['nome_completo']}* (@{m['username']})\n"
        text += f"   📂 Free: *GRÁTIS*\n"
        text += f"   🔥 FAN: *R$ {m['preco_fan']:.2f}*\n"
        text += f"   👑 VIP: *R$ {m['preco_vip']:.2f}*\n"
        text += f"   💎 PRIVE: *R$ {m['preco_prive']:.2f}*\n\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "💳 *Formas de pagamento:*\n"
    text += "✅ PIX (aprovado em minutos)\n"
    text += "✅ Cartão de Crédito\n\n"
    text += "🔞 Conteúdo exclusivo para maiores de 18 anos."
    
    await update.callback_query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Voltar", callback_data="menu")]]))

async def faq(update, context):
    """Perguntas frequentes."""
    text = (
        "❓ *PERGUNTAS FREQUENTES*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔹 *Como acessar o conteúdo?*\n"
        "Assine o plano desejado e receba acesso aos canais.\n\n"
        "🔹 *Quais formas de pagamento?*\n"
        "✅ PIX\n"
        "✅ Cartão de Crédito\n\n"
        "🔹 *Posso cancelar?*\n"
        "Sim, a qualquer momento.\n\n"
        "🔹 *O conteúdo é exclusivo?*\n"
        "Sim, conteúdo 100% original.\n\n"
        "🔞 Conteúdo para maiores de 18 anos."
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def suporte(update, context):
    """Comando de suporte."""
    text = (
        "📞 *SUPORTE AnnynhaFunny_PriveBot*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📱 *WhatsApp:* +5511940462611\n"
        "📧 *Email:* suporte@annynhafunny.com\n"
        "💬 *Telegram:* @AnynhaFunny_PriveBot\n\n"
        "🕐 *Horário de atendimento:*\n"
        "Segunda a Sexta: 09:00 - 18:00\n"
        "Sábado: 09:00 - 14:00\n\n"
        "💚 *Atendimento humanizado e rápido!*"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ════════════════════════════════════════════════════════════════
# COMANDOS ADMIN
# ════════════════════════════════════════════════════════════════

async def add_modelo(update, context):
    """Adiciona uma nova modelo."""
    if update.effective_user.id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    args = context.args
    if not args:
        await update.message.reply_text(
            "📝 *Como usar:*\n"
            "/add_modelo @username\n\n"
            "Exemplo: /add_modelo @bia\n\n"
            "Depois preencha as informações solicitadas.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    username = args[0].replace("@", "")
    
    if get_modelo_by_username(username):
        await update.message.reply_text(f"❌ Modelo @{username} já está cadastrada!")
        return
    
    context.user_data["nova_modelo"] = {"username": username}
    
    await update.message.reply_text(
        f"📝 *Cadastro da @{username}*\n\n"
        "Digite o *nome completo* da modelo:",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data["estado"] = "ADD_MODELO_NOME"

async def handle_add_modelo(update, context):
    """Processa o cadastro da modelo."""
    user_data = context.user_data
    text = update.message.text
    
    if user_data.get("estado") == "ADD_MODELO_NOME":
        user_data["nova_modelo"]["nome"] = text
        user_data["estado"] = "ADD_MODELO_PRECO_FAN"
        await update.message.reply_text(
            f"✅ Nome salvo: *{text}*\n\n"
            "Digite o *preço FAN* (ex: 29.90):",
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif user_data.get("estado") == "ADD_MODELO_PRECO_FAN":
        try:
            preco_fan = float(text.replace(",", "."))
            user_data["nova_modelo"]["preco_fan"] = preco_fan
            user_data["estado"] = "ADD_MODELO_PRECO_VIP"
            await update.message.reply_text(
                f"✅ Preço FAN: R$ {preco_fan:.2f}\n\n"
                "Digite o *preço VIP* (ex: 79.90):",
                parse_mode=ParseMode.MARKDOWN
            )
        except ValueError:
            await update.message.reply_text("❌ Valor inválido. Digite um número (ex: 29.90):")
    
    elif user_data.get("estado") == "ADD_MODELO_PRECO_VIP":
        try:
            preco_vip = float(text.replace(",", "."))
            user_data["nova_modelo"]["preco_vip"] = preco_vip
            user_data["estado"] = "ADD_MODELO_PRECO_PRIVE"
            await update.message.reply_text(
                f"✅ Preço VIP: R$ {preco_vip:.2f}\n\n"
                "Digite o *preço PRIVE* (ex: 299.90):",
                parse_mode=ParseMode.MARKDOWN
            )
        except ValueError:
            await update.message.reply_text("❌ Valor inválido. Digite um número (ex: 79.90):")
    
    elif user_data.get("estado") == "ADD_MODELO_PRECO_PRIVE":
        try:
            preco_prive = float(text.replace(",", "."))
            data = user_data["nova_modelo"]
            data["preco_prive"] = preco_prive
            
            resultado = add_modelo(
                username=data["username"],
                nome_completo=data["nome"],
                preco_fan=data["preco_fan"],
                preco_vip=data["preco_vip"],
                preco_prive=preco_prive
            )
            
            user_data["estado"] = None
            
            await update.message.reply_text(
                f"✅ *MODELO CADASTRADA COM SUCESSO!*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"💖 *{resultado['nome']}*\n"
                f"🔗 @{resultado['username']}\n\n"
                f"📂 *CANAIS:*\n"
                f"   Free: {resultado['canal_free']}\n"
                f"   FAN: {resultado['canal_fan']} - R$ {data['preco_fan']:.2f}\n"
                f"   VIP: {resultado['canal_vip']} - R$ {data['preco_vip']:.2f}\n"
                f"   PRIVE: {resultado['canal_prive']} - R$ {preco_prive:.2f}\n\n"
                "📌 *Próximos passos:*\n"
                "1. Adicione o bot como admin nos canais\n"
                "2. Use /drop @modelo VIP para postar conteúdo\n"
                "3. Divulgue os canais! 🚀",
                parse_mode=ParseMode.MARKDOWN
            )
            
        except ValueError:
            await update.message.reply_text("❌ Valor inválido. Digite um número (ex: 299.90):")

async def drop(update, context):
    """Posta um drop em um canal específico."""
    if update.effective_user.id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    args = context.args
    if not args or len(args) < 2:
        await update.message.reply_text(
            "📝 *Como usar:*\n"
            "/drop @modelo VIP\n\n"
            "Exemplo: /drop @bia VIP\n"
            "/drop @sheron FAN\n\n"
            "Opções: FAN, VIP, PRIVE",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    username = args[0].replace("@", "")
    canal_tipo = args[1].upper()
    
    if canal_tipo not in ["FAN", "VIP", "PRIVE"]:
        await update.message.reply_text("❌ Canal inválido. Use: FAN, VIP ou PRIVE")
        return
    
    modelo = get_modelo_by_username(username)
    if not modelo:
        await update.message.reply_text(f"❌ Modelo @{username} não encontrada!")
        return
    
    context.user_data["drop"] = {
        "modelo_id": modelo["id"],
        "canal_tipo": canal_tipo,
        "canal": modelo[f"canal_{canal_tipo.lower()}"]
    }
    
    await update.message.reply_text(
        f"📤 *Enviando drop para {modelo['nome_completo']} ({canal_tipo})*\n\n"
        "Envie a *foto ou vídeo* que deseja postar:",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data["estado"] = "DROP_MIDIA"

async def handle_drop(update, context):
    """Processa o envio do drop."""
    user_data = context.user_data
    
    if user_data.get("estado") != "DROP_MIDIA":
        return
    
    drop_info = user_data.get("drop")
    if not drop_info:
        await update.message.reply_text("❌ Erro: Drop não iniciado.")
        return
    
    file_id = None
    tipo_midia = None
    
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        tipo_midia = "photo"
    elif update.message.video:
        file_id = update.message.video.file_id
        tipo_midia = "video"
    elif update.message.document:
        file_id = update.message.document.file_id
        tipo_midia = "document"
    else:
        await update.message.reply_text("❌ Envie uma foto, vídeo ou documento.")
        return
    
    caption = update.message.caption or ""
    
    if not caption:
        caption = "🔥 *DROP EXCLUSIVO!*\n\nNão compartilhe! 🔞"
    else:
        caption += "\n\n🔥 *Não compartilhe! 🔞"
    
    caption += f"\n\n⏳ *Disponível por {DROP_DURATION_HOURS}h*"
    
    add_drop(
        modelo_id=drop_info["modelo_id"],
        canal_tipo=drop_info["canal_tipo"],
        file_id=file_id,
        tipo_midia=tipo_midia,
        caption=caption
    )
    
    try:
        canal = drop_info["canal"]
        
        if tipo_midia == "photo":
            await context.bot.send_photo(
                chat_id=canal,
                photo=file_id,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN
            )
        elif tipo_midia == "video":
            await context.bot.send_video(
                chat_id=canal,
                video=file_id,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await context.bot.send_document(
                chat_id=canal,
                document=file_id,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN
            )
        
        user_data["estado"] = None
        user_data["drop"] = None
        
        await update.message.reply_text(
            f"✅ *DROP ENVIADO COM SUCESSO!*\n\n"
            f"📤 Canal: {canal}\n"
            f"⏳ Válido por {DROP_DURATION_HOURS}h",
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao enviar: {e}")

async def drop_all(update, context):
    """Posta em todas as VIPs simultaneamente."""
    if update.effective_user.id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    args = context.args
    if not args:
        await update.message.reply_text(
            "📝 /drop_all VIP - Posta em todas VIPs\n"
            "/drop_all FAN - Posta em todas FANs",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    canal_tipo = args[0].upper()
    if canal_tipo not in ["FAN", "VIP", "PRIVE"]:
        await update.message.reply_text("❌ Use: FAN, VIP ou PRIVE")
        return
    
    modelos = get_modelos()
    if not modelos:
        await update.message.reply_text("❌ Nenhuma modelo cadastrada.")
        return
    
    context.user_data["drop_all"] = {
        "modelos": modelos,
        "canal_tipo": canal_tipo
    }
    
    await update.message.reply_text(
        f"📤 *Drop ALL ({canal_tipo})*\n\n"
        f"Será enviado para {len(modelos)} modelo(s).\n\n"
        "Envie a *foto ou vídeo* que deseja postar em TODOS os canais:",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data["estado"] = "DROP_ALL_MIDIA"

async def handle_drop_all(update, context):
    """Processa o drop_all."""
    user_data = context.user_data
    
    if user_data.get("estado") != "DROP_ALL_MIDIA":
        return
    
    drop_info = user_data.get("drop_all")
    if not drop_info:
        await update.message.reply_text("❌ Erro.")
        return
    
    file_id = None
    tipo_midia = None
    
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        tipo_midia = "photo"
    elif update.message.video:
        file_id = update.message.video.file_id
        tipo_midia = "video"
    else:
        await update.message.reply_text("❌ Envie uma foto ou vídeo.")
        return
    
    caption = update.message.caption or "🔥 *DROP COLETIVO!*\n\nNão compartilhe! 🔞"
    caption += f"\n\n⏳ *Disponível por {DROP_DURATION_HOURS}h*"
    
    modelos = drop_info["modelos"]
    canal_tipo = drop_info["canal_tipo"]
    
    enviados = 0
    for modelo in modelos:
        try:
            canal = modelo[f"canal_{canal_tipo.lower()}"]
            
            if tipo_midia == "photo":
                await context.bot.send_photo(
                    chat_id=canal,
                    photo=file_id,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await context.bot.send_video(
                    chat_id=canal,
                    video=file_id,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN
                )
            enviados += 1
        except Exception as e:
            logger.error(f"Erro ao enviar para {modelo['username']}: {e}")
    
    user_data["estado"] = None
    user_data["drop_all"] = None
    
    await update.message.reply_text(
        f"✅ *DROP ALL ENVIADO!*\n\n"
        f"📤 {enviados}/{len(modelos)} canais receberam o conteúdo.\n"
        f"📂 Canal: {canal_tipo}\n"
        f"⏳ Válido por {DROP_DURATION_HOURS}h",
        parse_mode=ParseMode.MARKDOWN
    )

async def relatorio(update, context):
    """Mostra relatório de vendas por modelo."""
    if update.effective_user.id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    modelos = get_modelos()
    if not modelos:
        await update.message.reply_text("📊 Nenhuma modelo cadastrada.")
        return
    
    text = "📊 *RELATÓRIO DE VENDAS*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for m in modelos:
        text += f"💖 *{m['nome_completo']}*\n"
        text += f"   🔗 @{m['username']}\n"
        text += f"   📂 Free: {m['canal_free']}\n"
        text += f"   💰 FAN: R$ {m['preco_fan']:.2f}\n"
        text += f"   💰 VIP: R$ {m['preco_vip']:.2f}\n"
        text += f"   💰 PRIVE: R$ {m['preco_prive']:.2f}\n\n"
    
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def listar_modelos(update, context):
    """Lista todas as modelos (admin)."""
    if update.effective_user.id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    modelos = get_modelos()
    if not modelos:
        await update.message.reply_text("📋 Nenhuma modelo cadastrada.")
        return
    
    text = "📋 *MODELOS CADASTRADAS*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for m in modelos:
        text += f"{m['id']}. 💖 *{m['nome_completo']}*\n"
        text += f"   🔗 @{m['username']}\n"
        text += f"   📂 Free: {m['canal_free']}\n"
        text += f"   💰 FAN: R$ {m['preco_fan']:.2f}\n"
        text += f"   💰 VIP: R$ {m['preco_vip']:.2f}\n"
        text += f"   💰 PRIVE: R$ {m['preco_prive']:.2f}\n"
        text += f"   📅 Criada: {m['criado_em'][:10]}\n\n"
    
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ════════════════════════════════════════════════════════════════
# HANDLER PRINCIPAL
# ════════════════════════════════════════════════════════════════

async def button(update, context):
    """Gerenciador de botões."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "menu":
        await start(update, context)
    elif data == "modelos":
        await ver_modelos(update, context)
    elif data == "planos":
        await ver_planos(update, context)
    elif data == "faq":
        await query.edit_message_text(
            "❓ *PERGUNTAS FREQUENTES*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔹 *Como acessar o conteúdo?*\n"
            "Assine o plano desejado e receba acesso aos canais.\n\n"
            "🔹 *Quais formas de pagamento?*\n"
            "✅ PIX\n"
            "✅ Cartão de Crédito\n\n"
            "🔹 *Posso cancelar?*\n"
            "Sim, a qualquer momento.\n\n"
            "🔹 *O conteúdo é exclusivo?*\n"
            "Sim, conteúdo 100% original.\n\n"
            "🔞 Conteúdo para maiores de 18 anos.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Voltar", callback_data="menu")]])
        )
    elif data == "suporte":
        await query.edit_message_text(
            "📞 *SUPORTE*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📱 WhatsApp: +5511940462611\n"
            "📧 Email: suporte@annynhafunny.com\n\n"
            "💚 Atendimento humanizado!",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Voltar", callback_data="menu")]])
        )

# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════

async def main_async():
    print("=" * 60)
    print("🔥 AnnynhaFunny_PriveBot - Iniciando...")
    print("=" * 60)
    
    init_db()
    print("✅ Banco de dados: prive_bot.db")
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Comandos do bot
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", start))
    app.add_handler(CommandHandler("modelos", ver_modelos))
    app.add_handler(CommandHandler("planos", ver_planos))
    app.add_handler(CommandHandler("faq", faq))
    app.add_handler(CommandHandler("suporte", suporte))
    
    # Comandos Admin
    app.add_handler(CommandHandler("add_modelo", add_modelo))
    app.add_handler(CommandHandler("drop", drop))
    app.add_handler(CommandHandler("drop_all", drop_all))
    app.add_handler(CommandHandler("relatorio", relatorio))
    app.add_handler(CommandHandler("modelos_admin", listar_modelos))
    
    # Handlers
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, handle_drop))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, handle_drop_all))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_add_modelo))
    
    print("🚀 Bot rodando!")
    print("=" * 60)
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    
    await asyncio.Event().wait()

def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n🛑 Bot finalizado.")

if __name__ == "__main__":
    main()
'@ | Out-File -FilePath bot_prive.py -Encoding ascii

# Verificar se o bot_prive.py existe
cat bot_prive.py | Select-Object -First 5