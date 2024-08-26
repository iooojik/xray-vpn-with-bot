import qrcode
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from src.config import load_config
from translations import translate
from db import init_db, save_vpn_config, get_vpn_configs


# Handle /start command
async def start(update: Update, context) -> None:
    user = update.message.from_user
    welcome_message = translate('welcome', 'en', name=user.first_name)
    keyboard = [
        [InlineKeyboardButton("Русский", callback_data='lang_ru')],
        [InlineKeyboardButton("English", callback_data='lang_en')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)


# Handle language choice
async def language_choice(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'lang_ru':
        context.user_data['language'] = 'ru'
    elif query.data == 'lang_en':
        context.user_data['language'] = 'en'

    await main_menu(update, context)


# Main menu
async def main_menu(update: Update, context) -> None:
    query = update.callback_query
    lang = context.user_data.get('language', 'en')
    menu_message = translate('menu_message', lang)
    buttons = [
        [InlineKeyboardButton(translate('generate_vpn', lang), callback_data='generate_vpn')],
        [InlineKeyboardButton(translate('view_vpn', lang), callback_data='view_vpn')],
        [InlineKeyboardButton(translate('manuals', lang), callback_data='manuals')]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(text=menu_message, reply_markup=reply_markup)


# Generate VPN configuration and save to database
async def generate_vpn(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()

    vpn_config = "your-vpn-configuration-string"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(vpn_config)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    bio = BytesIO()
    bio.name = 'vpn_qr.png'
    img.save(bio, 'PNG')
    bio.seek(0)

    user_id = query.from_user.id
    save_vpn_config(user_id, vpn_config)

    lang = context.user_data.get('language', 'en')
    await query.message.reply_photo(photo=InputFile(bio), caption=translate('vpn_generated', lang))


# View existing VPN configurations
async def view_vpn(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    configs = get_vpn_configs(user_id)

    lang = context.user_data.get('language', 'en')
    if not configs:
        await query.edit_message_text(text=translate('no_vpn_configs', lang), reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(translate('back', lang), callback_data='back_to_menu')]]))
    else:
        messages = []
        for config, created_at in configs:
            messages.append(f"Configuration: {config}\nCreated at: {created_at}\n\n")

        await query.edit_message_text(text=''.join(messages), reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(translate('back', lang), callback_data='back_to_menu')]]))


# Show manuals
async def manuals(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('language', 'en')
    menu_message = translate('select_os', lang)
    buttons = [
        [InlineKeyboardButton("Windows", url="https://example.com/windows_manual")],
        [InlineKeyboardButton("Linux", url="https://example.com/linux_manual")],
        [InlineKeyboardButton("MacOS", url="https://example.com/macos_manual")],
        [InlineKeyboardButton(translate('back', lang), callback_data='back_to_menu')]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(text=menu_message, reply_markup=reply_markup)


# Handle "Back" button in the main menu
async def back_to_menu(update: Update, context) -> None:
    await main_menu(update, context)


# Handle "Back" button to return to start
async def back_to_start(update: Update, context) -> None:
    await start(update, context)


def main():
    config = load_config()
    init_db()  # Initialize the database
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
