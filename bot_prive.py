from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import logging
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN_PRIVE")
ADMIN_CHAT_IDS = [int(x.strip()) for x in os.getenv("ADMIN_CHAT_IDS", "0").split(",") if x.strip()]

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update, context):
    user = update.effective_user
    welcome = (
        f"🔥 *AnnynhaFunny_PriveBot*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Olá, *{user.first_name}*! 👋\n\n"
        f"💋 Conteúdo exclusivo das melhores modelos!\n\n"
        f"🔞 Conteúdo para maiores de 18 anos.\n\n"
        f"📌 *Comandos:*\n"
        f"/start - Iniciar\n"
        f"/modelos - Ver modelos disponíveis\n"
        f"/planos - Ver planos e preços\n"
        f"/suporte - Falar com suporte"
    )
    keyboard = [
        [InlineKeyboardButton("🎭 Ver Modelos", callback_data="modelos")],
        [InlineKeyboardButton("💎 Planos e Preços", callback_data="planos")],
        [InlineKeyboardButton("📞 Suporte", callback_data="suporte")],
    ]
    await update.message.reply_text(welcome, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))

async def modelos(update, context):
    text = "🎭 *MODELOS DISPONÍVEIS*\n━━━━━━━━━━━━━━━━━━━━━━\n\nEm breve teremos novidades!"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def planos(update, context):
    text = "💎 *PLANOS E PREÇOS*\n━━━━━━━━━━━━━━━━━━━━━━\n\nEm breve!"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def suporte(update, context):
    text = "📞 *SUPORTE*\n━━━━━━━━━━━━━━━━━━━━━━\n\n📱 WhatsApp: +5511940462611\n📧 Email: suporte@annynhafunny.com"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def button(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "modelos":
        await modelos(update, context)
    elif query.data == "planos":
        await planos(update, context)
    elif query.data == "suporte":
        await suporte(update, context)

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("modelos", modelos))
    app.add_handler(CommandHandler("planos", planos))
    app.add_handler(CommandHandler("suporte", suporte))
    app.add_handler(CallbackQueryHandler(button))
    print("🚀 AnnynhaFunny_PriveBot rodando!")
    app.run_polling()

if __name__ == "__main__":
    main()
