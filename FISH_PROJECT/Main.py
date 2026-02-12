from telebot import util
import telebot
import os
import json
import random
import time
import threading
from FISH_PROJECT.rods_f import load_rods_select
from FISH_PROJECT.config import secret
from telebot import types
from FISH_PROJECT.fish_list import *
from FISH_PROJECT.logic_json import *
import FISH_PROJECT.rods_f as rods_f
import FISH_PROJECT.bait_f as bait_f
import FISH_PROJECT.boat_f as boat_f
from telebot import apihelper
import sys
import select
import matplotlib
matplotlib.use('Agg')  # Важно для работы без GUI
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

# print("Текущая рабочая директория:", os.getcwd())
# print("Путь к скрипту:", os.path.dirname(os.path.abspath(__file__)))

# Глобальные переменные
last_message_id = None
user_cooldowns = {}
user_bets = {}
user_xp = load_xp_data()
selected_bait = bait_f.load_bait_select()
inline_sessions = {}
kazik_history_file = os.path.join(os.path.dirname(__file__), 'json', "kazik_history.json")  # Файл для истории баланса

# Инициализация бота
token = secret.get('BOT_API_TOKEN')
bot = telebot.TeleBot(token)





# ============ INLINE HANDLERS ============
@bot.inline_handler(func=lambda query: True)
def handle_inline_query(inline_query):
    try:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("fish", callback_data='button_fish')
        markup.add(btn1)

        result = types.InlineQueryResultArticle(
            id="1",
            title="Fishing Bot",
            description="Press to start fishing",
            input_message_content=types.InputTextMessageContent(
                message_text="Hey, {0.first_name} 👋\nTo start fishing, press fish button".format(
                    inline_query.from_user)
            ),
            reply_markup=markup
        )
        bot.answer_inline_query(inline_query.id, [result])
    except Exception as e:
        print(f"Inline query error: {e}")


# ============ CORE FUNCTIONS ============
def clean_cooldowns():
    while True:
        current_time = time.time()
        for user_id in list(user_cooldowns.keys()):
            if current_time - user_cooldowns[user_id] > 600:
                del user_cooldowns[user_id]
        time.sleep(1800)


cleanup_thread = threading.Thread(target=clean_cooldowns)
cleanup_thread.daemon = True
cleanup_thread.start()

# ============ KAZIK HISTORY FUNCTIONS ============
# ============ KAZIK HISTORY FUNCTIONS ============
def load_kazik_history():
    """Загружаем историю баланса Kazik_Bank"""
    try:
        with open(kazik_history_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_kazik_history(history):
    """Сохраняем историю баланса Kazik_Bank"""
    with open(kazik_history_file, 'w') as f:
        json.dump(history, f)

def update_kazik_history(balance):
    """Обновляем историю баланса"""
    history = load_kazik_history()

    # Ограничиваем историю 1000 последними записями
    if len(history) >= 1000:
        history = history[-999:]

    history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "balance": balance
    })

    save_kazik_history(history)
# ============ STAT COMMAND HANDLER ============
@bot.message_handler(commands=['stat'])
def handle_stat_command(message):
    """Обработчик команды stat для показа графика баланса"""
    history = load_kazik_history()

    if not history:
        bot.reply_to(message, "История баланса казика пустая.")
        return

    # Подготовка данных для графика
    changes = list(range(1, len(history) + 1))
    balances = [point["balance"] for point in history]
    current_balance = balances[-1] if balances else 0

    # Создаем график с улучшенной визуализацией
    plt.figure(figsize=(12, 6))

    # Основная линия графика
    plt.plot(changes, balances, linestyle='-', color='#1f77b4', linewidth=2, alpha=0.8)

    # Точки для важных изменений
    plt.scatter(changes, balances, color='#ff7f0e', s=15, alpha=0.6)

    # Добавляем горизонтальную линию для текущего баланса
    plt.axhline(y=current_balance, color='g', linestyle='--', alpha=0.5)

    # Заголовки и подписи
    plt.title(f'История баланса Kazik Bank\nТекущий баланс: {current_balance}$', fontsize=14)
    plt.xlabel('Количество игр в coinflip', fontsize=12)
    plt.ylabel('Баланс ($)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)

    # Автоматическое масштабирование
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Сохраняем график во временный файл
    temp_file = "kazik_stat.png"
    plt.savefig(temp_file, dpi=150)  # Увеличиваем разрешение
    plt.close()

    # Создаем HTML-версию с улучшенной визуализацией
    # Замените HTML-часть в вашем коде на эту версию:

    # Замените HTML-часть в вашем коде на эту версию:

    html_content = f"""
    <html>
    <head>
        <title>История баланса Kazik Bank</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 10px;
                background-color: #f8f9fa;
            }}
            .container {{ 
                max-width: 95vw; 
                width: 95vw;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                padding: 20px;
                min-height: 90vh;
            }}
            .stats {{ 
                margin-top: 30px;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
            }}
            .stat-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}
            .stat-value {{
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .stat-label {{
                font-size: 14px;
                opacity: 0.9;
            }}
            #plot {{
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            h1 {{
                text-align: center;
                color: #2c3e50;
                margin-bottom: 30px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📈 История баланса Kazik Bank</h1>
            <div id="plot"></div>

            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{current_balance}$</div>
                    <div class="stat-label">Текущий баланс</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(history)}</div>
                    <div class="stat-label">Всего игр</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{max(balances) if balances else 0}$</div>
                    <div class="stat-label">Максимальный баланс</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{min(balances) if balances else 0}$</div>
                    <div class="stat-label">Минимальный баланс</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{sum(balances) / len(balances) if balances else 0:.2f}$</div>
                    <div class="stat-label">Средний баланс</div>
                </div>
            </div>
        </div>

        <script>
            // Подготавливаем данные с временными метками для лучшего отображения
            var timestamps = {[f'"{point["timestamp"]}"' for point in history]};
            var averageBalance = {sum(balances) / len(balances) if balances else 0:.2f};

            var trace1 = {{
                x: timestamps,
                y: {balances},
                type: 'scatter',
                mode: 'lines',
                line: {{
                    color: '#2E86AB',
                    width: 2,
                    shape: 'linear'
                }},
                name: 'Баланс',
                hovertemplate: '<b>Время:</b> %{{x}}<br><b>Баланс:</b> %{{y}}$<extra></extra>',
                connectgaps: false
            }};

            // Добавляем точки для маркеров (показываются только при сильном приближении)
            var trace2 = {{
                x: timestamps,
                y: {balances},
                type: 'scatter',
                mode: 'markers',
                marker: {{
                    color: '#A23B72',
                    size: 4,
                    opacity: 0.7
                }},
                name: 'Точки',
                hovertemplate: '<b>Время:</b> %{{x}}<br><b>Баланс:</b> %{{y}}$<extra></extra>',
                visible: 'legendonly'
            }};

            // Линия среднего баланса
            var trace3 = {{
                x: timestamps,
                y: Array(timestamps.length).fill(averageBalance),
                type: 'scatter',
                mode: 'lines',
                line: {{
                    color: '#FF6B35',
                    width: 2,
                    dash: 'dash'
                }},
                name: 'Средний баланс (' + averageBalance.toFixed(0) + '$)',
                hovertemplate: '<b>Средний баланс:</b> ' + averageBalance.toFixed(0) + '$<extra></extra>',
                opacity: 0.8
            }};

            var data = [trace1, trace2, trace3];

            var layout = {{
                title: {{
                    text: 'Динамика баланса Kazik Bank',
                    font: {{
                        size: 20,
                        color: '#2c3e50'
                    }}
                }},
                xaxis: {{
                    title: {{
                        text: 'Время',
                        font: {{ size: 14 }}
                    }},
                    type: 'category',
                    tickangle: -45,
                    tickfont: {{ size: 10 }},
                    rangeslider: {{
                        visible: true,
                        thickness: 0.1,
                        yaxis: {{
                            rangemode: 'match'
                        }}
                    }},
                    rangeselector: {{
                        buttons: [
                            {{
                                count: 10,
                                label: 'Последние 10',
                                step: 'all',
                                stepmode: 'backward'
                            }},
                            {{
                                count: 50,
                                label: 'Последние 50',
                                step: 'all',
                                stepmode: 'backward'
                            }},
                            {{
                                count: 100,
                                label: 'Последние 100',
                                step: 'all',
                                stepmode: 'backward'
                            }},
                            {{ step: 'all', label: 'Все' }}
                        ]
                    }}
                }},
                yaxis: {{
                    title: {{
                        text: 'Баланс ($)',
                        font: {{ size: 14 }}
                    }},
                    tickformat: '$,.0f',
                    autorange: false,
                    fixedrange: false,
                    range: [{min(balances) if balances else 0}, {max(balances) if balances else 0}]
                }},
                hovermode: 'x unified',
                showlegend: true,
                legend: {{
                    x: 0.02,
                    y: 0.98,
                    bgcolor: 'rgba(255,255,255,0.8)',
                    bordercolor: 'rgba(0,0,0,0.2)',
                    borderwidth: 1
                }},
                plot_bgcolor: 'rgba(248,249,250,0.8)',
                paper_bgcolor: 'white',
                margin: {{
                    l: 80,
                    r: 40,
                    t: 80,
                    b: 120
                }},
                height: 800
            }};

            var config = {{
                displayModeBar: true,
                displaylogo: false,
                modeBarButtonsToRemove: ['lasso2d', 'select2d'],
                modeBarButtonsToAdd: [
                    {{
                        name: 'Показать точки',
                        icon: Plotly.Icons.pencil,
                        click: function(gd) {{
                            var visible = gd.data[1].visible;
                            if (visible === true || visible === undefined) {{
                                Plotly.restyle(gd, 'visible', 'legendonly', [1]);
                            }} else {{
                                Plotly.restyle(gd, 'visible', true, [1]);
                            }}
                        }}
                    }},
                    {{
                        name: 'Автомасштаб Y для видимой области',
                        icon: {{
                            'width': 857.1,
                            'height': 1000,
                            'path': 'm214 429h571v142h-571v-142z m571 286h-571v-143h571v143z m-571-429h571v143h-571v-143z',
                            'transform': 'matrix(1 0 0 -1 0 850)'
                        }},
                        click: function(gd) {{
                            var xRange = gd.layout.xaxis.range;
                            if (xRange) {{
                                var startIdx = Math.max(0, Math.floor(xRange[0]));
                                var endIdx = Math.min(timestamps.length - 1, Math.ceil(xRange[1]));
                                var visibleBalances = {balances}.slice(startIdx, endIdx + 1);

                                if (visibleBalances.length > 0) {{
                                    var minBalance = Math.min(...visibleBalances);
                                    var maxBalance = Math.max(...visibleBalances);
                                    var range = maxBalance - minBalance;
                                    var padding = Math.max(range * 0.1, 50);

                                    Plotly.relayout(gd, {{
                                        'yaxis.range': [minBalance - padding, maxBalance + padding]
                                    }});
                                }}
                            }}
                        }}
                    }}
                ],
                scrollZoom: true,
                doubleClick: 'reset+autosize',
                responsive: true
            }};

            Plotly.newPlot('plot', data, layout, config);

            // Обработчик изменения масштаба для адаптивного отображения точек и масштабирования Y
            document.getElementById('plot').on('plotly_relayout', function(eventdata) {{
                var plot = document.getElementById('plot');

                // Адаптивное масштабирование оси Y при изменении диапазона X
                if (eventdata['xaxis.range[0]'] !== undefined && eventdata['xaxis.range[1]'] !== undefined) {{
                    var startIdx = Math.max(0, Math.floor(eventdata['xaxis.range[0]']));
                    var endIdx = Math.min(timestamps.length - 1, Math.ceil(eventdata['xaxis.range[1]']));

                    // Находим мин и макс значения в видимом диапазоне
                    var visibleBalances = {balances}.slice(startIdx, endIdx + 1);
                    if (visibleBalances.length > 0) {{
                        var minBalance = Math.min(...visibleBalances);
                        var maxBalance = Math.max(...visibleBalances);

                        // Добавляем небольшой отступ для лучшей визуализации
                        var range = maxBalance - minBalance;
                        var padding = range * 0.1; // 10% отступ

                        // Если диапазон очень маленький, устанавливаем минимальный отступ
                        if (range < 100) {{
                            padding = 50;
                        }}

                        var newMin = minBalance - padding;
                        var newMax = maxBalance + padding;

                        // Обновляем диапазон оси Y
                        Plotly.relayout(plot, {{
                            'yaxis.range': [newMin, newMax],
                            'yaxis.autorange': false
                        }});
                    }}

                    // Показываем точки при сильном приближении
                    var totalRange = timestamps.length;
                    var visibleRange = endIdx - startIdx;
                    if (visibleRange < totalRange * 0.15) {{
                        Plotly.restyle('plot', 'visible', true, [1]);
                    }} else {{
                        Plotly.restyle('plot', 'visible', 'legendonly', [1]);
                    }}
                }}

                // Сброс к полному диапазону при двойном клике или кнопке "Все"
                if (eventdata['xaxis.autorange'] === true || eventdata['yaxis.autorange'] === true) {{
                    Plotly.relayout(plot, {{
                        'yaxis.range': [{min(balances) if balances else 0}, {max(balances) if balances else 0}],
                        'yaxis.autorange': false
                    }});
                }}
            }});

            // Обработчик для кнопки "Автомасштаб Y"
            document.getElementById('plot').on('plotly_doubleclick', function() {{
                var plot = document.getElementById('plot');
                setTimeout(function() {{
                    var xRange = plot.layout.xaxis.range;
                    if (xRange) {{
                        var startIdx = Math.max(0, Math.floor(xRange[0]));
                        var endIdx = Math.min(timestamps.length - 1, Math.ceil(xRange[1]));
                        var visibleBalances = {balances}.slice(startIdx, endIdx + 1);

                        if (visibleBalances.length > 0) {{
                            var minBalance = Math.min(...visibleBalances);
                            var maxBalance = Math.max(...visibleBalances);
                            var range = maxBalance - minBalance;
                            var padding = Math.max(range * 0.1, 50);

                            Plotly.relayout(plot, {{
                                'yaxis.range': [minBalance - padding, maxBalance + padding]
                            }});
                        }}
                    }}
                }}, 100);
            }});
        </script>
    </body>
    </html>
    """
    # Сохраняем HTML во временный файл
    html_file = "kazik_stat.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Отправляем пользователю оба варианта
    with open(temp_file, 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption="График баланса Kazik_Bank")

    with open(html_file, 'rb') as html:
        bot.send_document(message.chat.id, html, caption="html версия")

    # Удаляем временные файлы
    os.remove(temp_file)
    os.remove(html_file)


@bot.callback_query_handler(func=lambda call: call.data == 'stats_menu')
def handle_stats_menu(call):
    user_money = load_money_data()

    # Создаем список пользователей, исключая Kazik_Bank
    users_list = []
    for user_id, money in user_money.items():
        if user_id == "Kazik_Bank":
            continue
        users_list.append((user_id, money))

    # Сортируем по убыванию денег
    users_list.sort(key=lambda x: x[1], reverse=True)

    # Формируем текст сообщения
    text = "💰 Top 10 Users by Money:\n\n"

    # Всегда добавляем Kazik_Bank первым
    text += f"0. Kazik_Bank: {user_money.get('Kazik_Bank', 0)}$\n"

    # Добавляем топ-10 пользователей
    for i, (user_id, money) in enumerate(users_list[:10], start=1):
        try:
            # Пытаемся получить имя пользователя по ID
            user_info = bot.get_chat(user_id)
            name = user_info.first_name
        except:
            name = f"User {user_id}"
        text += f"{i}. {name}: {money}$\n"

    # Создаем клавиатуру с кнопкой "Back"
    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton("Back", callback_data='button_menu')
    markup.add(btn_back)

    # Редактируем сообщение
    if hasattr(call, 'inline_message_id'):
        bot.edit_message_text(
            inline_message_id=call.inline_message_id,
            text=text,
            reply_markup=markup
        )
    else:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=markup
        )


def menu_button(chat_id, inline_message_id=None):
    global last_message_id

    user_id = str(chat_id)
    user_bait_data = load_bait_data()

    # Добавляем кнопки
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("Shop 🪱", callback_data='button_shop')
    btn2 = types.InlineKeyboardButton("Fishing 🎣", callback_data='sub_button_menu')
    btn3 = types.InlineKeyboardButton("Coinflip 🎰", callback_data='coinflip_menu')
    btn4 = types.InlineKeyboardButton("Stats 📊", callback_data='stats_menu')
    markup.add(btn2, btn1, btn3, btn4)

    selected_bait = bait_f.load_bait_select()
    user_money = load_money_data()
    user_xp = load_xp_data()

    # Получаем данные уровня
    current_xp = user_xp[user_id]
    current_level = calculate_level(current_xp)
    color = get_level_color(current_level)
    next_level_xp = get_xp_for_next_level(current_level)
    progress = get_level_progress(current_xp)
    progress_bar = create_progress_bar(progress)

    # Формируем текст с прогрессом уровня
    # {progress_bar} {progress}%
    text = f"""Menu:
Balance: {user_money.get(user_id, 0)}$
Level: {current_level} {color}
{progress_bar} {progress}%
XP: {current_xp} | Next: {next_level_xp} XP

Bait: {selected_bait.get(user_id, "Empty")} {user_bait_data.get(user_id, {}).get(selected_bait.get(user_id, "Empty"), 0)}"""

    if inline_message_id:
        bot.edit_message_text(
            inline_message_id=inline_message_id,
            text=text,
            reply_markup=markup
        )
    elif last_message_id:
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=last_message_id,
                text=text,
                reply_markup=markup
            )
        except:
            msg = bot.send_message(chat_id, text, reply_markup=markup)
            last_message_id = msg.message_id
    else:
        msg = bot.send_message(chat_id, text, reply_markup=markup)
        last_message_id = msg.message_id


@bot.callback_query_handler(func=lambda call: call.data == 'coinflip_menu')
def handle_coinflip_menu(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_heads = types.InlineKeyboardButton("Heads", callback_data='coinflip_heads')
    btn_tails = types.InlineKeyboardButton("Tails", callback_data='coinflip_tails')
    btn_back = types.InlineKeyboardButton("Back", callback_data='button_menu')
    markup.add(btn_heads, btn_tails, btn_back)

    try:
        if hasattr(call, 'inline_message_id'):
            bot.edit_message_text(
                inline_message_id=call.inline_message_id,
                text="Choose Heads or Tails:",
                reply_markup=markup
            )
        else:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Choose Heads or Tails:",
                reply_markup=markup
            )
    except Exception as e:
        print(f"Error editing message: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('coinflip_'))
def handle_coinflip_actions(call):
    user_id = str(call.from_user.id)

    # Обработка выбора "Heads" или "Tails"
    if call.data in ['coinflip_heads', 'coinflip_tails']:
        choice = call.data.split('_')[1]
        user_bets[user_id] = {'choice': choice}

        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("Back", callback_data='coinflip_menu')
        btn_20 = types.InlineKeyboardButton("20% of balance", callback_data='coinflip_bet_20')
        btn_50 = types.InlineKeyboardButton("50% of balance", callback_data='coinflip_bet_50')
        btn_100 = types.InlineKeyboardButton("100% of balance", callback_data='coinflip_bet_100')
        markup.add(btn_20, btn_50, btn_100, btn_back)

        bot.edit_message_text(
            inline_message_id=call.inline_message_id if hasattr(call, 'inline_message_id') else None,
            chat_id=None if hasattr(call, 'inline_message_id') else call.message.chat.id,
            message_id=None if hasattr(call, 'inline_message_id') else call.message.message_id,
            text=f"You chose {choice.capitalize()}. Now choose the bet amount:",
            reply_markup=markup
        )

    # Обработка ставки (20%, 50%, 100%)
    elif call.data.startswith('coinflip_bet_'):
        if user_id not in user_bets:
            bot.answer_callback_query(call.id, "❌ Error: Choice not found. Start again.")
            return

        user_money = load_money_data()
        current_money = user_money.get(user_id, 0)
        choice = user_bets[user_id]['choice']

        # Определяем ставку
        percent = int(call.data.split('_')[2])  # 20, 50, 100
        bet = int(current_money * (percent / 100))

        if bet <= 0:
            bot.answer_callback_query(call.id, "❌ Your balance is too low!")
            return

        # Подбрасываем монету
        result = random.choice(['heads', 'tails'])
        win = choice == result

        # Обновляем баланс
        user_money[user_id] = current_money + (bet if win else -bet)
        user_money['Kazik_Bank'] += (-bet if win else bet)

        save_money_data(user_money)

        update_kazik_history(user_money['Kazik_Bank'])

        # Формируем результат
        result_text = (
            f"🪙 Coin flip result: {result.capitalize()}!\n"
            f"Your choice: {choice.capitalize()}\n"
            f"Bet: {bet}$\n\n"
            f"{'🎉 You won!' if win else '😢 You lost...'} {'+' if win else '-'}{bet}$\n"
            f"Balance: {user_money[user_id]}$"
        )

        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_again = types.InlineKeyboardButton("Play again", callback_data='coinflip_menu')
        btn_back = types.InlineKeyboardButton("Back to menu", callback_data='button_menu')
        markup.add(btn_again, btn_back)

        # Отправляем результат
        if hasattr(call, 'inline_message_id'):
            bot.edit_message_text(
                inline_message_id=call.inline_message_id,
                text=result_text,
                reply_markup=markup
            )
        else:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=result_text,
                reply_markup=markup
            )

    # Обработка возврата в меню
    elif call.data == 'coinflip_menu':
        handle_coinflip_menu(call)





@bot.callback_query_handler(func=lambda call: call.data == 'rod')
def handle_rod_callback(call):
    if hasattr(call, 'inline_message_id'):
        rods_f.rods_func(call.from_user.id, inline_message_id=call.inline_message_id)
    else:
        rods_f.rods_func(call.message.chat.id, message_id=call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == 'boat')
def handle_boat_callback(call):
    if hasattr(call, 'inline_message_id'):
        boat_f.boat_func(call.from_user.id, inline_message_id=call.inline_message_id)
    else:
        boat_f.boat_func(call.message.chat.id, message_id=call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == 'bait')
def handle_bait_callback(call):
    if hasattr(call, 'inline_message_id'):
        bait_f.bait_func(call.from_user.id, inline_message_id=call.inline_message_id)
    else:
        bait_f.bait_func(call.message.chat.id, message_id=call.message.message_id)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    global last_message_id

    user_id = str(call.from_user.id)
    inline_msg_id = call.inline_message_id if hasattr(call, 'inline_message_id') else None

    # Инициализация данных пользователя (остается без изменений)
    user_money = load_money_data()
    user_xp = load_xp_data()
    if user_id not in user_money:
        user_money[user_id] = 0
        save_money_data(user_money)
    if user_id not in user_xp:
        user_xp[user_id] = 0
        save_xp_data(user_xp)

    user_bait_data = load_bait_data()
    if user_id not in user_bait_data:
        user_bait_data[user_id] = {
            "Empty": 0,
            "Worms": 0,
            "Leeches": 0,
            "Magnet": 0
        }
        save_bait_data(user_bait_data)

    selected_bait = bait_f.load_bait_select()
    if user_id not in selected_bait:
        selected_bait[user_id] = "Empty"
        bait_f.save_state_bait(selected_bait)

    biome = load_biome_data()
    if user_id not in biome:
        biome[user_id] = "River"
    save_biome_data(biome)

    boat = boat_f.load_boat_select()
    if user_id not in boat:
        boat[user_id] = "Empty"
        boat_f.save_state_boat(boat)

    selected_rods = rods_f.load_rods_select()
    if user_id not in selected_rods:
        selected_rods[user_id] = "Empty"
        rods_f.save_state_rods(selected_rods)

    # Обработка callback данных
    if call.data == 'button_fish':
        user_money[user_id] += fish_price1()
        save_money_data(user_money)


        bait_type = selected_bait[user_id]
        if user_bait_data[user_id][bait_type] > 0:
            user_bait_data[user_id][bait_type] -= 1
        else:
            bot.answer_callback_query(call.id, text="You out of baits", show_alert=False)
            selected_bait[user_id] = "Empty"
        bait_f.save_state_bait(selected_bait)
        save_bait_data(user_bait_data)

        bot.answer_callback_query(call.id, text="+" + str(fish_price1()) + "$", show_alert=False)
        fish_menu(call)

    elif call.data == 'button_menu':
        menu_button(call.from_user.id, inline_msg_id)
    elif call.data == 'sub_btn_fish':
        fish_menu(call)
    elif call.data == 'sub_button_menu':
        fish_menu(call)
    elif call.data == 'button_shop':
        shop_button(call.from_user.id, inline_msg_id)
    elif call.data == 'button_back':
        menu_button(call.from_user.id, inline_msg_id)
    elif call.data == 'rod':
        rods_f.rods_func(call.from_user.id, inline_msg_id if inline_msg_id else call.message.message_id)
    elif call.data in ["rod1", 'rod2', 'rod3', "rod4", 'rod5', 'rod6', 'rod7', 'rod8']:
        rods_f.callback_query_rods(call)
    elif call.data == 'boat':
        boat_f.boat_func(call.from_user.id, inline_msg_id if inline_msg_id else call.message.message_id)
    elif call.data in ["boat1", 'boat2', 'boat3', "boat4", 'boat5', 'boat6']:
        boat_f.callback_query_boat(call)
    # elif call.data == 'bait':
    #     bait_f.bait_func(call.from_user.id, inline_msg_id if inline_msg_id else call.message.message_id)

    # elif call.data == 'Worms':
    #     if selected_bait[user_id] in ["Worms"]:
    #         bait_f.save_state_bait(selected_bait)
    #         bait_f.callback_query_bait(call)
    #         user_bait_data = load_bait_data()
    #         user_bait_data[user_id]["Worms"] += 20
    #         save_bait_data(user_bait_data)
    #         return
    #
    #     if user_money[user_id] >= 80:
    #         user_money[user_id] -= 80
    #         save_money_data(user_money)
    #         bait_type = "Worms"
    #         selected_bait[user_id] = bait_f.load_bait_select()
    #         user_bait_data = load_bait_data()
    #         if (bait_type not in selected_bait[user_id]) and (user_bait_data[user_id]["Worms"] > 0):
    #             selected_bait[user_id] = "Empty"
    #             bait_f.save_state_bait(selected_bait)
    #             bait_f.callback_query_bait(call)
    #         else:
    #             selected_bait[user_id] = "Worms"
    #             bait_f.save_state_bait(selected_bait)
    #             bait_f.callback_query_bait(call)
    #             user_bait_data[user_id][bait_type] = 20
    #             save_bait_data(user_bait_data)
    #         save_bait_data(user_bait_data)
    #     elif user_bait_data[user_id]["Worms"] > 0:
    #         bait_f.callback_query_bait(call)
    #     else:
    #         bot.answer_callback_query(call.id, text="You don't have enough money(", show_alert=False)
    # elif call.data == 'Leeches':
    #     if selected_bait[user_id] in ["Leeches"]:
    #         bait_f.save_state_bait(selected_bait)
    #         bait_f.callback_query_bait(call)
    #         user_bait_data = load_bait_data()
    #         user_bait_data[user_id]["Leeches"] += 20
    #         save_bait_data(user_bait_data)
    #         return
    #
    #     if user_money[user_id] >= 500:
    #         user_money[user_id] -= 500
    #         save_money_data(user_money)
    #         bait_type = "Leeches"
    #         selected_bait[user_id] = bait_f.load_bait_select()
    #         user_bait_data = load_bait_data()
    #         if (bait_type not in selected_bait[user_id]) and (user_bait_data[user_id]["Leeches"] > 0):
    #             selected_bait[user_id] = "Empty"
    #             bait_f.save_state_bait(selected_bait)
    #             bait_f.callback_query_bait(call)
    #         else:
    #             selected_bait[user_id] = "Leeches"
    #             bait_f.save_state_bait(selected_bait)
    #             bait_f.callback_query_bait(call)
    #             user_bait_data[user_id][bait_type] = 20
    #             save_bait_data(user_bait_data)
    #         save_bait_data(user_bait_data)
    #     elif user_bait_data[user_id]["Leeches"] > 0:
    #         bait_f.callback_query_bait(call)
    #     else:
    #         bot.answer_callback_query(call.id, text="You don't have enough money(", show_alert=False)
    # elif call.data == 'Magnet':
    #     if selected_bait[user_id] in ["Magnet"]:
    #         bait_f.save_state_bait(selected_bait)
    #         bait_f.callback_query_bait(call)
    #         user_bait_data = load_bait_data()
    #         user_bait_data[user_id]["Magnet"] += 20
    #         save_bait_data(user_bait_data)
    #         return
    #
    #     if user_money[user_id] >= 500:
    #         user_money[user_id] -= 500
    #         save_money_data(user_money)
    #         bait_type = "Magnet"
    #         selected_bait[user_id] = bait_f.load_bait_select()
    #         user_bait_data = load_bait_data()
    #         if (bait_type not in selected_bait[user_id]) and (user_bait_data[user_id]["Magnet"] > 0):
    #             selected_bait[user_id] = "Empty"
    #             bait_f.save_state_bait(selected_bait)
    #             bait_f.callback_query_bait(call)
    #         else:
    #             selected_bait[user_id] = "Magnet"
    #             bait_f.save_state_bait(selected_bait)
    #             bait_f.callback_query_bait(call)
    #             user_bait_data[user_id][bait_type] = 20
    #             save_bait_data(user_bait_data)
    #         save_bait_data(user_bait_data)
    #     elif user_bait_data[user_id]["Magnet"] > 0:
    #         bait_f.callback_query_bait(call)
    #     else:
    #         bot.answer_callback_query(call.id, text="You don't have enough money(", show_alert=False)
    elif call.data in ['Worms', 'Leeches', 'Magnet']:
        bait_f.callback_query_bait(call)
        return  # Важно! Чтобы не было двойного answer_callback_query
    bot.answer_callback_query(call.id)


# ============ LEVEL SYSTEM ============
def calculate_level(xp):
    """Calculate level based on exponential formula"""
    if xp < 100:
        return 0
    return int((xp / 100) ** 0.5)


def get_level_color(level):
    """Get color symbol based on level"""
    colors = ['🟤', '🟣', '🔵', '🟢', '🟡', '🟠', '🔴', '⚪', '⚫','🔘','⭕','☢','⚜']
    if level < 10:
        return colors[0]
    elif level < 20:
        return colors[1]
    elif level < 35:
        return colors[2]
    elif level < 50:
        return colors[3]
    elif level < 75:
        return colors[4]
    elif level < 100:
        return colors[5]
    elif level < 150:
        return colors[6]
    elif level < 200:
        return colors[7]
    elif level < 250:
        return colors[8]
    elif level < 300:
        return colors[9]
    elif level < 400:
        return colors[10]
    elif level < 666:
        return colors[11]
    elif level >= 666:
        return colors[12]

def get_xp_for_next_level(current_level):
    """Calculate XP needed for next level"""
    return (current_level + 1) ** 2 * 100


def get_level_progress(current_xp):
    """Get progress to next level"""
    current_level = calculate_level(current_xp)
    next_level_xp = get_xp_for_next_level(current_level)
    current_level_xp = (current_level ** 2) * 100

    # Calculate progress percentage
    progress = (current_xp - current_level_xp) / (next_level_xp - current_level_xp) * 100
    return min(100, max(0, int(progress)))  # Clamp between 0-100


def create_progress_bar(progress):
    """Create visual progress bar"""
    bar_length = 10
    filled = int(progress / 100 * bar_length)
    return '=' * filled + '-' * (bar_length - filled)



def fish_menu(call):
    global last_message_id
    user_xp = load_xp_data()
    current_time = time.time()
    user_id = str(call.from_user.id)

    if user_id in user_cooldowns:
        last_request_time = user_cooldowns[user_id]
        if current_time - last_request_time < 3:
            bot.answer_callback_query(call.id, "You must wait 3s before performing this action again.", show_alert=True)
            return
    user_cooldowns[user_id] = current_time

    selected_rods = rods_f.load_rods_select()
    selected_bait = bait_f.load_bait_select()
    boat_data = boat_f.load_boat_select()
    current_rod = selected_rods.get(user_id, "Empty")
    current_bait = selected_bait.get(user_id, "Empty")
    current_boat = boat_data.get(user_id, "Empty")

    rod_number = rods_f.get_rods_number(current_rod)
    bait_number = bait_f.get_bait_number(current_bait)
    boat_number = boat_f.get_boat_number(current_boat)
    fMAX = int(((rod_number ** 1.3) + (bait_number * 4) + random.choice([-1, -2, 1, 2, 3, 4, 5, 6, 3, 2, 3]) + (
                boat_number * 40))+1//1.3)

    temp_money = 0
    temp_xp = 0
    fish_list = []

    if current_rod in ['Empty', 'rod1', 'rod2']:
        temp_fishlist = random.choice(T1)
        if isinstance(temp_fishlist, tuple):
            for _ in range(abs(fMAX - 16)):
                temp_fish = random.choice(temp_fishlist)
                parts = temp_fish.split()
                temp_money += int(parts[0])
                temp_xp += int(parts[1])
                fish_list.append(parts[2])
            if bait_number == 2:
                if random.randint(1, 2) == 2:
                    CHparts = ChestT1.split()
                    temp_money += int(CHparts[0])
                    temp_xp += int(CHparts[1])
                    fish_list.append(CHparts[2])
                fish_list = sorted(fish_list)
            if random.randint(1, 2) == 2:
                CHparts = ChestT1.split()
                temp_money += int(CHparts[0])
                temp_xp += int(CHparts[1])
                fish_list.append(CHparts[2])
            fish_list = sorted(fish_list)
        else:
            for _ in range(abs(fMAX - 16)):
                temp_fish = temp_fishlist
                parts = temp_fish.split()
                temp_money += int(parts[0])
                temp_xp += int(parts[1])
                fish_list.append(parts[2])

    elif current_rod in ['rod3']:
        temp_fishlist = random.choice(T2)
        if isinstance(temp_fishlist, tuple):
            for _ in range(abs(fMAX - 5)):
                temp_fish = random.choice(temp_fishlist)
                parts = temp_fish.split()
                temp_money += int(parts[0])
                temp_xp += int(parts[1])
                fish_list.append(parts[2])
            if random.randint(1, 18) <= 3:
                CHparts = ChestT2.split()
                temp_money += int(CHparts[0])
                temp_xp += int(CHparts[1])
                fish_list.append(CHparts[2])
            if bait_number == 2:
                if random.randint(1, 5) == 2:
                    CHparts = ChestT3.split()
                    temp_money += int(CHparts[0])
                    temp_xp += int(CHparts[1])
                    fish_list.append(CHparts[2])
                fish_list = sorted(fish_list)
            elif random.randint(1, 25) == 10:
                CHparts = ChestT3.split()
                temp_money += int(CHparts[0])
                temp_xp += int(CHparts[1])
                fish_list.append(CHparts[2])
            fish_list = sorted(fish_list)
        else:
            for _ in range(abs(fMAX - 10)):
                temp_fish = temp_fishlist
                parts = temp_fish.split()
                temp_money += int(parts[0])
                temp_xp += int(parts[1])
                fish_list.append(parts[2])
            if random.randint(1, 100) <= 15:
                CHparts = ChestT2.split()
                temp_money += int(CHparts[0])
                temp_xp += int(CHparts[1])
                fish_list.append(CHparts[2])

    elif current_rod in ['rod4']:
        temp_fishlist = random.choice(T3)
        if isinstance(temp_fishlist, tuple):
            for _ in range(abs(fMAX - 5)):
                temp_fish = random.choice(temp_fishlist)
                parts = temp_fish.split()
                temp_money += int(parts[0])
                temp_xp += int(parts[1])
                fish_list.append(parts[2])
            if bait_number == 2:
                if random.randint(1, 100) <= 40:
                    CHparts = ChestT3.split()
                    temp_money += int(CHparts[0])
                    temp_xp += int(CHparts[1])
                    fish_list.append(CHparts[2])
            if random.randint(1, 100) <= 10:
                CHparts = ChestT2.split()
                temp_money += int(CHparts[0])
                temp_xp += int(CHparts[1])
                fish_list.append(CHparts[2])
                fish_list = sorted(fish_list)
            if bait_number == 2:
                if random.randint(1, 100) <= 40:
                    CHparts = ChestT3.split()
                    temp_money += int(CHparts[0])
                    temp_xp += int(CHparts[1])
                    fish_list.append(CHparts[2])
                fish_list = sorted(fish_list)
            elif random.randint(1, 65) == 1:
                CHparts = ChestT4.split()
                temp_money += int(CHparts[0])
                temp_xp += int(CHparts[1])
                fish_list.append(CHparts[2])
            fish_list = sorted(fish_list)
        else:
            for _ in range(abs(fMAX - 5)):
                temp_fish = temp_fishlist
                parts = temp_fish.split()
                temp_money += int(parts[0])
                temp_xp += int(parts[1])
                fish_list.append(parts[2])
                fish_list = sorted(fish_list)

    elif current_rod in ['rod5']:
        temp_fishlist = random.choice(T4)
        if isinstance(temp_fishlist, tuple):
            for _ in range(abs(fMAX - 5)):
                temp_fish = random.choice(temp_fishlist)
                parts = temp_fish.split()
                temp_money += int(parts[0])
                temp_xp += int(parts[1])
                fish_list.append(parts[2])
            if random.randint(1, 100) <= 7:
                CHparts = ChestT3.split()
                temp_money += int(CHparts[0])
                temp_xp += int(CHparts[1])
                fish_list.append(CHparts[2])
            if bait_number == 2:
                if random.randint(1, 100) <= 40:
                    CHparts = ChestT4.split()
                    temp_money += int(CHparts[0])
                    temp_xp += int(CHparts[1])
                    fish_list.append(CHparts[2])
            elif random.randint(1, 80) == 1:
                CHparts = ChestT2.split()
                temp_money += int(CHparts[0])
                temp_xp += int(CHparts[1])
                fish_list.append(CHparts[2])
            fish_list = sorted(fish_list)

        else:
            for _ in range(abs(fMAX - 5)):
                if bait_number == 2:
                    if random.randint(1, 120) == 2:
                        CHparts = ChestT3.split()
                        temp_money += int(CHparts[0])
                        temp_xp += int(CHparts[1])
                        fish_list.append(CHparts[2])
                temp_fish = temp_fishlist
                parts = temp_fish.split()
                temp_money += int(parts[0])
                temp_xp += int(parts[1])
                fish_list.append(parts[2])
                fish_list = sorted(fish_list)


    elif current_rod in ['rod6']:
        temp_fishlist = random.choice(LT1)
        if isinstance(temp_fishlist, tuple):
            for _ in range(abs(fMAX - 5)):
                temp_fish = random.choice(temp_fishlist)
                parts = temp_fish.split()
                temp_money += int(parts[0])
                temp_xp += int(parts[1])
                fish_list.append(parts[2])
            if bait_number == 2:
                if random.randint(1, 100) <= 30:
                    CHparts = ChestT4.split()
                    temp_money += int(CHparts[0])
                    temp_xp += int(CHparts[1])
                    fish_list.append(CHparts[2])
                if random.randint(1, 100) <= 20:
                    CHparts = ChestT5.split()
                    temp_money += int(CHparts[0])
                    temp_xp += int(CHparts[1])
                    fish_list.append(CHparts[2])
            if random.randint(1, 120) <= 10:
                CHparts = ChestT4.split()
                temp_money += int(CHparts[0])
                temp_xp += int(CHparts[1])
                fish_list.append(CHparts[2])
            if bait_number == 2:
                if random.randint(1, 100) <= 20:
                    CHparts = ChestT4.split()
                    temp_money += int(CHparts[0])
                    temp_xp += int(CHparts[1])
                    fish_list.append(CHparts[2])
                fish_list = sorted(fish_list)
            elif random.randint(1, 100) == 1:
                CHparts = ChestT5.split()
                temp_money += int(CHparts[0])
                temp_xp += int(CHparts[1])
                fish_list.append(CHparts[2])
            fish_list = sorted(fish_list)
            fish_list = sorted(fish_list)
        else:
            for _ in range(abs(fMAX - 5)):
                temp_fish = temp_fishlist
                parts = temp_fish.split()
                temp_money += int(parts[0])
                temp_xp += int(parts[1])
                fish_list.append(parts[2])
            if random.randint(1, 100) <= 10:
                CHparts = ChestT3.split()
                temp_money += int(CHparts[0])
                temp_xp += int(CHparts[1])
                fish_list.append(CHparts[2])
            fish_list = sorted(fish_list)


    elif current_rod in ['rod7']:
        temp_fishlist = random.choice(LT1)
        if isinstance(temp_fishlist, tuple):
            for _ in range(abs(fMAX + 5)):
                temp_fish = random.choice(temp_fishlist)
                parts = temp_fish.split()
                temp_money += int(parts[0])
                temp_xp += int(parts[1])
                fish_list.append(parts[2])
            if bait_number == 2:
                if random.randint(1, 100) <= 40:
                    CHparts = ChestT4.split()
                    temp_money += int(CHparts[0])
                    temp_xp += int(CHparts[1])
                    fish_list.append(CHparts[2])
                if random.randint(1, 100) <= 20:
                    CHparts = ChestT5.split()
                    temp_money += int(CHparts[0])
                    temp_xp += int(CHparts[1])
                    fish_list.append(CHparts[2])
            if random.randint(1, 120) <= 10:
                CHparts = ChestT5.split()
                temp_money += int(CHparts[0])
                temp_xp += int(CHparts[1])
                fish_list.append(CHparts[2])
            if bait_number == 2:
                if random.randint(1, 100) <= 50:
                    CHparts = ChestT5.split()
                    temp_money += int(CHparts[0])
                    temp_xp += int(CHparts[1])
                    fish_list.append(CHparts[2])
                fish_list = sorted(fish_list)
            elif random.randint(1, 100) == 1:
                CHparts = ChestT4.split()
                temp_money += int(CHparts[0])
                temp_xp += int(CHparts[1])
                fish_list.append(CHparts[2])
            fish_list = sorted(fish_list)
            fish_list = sorted(fish_list)
        else:
            for _ in range(abs(fMAX - 5)):
                temp_fish = temp_fishlist
                parts = temp_fish.split()
                temp_money += int(parts[0])
                temp_xp += int(parts[1])
                fish_list.append(parts[2])
            if random.randint(1, 100) <= 10:
                CHparts = ChestT3.split()
                temp_money += int(CHparts[0])
                temp_xp += int(CHparts[1])
                fish_list.append(CHparts[2])
            fish_list = sorted(fish_list)

    elif current_rod in ['rod8']:
        temp_fishlist = random.choice(LT1)
        if isinstance(temp_fishlist, tuple):
            for _ in range(abs(fMAX + 20)):
                temp_fish = random.choice(temp_fishlist)
                parts = temp_fish.split()
                temp_money += int(parts[0])
                temp_xp += int(parts[1])
                fish_list.append(parts[2])
            if bait_number == 2:
                if random.randint(1, 100) <= 30:
                    CHparts = ChestT4.split()
                    temp_money += int(CHparts[0])
                    temp_xp += int(CHparts[1])
                    fish_list.append(CHparts[2])
                if random.randint(1, 100) <= 20:
                    CHparts = ChestT5.split()
                    temp_money += int(CHparts[0])
                    temp_xp += int(CHparts[1])
                    fish_list.append(CHparts[2])
            if random.randint(1, 120) <= 10:
                CHparts = ChestT4.split()
                temp_money += int(CHparts[0])
                temp_xp += int(CHparts[1])
                fish_list.append(CHparts[2])
            if bait_number == 2:
                if random.randint(1, 100) <= 20:
                    CHparts = ChestT5.split()
                    temp_money += int(CHparts[0])
                    temp_xp += int(CHparts[1])
                    fish_list.append(CHparts[2])
                fish_list = sorted(fish_list)
            elif random.randint(1, 100) == 1:
                CHparts = ChestT5.split()
                temp_money += int(CHparts[0])
                temp_xp += int(CHparts[1])
                fish_list.append(CHparts[2])
            fish_list = sorted(fish_list)
            fish_list = sorted(fish_list)
        else:
            for _ in range(abs(fMAX - 5)):
                temp_fish = temp_fishlist
                parts = temp_fish.split()
                temp_money += int(parts[0])
                temp_xp += int(parts[1])
                fish_list.append(parts[2])
            if random.randint(1, 100) <= 10:
                CHparts = ChestT3.split()
                temp_money += int(CHparts[0])
                temp_xp += int(CHparts[1])
                fish_list.append(CHparts[2])
            fish_list = sorted(fish_list)


    user_money = load_money_data()
    user_xp = load_xp_data()
    user_money[user_id] += temp_money
    save_money_data(user_money)

    user_xp[user_id] += temp_xp
    save_xp_data(user_xp)

    # Добавляем расчет уровня и цвета
    current_xp = user_xp[user_id]
    level = calculate_level(current_xp)
    color = get_level_color(level)

    fish_counts = {fish: fish_list.count(fish) for fish in set(fish_list)}
    message_text = f"{call.from_user.first_name} {color}\nLevel: {level}\n\nYou caught:\n"
    for fish, count in fish_counts.items():
        message_text += f"x{count} {fish}\n"
    message_text += f"\n +{temp_money}$\n +{temp_xp} XP"

    user_bait_data = load_bait_data()
    if user_bait_data[user_id].get(current_bait, 0) > 0:
        user_bait_data[user_id][current_bait] -= 1
        save_bait_data(user_bait_data)
    else:
        bot.answer_callback_query(call.id, "You're out of baits!", show_alert=False)
        selected_bait[user_id] = "Empty"
        bait_f.save_state_bait(selected_bait)

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("fish again 🎣", callback_data='sub_btn_fish'),
        types.InlineKeyboardButton("menu", callback_data='button_menu')
    )


    if hasattr(call, 'inline_message_id'):
        bot.edit_message_text(
            inline_message_id=call.inline_message_id,
            text=message_text,
            reply_markup=markup
        )
    else:
        msg = bot.send_message(call.message.chat.id, message_text, reply_markup=markup)
        last_message_id = msg.message_id



def shop_button(chat_id, inline_message_id=None):
    global last_message_id

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("fishing rod", callback_data='rod')
    btn4 = types.InlineKeyboardButton("boats", callback_data='boat')
    btn2 = types.InlineKeyboardButton("baits", callback_data='bait')
    btn3 = types.InlineKeyboardButton("back", callback_data='button_back')
    markup.add(btn1, btn4, btn2, btn3)

    user_id = str(chat_id)
    user_money = load_money_data()
    user_xp = load_xp_data()

    text = f"Shop: \n  Balance: {user_money[user_id]}"

    if inline_message_id:
        bot.edit_message_text(
            inline_message_id=inline_message_id,
            text=text,
            reply_markup=markup
        )
    elif last_message_id:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=last_message_id,
            text=text,
            reply_markup=markup
        )
    else:
        msg = bot.send_message(chat_id, text, reply_markup=markup)
        last_message_id = msg.message_id

    save_money_data(user_money)



@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "Bot running🎣💕\nMention @VirtualFisherBot in any chat to start fishing, enjoy")



def check_input():
    while True:
        try:
            cmd = input().strip()
            if cmd == "fish_stop":
                print("Остановка по коду 1488")
                os._exit(0)  # Мгновенный выход

                # ========== ОБЩИЕ КОМАНДЫ ==========
            elif cmd == "fish_list":
                user_money = load_money_data()
                user_xp = load_xp_data()

                all_users = set(user_money.keys()) | set(user_xp.keys())

                if not all_users:
                    print("📝 Пользователей не найдено")
                else:
                    print("📝 Список всех пользователей:")
                    for user_id in sorted(all_users):
                        money = user_money.get(user_id, 0)
                        xp = user_xp.get(user_id, 0)

                        try:
                            # Пытаемся получить имя пользователя по ID
                            user_info = bot.get_chat(user_id)
                            name = user_info.first_name
                        except:
                            name = f"User {user_id}"

                        print(f"   👤 {user_id} {name}: {money}$ | {xp} XP")




            elif cmd == "fish_reset_user":
                print("Введите ID пользователя для сброса данных:")
                user_id = input().strip()

                if not user_id:
                    print("❌ Ошибка: ID пользователя не может быть пустым")
                    continue

                print("⚠️  ВНИМАНИЕ! Это действие удалит ВСЕ данные пользователя:")
                print(f"   -прогресс")
                print("ГОООЛ? (да/нет):")

                confirm = input().strip().lower()
                if confirm in ['да', 'yes', 'y']:
                    # Сброс денег
                    user_money = load_money_data()
                    if user_id in user_money:
                        del user_money[user_id]
                        save_money_data(user_money)

                    # Сброс XP
                    user_xp = load_xp_data()
                    if user_id in user_xp:
                        user_xp[user_id] = 0
                        del user_xp[user_id]
                        save_xp_data(user_xp)

                    # Сброс наживки
                    user_bait_data = load_bait_data()
                    if user_id in user_bait_data:
                        del user_bait_data[user_id]
                        save_bait_data(user_bait_data)

                    # Сброс выбранной наживки
                    selected_bait = bait_f.load_bait_select()
                    if user_id in selected_bait:
                        del selected_bait[user_id]
                        bait_f.save_state_bait(selected_bait)

                    # Сброс удочки
                    user_rods_data = load_rods_select()
                    if user_id in user_rods_data:
                        del user_rods_data[user_id]
                        rods_f.save_state_rods(user_rods_data)

                    # Сброс выбранной удочки
                    selected_rods = rods_f.load_rods_select()
                    if user_id in selected_rods:
                        del selected_rods[user_id]
                        rods_f.save_state_rods(selected_rods)

                    # Сброс лодки
                    user_boat_data = boat_f.load_boat_select()
                    if user_id in user_boat_data:
                        del user_boat_data[user_id]
                        boat_f.save_state_boat(user_boat_data)


                    print(f"✅ Все данные пользователя {user_id} успешно сброшены")
                else:
                    print("❌ Операция отменена")

            elif cmd == "fish_user":
                print("Введите ID пользователя для просмотра:")
                user_id = input().strip()
                user_money = load_money_data()
                user_xp = load_xp_data()
                user_bait_data = load_bait_data()
                selected_bait = bait_f.load_bait_select()
                user_rods_data = load_rods_select()
                selected_rods = rods_f.load_rods_select()
                user_boat_data = boat_f.load_boat_select()
                try:
                    # Пытаемся получить имя пользователя по ID
                    user_info = bot.get_chat(user_id)
                    name = user_info.first_name
                except:
                    name = f"User {user_id}"

                print(f"👤 {user_id} {name}:"
                      f"\n{user_money[user_id]}$ "
                      f"\n{user_xp[user_id]}XP "
                      f"\n{calculate_level(user_xp[user_id])}lvl "
                      f"\nBAITS| {user_bait_data[user_id]}"
                      f"\nCURRENT_BAIT| {selected_bait[user_id]}"
                      f"\nRODS| {user_rods_data[user_id]}"
                      f"\nCURRENT_ROD| {selected_rods[user_id]}"
                      f"\nBOAT| {user_boat_data[user_id]}"
                      )



            elif cmd == "fish_help":
                print("📋 Доступные команды:")
                print("\n💰 ДЕНЬГИ:")
                print("  fish_add_money - добавить деньги пользователю")
                print("  fish_check_money - проверить баланс пользователя")
                print("\n⭐ ОПЫТ (XP):")
                print("  fish_add_xp - добавить XP пользователю")
                print("  fish_check_xp - проверить XP пользователя")
                print("\n🔧 УПРАВЛЕНИЕ:")
                print("  fish_list - показать всех пользователей")
                print("  fish_reset_user - сбросить все данные пользователя")
                print("  fish_stop - остановка бота")
                print("  fish_help - показать эту справку")

# ========== КОМАНДЫ ДЛЯ BABLO =======================================================================================
            elif cmd == "fish_add_money":
                print("Введите ID пользователя:")
                user_id = input().strip()

                if not user_id:
                    print("❌ Ошибка: ID пользователя не может быть пустым")
                    continue

                print("Введите сумму для добавления:")
                amount = int(input().strip())
                # Загружаем данные о деньгах
                user_money = load_money_data()
                # Добавляем деньги пользователю
                if user_id not in user_money:
                    user_money[user_id] = 0

                old_amount = user_money[user_id]
                user_money[user_id] += amount
                # Сохраняем данные
                save_money_data(user_money)

                print(f"✅ Добавлено {amount}$ пользователю {user_id}")
                print(f"   Было: {old_amount}$ → Стало: {user_money[user_id]}$")

            elif cmd == "fish_check_money":
                print("Введите ID пользователя для проверки баланса:")
                user_id = input().strip()

                if not user_id:
                    print("❌ Ошибка: ID пользователя не может быть пустым")
                    continue

                user_money = load_money_data()
                balance = user_money.get(user_id, 0)
                print(f"💰 Баланс пользователя {user_id}: {balance}$")

# ========== КОМАНДЫ ДЛЯ XP =======================================================================================
            elif cmd == "fish_add_xp":
                print("Введите ID пользователя:")
                user_id = input().strip()

                if not user_id:
                    print("❌ Ошибка: ID пользователя не может быть пустым")
                    continue

                print("Введите количество XP для добавления:")

                amount = int(input().strip())
                user_xp = load_xp_data()
                if user_id not in user_xp:
                    user_xp[user_id] = 0
                    save_xp_data(user_xp)

                old_amount = user_xp[user_id]
                user_xp[user_id] += amount
                save_xp_data(user_xp)
                # level = calculate_level(current_xp)
                print(f"✅ Добавлено {amount} XP пользователю {user_id}")
                print(f"   Было: {old_amount} XP → Стало: {user_xp[user_id]} XP")
                print(f"   Было: {calculate_level(old_amount)}lvl → Стало: {calculate_level(user_xp[user_id])} lvl")

            elif cmd == "fish_check_xp":
                print("Введите ID пользователя для проверки XP:")
                user_id = input().strip()

                if not user_id:
                    print("❌ Ошибка: ID пользователя не может быть пустым")
                    continue

                user_xp = load_xp_data()
                xp = user_xp.get(user_id, 0)
                print(f"⭐ XP пользователя {user_id}: {xp}XP {calculate_level(user_xp[user_id])}lvl")



            elif cmd.strip() == "":
                continue  # Игнорируем пустые строки
            else:
                print(f"❓ Неизвестная команда: {cmd}")
                print("Введите 'fish_help' для списка команд")

        except EOFError:
            # Обработка Ctrl+C или закрытия терминала
            break
        except Exception as e:
            print(f"❌ Ошибка при выполнении команды: {e}")


# Запускаем проверку ввода в отдельном потоке
input_thread = threading.Thread(target=check_input, daemon=True)
input_thread.start()

print("Бот запущен. Введите 'fish_stop' в терминале для остановки")

try:
    while True:
        try:
            bot.polling(none_stop=True, timeout=5)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(15)

except KeyboardInterrupt:
    print("Остановка по Ctrl+C")
