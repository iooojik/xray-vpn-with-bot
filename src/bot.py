from io import BytesIO

from qrcode.constants import ERROR_CORRECT_L
from qrcode.main import QRCode
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from src.config import load_config
from src.db import init_db, save_vpn_config, get_vpn_configs
from src.translations import translate
from src.xray import cfg_dsn, add_xray_user


class TelegramBot:

    def __init__(self, cfg_path: str):
        config = load_config(cfg_path)
        self._server_ip = config.get("server").get("ip")
        self._server_port = config.get("server").get("port")
        self._public_key = config.get("server").get("public_key")
        self._short_id = config.get("server").get("short_id")
        self._xray_cfg_path = config.get("server").get("xray_cfg_path")
        self._xray_container = config.get("xray_container")

        self._application = Application.builder().token(config['bot_token']).build()

        self._bind_handlers()

    # Main menu
    async def _main_menu(self, update: Update, _) -> None:
        msg = update.message if update.message else update.effective_message
        lang = msg.from_user.language_code

        menu_message = translate('menu_message', lang)

        user_config = self.vpn_config(msg.from_user.id)

        keyboard = []

        if not user_config:
            keyboard.append(
                [InlineKeyboardButton(translate('generate_vpn', lang), callback_data='generate_vpn')]
            )

        keyboard.extend(
            [
                [InlineKeyboardButton(translate('view_vpn', lang), callback_data='view_vpn')],
                [InlineKeyboardButton(translate('manuals', lang), callback_data='manuals')]
            ]
        )

        reply_markup = InlineKeyboardMarkup(keyboard)

        await msg.reply_text(menu_message, reply_markup=reply_markup)

    def vpn_config(self, user_id: int) -> str:
        configs = get_vpn_configs(user_id)

        if configs:
            return configs[0][0]

        vpn_dsn, user_uuid = cfg_dsn(
            self._server_ip,
            self._server_port,
            self._public_key,
            self._short_id,
        )

        add_xray_user(
            self._xray_cfg_path,
            str(user_id),
            str(user_uuid),
            self._xray_container,
        )

        save_vpn_config(user_id, vpn_dsn)
        return vpn_dsn

    # Generate VPN configuration and save to database
    async def _generate_vpn(self, update: Update, _) -> None:
        query = update.callback_query
        await query.answer()

        user_config = self.vpn_config(query.from_user.id)

        qr = QRCode(
            version=1,
            error_correction=ERROR_CORRECT_L,
            box_size=5,
            border=1,
        )

        qr.add_data(user_config)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')

        bio = BytesIO()
        bio.name = 'vpn_qr.png'
        img.save(bio, 'PNG')
        bio.seek(0)

        lang = update.effective_sender.language_code

        await query.message.reply_text(translate('vpn_generated', lang))

        await query.message.reply_photo(
            photo=InputFile(bio),
            caption=f"```{user_config}```",
            parse_mode='MarkdownV2',
        )

    # Show manuals
    @staticmethod
    async def _manuals(update: Update, _) -> None:
        query = update.callback_query

        await query.answer()

        lang = update.effective_sender.language_code
        menu_message = translate('select_os', lang)

        buttons = [
            [InlineKeyboardButton("Android", url="https://example.com/linux_manual")],
            [InlineKeyboardButton("iOS/MacOS", url="https://example.com/macos_manual")],
            [InlineKeyboardButton(translate('back', lang), callback_data='back_to_menu')]
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        await query.edit_message_text(text=menu_message, reply_markup=reply_markup)

    # Handle "Back" button in the main menu
    async def _back_to_menu(self, update: Update, context) -> None:
        await self._main_menu(update, context)

    def _bind_handlers(self, ) -> None:
        self._application.add_handler(CommandHandler("start", self._main_menu))
        self._application.add_handler(CallbackQueryHandler(self._main_menu, pattern='^menu_'))
        self._application.add_handler(CallbackQueryHandler(self._generate_vpn, pattern='^generate_vpn$'))
        self._application.add_handler(CallbackQueryHandler(self._generate_vpn, pattern='^view_vpn$'))
        self._application.add_handler(CallbackQueryHandler(self._manuals, pattern='^manuals$'))
        self._application.add_handler(CallbackQueryHandler(self._back_to_menu, pattern='^back_to_menu$'))

    def run(self):
        self._application.run_polling()


def main():
    init_db()

    bot = TelegramBot(cfg_path="configs/config.yaml")
    bot.run()


if __name__ == '__main__':
    main()
