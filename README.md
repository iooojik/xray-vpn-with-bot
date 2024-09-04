# Xray VPN with Telegram Bot

This project integrates Xray VPN functionalities with a Telegram bot to provide a user-friendly way to generate VPN
configurations, select languages, and access manuals for different operating systems.

## Features

- **Multi-language Support**: Users can choose their preferred language for interaction with the bot.
- **VPN Configuration Generation**: The bot generates VPN configuration files based on user input.
- **Cross-Platform Manuals**: Manuals available for different operating systems to guide users through the VPN setup.
- **Dockerized Deployment**: Easily deploy the entire system using Docker and Docker Compose.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/iooojik/xray-vpn-with-bot.git
   cd xray-vpn-with-bot
   ```

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up configurations:**
    - Modify the configuration files in the `configs` directory as needed.

4. **Run the application:**
   ```bash
   python src/bot.py
   ```

Alternatively, you can use Docker:

```bash
docker compose build && docker compose up
```

## Usage

- **Start the Bot**: Run the `bot.py` script to start the Telegram bot.
- **Interact with the Bot**: Use the provided commands to generate VPN configurations, select languages, and view
  manuals.

## File Structure

- `src/`: Contains the source code for the bot and VPN functionalities.
- `configs/`: Configuration files for the VPN and bot settings.
- `build/`: Build scripts and related files.
- `docker-compose.yaml`: Docker Compose file to deploy the project easily.
- `install.sh`: Script to install necessary dependencies and set up the environment.

## Contributing

Feel free to open issues or submit pull requests for new features, bug fixes, or improvements.
