import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Bot parametrlari
TOKEN = "8758162405:AAGW3krs7B5UDtub2EyRg4LJ_qSBnGu1go8"
ADMIN_ID = 6522573426

CHANNELS = [
    {"username": "@Turk_seriallar_uzbsub", "link": "https://t.me/Turk_seriallar_uzbsub"},
    {"username": "@luna_uzbsub", "link": "https://t.me/luna_uzbsub"},
    {"username": "@Drama_uzbsub", "link": "https://t.me/Drama_uzbsub"}
]

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Kino bazasi (Vaqtincha xotirada)
MOVIES_DB = {}

class AddMovieState(StatesGroup):
    waiting_for_video = State()
    waiting_for_code = State()

# Obuna tekshirish funksiyasi
async def check_subscriptions(user_id: int) -> bool:
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=ch["username"], user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception:
            return False
    return True

# Obuna tugmalarini yaratish
def get_sub_keyboard():
    buttons = []
    for ch in CHANNELS:
        buttons.append([types.InlineKeyboardButton(text=f"➕ {ch['username']} ga a'zo bo'lish", url=ch["link"])])
    buttons.append([types.InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_sub")])
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

# /start komandasi
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if not await check_subscriptions(user_id):
        await message.answer(
            " Botdan foydalanish uchun quyidagi kanallarga a'zo bo'ling va **'Obunani tekshirish'** tugmasini bosing:",
            reply_markup=get_sub_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await message.answer("Xush kelibsiz! Kino kodini yuboring 🎬")

# Tekshirish tugmasi bosilganda
@dp.callback_query(F.data == "check_sub")
async def callback_check_sub(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await check_subscriptions(user_id):
        await callback.message.delete()
        await callback.message.answer(" Baraka toping! Obuna tasdiqlandi. Endi kino kodini yuborishingiz mumkin 🎬")
    else:
        await callback.answer("❌ Hali barcha kanallarga a'zo bo'lmadingiz!", show_alert=True)

# Admin uchun kino qo'shish: /add
@dp.message(Command("add"))
async def cmd_add(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Iltimos, yuklamoqchi bo'lgan kino videosingizni yuboring:")
    await state.set_state(AddMovieState.waiting_for_video)

@dp.message(AddMovieState.waiting_for_video, F.video)
async def process_video(message: types.Message, state: FSMContext):
    await state.update_data(file_id=message.video.file_id)
    await message.answer("Ajoyib! Endi bu kino uchun **kod** kiriting (masalan: 105):", parse_mode="Markdown")
    await state.set_state(AddMovieState.waiting_for_code)

@dp.message(AddMovieState.waiting_for_code, F.text)
async def process_code(message: types.Message, state: FSMContext):
    code = message.text.strip()
    data = await state.get_data()
    MOVIES_DB[code] = data["file_id"]
    await state.clear()
    await message.answer(f"✅ Kino saqlandi! Kodi: `{code}`", parse_mode="Markdown")

# Admin uchun kinoni o'chirish: /delete [kod]
@dp.message(Command("delete"))
async def cmd_delete(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Foydalanish: `/delete [kino_kodi]`", parse_mode="Markdown")
        return
    code = args[1]
    if code in MOVIES_DB:
        del MOVIES_DB[code]
        await message.answer(f"🗑 `{code}` kodli kino o'chirildi!", parse_mode="Markdown")
    else:
        await message.answer("Bunday kodli kino topilmadi.")

# Kino kodini qabul qilish
@dp.message(F.text)
async def get_movie(message: types.Message):
    user_id = message.from_user.id
    if not await check_subscriptions(user_id):
        await message.answer(
            " Botdan foydalanish uchun avval kanallarga a'zo bo'ling:",
            reply_markup=get_sub_keyboard()
        )
        return
    
    code = message.text.strip()
    if code in MOVIES_DB:
        await message.answer_video(video=MOVIES_DB[code], caption=f"🎬 Kino kodi: {code}")
    else:
        await message.answer("❌ Bunday kodli kino topilmadi. Tekshirib qayta yuboring.")

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
