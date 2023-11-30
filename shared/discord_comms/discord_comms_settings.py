# Import the necessary discord libraries
from discord import Intents

# Config
class DiscordCommsSettings:
    def __init__(self):
        self.token = 'YOUR_BOT_TOKEN'  # Replace with your bot token
        self.channel_id = 0 # Replace with your channel ID

        self.intents = Intents.default()
        self.intents.messages = True
        self.intents.message_content = True
        self.intents.guilds = True
