import asyncio
import logging
import os
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

TOKEN = "8758162405:AAGW3krs7B5UDtub2EyRg4LJ_qSBnGu1go8"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 1. Render porti uchun oddiy sahifa
async def handle(request):
    return web.Response(text="Bot active")

async def start_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server started on port {port}")

# 2. Telegram bot buyrug'i
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Salom! Bot muvaffaqiyatli ishga tushdi!")

# 3. Asosiy funksiya
async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # MUHIM QADAM: Telegram'dagi eski webhook'ni tozalab tashlaymiz
    # Shundagina start_polling xabarlarni qabul qila boshlaydi
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Server va pollingni birga ishga tushiramiz
    await asyncio.gather(
        start_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
