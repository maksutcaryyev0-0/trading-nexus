"""
NEXUS Telegram Bot
Full trading terminal in Telegram
"""
import asyncio
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from loguru import logger

BACKEND_URL = "http://backend:8000/api/v1"
LANGUAGES = {"en": "🇬🇧", "ru": "🇷🇺", "tr": "🇹🇷", "ar": "🇸🇦"}

MESSAGES = {
    "en": {
        "welcome": "🚀 *NEXUS Trading OS*\nYour institutional trading system is ready.",
        "analyzing": "⏳ Analyzing {symbol}...",
        "no_key": "⚠️ API key not configured. Add in /settings",
        "help": """
*NEXUS Commands:*
/analyze SYMBOL — Full analysis
/price SYMBOL — Live price
/risk — Risk dashboard
/journal — Recent trades
/brief — Morning briefing
/sessions — Trading sessions
/watchlist — Your watchlist
/calendar — Economic calendar
/stop — Kill switch
/resume — Resume trading
/settings — Settings
/lang — Change language
/help — This message
        """,
    },
    "ru": {
        "welcome": "🚀 *NEXUS Trading OS*\nВаша институциональная торговая система готова.",
        "analyzing": "⏳ Анализирую {symbol}...",
        "no_key": "⚠️ API ключ не настроен. Добавьте в /settings",
        "help": """
*Команды NEXUS:*
/analyze SYMBOL — Полный анализ
/price SYMBOL — Живая цена
/risk — Риск дашборд
/journal — Последние сделки
/brief — Утренний брифинг
/sessions — Торговые сессии
/watchlist — Ваш вотчлист
/calendar — Экономический календарь
/stop — Kill switch
/resume — Возобновить торговлю
/settings — Настройки
/lang — Сменить язык
/help — Эта справка
        """,
    },
    "tr": {
        "welcome": "🚀 *NEXUS Trading OS*\nKurumsal işlem sisteminiz hazır.",
        "analyzing": "⏳ {symbol} analiz ediliyor...",
        "no_key": "⚠️ API anahtarı yapılandırılmadı. /settings'den ekleyin",
        "help": """
*NEXUS Komutları:*
/analyze SEMBOL — Tam analiz
/price SEMBOL — Canlı fiyat
/risk — Risk paneli
/journal — Son işlemler
/brief — Sabah brifing
/sessions — Seans saatleri
/watchlist — İzleme listem
/calendar — Ekonomik takvim
/stop — Acil durdur
/resume — Ticareti devam ettir
/settings — Ayarlar
/lang — Dil değiştir
/help — Bu mesaj
        """,
    },
    "ar": {
        "welcome": "🚀 *NEXUS Trading OS*\nنظام التداول المؤسسي الخاص بك جاهز.",
        "analyzing": "⏳ جاري تحليل {symbol}...",
        "no_key": "⚠️ مفتاح API غير مكوَّن. أضفه في /settings",
        "help": """
*أوامر NEXUS:*
/analyze رمز — تحليل كامل
/price رمز — السعر المباشر
/risk — لوحة المخاطر
/journal — الصفقات الأخيرة
/brief — موجز الصباح
/sessions — جلسات التداول
/watchlist — قائمة المراقبة
/calendar — التقويم الاقتصادي
/stop — إيقاف الطوارئ
/resume — استئناف التداول
/settings — الإعدادات
/lang — تغيير اللغة
/help — هذه الرسالة
        """,
    },
}

user_langs = {}


def get_lang(user_id: int) -> str:
    return user_langs.get(user_id, "en")


def t(user_id: int, key: str, **kwargs) -> str:
    lang = get_lang(user_id)
    msg = MESSAGES.get(lang, MESSAGES["en"]).get(key, key)
    return msg.format(**kwargs) if kwargs else msg


async def api_get(endpoint: str) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(f"{BACKEND_URL}{endpoint}")
        return r.json()


async def api_post(endpoint: str, data: dict) -> dict:
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(f"{BACKEND_URL}{endpoint}", json=data)
        return r.json()


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    kb = [
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        ],
        [
            InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr"),
            InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
        ],
    ]
    await update.message.reply_text(
        "🌐 Select language / Выберите язык / Dil seçin / اختر اللغة",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown",
    )


async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(t(uid, "help"), parse_mode="Markdown")


async def analyze(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_lang(uid)

    if not ctx.args:
        await update.message.reply_text(
            "Usage: /analyze XAUUSD" if lang == "en"
            else "Использование: /analyze XAUUSD" if lang == "ru"
            else "Kullanım: /analyze XAUUSD" if lang == "tr"
            else "الاستخدام: /analyze XAUUSD"
        )
        return

    symbol = ctx.args[0].upper()
    msg = await update.message.reply_text(
        t(uid, "analyzing", symbol=symbol), parse_mode="Markdown"
    )

    try:
        result = await api_post("/analysis/full", {
            "symbol": symbol, "lang": lang, "timezone": "UTC"
        })

        score = result.get("confluence_score", 0)
        rating = result.get("rating", "?")
        regime = result.get("regime", "UNKNOWN")
        scenarios = result.get("scenarios", {})
        plan = result.get("trade_plan", {})

        bull = scenarios.get("bull", {})
        bear = scenarios.get("bear", {})

        if lang == "ru":
            text = f"""
📊 *{symbol} — Полный анализ*

🎯 Confluence Score: *{score}/100* — *{rating}*
📈 Режим: *{regime}*

🟢 *Бычий сценарий* ({bull.get('probability', '?')}%)
Цель: {bull.get('target', '?')}
Триггер: {bull.get('trigger', '?')}

🔴 *Медвежий сценарий* ({bear.get('probability', '?')}%)
Цель: {bear.get('target', '?')}
Триггер: {bear.get('trigger', '?')}

📋 *Торговый план:*
Вход: {plan.get('entry', '?')}
Стоп: {plan.get('stop', '?')}
TP1/TP2/TP3: {plan.get('tp1', '?')} / {plan.get('tp2', '?')} / {plan.get('tp3', '?')}
R/R: {plan.get('risk_reward', '?')}
"""
        elif lang == "tr":
            text = f"""
📊 *{symbol} — Tam Analiz*

🎯 Confluence Skoru: *{score}/100* — *{rating}*
📈 Rejim: *{regime}*

🟢 *Boğa Senaryosu* ({bull.get('probability', '?')}%)
Hedef: {bull.get('target', '?')}

🔴 *Ayı Senaryosu* ({bear.get('probability', '?')}%)
Hedef: {bear.get('target', '?')}

📋 *İşlem Planı:*
Giriş: {plan.get('entry', '?')}
Stop: {plan.get('stop', '?')}
R/R: {plan.get('risk_reward', '?')}
"""
        elif lang == "ar":
            text = f"""
📊 *{symbol} — تحليل كامل*

🎯 نقاط التقاطع: *{score}/100* — *{rating}*
📈 النظام: *{regime}*

🟢 *السيناريو الصعودي* ({bull.get('probability', '?')}%)
الهدف: {bull.get('target', '?')}

🔴 *السيناريو الهبوطي* ({bear.get('probability', '?')}%)
الهدف: {bear.get('target', '?')}

📋 *خطة التداول:*
الدخول: {plan.get('entry', '?')}
وقف الخسارة: {plan.get('stop', '?')}
"""
        else:
            text = f"""
📊 *{symbol} — Full Analysis*

🎯 Confluence Score: *{score}/100* — *{rating}*
📈 Regime: *{regime}*

🟢 *Bull Scenario* ({bull.get('probability', '?')}%)
Target: {bull.get('target', '?')}
Trigger: {bull.get('trigger', '?')}

🔴 *Bear Scenario* ({bear.get('probability', '?')}%)
Target: {bear.get('target', '?')}
Trigger: {bear.get('trigger', '?')}

📋 *Trade Plan:*
Entry: {plan.get('entry', '?')}
Stop: {plan.get('stop', '?')}
TP1/TP2/TP3: {plan.get('tp1','?')} / {plan.get('tp2','?')} / {plan.get('tp3','?')}
R/R: {plan.get('risk_reward', '?')}
"""

        await msg.edit_text(text.strip(), parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Analyze error: {e}")
        await msg.edit_text(f"❌ Error: {e}")


async def price_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not ctx.args:
        await update.message.reply_text("/price XAUUSD")
        return
    symbol = ctx.args[0].upper()
    try:
        data = await api_get(f"/analysis/price/{symbol}")
        price = data.get("price", "N/A")
        source = data.get("source", "unknown")
        quality = data.get("quality", "?")
        await update.message.reply_text(
            f"💰 *{symbol}*: `{price}`\n"
            f"Source: {source} | Quality: {quality}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def brief_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_lang(uid)
    msg = await update.message.reply_text("⏳ Generating morning brief...")
    try:
        result = await api_post("/ai/morning-brief", {"lang": lang})
        brief = result.get("brief", "No brief available")
        await msg.edit_text(f"☀️ *Morning Brief*\n\n{brief}", parse_mode="Markdown")
    except Exception as e:
        await msg.edit_text(f"❌ {e}")


async def stop_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_lang(uid)
    try:
        await api_post("/risk/kill-switch", {"action": "activate", "reason": "Telegram command"})
        text = {
            "en": "🔴 *KILL SWITCH ACTIVATED*\nAll trading stopped. Use /resume to unlock.",
            "ru": "🔴 *KILL SWITCH АКТИВИРОВАН*\nТорговля остановлена. /resume для возобновления.",
            "tr": "🔴 *ACİL DURDURMA AKTİF*\nTicaret durduruldu. /resume ile devam ettirin.",
            "ar": "🔴 *تم تفعيل مفتاح الإيقاف*\nتم إيقاف التداول. استخدم /resume للاستئناف.",
        }.get(lang, "🔴 KILL SWITCH ACTIVATED")
        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def resume_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_lang(uid)
    try:
        await api_post("/risk/kill-switch", {"action": "deactivate"})
        text = {
            "en": "🟢 *Trading resumed*",
            "ru": "🟢 *Торговля возобновлена*",
            "tr": "🟢 *Ticaret devam ediyor*",
            "ar": "🟢 *تم استئناف التداول*",
        }.get(lang, "🟢 Trading resumed")
        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def lang_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = [
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        ],
        [
            InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr"),
            InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
        ],
    ]
    await update.message.reply_text(
        "Select language:", reply_markup=InlineKeyboardMarkup(kb)
    )


async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    data = query.data

    if data.startswith("lang_"):
        lang = data.replace("lang_", "")
        user_langs[uid] = lang
        flag = LANGUAGES.get(lang, "🌐")
        await query.edit_message_text(
            f"{flag} Language set to: *{lang.upper()}*\n\n" + t(uid, "welcome"),
            parse_mode="Markdown"
        )


async def message_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle free-form messages as AI chat"""
    uid = update.effective_user.id
    lang = get_lang(uid)
    text = update.message.text

    msg = await update.message.reply_text("⏳ ...")
    try:
        result = await api_post("/ai/chat", {
            "message": text,
            "lang": lang,
            "context": "telegram",
        })
        answer = result.get("answer", "No response")
        await msg.edit_text(answer[:4000])
    except Exception as e:
        await msg.edit_text(f"❌ {e}")


def run_bot(token: str):
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start",    start))
    app.add_handler(CommandHandler("help",     help_cmd))
    app.add_handler(CommandHandler("analyze",  analyze))
    app.add_handler(CommandHandler("price",    price_cmd))
    app.add_handler(CommandHandler("brief",    brief_cmd))
    app.add_handler(CommandHandler("stop",     stop_cmd))
    app.add_handler(CommandHandler("resume",   resume_cmd))
    app.add_handler(CommandHandler("lang",     lang_cmd))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    logger.info("NEXUS Telegram Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    import os
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set")
    else:
        run_bot(token)
