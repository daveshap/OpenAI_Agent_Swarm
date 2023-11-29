# Dependancies
#!pip install discord.py

import time
wait_duration = 40 # 40s duration

# Import the DiscordComms class and DiscordCommsSettings
from discord_comms import DiscordComms
from discord_comms_settings import DiscordCommsSettings

# Using the class
nest_asyncio.apply()
dc_settings = DiscordCommsSettings()

dc_comms = DiscordComms(dc_settings.token,
                        dc_settings.intents,
                        dc_settings.channel_id
                        )

# Send a normal message
dc_comms.create_task(dc_comms.send,
                     "This is a normal test message", 
                     dc_settings.channel_id
                     )

# Wait for the message to finish sending
time.sleep(wait_duration)

# Send a pinned message
pinned = True
dc_comms.create_task(dc_comms.send,
                     "This is a pinned test message", 
                     dc_settings.channel_id,
                     pinned
                     )

# Wait for the message to finish sending
time.sleep(wait_duration)

# Get the last n_messages
n_messages = 5
dc_comms.create_task(dc_comms.get_messages,
                     dc_settings.channel_id,
                     n_messages
                     )

# Wait for the messages to be retrieved
time.sleep(wait_duration)

# Print the messages
print("\n".join(dc_comms.messages) if dc_comms.messages else "No messages found.")

# Create a public thread
thread_name = "Test Thread"
public = True
dc_comms.create_task(dc_comms.create_thread,
                     thread_name,
                     dc_settings.channel_id,
                     public
                     )

# Wait for the thread to be created
time.sleep(wait_duration)

# Print the thread IDs
print(f'Thread IDs: {dc_comms.thread_ids}')

thread_name_to_check = thread_name

# Check if the thread ID of a thread_name_to_check is stored
if thread_name_to_check in dc_comms.thread_ids:
    thread_id = dc_comms.thread_ids[thread_name_to_check]

    print(f"ID of thread {thread_name_to_check} is {thread_id}")
else:
    print(f"No thread ID stored for {thread_name_to_check}")

# Gracefully shutdown the Discord bot
dc_comms.create_task(dc_comms.shutdown)
