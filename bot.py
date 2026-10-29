import os
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import RPCError

# ==========================================
# LORD Security UserBot (Pyrogram v2)
# ==========================================

OWNER_ID = 7792838970

# بيانات التطبيق الرسمية لتلجرام (تستخدم لتشغيل الحساب)
API_ID = 611335
API_HASH = "d524b414d21f4d37f08684c1f4cacf0c"

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("LORD-UserBot")

# إنشاء العميل
app = Client(
    "lord_userbot_session",
    api_id=API_ID,
    api_hash=API_HASH
)

def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


@app.on_message(filters.command("start") & filters.me)
async def start_command(client: Client, message: Message):
    await message.edit_text(
        "🛡️ **LORD Security UserBot (Pyrogram)**\n\n"
        "✅ يعمل اليوزربوت بنجاح بحسابك الشخصي.\n\n"
        "**الأوامر المتاحة:**\n"
        "• `/ban` - حظر عضو بالرد عليه\n"
        "• `/banall` - حظر جميع أعضاء القروب\n"
        "• `/admins` - عرض مشرفي القروب\n"
        "• `/id` - عرض الآيديهات"
    )


@app.on_message(filters.command("id") & (filters.group | filters.private))
async def id_command(client: Client, message: Message):
    chat = message.chat
    user = message.from_user
    await message.reply_text(
        f"👤 آيديك: `{user.id}`\n"
        f"💬 آيدي المحادثة/القروب: `{chat.id}`"
    )


@app.on_message(filters.command("admins") & filters.group)
async def admins_command(client: Client, message: Message):
    try:
        lines = ["👮 **المشرفون في القروب:**"]
        async for member in client.get_chat_members(message.chat.id, filter="administrators"):
            u = member.user
            lines.append(f"• {u.mention} — `{u.id}`")
        await message.reply_text("\n".join(lines))
    except RPCError as e:
        await message.reply_text(f"❌ تعذر جلب المشرفين: {e}")


@app.on_message(filters.command("ban") & filters.group)
async def ban_command(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        return

    if not message.reply_to_message or not message.reply_to_message.from_user:
        await message.reply_text("⚠️ يرجى الرد على رسالة العضو المراد حظره.")
        return

    target = message.reply_to_message.from_user
    if target.id == OWNER_ID:
        await message.reply_text("❌ لا يمكنك حظر نفسك.")
        return

    try:
        await client.ban_chat_member(message.chat.id, target.id)
        await message.reply_text(f"✅ تم حظر العضو: {target.mention}")
    except RPCError as e:
        await message.reply_text(f"❌ فشل الحظر: {e}")


@app.on_message(filters.command("banall") & filters.group)
async def banall_command(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        return

    status_msg = await message.reply_text("⚠️ **جاري بدء عملية الحظر الشامل للأعضاء...**")
    banned_count = 0
    failed_count = 0

    try:
        async for member in client.get_chat_members(message.chat.id):
            if member.user.id == OWNER_ID or member.user.is_bot:
                continue
            if member.status in ["administrator", "creator"]:
                continue

            try:
                await client.ban_chat_member(message.chat.id, member.user.id)
                banned_count += 1
                await asyncio.sleep(0.5)
            except RPCError:
                failed_count += 1

        await status_msg.edit_text(
            f"✅ **تمت عملية الحظر الشامل بنجاح!**\n\n"
            f"• عدد من تم حظرهم: `{banned_count}`\n"
            f"• الفاشلون/المستثنون: `{failed_count}`"
        )
    except RPCError as e:
        await status_msg.edit_text(f"❌ حدث خطأ أثناء جلب الأعضاء: {e}")


def main():
    logger.info("LORD UserBot is starting...")
    app.run()


if __name__ == "__main__":
    main()
