#!/bin/bash
echo "🔄 Updating Fish Bot from GitHub..."

# Останавливаем сервис
echo "⏹️  Stopping bot service..."
sudo systemctl stop fishbot.service

# Сохраняем изменения на сервере (если есть)
echo "💾 Saving local changes..."
git add .
git stash

# Получаем обновления с GitHub
echo "⬇️  Pulling updates from GitHub..."
git pull origin main

# Активируем виртуальное окружение и обновляем зависимости
echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Запускаем сервис
echo "▶️  Starting bot service..."
sudo systemctl start fishbot.service

# Проверяем статус
echo "✅ Checking bot status..."
sudo systemctl status fishbot.service --no-pager -l

echo "🎉 Bot update completed!"
