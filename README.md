# 🤖 MaxPost

[![Python](https://img.shields.io/badge/Python-3.14-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## ✨ Возможности

- Получение сообщений, медиафайлов и файлов из мессенджера MAX
- Отправка полученных из MAX сообщений в выбранный чат в Telegram

## 📦 Требования

```
- Python 3.14
- uv — менеджер пакетов
```

## 🚀 Установка

**1. Клонируй репозиторий:**
```bash
git clone https://github.com/Arkline-1/MaxPost.git
cd MaxPost
```

**2. Установи зависимости**
```bash
uv sync
```

**3. Создайте Telegram бота <br>**
Создайте Telegram бота в @BotFather в Telegram

**4. Создайте файл .env**
```env
MAX_TOKEN=токен_твоего_аккаунта_в_max
MAX_CHAT_ID=id_твоего_чата_в_max

TG_TOKEN=токен_твоего_telegram_бота
TG_CHAT_ID=id_твоего_чата_в_telegram
```

**5. Запусти программу:**
```bash
uv run main.py
```

## ⚙️ Конфигурация
| Переменная | Описание |
|-----------|----------|
| MAX_TOKEN | Токен твоего аккаунта в MAX |
| MAX_CHAT_ID | ID чата в MAX |
| TG_TOKEN | Токен Telegram бота |
| TG_CHAT_ID | ID чата в Telegram |

## 🛠 Технологии

- [aiogram](https://docs.aiogram.dev/en/v3.26.0/) — библиотека для Telegram ботов
- [aiohttp](https://docs.aiohttp.org/) — библиотека для HTTP запросов
- [python-dotenv](https://pypi.org/project/python-dotenv/) — управление переменными окружения

## 🗂️ Файловая структура

📁 MaxPost/ <br>
├── 📄 .env             — Переменные окружения (нужно создать, подробнее в "🚀 Установка") <br>
├── 📄 .gitignore       — Игнорирумые файлы <br>
├── 📄 LICENSE          — Лицензия <br>
├── 📄 main.py          — Запуск программы <br>
├── 📄 pyproject.toml   — Настройки uv (зависимости проекта и тд) <br>
├── 📄 README.md        — Документация к проекту <br>
├── 📄 ruff.toml        — Форматирование проекта <br>
├── 📄 setup.py         — Получения перееменных окружения <br>
├── 📄 tg_bot.py        — Функции тг-бота <br>
├── 📄 uv.lock          — Информация о скачанных пакетах и их зависимостях <br>
└── 📄 websocket.py     — Получение данных из MAX <br>

## 📄 Лицензия

MIT License — подробнее в [LICENSE](LICENSE)