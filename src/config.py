# Чтение конфигурации из YAML файла
def load_config():
    with open("../config.yaml", "r") as file:
        return yaml.safe_load(file)
