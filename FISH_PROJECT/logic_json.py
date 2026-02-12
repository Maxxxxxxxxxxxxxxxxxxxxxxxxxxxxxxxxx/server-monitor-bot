import os
import json
MONEY_FILE = os.path.join(os.path.dirname(__file__), 'json', 'user_money.json')
XP_FILE = os.path.join(os.path.dirname(__file__), 'json','user_xp.json')
BAIT_FILE = os.path.join(os.path.dirname(__file__), 'json','user_bait.json')
BIOME_FILE = os.path.join(os.path.dirname(__file__), 'json','user_biome.json')



# ============================MONEY======================================================================
# Загружаем данные из JSON-файла деньги
def load_money_data():
    if os.path.exists(MONEY_FILE):
        with open(MONEY_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

# Сохраняем данные в JSON-файл деньги
def save_money_data(user_money):
    with open(MONEY_FILE, 'w', encoding='utf-8') as file:
        json.dump(user_money, file, ensure_ascii=False, indent=4)
        # print("BABLO IN SAFE")


# ============================XP======================================================================
# Загружаем данные из JSON-файла xp
def load_xp_data():
    if os.path.exists(XP_FILE):
        with open(XP_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

# Сохраняем данные в JSON-файл xp
def save_xp_data(user_xp):
    with open(XP_FILE, 'w', encoding='utf-8') as file:
        json.dump(user_xp, file, ensure_ascii=False, indent=4)

# =============================================================================================================

# ============================BAITCOUNT==========================================================================================
# Загружаем данные из JSON-файла наживка
def load_bait_data():
    if os.path.exists(BAIT_FILE):
        with open(BAIT_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}


# Сохраняем данные в JSON-файл количество наживки
def save_bait_data(user_bait):
    with open(BAIT_FILE, 'w', encoding='utf-8') as file:
        json.dump(user_bait, file, ensure_ascii=False, indent=4)

# =============================================================================================================
# ============================BIOME=-=-=-=-=-=-=--=-=======================================================================
# Загружаем данные из JSON-файла xp
def load_biome_data():
    if os.path.exists(BIOME_FILE):
        with open(BIOME_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

# Сохраняем данные в JSON-файл xp
def save_biome_data(user_biome):
    with open(BIOME_FILE, 'w', encoding='utf-8') as file:
        json.dump(user_biome, file, ensure_ascii=False, indent=4)

# =============================================================================================================


# River -  fish 1$/1xp  salmon 3$/2xp  cod 10$/5xp  tropical_fish 50$/10xp  pufferfish 150$/25xp
# Lava  - fiery_puffer 250$/50xp  hot_cod 500$/100xp
def fish_price1():
    fish_price1 = 0
    return(fish_price1)


def xp_price1():
    xp_price1 = 0
    return(xp_price1)

