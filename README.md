# kispython_point

Функциональные требования к приложению:

- Мне как студенту, изучающему курс Python нужно сдать домашние работы.

- Как пользователю telegram-а мне удобно отправлять решение в telegram.

- Как человеку занятому, мне не хочется заботиться о PEP8.

## Зависимости

### Бот

Зависимости в файле requirements.txt

### Документация

Зависимости в файле docs/requirements.txt

## Запуск

### Запуск бота

1. Установка переменной окружения `BOT_TOKEN` в docker-compose.yml

2. `docker compose up`

### Построение документации

1. `python -m venv venv && source ./venv/bin/activate`

2. `python -m pip install -r requirements.txt`

3. `python setup.py build_sphinx -s ./docs/source/ --build-dir ./docs/build -b html`
