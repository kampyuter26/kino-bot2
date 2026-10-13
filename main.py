import asyncio
import logging
import os
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Bot parametrlari
TOKEN = "8758162405:AAGW3krs7B5UDtub2EyRq..."  # Tokeningiz o'zi turibdi
ADMIN_ID = 6522573426

CHANNELS = [
    {"username": "@Turk_seriallar_uzbsub"},
    {"username": "@luna_uzbsub", "link": "..."},
    {"username": "@Drama_uzbsub", "link": "..."}
]

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Render porti uchun kichik web-server
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- BU YERDAN PASTDAGI BO'LIMGA O'ZINGIZNING MAVJUD HANDLER'LARINGIZNI / MANTIQINGIZNI QO'SHASIZ ---

async def main():
    # Web serverni orqa fonda ishga tushirish (Render o'chib qolmasligi uchun)
    await start_web_server()
    
    # Telegram bot polling
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
