import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# ==================== НАСТРОЙКИ ====================
BOT_TOKEN = "8647204871:AAEDveUJo9mgzExI0LhdOnh3NEBJO96FzpE"
ADMIN_ID = 6825447755   # <<< ЗАМЕНИ НА СВОЙ CHAT ID
# ===================================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_state = {}
user_method = {}

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Buy Key", callback_data="buy_key")]
    ])

def method_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="₿ Crypto", callback_data="method_crypto")],
        [InlineKeyboardButton(text="💳 Card", callback_data="method_card")],
        [InlineKeyboardButton(text="⬅ Back", callback_data="back")]
    ])

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "👋 Welcome to De HUB!\n\n"
        "Press the button below to buy a premium key.",
        reply_markup=main_menu()
    )

@dp.callback_query(F.data == "buy_key")
async def buy_key(callback: CallbackQuery):
    await callback.message.edit_text(
        "Choose a payment method:",
        reply_markup=method_menu()
    )
    await callback.answer()

@dp.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
    await callback.message.edit_text(
        "👋 Welcome to De HUB!",
        reply_markup=main_menu()
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("method_"))
async def method_choice(callback: CallbackQuery):
    method = callback.data.replace("method_", "")
    user_method[callback.from_user.id] = method
    user_state[callback.from_user.id] = "waiting_username"

    method_text = "Crypto" if method == "crypto" else "Card"
    await callback.message.edit_text(
        f"Payment method: {method_text}\n\n"
        "Send your Telegram username (e.g. @yourname)\n"
        "so I can contact you about payment."
    )
    await callback.answer()

@dp.message()
async def username_handler(message: Message):
    uid = message.from_user.id
    logging.info(f"Message from {uid}: {message.text}")

    if user_state.get(uid) != "waiting_username":
        logging.info(f"User {uid} not in waiting_username state, ignoring")
        return

    username = (message.text or "").strip()
    method = user_method.get(uid, "unknown")
    method_text = "Crypto" if method == "crypto" else "Card"

    # === ОТПРАВЛЯЕМ ЗАЯВКУ АДМИНУ ===
    admin_msg = (
        "🔔 NEW KEY REQUEST\n"
        "━━━━━━━━━━━━━━━━━\n"
        f"👤 Username: {username}\n"
        f"🆔 User ID: {uid}\n"
        f"💳 Method: {method_text}\n"
        "📌 Status: Waiting for contact"
    )

    try:
        await bot.send_message(chat_id=ADMIN_ID, text=admin_msg)
        logging.info(f"Request sent to admin {ADMIN_ID}")
    except Exception as e:
        logging.error(f"Admin notify failed: {e}")

    # === ОТВЕЧАЕМ ЮЗЕРУ ===
    await message.answer(
        "✅ Your purchase request has been sent!\n\n"
        "Please wait for a notification. I will contact you soon."
    )

    user_state.pop(uid, None)
    user_method.pop(uid, None)

async def main():
    logging.info("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())