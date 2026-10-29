import os
import asyncio
import logging
from telegram import Update
from telegram.constants import ChatType
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    CommandHandler,
    ChatMemberHandler,
    ContextTypes,
)

# ==========================================
# LORD Security Bot
# Python + Telegram Bot API
# ==========================================

OWNER_ID = 7792838970
BOT_TOKEN = "9213408858:AAF-73_fOGtMuv1VmuHZCXA9EfJ9XHgeyyI"

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("LORD")


def is_group(update: Update) -> bool:
    chat = update.effective_chat
    return bool(chat and chat.type in (ChatType.GROUP, ChatType.SUPERGROUP))


async def is_group_admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    user = update.effective_user
    chat = update.effective_chat
    if not user or not chat:
        return False
    if user.id == OWNER_ID:
        return True
    if not is_group(update):
        return False
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        return member.status in ("administrator", "creator")
    except TelegramError:
        return False


async def bot_is_admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    chat = update.effective_chat
    if not chat or not is_group(update):
        return False
    try:
        member = await context.bot.get_chat_member(chat.id, context.bot.id)
        return member.status in ("administrator", "creator")
    except TelegramError:
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return
    if user.id != OWNER_ID:
        await update.effective_message.reply_text("🔒 هذا البوت مخصص لمالكه.")
        return
    await update.effective_message.reply_text(
        "🛡️ LORD Security Bot\n\n"
        "✅ يعمل بنجاح.\n\n"
        "الأوامر:\n"
        "/ban - حظر بالرد\n"
        "/banall - ملاحظة حول قيود الحظر الشامل\n"
        "/admins - مشرفو القروب"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "📋 قائمة أوامر LORD:\n"
        "/start - التشغيل\n"
        "/ban - حظر عضو بالرد\n"
        "/unban [id] - لرفع الحظر\n"
        "/admins - عرض المشرفين"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("🟢 البوت يعمل بكفاءة.")


async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    if not user or not chat:
        return
    await update.effective_message.reply_text(f"👤 آيديك: {user.id}\n💬 آيدي القروب: {chat.id}")


async def admins_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_group(update):
        await update.effective_message.reply_text("استخدم هذا الأمر داخل القروب.")
        return
    try:
        admins = await context.bot.get_chat_administrators(update.effective_chat.id)
        lines = ["👮 المشرفون:"]
        for admin in admins:
            u = admin.user
            lines.append(f"• {u.full_name} — {u.id}")
        await update.effective_message.reply_text("\n".join(lines))
    except TelegramError:
        await update.effective_message.reply_text("تعذر جلب المشرفين.")


async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    if not message or not chat or not is_group(update):
        return
    if not await is_group_admin(update, context) or not await bot_is_admin(update, context):
        await message.reply_text("⚠️ تأكد من صلاحيات البوت والمشرف.")
        return

    replied = message.reply_to_message
    if not replied or not replied.from_user:
        await message.reply_text("رد على رسالة العضو واكتب /ban")
        return

    target = replied.from_user
    if target.id == OWNER_ID or target.is_bot:
        await message.reply_text("لا يمكنني حظر هذا الحساب.")
        return

    try:
        await context.bot.ban_chat_member(chat.id, target.id)
        await message.reply_text(f"✅ تم حظر: {target.full_name}")
    except TelegramError:
        await message.reply_text("❌ فشل الحظر. تحقق من الصلاحيات.")


async def banall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    if not message or not chat or not is_group(update):
        return
    
    # تصحيح دالة تعديل الرسالة لاستخدام edit_text بدلاً من edit
    status_msg = await message.reply_text("⚠️ جارٍ فحص القيود التقنية للحظر الشامل...")
    await asyncio.sleep(1)
    
    await status_msg.edit_text(
        "❌ تنبيه برمجي مهم:\n"
        "واجهة Telegram Bot API الرسمية التي يعمل عليها هذا البوت تمنع برمجيًا جلب قائمة جميع الأعضاء دفعة واحدة.\n"
        "إذا كنت تريد بوت يحظر الجميع (Mass Ban) تلقائياً، فيجب استنزاف مكتبة (Telethon) بحساب حقيقي (Userbot) كما شرحنا سابقاً، لأن البوت العادي يملك صلاحيات محدودة من شركة تيليجرام."
    )


async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    if not message or not chat or not len(context.args) == 1:
        return
    try:
        target_id = int(context.args[0])
        await context.bot.unban_chat_member(chat.id, target_id, only_if_banned=True)
        await message.reply_text(f"✅ تم رفع الحظر عن: {target_id}")
    except TelegramError:
        await message.reply_text("❌ تعذر رفع الحظر.")


async def member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("خطأ في البوت:", exc_info=context.error)


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("admins", admins_command))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("banall", banall_command))
    app.add_handler(CommandHandler("unban", unban_command))
    app.add_error_handler(error_handler)
    
    logger.info("LORD Security Bot is starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
