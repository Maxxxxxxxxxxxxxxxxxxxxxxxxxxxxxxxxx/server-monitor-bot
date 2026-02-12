import telebot # импортируем telebot
import os
import json
import random # для выбора случайного комплимента
import time
import threading
from FISH_PROJECT.config import secret

token = secret.get('BOT_API_TOKEN')
bot = telebot.TeleBot(token)


# Обработчик inline-запросов с КД
@bot.callback_query_handler(func=lambda call: True)
def cooldowns_func(call):
    user_id = call.from_user.id
    current_time = time.time()
    # Проверяем, есть ли запись о последнем запросе пользователя
    if user_id in user_cooldowns:
        last_request_time = user_cooldowns[user_id]
        # Если прошло меньше 3 секунд, игнорируем запрос
        if current_time - last_request_time < 1:
            bot.answer_callback_query(call.id, "You must wait 3s before fishing again.", show_alert=True)
            return
    # Обновляем время последнего запроса
    user_cooldowns[user_id] = current_time


# Функция для очистки колдавна
def clean_cooldowns():
    while True:
        current_time = time.time()
        # Удаляем записи старше 10 минут
        for user_id in list(user_cooldowns.keys()):
            if current_time - user_cooldowns[user_id] > 600:  # 600 секунд = 10 минут
                del user_cooldowns[user_id]
        # Ждем 1 час перед следующей очисткой
        time.sleep(3600)  # 3600 секунд = 1 час


# Запуск функции очистки в отдельном потоке
cleanup_thread = threading.Thread(target=clean_cooldowns)
cleanup_thread.daemon = True  # Поток завершится, если завершится основной поток
cleanup_thread.start()
