import asyncio
import logging
import os
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

TOKEN = "8758162405: AAGW3krs7B5UDtub2EyRg 4LJ_qSBnGu1go8"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Render porti uchun oddiy sahifa
async def handle(request):
    return web.Response(text="Bot active")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Salom! Bot ishlamoqda.")

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # Server va pollingni birga ishga tushirish
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )

if __name__ == '__main__':
    asyncio.run(main())
