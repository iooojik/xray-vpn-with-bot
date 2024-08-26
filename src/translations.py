translations = {
    'welcome': {
        'ru': "Привет, {name}! Выберите язык:",
        'en': "Hello, {name}! Please choose a language:"
    },
    'menu_message': {
        'ru': "Выберите действие:",
        'en': "Choose an action:"
    },
    'generate_vpn': {
        'ru': "Сгенерировать VPN конфигурацию",
        'en': "Generate VPN configuration"
    },
    'view_vpn': {
        'ru': "Посмотреть существующие",
        'en': "View existing"
    },
    'manuals': {
        'ru': "Мануалы",
        'en': "Manuals"
    },
    'back': {
        'ru': "Назад",
        'en': "Back"
    },
    'no_vpn_configs': {
        'ru': "У вас нет сохраненных VPN конфигураций.",
        'en': "You have no saved VPN configurations."
    },
    'vpn_generated': {
        'ru': "Ваша VPN конфигурация:",
        'en': "Your VPN configuration:"
    },
    'select_os': {
        'ru': "Выберите операционную систему:",
        'en': "Select an operating system:"
    }
}


def translate(key, lang, **kwargs):
    return translations[key][lang].format(**kwargs)
