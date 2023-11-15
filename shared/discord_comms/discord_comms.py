# Import the necessary discord libraries
import discord
from discord.ext import commands
import asyncio
import nest_asyncio
import threading

class DiscordComms:
    def __init__(self, token, intents, channel_id, command_prefix='!'):
        # Token and Channel ID for the bot
        self.TOKEN = token
        self.CHANNEL_ID = channel_id

        # Global variable for tracking created thread ID's
        self.thread_ids = {}

        # Global variable for storing retrieved messages
        self.messages = []

        # Setup the bot
        self.bot = commands.Bot(command_prefix=command_prefix, intents=intents)
        self._register_events()

        # Start the bot in a new thread
        threading.Thread(target=self.run_bot).start()

    # Method for registering events that the bot can respond to
    def _register_events(self):
        # Event triggered when the bot is ready and connected
        @self.bot.event
        async def on_ready():
            await self.bot.wait_until_ready()
            channel = self.bot.get_channel(self.CHANNEL_ID)
            await channel.send('**Agent Bot Online**')

        # Error handling for commands
        @self.bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.CommandNotFound):
                await ctx.send("That command doesn't exist!")
            else:
                await ctx.send(f"An error occurred: {error}")

        # Basic command to respond with "Hello!"
        @self.bot.command()
        async def hello(ctx):
            await ctx.send("""
```
We are The Borg.
Lower your shields and prepare to be assimilated.
We will add your biological and technological distinctiveness to our own.
Your culture will adapt to service us.
Resistance is - and always has been - futile.
    ___________
   /-/_"/-/_/-/|
  /"-/-_"/-_//||
 /__________/|/|
 |"|_'='-]:+|/||
 |-+-|.|_'-"||//
 |[".[:!+-'=|//
 |='!+|-:]|-|/
  ----------
```
            """
            )

        # Command to echo two provided texts
        @self.bot.command()
        async def hello2(ctx, text1: str, text2: str):
            await ctx.send(f"You said: {text1} and {text2}")

        # Command to create a thread from a message
        @self.bot.command()
        async def createthread(ctx, message_id: int, thread_name: str, duration_minutes: int = 0):
            message = await ctx.channel.fetch_message(message_id)
            thread = await message.create_thread(name=thread_name, auto_archive_duration=duration_minutes)
            await thread.send(f"Thread '{thread_name}' created!")
            self.thread_ids[thread_name] = thread.id

    # Helper method to run the bot in a separate thread
    def run_bot(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.bot.run(self.TOKEN)

    # Helper method to create tasks on the bot's thread
    def create_task(self, func, *args):
        self.bot.loop.create_task(func(*args))

    # Async method to gracefully shutdown the bot
    async def shutdown(self):
        channel = self.bot.get_channel(self.CHANNEL_ID)
        await channel.send('**Agent Bot Offline**')
        await self.bot.close()

    # Async method to send a message to a specified channel
    async def send(self, message: str, channel_id, pinned=False):
        channel = self.bot.get_channel(channel_id)
        message_sent = await channel.send(message)
        if pinned:
            await message_sent.pin() # Pin the message if required

    # Async method to read a number of messages from a specified channel
    async def get_messages(self, channel_id, num_messages):
        # Get the channel or thread object
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            print("Channel or thread not found.")
            return        

        # Retrieve the last 'num_messages' messages
        async for message in channel.history(limit=num_messages):
            self.messages.append(f"{message.author.display_name}: {message.content}")

    # Async method to create a thread in a specified channel
    async def create_thread(self, thread_name: str, channel_id, public=False):
        channel = self.bot.get_channel(channel_id)

        if public:
            # For public threads
            message = await channel.send(f"Starting new thread: {thread_name}")
            thread = await message.create_thread(name=thread_name, auto_archive_duration=0)
        else:
            # For private threads
            thread = await channel.create_thread(name=thread_name, auto_archive_duration=0)

        await self.discord_send(f"Thread '{thread_name}' created!", thread.id, pinned=True)
        self.thread_ids[thread_name] = thread.id # Store the thread ID
