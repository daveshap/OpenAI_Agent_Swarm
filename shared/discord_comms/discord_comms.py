# Dependancies
# !pip install discord.py

# Import the necessary discord libraries
import discord
from discord.ext import commands
from discord import Intents

# Token and Channel ID for the bot (Replace with actual values)
TOKEN = 'YOUR_BOT_TOKEN'  # Replace with your bot token
CHANNEL_ID = 0 # Replace with your channel ID

# Setting up bot intents for various functionalities
intents = Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

# Initialize the bot with a command prefix and specified intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Event triggered when the bot is ready and connected
@bot.event
async def on_ready():
    await bot.wait_until_ready()  # Ensure bot is fully connected
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send('**Agent Bot Online**')  # Send initial message to the channel

# Error handling for commands
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("That command doesn't exist!")  # Command not found error
    else:
        await ctx.send(f"An error occurred: {error}")  # Other errors

# Basic command to respond with "Hello!"
@bot.command()
async def hello(ctx):
    await ctx.send("Hello!")

# Command to echo two provided texts
@bot.command()
async def hello2(ctx, text1: str, text2: str):
    await ctx.send(f"You said: {text1} and {text2}")

# Command to create a thread from a message
@bot.command()
async def createthread(ctx, message_id: int, thread_name: str, duration_minutes: int = 0):
    message = await ctx.channel.fetch_message(message_id)  # Fetch the message
    thread = await message.create_thread(name=thread_name, auto_archive_duration=duration_minutes)  # Create thread
    await thread.send(f"Thread '{thread_name}' created!")  # Send confirmation message in thread

# Necessary imports for asynchronous operation
import asyncio
import nest_asyncio
nest_asyncio.apply()

import threading

# Function to run the bot in a separate thread
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

# Start the bot in a new thread
threading.Thread(target=run_bot).start()

# Helper function to create tasks for discord bot
def discord_thread_task(func, *args):
    bot.loop.create_task(func(*args))

# Async function to send a message to a specified channel
async def discord_send(message: str, channel_id, pinned=False):
    channel = bot.get_channel(channel_id)
    message_sent = await channel.send(message)
    if pinned:
        await message_sent.pin()  # Pin the message if required

messages = []
channel_not_found = False

# Async function to read a number of messages from a specified channel
async def discord_get_messages(channel_id, num_messages):
    channel_not_found = False
    # Get the channel or thread object
    channel = bot.get_channel(channel_id)
    if channel is None:
        channel_not_found = True
        print("Channel or thread not found.")
        return

    # Retrieve the last 'num_messages' messages
    async for message in channel.history(limit=num_messages):
        messages.append(f"{message.author.display_name}: {message.content}")

    # Process the messages
    # (For example, print them. You can modify this part as per your requirement)
    print("\n".join(messages) if messages else "No messages found.")

# Global variable to store thread IDs
thread_ids = {}

# Async function to create a thread in a specified channel
async def discord_create_thread(thread_name: str, channel_id, public=False):
    channel = bot.get_channel(channel_id)
    thread = None

    if public:
        # For public threads
        message = await channel.send(f"Starting new thread: {thread_name}")
        thread = await message.create_thread(name=thread_name, auto_archive_duration=0)
    else:
        # For private threads
        thread = await channel.create_thread(name=thread_name, auto_archive_duration=0)

    await discord_send(f"Thread '{thread_name}' created!", thread.id, pinned=True)
    thread_ids[thread_name] = thread.id  # Store the thread ID
