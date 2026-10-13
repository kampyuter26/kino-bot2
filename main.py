import asyncio
import logging
import os
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# 1. Bot tokeningizni shu yerga yozasiz
TOKEN = "8758162405: AAGW3krs7B5UDtub2EyRg 4LJ_qSBnGu1go8" 
ADMIN_ID = 6522573426

# Kanallar ro'yxati (agar bo'lsa)
CHANNELS = [
    {"username": "@Turk_seriallar_uzbsub"},
]

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- RENDER UCHUN WEB SERVER ---
async def handle(request):
    return web.Response(text="Bot is running and alive!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- BOT BUYruqlari (HANDLERS) ---
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Salom! Kinolar botiga xush kelibsiz. Kino kodini yuboring:")

# Aytaylik, kino qidirish qismi yoki boshqa handler'laringiz shu yerda bo'ladi...
# @dp.message() ...


# --- ASOSIY FUNKSIYA ---
async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # Web server va botni bir vaqtda ishga tushiramiz
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )

if __name__ == '__main__':
    asyncio.run(main())
