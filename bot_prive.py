"""
===============================================
AnnynhaFunny_PriveBot - Bot Principal
===============================================
Bot que gerencia v?rias modelos com canais Free, FAN, VIP e PRIVE
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

# ?? Logging ??
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ????????????????????????????????????????????????????????????????
# COMANDOS PRINCIPAIS
# ????????????????????????????????????????????????????????????????

async def start(update, context):
    """In?cio do bot."""
    user = update.effective_user

    welcome = (
        "?? *AnnynhaFunny_PriveBot*\n"
        "??????????????????????\n\n"
        f"Ol?, *{user.first_name}*! ??\n\n"
        "?? Conte?do exclusivo das melhores modelos!\n\n"
        "?? *Quem est? no nosso cat?logo?*\n"
    )

    modelos = get_modelos()
    if modelos:
        for m in modelos:
            welcome += f"\n?? @{m['username']}\n"
            welcome += f"   ? Free: {m['canal_free']}\n"
            welcome += f"   ? FAN: {m['canal_fan']} - R$ {m['preco_fan']:.2f}\n"
            welcome += f"   ? VIP: {m['canal_vip']} - R$ {m['preco_vip']:.2f}\n"
            welcome += f"   ? PRIVE: {m['canal_prive']} - R$ {m['preco_prive']:.2f}\n"
    else:
        welcome += "\n?? *Em breve novas modelos!*\n"

    welcome += "\n??????????????????????\n"
    welcome += "?? Conte?do exclusivo para maiores de 18 anos."

    keyboard = [
        [InlineKeyboardButton("?? Ver Modelos", callback_data="modelos")],
        [InlineKeyboardButton("?? Planos e Pre?os", callback_data="planos")],
        [InlineKeyboardButton("? D?vidas", callback_data="faq")],
        [InlineKeyboardButton("?? Suporte", callback_data="suporte")],
    ]

    await update.message.reply_text(welcome, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))

async def ver_modelos(update, context):
    """Lista todas as modelos."""
    modelos = get_modelos()

    if not modelos:
        await update.callback_query.edit_message_text(
            "?? Nenhuma modelo cadastrada ainda.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("?? Voltar", callback_data="menu")]])
        )
        return

    text = "?? *NOSSAS MODELOS*\n??????????????????????\n\n"
    keyboard = []

    for m in modelos:
        text += f"?? *{m['nome_completo']}*\n"
        text += f"   ?? @{m['username']}\n"
        text += f"   ?? Free: {m['canal_free']}\n"
        text += f"   ?? FAN: R$ {m['preco_fan']:.2f}\n"
        text += f"   ?? VIP: R$ {m['preco_vip']:.2f}\n"
        text += f"   ?? PRIVE: R$ {m['preco_prive']:.2f}\n\n"

        keyboard.append([InlineKeyboardButton(f"?? Ver {m['nome_completo']}", callback_data=f"modelo_{m['id']}")])

    keyboard.append([InlineKeyboardButton("?? Menu Principal", callback_data="menu")])

    await update.callback_query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))

async def ver_planos(update, context):
    """Exibe planos e pre?os."""
    modelos = get_modelos()

    text = "?? *PLANOS E PRE?OS*\n??????????????????????\n\n"

    for m in modelos:
        text += f"?? *{m['nome_completo']}* (@{m['username']})\n"
        text += f"   ?? Free: *GR?TIS*\n"
        text += f"   ?? FAN: *R$ {m['preco_fan']:.2f}*\n"
        text += f"   ?? VIP: *R$ {m['preco_vip']:.2f}*\n"
        text += f"   ?? PRIVE: *R$ {m['preco_prive']:.2f}*\n\n"

    text += "??????????????????????\n"
    text += "?? *Formas de pagamento:*\n"
    text += "? PIX (aprovado em minutos)\n"
    text += "? Cart?o de Cr?dito\n\n"
    text += "?? Conte?do exclusivo para maiores de 18 anos."

    await update.callback_query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("?? Voltar", callback_data="menu")]]))

# ????????????????????????????????????????????????????????????????
# COMANDOS ADMIN
# ????????????????????????????????????????????????????????????????

async def add_modelo(update, context):
    """Adiciona uma nova modelo."""
    if update.effective_user.id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("? Acesso negado.")
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "?? *Como usar:*\n"
            "/add_modelo @username\n\n"
            "Exemplo: /add_modelo @bia\n\n"
            "Depois preencha as informa??es solicitadas.",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    username = args[0].replace("@", "")

    if get_modelo_by_username(username):
        await update.message.reply_text(f"? Modelo @{username} j? est? cadastrada!")
        return

    context.user_data["nova_modelo"] = {"username": username}

    await update.message.reply_text(
        f"?? *Cadastro da @{username}*\n\n"
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
            f"? Nome salvo: *{text}*\n\n"
            "Digite o *pre?o FAN* (ex: 29.90):",
            parse_mode=ParseMode.MARKDOWN
        )

    elif user_data.get("estado") == "ADD_MODELO_PRECO_FAN":
        try:
            preco_fan = float(text.replace(",", "."))
            user_data["nova_modelo"]["preco_fan"] = preco_fan
            user_data["estado"] = "ADD_MODELO_PRECO_VIP"
            await update.message.reply_text(
                f"? Pre?o FAN: R$ {preco_fan:.2f}\n\n"
                "Digite o *pre?o VIP* (ex: 79.90):",
                parse_mode=ParseMode.MARKDOWN
            )
        except ValueError:
            await update.message.reply_text("? Valor inv?lido. Digite um n?mero (ex: 29.90):")

    elif user_data.get("estado") == "ADD_MODELO_PRECO_VIP":
        try:
            preco_vip = float(text.replace(",", "."))
            user_data["nova_modelo"]["preco_vip"] = preco_vip
            user_data["estado"] = "ADD_MODELO_PRECO_PRIVE"
            await update.message.reply_text(
                f"? Pre?o VIP: R$ {preco_vip:.2f}\n\n"
                "Digite o *pre?o PRIVE* (ex: 299.90):",
                parse_mode=ParseMode.MARKDOWN
            )
        except ValueError:
            await update.message.reply_text("? Valor inv?lido. Digite um n?mero (ex: 79.90):")

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
                f"? *MODELO CADASTRADA COM SUCESSO!*\n"
                f"??????????????????????\n\n"
                f"?? *{resultado['nome']}*\n"
                f"?? @{resultado['username']}\n\n"
                f"?? *CANAIS:*\n"
                f"   Free: {resultado['canal_free']}\n"
                f"   FAN: {resultado['canal_fan']} - R$ {data['preco_fan']:.2f}\n"
                f"   VIP: {resultado['canal_vip']} - R$ {data['preco_vip']:.2f}\n"
                f"   PRIVE: {resultado['canal_prive']} - R$ {preco_prive:.2f}\n\n"
                "?? *Pr?ximos passos:*\n"
                "1. Adicione o bot como admin nos canais\n"
                "2. Use /drop @modelo VIP para postar conte?do\n"
                "3. Divulgue os canais! ??",
                parse_mode=ParseMode.MARKDOWN
            )

        except ValueError:
            await update.message.reply_text("? Valor inv?lido. Digite um n?mero (ex: 299.90):")

async def drop(update, context):
    """Posta um drop em um canal espec?fico."""
    if update.effective_user.id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("? Acesso negado.")
        return

    args = context.args
    if not args or len(args) < 2:
        await update.message.reply_text(
            "?? *Como usar:*\n"
            "/drop @modelo VIP\n\n"
            "Exemplo: /drop @bia VIP\n"
            "/drop @sheron FAN\n\n"
            "Op??es: FAN, VIP, PRIVE",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    username = args[0].replace("@", "")
    canal_tipo = args[1].upper()

    if canal_tipo not in ["FAN", "VIP", "PRIVE"]:
        await update.message.reply_text("? Canal inv?lido. Use: FAN, VIP ou PRIVE")
        return

    modelo = get_modelo_by_username(username)
    if not modelo:
        await update.message.reply_text(f"? Modelo @{username} n?o encontrada!")
        return

    context.user_data["drop"] = {
        "modelo_id": modelo["id"],
        "canal_tipo": canal_tipo,
        "canal": modelo[f"canal_{canal_tipo.lower()}"]
    }

    await update.message.reply_text(
        f"?? *Enviando drop para {modelo['nome_completo']} ({canal_tipo})*\n\n"
        "Envie a *foto ou v?deo* que deseja postar:",
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
        await update.message.reply_text("? Erro: Drop n?o iniciado.")
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
        await update.message.reply_text("? Envie uma foto, v?deo ou documento.")
        return

    caption = update.message.caption or ""

    if not caption:
        caption = "?? *DROP EXCLUSIVO!*\n\nN?o compartilhe! ??"
    else:
        caption += "\n\n?? *N?o compartilhe! ??"

    caption += f"\n\n? *Dispon?vel por {DROP_DURATION_HOURS}h*"

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
            f"? *DROP ENVIADO COM SUCESSO!*\n\n"
            f"?? Canal: {canal}\n"
            f"? V?lido por {DROP_DURATION_HOURS}h",
            parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        await update.message.reply_text(f"? Erro ao enviar: {e}")

async def drop_all(update, context):
    """Posta em todas as VIPs simultaneamente."""
    if update.effective_user.id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("? Acesso negado.")
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "?? /drop_all VIP - Posta em todas VIPs\n"
            "/drop_all FAN - Posta em todas FANs",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    canal_tipo = args[0].upper()
    if canal_tipo not in ["FAN", "VIP", "PRIVE"]:
        await update.message.reply_text("? Use: FAN, VIP ou PRIVE")
        return

    modelos = get_modelos()
    if not modelos:
        await update.message.reply_text("? Nenhuma modelo cadastrada.")
        return

    context.user_data["drop_all"] = {
        "modelos": modelos,
        "canal_tipo": canal_tipo
    }

    await update.message.reply_text(
        f"?? *Drop ALL ({canal_tipo})*\n\n"
        f"Ser? enviado para {len(modelos)} modelo(s).\n\n"
        "Envie a *foto ou v?deo* que deseja postar em TODOS os canais:",
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
        await update.message.reply_text("? Erro.")
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
        await update.message.reply_text("? Envie uma foto ou v?deo.")
        return

    caption = update.message.caption or "?? *DROP COLETIVO!*\n\nN?o compartilhe! ??"
    caption += f"\n\n? *Dispon?vel por {DROP_DURATION_HOURS}h*"

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
        f"? *DROP ALL ENVIADO!*\n\n"
        f"?? {enviados}/{len(modelos)} canais receberam o conte?do.\n"
        f"?? Canal: {canal_tipo}\n"
        f"? V?lido por {DROP_DURATION_HOURS}h",
        parse_mode=ParseMode.MARKDOWN
    )

async def relatorio(update, context):
    """Mostra relat?rio de vendas por modelo."""
    if update.effective_user.id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("? Acesso negado.")
        return

    modelos = get_modelos()
    if not modelos:
        await update.message.reply_text("?? Nenhuma modelo cadastrada.")
        return

    text = "?? *RELAT?RIO DE VENDAS*\n??????????????????????\n\n"

    for m in modelos:
        text += f"?? *{m['nome_completo']}*\n"
        text += f"   ?? @{m['username']}\n"
        text += f"   ?? Free: {m['canal_free']}\n"
        text += f"   ?? FAN: R$ {m['preco_fan']:.2f}\n"
        text += f"   ?? VIP: R$ {m['preco_vip']:.2f}\n"
        text += f"   ?? PRIVE: R$ {m['preco_prive']:.2f}\n\n"

    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def listar_modelos(update, context):
    """Lista todas as modelos (admin)."""
    if update.effective_user.id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("? Acesso negado.")
        return

    modelos = get_modelos()
    if not modelos:
        await update.message.reply_text("?? Nenhuma modelo cadastrada.")
        return

    text = "?? *MODELOS CADASTRADAS*\n??????????????????????\n\n"
    for m in modelos:
        text += f"{m['id']}. ?? *{m['nome_completo']}*\n"
        text += f"   ?? @{m['username']}\n"
        text += f"   ?? Free: {m['canal_free']}\n"
        text += f"   ?? FAN: R$ {m['preco_fan']:.2f}\n"
        text += f"   ?? VIP: R$ {m['preco_vip']:.2f}\n"
        text += f"   ?? PRIVE: R$ {m['preco_prive']:.2f}\n"
        text += f"   ?? Criada: {m['criado_em'][:10]}\n\n"

    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ????????????????????????????????????????????????????????????????
# HANDLER PRINCIPAL
# ????????????????????????????????????????????????????????????????

async def button(update, context):
    """Gerenciador de bot?es."""
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
            "? *PERGUNTAS FREQUENTES*\n"
            "??????????????????????\n\n"
            "?? *Como acessar o conte?do?*\n"
            "Assine o plano desejado e receba acesso aos canais.\n\n"
            "?? *Quais formas de pagamento?*\n"
            "? PIX\n"
            "? Cart?o de Cr?dito\n\n"
            "?? *Posso cancelar?*\n"
            "Sim, a qualquer momento.\n\n"
            "?? *O conte?do ? exclusivo?*\n"
            "Sim, conte?do 100% original.\n\n"
            "?? Conte?do para maiores de 18 anos.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("?? Voltar", callback_data="menu")]])
        )
    elif data == "suporte":
        await query.edit_message_text(
            "?? *SUPORTE*\n"
            "??????????????????????\n\n"
            "?? WhatsApp: +5511940462611\n"
            "?? Email: suporte@annynhafunny.com\n\n"
            "?? Atendimento humanizado!",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("?? Voltar", callback_data="menu")]])
        )

# ????????????????????????????????????????????????????????????????
# MAIN
# ????????????????????????????????????????????????????????????????

async def suporte(update, context):
    text = (
        "?? *SUPORTE AnnynhaFunny_PriveBot*\n"
        "??????????????????????\n\n"
        "?? *WhatsApp:* +5511940462611\n"
        "?? *Email:* suporte@annynhafunny.com\n"
        "?? *Telegram:* @AnynhaFunny_PriveBot\n\n"
        "?? *Hor?rio de atendimento:*\n"
        "Segunda a Sexta: 09:00 - 18:00\n"
        "S?bado: 09:00 - 14:00\n\n"
        "?? *Atendimento humanizado e r?pido!*"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def main_async():
    print("=" * 60)
    print("?? AnnynhaFunny_PriveBot - Iniciando...")
    print("=" * 60)

    init_db()
    print("? Banco de dados: prive_bot.db")

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
    app.add_handler(CommandHandler("suporte", suporte))

    # Handlers
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, handle_drop))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, handle_drop_all))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_add_modelo))

    print("?? Bot rodando!")
    print("=" * 60)

    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)

    await asyncio.Event().wait()

def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n?? Bot finalizado.")

if __name__ == "__main__":
    main()

