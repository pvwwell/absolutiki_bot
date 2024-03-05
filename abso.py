import telebot
import sqlite3
import threading

bot = telebot.TeleBot("7132312541:AAEz2xkq72KisXqsvwG9G5l5X1mlY_DzLAE")

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Привет! Давай начнем сбор данных. Отправь мне свой никнейм Главное помни, что при дальнейших авторизациях он не должен меняться, иначе я не смогу обновлять твою информацию!😊 ')

# Обработчик текстовых сообщений для никнейма
@bot.message_handler(func=lambda message: True)
def collect_name(message):
    if message.text.strip():
        bot.send_message(message.chat.id, 'Отлично! Теперь отправь мне количество очков.😁 ')
        bot.register_next_step_handler(message, collect_data, {'name': message.text.strip()})  # Регистрируем обработчик для ввода количества очков и передаем никнейм
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, отправьте непустой никнейм.')

# Обработчик текстовых сообщений для количества очков
def collect_data(message, user_info):
    points = message.text.strip()
    if points.isdigit() and int(points) >= 0:
        user_info['points'] = points
        bot.send_message(message.chat.id, 'Так много! Теперь отправь мне количество побед на арене.😎')
        bot.register_next_step_handler(message, collect_wins, user_info)  # Регистрируем обработчик для ввода количества побед на арене и передаем информацию о пользователе
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, введите корректное количество очков (целое неотрицательное число).')

# Обработчик текстовых сообщений для количества побед на арене
def collect_wins(message, user_info):
    wins = message.text.strip()
    if wins.isdigit() and int(wins) >= 0:
        user_info['wins'] = wins
        bot.send_message(message.chat.id, 'Да ты гладиатор! Напоследок отправь мне мощь своей команды.🥰')
        bot.register_next_step_handler(message, collect_power, user_info)  # Регистрируем обработчик для ввода мощи команды и передаем информацию о пользователе
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, введите корректное количество побед на арене (целое неотрицательное число).')

# Обработчик текстовых сообщений для мощи команды
def collect_power(message, user_info):
    power = message.text.strip()
    if power.isdigit():
        user_info['power'] = power
        # Сохраняем информацию о пользователе в базе данных в отдельном потоке
        threading.Thread(target=save_to_db, args=(message, user_info)).start()
        bot.send_message(message.chat.id, 'Спасибо! Информация успешно сохранена.😋')
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, введите мощь команды только цифрами.')

# Функция для сохранения или обновления информации о пользователе в базе данных
def save_to_db(message, user_info):
    # Подключаемся к базе данных
    conn = sqlite3.connect('Absolutiks.db')
    cursor = conn.cursor()
    # Проверяем, существует ли пользователь с таким именем
    cursor.execute("SELECT * FROM users WHERE name=?", (user_info['name'],))
    existing_user = cursor.fetchone()
    if existing_user:
        # Если пользователь существует, обновляем его запись
        cursor.execute("UPDATE users SET points=?, wins=?, power=? WHERE name=?",
                       (user_info['points'], user_info['wins'], user_info['power'], user_info['name']))
    else:
        # Если пользователь не существует, создаем новую запись
        cursor.execute("INSERT INTO users (name, points, wins, power) VALUES (?, ?, ?, ?)",
                       (user_info['name'], user_info['points'], user_info['wins'], user_info['power']))
    conn.commit()
    # Закрываем соединение с базой данных
    conn.close()

bot.infinity_polling()




