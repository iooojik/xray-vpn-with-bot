import yaml
import qrcode
import sqlite3
from io import BytesIO
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler


# Чтение конфигурации из YAML файла
def load_config():
    with open("../config.yaml", "r") as file:
        return yaml.safe_load(file)


# Подключение к базе данных и создание таблицы, если она не существует
def init_db():
    conn = sqlite3.connect('../vpn_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vpn_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            config TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


# Сохранение VPN конфигурации в базу данных
def save_vpn_config(user_id, config):
    conn = sqlite3.connect('../vpn_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO vpn_configs (user_id, config, created_at) 
        VALUES (?, ?, ?)
    ''', (user_id, config, datetime.now().isoformat()))
    conn.commit()
    conn.close()


# Получение VPN конфигураций пользователя из базы данных
def get_vpn_configs(user_id):
    conn = sqlite3.connect('../vpn_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT config, created_at FROM vpn_configs WHERE user_id = ?
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


# Обработка команды /start
async def start(update: Update, context) -> None:
    user = update.message.from_user
    welcome_message = f"Привет, {user.first_name}! Выберите язык / Hello, {user.first_name}! Please choose a language."
    keyboard = [
        [InlineKeyboardButton("Русский", callback_data='lang_ru')],
        [InlineKeyboardButton("English", callback_data='lang_en')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)


# Обработка выбора языка
async def language_choice(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'lang_ru':
        context.user_data['language'] = 'ru'
        await main_menu(update, context)
    elif query.data == 'lang_en':
        context.user_data['language'] = 'en'
        await main_menu(update, context)


# Главное меню
async def main_menu(update: Update, context) -> None:
    query = update.callback_query
    lang = context.user_data.get('language', 'en')
    if lang == 'ru':
        menu_message = "Выберите действие:"
        buttons = [
            [InlineKeyboardButton("Сгенерировать VPN конфигурацию", callback_data='generate_vpn')],
            [InlineKeyboardButton("Посмотреть существующие", callback_data='view_vpn')],
            [InlineKeyboardButton("Мануалы", callback_data='manuals')],
            [InlineKeyboardButton("Назад", callback_data='back_to_start')]
        ]
    else:
        menu_message = "Choose an action:"
        buttons = [
            [InlineKeyboardButton("Generate VPN configuration", callback_data='generate_vpn')],
            [InlineKeyboardButton("View existing", callback_data='view_vpn')],
            [InlineKeyboardButton("Manuals", callback_data='manuals')],
            [InlineKeyboardButton("Back", callback_data='back_to_start')]
        ]

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(text=menu_message, reply_markup=reply_markup)


# Генерация QR-кода с VPN конфигурацией и сохранение в базу данных
async def generate_vpn(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()

    # Пример строки конфигурации VPN
    vpn_config = "your-vpn-configuration-string"

    # Генерация QR-кода
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(vpn_config)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    # Сохранение изображения в байтовый поток
    bio = BytesIO()
    bio.name = 'vpn_qr.png'
    img.save(bio, 'PNG')
    bio.seek(0)

    # Сохранение конфигурации в базу данных
    user_id = query.from_user.id
    save_vpn_config(user_id, vpn_config)

    # Отправка изображения пользователю
    lang = context.user_data.get('language', 'en')
    if lang == 'ru':
        await query.message.reply_photo(photo=InputFile(bio), caption="Ваша VPN конфигурация:")
    else:
        await query.message.reply_photo(photo=InputFile(bio), caption="Your VPN configuration:")


# Обработка просмотра существующих VPN конфигураций
async def view_vpn(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    configs = get_vpn_configs(user_id)

    if not configs:
        lang = context.user_data.get('language', 'en')
        if lang == 'ru':
            await query.edit_message_text(text="У вас нет сохраненных VPN конфигураций.",
                                          reply_markup=InlineKeyboardMarkup(
                                              [[InlineKeyboardButton("Назад", callback_data='back_to_menu')]]))
        else:
            await query.edit_message_text(text="You have no saved VPN configurations.",
                                          reply_markup=InlineKeyboardMarkup(
                                              [[InlineKeyboardButton("Back", callback_data='back_to_menu')]]))
    else:
        messages = []
        for config, created_at in configs:
            messages.append(
                f"Конфигурация: {config}\nДата создания: {created_at}\n\n" if context.user_data.get('language',
                                                                                                    'en') == 'ru' else f"Configuration: {config}\nCreated at: {created_at}\n\n")

        await query.edit_message_text(text=''.join(messages), reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Назад", callback_data='back_to_menu')]] if context.user_data.get('language',
                                                                                                     'en') == 'ru' else [
                [InlineKeyboardButton("Back", callback_data='back_to_menu')]]))


# Обработка выбора мануалов
async def manuals(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('language', 'en')
    if lang == 'ru':
        menu_message = "Выберите операционную систему:"
        buttons = [
            [InlineKeyboardButton("Windows", url="https://example.com/windows_manual")],
            [InlineKeyboardButton("Linux", url="https://example.com/linux_manual")],
            [InlineKeyboardButton("MacOS", url="https://example.com/macos_manual")],
            [InlineKeyboardButton("Назад", callback_data='back_to_menu')]
        ]
    else:
        menu_message = "Select an operating system:"
        buttons = [
            [InlineKeyboardButton("Windows", url="https://example.com/windows_manual")],
            [InlineKeyboardButton("Linux", url="https://example.com/linux_manual")],
            [InlineKeyboardButton("MacOS", url="https://example.com/macos_manual")],
            [InlineKeyboardButton("Back", callback_data='back_to_menu')]
        ]

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(text=menu_message, reply_markup=reply_markup)


# Обработка кнопки "Назад" для возврата в главное меню
async def back_to_menu(update: Update, context) -> None:
    await main_menu(update, context)


# Обработка кнопки "Назад" для возврата на стартовый экран
async def back_to_start(update: Update, context) -> None:
    await start(update, context)


def main():
    config = load_config()
    init_db()  # Инициализация базы данных
    application = Application.builder().token(config['bot_token']).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(language_choice, pattern='^lang_'))
    application.add_handler(CallbackQueryHandler(main_menu, pattern='^menu_'))
    application.add_handler(CallbackQueryHandler(generate_vpn, pattern='^generate_vpn$'))
    application.add_handler(CallbackQueryHandler(view_vpn, pattern='^view_vpn$'))
    application.add_handler(CallbackQueryHandler(manuals, pattern='^manuals$'))
    application.add_handler(CallbackQueryHandler(back_to_menu, pattern='^back_to_menu$'))
    application.add_handler(CallbackQueryHandler(back_to_start, pattern='^back_to_start$'))

    application.run_polling()


if __name__ == '__main__':
    main()
