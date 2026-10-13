import asyncio
import logging
import os
import sys
import sqlite3
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# --- SOZLAMALAR ---
TOKEN = "8758162405:AAGW3krs7B5UDtub2EyRg4LJ_qSBnGu1go8"  # <-- BotFather'dan olgan tokeningizni shu yerga yozasiz
ADMIN_ID = 6522573426                   # Sizning Telegram ID'ingiz

# Majburiy obuna uchun siz ko'rsatgan 3 ta kanal
CHANNELS = [
    {"name": "Türk Seriallar Uzb", "username": "@Turk_seriallar_uzbsub"},
    {"name": "Luna Uzb", "username": "@luna_uzbsub"},
    {"name": "Drama Uzb", "username": "@Drama_uzbsub"}
]

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- BAZA BILAN ISHLASH (SQLITE) ---
def db_start():
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            code TEXT PRIMARY KEY,
            file_id TEXT,
            caption TEXT
        )
    """)
    conn.commit()
    conn.close()

db_start()

# --- ADMIN QO'SHISH FSM (STATE) ---
class AddMovie(StatesGroup):
    waiting_for_code = State()
    waiting_for_file = State()
    waiting_for_caption = State()

# --- 3 TA KANALGA OBUNANI TEKSHIRISH ---
async def check_subscriptions(user_id: int) -> list:
    not_subscribed = []
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel["username"], user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                not_subscribed.append(channel)
        except Exception:
            not_subscribed.append(channel)
    return not_subscribed

def get_sub_keyboard(not_subscribed_channels):
    keyboard = []
    for ch in not_subscribed_channels:
        clean_username = ch["username"].replace('@', '')
        keyboard.append([InlineKeyboardButton(text=f"📢 {ch['name']}ga obuna bo'lish", url=f"https://t.me/{clean_username}")])
    keyboard.append([InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# --- START BUYRUQI ---
@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    not_sub = await check_subscriptions(user_id)
    
    if not_sub:
        text = "Botdan to'liq foydalanish uchun quyidagi barcha kanallarga a'zo bo'ling:\n\n"
        for ch in not_sub:
            text += f"• {ch['name']}: {ch['username']}\n"
        await message.answer(text, reply_markup=get_sub_keyboard(not_sub))
        return
    
    await message.answer("Salom! Kinolar botiga xush kelibsiz. 🎬\nKino kodini yuboring:")

@dp.callback_query(F.data == "check_sub")
async def process_check_sub(callback: CallbackQuery):
    user_id = callback.from_user.id
    not_sub = await check_subscriptions(user_id)
    
    if not not_sub:
        await callback.message.delete()
        await callback.message.answer("Rahmat! Barcha kanallarga obuna tasdiqlandi. Endi kino kodini yuborishingiz mumkin:")
    else:
        await callback.answer("Siz hali hamma kanalga a'zo bo'lmadingiz!", show_alert=True)

# --- ADMIN: KINO QO'SHISH (/add) ---
@dp.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Kino uchun raqam (kod) yuboring:")
    await state.set_state(AddMovie.waiting_for_code)

@dp.message(AddMovie.waiting_for_code)
async def process_code(message: Message, state: FSMContext):
    await state.update_data(code=message.text)
    await message.answer("Endi kino videosini yuboring:")
    await state.set_state(AddMovie.waiting_for_file)

@dp.message(AddMovie.waiting_for_file, F.video | F.document)
async def process_file(message: Message, state: FSMContext):
    file_id = message.video.file_id if message.video else message.document.file_id
    await state.update_data(file_id=file_id)
    await message.answer("Kino uchun izoh (nomi) yuboring:")
    await state.set_state(AddMovie.waiting_for_caption)

@dp.message(AddMovie.waiting_for_caption)
async def process_caption(message: Message, state: FSMContext):
    data = await state.get_data()
    code = data.get("code")
    file_id = data.get("file_id")
    caption = message.text

    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO movies (code, file_id, caption) VALUES (?, ?, ?)", (code, file_id, caption))
    conn.commit()
    conn.close()

    await state.clear()
    await message.answer(f"✅ {code}-kodli kino muvaffaqiyatli saqlandi!")

# --- ADMIN: KINO O'CHIRISH (/del) ---
@dp.message(Command("del"))
async def cmd_del(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Foydalanish: `/del 101`", parse_mode="Markdown")
        return
    
    code = args[1]
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM movies WHERE code = ?", (code,))
    conn.commit()
    conn.close()
    
    await message.answer(f"🗑 {code}-kodli kino bazadan o'chirildi.")

# --- KINO QIDIRISH ---
@dp.message(F.text.isdigit())
async def get_movie(message: Message):
    user_id = message.from_user.id
    not_sub = await check_subscriptions(user_id)
    
    if not_sub:
        text = "Botdan foydalanish uchun quyidagi barcha kanallarga a'zo bo'ling:\n\n"
        for ch in not_sub:
            text += f"• {ch['name']}: {ch['username']}\n"
        await message.answer(text, reply_markup=get_sub_keyboard(not_sub))
        return

    code = message.text
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("SELECT file_id, caption FROM movies WHERE code = ?", (code,))
    movie = cursor.fetchone()
    conn.close()

    if movie:
        file_id, caption = movie
        await message.answer_video(video=file_id, caption=caption)
    else:
        await message.answer("❌ Bunday kodli kino topilmadi.")

# --- RENDER WEBHOOK SERVER ---
async def handle(request):
    return web.Response(text="Bot active")

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    app = web.Application()
    
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path="/webhook")
    setup_application(app, dp, bot=bot)
    
    async def on_startup(bot: Bot):
        render_url = os.environ.get("RENDER_EXTERNAL_URL")
        if render_url:
            webhook_url = f"{render_url}/webhook"
            await bot.set_webhook(webhook_url)
            logging.info(f"Webhook set to: {webhook_url}")

    app.on_startup.append(lambda app: on_startup(bot))
    app.router.add_get("/", handle)
    
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
