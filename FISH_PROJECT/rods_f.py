import telebot
from telebot import types
import json
import os
from FISH_PROJECT.config import secret
from FISH_PROJECT.logic_json import *

token = secret.get('BOT_API_TOKEN')
bot = telebot.TeleBot(token)

JSON_FOLDER = 'json'
SAVE_FILE_RODS = os.path.join(os.path.dirname(__file__), JSON_FOLDER, 'selected_rods.json')

if os.path.exists(SAVE_FILE_RODS):
    with open(SAVE_FILE_RODS, 'r', encoding='utf-8') as f:
        selected_rods = json.load(f)
else:
    selected_rods = {}

def load_rods_select():
    if os.path.exists(SAVE_FILE_RODS):
        with open(SAVE_FILE_RODS, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

def save_state_rods(selected_rods):
    with open(SAVE_FILE_RODS, 'w', encoding='utf-8') as f:
        json.dump(selected_rods, f, ensure_ascii=False, indent=4)

def create_markup_rods(user_selected_rod):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(f"{'✅ ' if user_selected_rod == 'rod1' else '100$ '}Plastic rod 🎣", callback_data="rod1"),
        types.InlineKeyboardButton(f"{'✅ ' if user_selected_rod == 'rod2' else '500$ '}Improved rod 🎣", callback_data="rod2"),
        types.InlineKeyboardButton(f"{'✅ ' if user_selected_rod == 'rod3' else '8000$ '}Steel rod 🎣", callback_data="rod3"),
        types.InlineKeyboardButton(f"{'✅ ' if user_selected_rod == 'rod4' else '50000$ '}Fiberglass rod 🎣", callback_data="rod4"),
        types.InlineKeyboardButton(f"{'✅ ' if user_selected_rod == 'rod5' else '100000$ '}Heavy rod 🎣", callback_data="rod5"),
        types.InlineKeyboardButton(f"{'✅ ' if user_selected_rod == 'rod6' else '250000$ '}Alloy rod 🎣🔥", callback_data="rod6"),
        types.InlineKeyboardButton(f"{'✅ ' if user_selected_rod == 'rod7' else '1000000$ '}Lava rod 🎣🔥", callback_data="rod7"),
        types.InlineKeyboardButton(f"{'✅ ' if user_selected_rod == 'rod8' else '10000000$ '}Magma rod 🎣🔥", callback_data="rod8"),
        types.InlineKeyboardButton("back", callback_data='button_shop')
    ]
    markup.add(*buttons)
    return markup

def rods_func(chat_id, inline_message_id=None, message_id=None):
    user_id = str(chat_id)
    selected_rods = load_rods_select()

    if user_id not in selected_rods:
        selected_rods[user_id] = "Empty"
        save_state_rods(selected_rods)

    current_rod = selected_rods.get(user_id, "Empty")
    markup = create_markup_rods(current_rod)

    if inline_message_id:
        try:
            bot.edit_message_text(
                inline_message_id=inline_message_id,
                text="Choose fishing rod:",
                reply_markup=markup
            )
        except Exception as e:
            print(f"Error editing inline message: {e}")
    elif message_id:
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="Choose fishing rod:",
                reply_markup=markup
            )
        except Exception as e:
            print(f"Error editing message: {e}")
            bot.send_message(chat_id, "Choose fishing rod:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Choose fishing rod:", reply_markup=markup)

def callback_query_rods(call):
    user_id = str(call.from_user.id)
    button_id = call.data
    user_money = load_money_data()
    selected_rods = load_rods_select()

    if user_id not in selected_rods:
        selected_rods[user_id] = "Empty"

    price_map = {
        "rod1": 100, "rod2": 500, "rod3": 8000, "rod4": 50000,
        "rod5": 100000, "rod6": 250000, "rod7": 1000000, "rod8": 10000000
    }

    if button_id == selected_rods.get(user_id, "Empty"):
        selected_rods[user_id] = "Empty"
    else:
        price = price_map.get(button_id, 0)
        if user_money.get(user_id, 0) >= price:
            user_money[user_id] -= price
            selected_rods[user_id] = button_id
            save_money_data(user_money)
        else:
            bot.answer_callback_query(call.id, text="You don't have enough money(", show_alert=False)
            return

    save_state_rods(selected_rods)
    updated_markup = create_markup_rods(selected_rods.get(user_id, "Empty"))

    try:
        if hasattr(call, 'inline_message_id'):
            bot.edit_message_text(
                inline_message_id=call.inline_message_id,
                text="Choose fishing rod:",
                reply_markup=updated_markup
            )
        else:
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=updated_markup
            )
    except Exception as e:
        print(f"Error updating markup: {e}")

    bot.answer_callback_query(call.id)

def get_rods_number(rods_type):
    if not rods_type or rods_type == "Empty":
        return 1
    return int(rods_type[-1]) if rods_type[-1].isdigit() else 1
