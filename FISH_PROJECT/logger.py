import random

# Список рыб и их базовые веса
fish_data = [
    {"name": "Fish_🐟", "weight": 50},
    {"name": "Salmon_🐟", "weight": 30},
    {"name": "Cod_🦈", "weight": 15},
    {"name": "Tropical_Fish_🐠", "weight": 4},
    {"name": "Pufferfish_🐡", "weight": 1},
]

# Функция для выбора рыбы с учетом удачи
def catch_fish(luck):
    # Увеличиваем вес редких рыб в зависимости от удачи
    weighted_fish = [
        {"name": fish["name"], "weight": fish["weight"] * (1 + luck * (i / len(fish_data)))}
        for i, fish in enumerate(fish_data)
    ]

    # Выбираем рыбу с учетом весов
    chosen_fish = random.choices(
        [fish["name"] for fish in weighted_fish],
        weights=[fish["weight"] for fish in weighted_fish],
        k=10  # Количество рыб для выбора
    )[0]

    return chosen_fish

# Пример использования
user_luck = 100  # Удача пользователя (от 0 до 10)
caught_fish = catch_fish(user_luck)
print(f"You caught: {caught_fish}")