import asyncio
import logging
import os
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

TOKEN = "8758162405: AAGW3krs7B5UDtub2EyRg 4LJ_qSBnGu1go8"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 1. Render talab qiladigan veb-server (Portni ushlash uchun)
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render avtomatik beradigan PORT'ni olamiz (odatda 10000 yoki boshqa)
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server started on port {port}")

# 2. Telegram bot buyrug'i
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Salom! Bot muvaffaqiyatli ishga tushdi!")

# 3. Ikkalasini birgalikda yurgizish
async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # Veb-server va Bot polling'ni parallel ishga tushiramiz
    await asyncio.gather(
        start_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
