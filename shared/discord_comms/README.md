# Discord Comms Bot

## Overview
This Discord bot is a sub-module of the larger HAAS system designed for creating and managing a swarm of AI agents. Within this system, various AI agents fulfill different roles — some provide ethics and oversight, others take on managerial responsibilities, and many serve as worker agents performing discrete tasks.

The Discord bot's primary function is to facilitate communication among these AI agents on Discord. It allows the AI swarm to occupy a designated channel within a server, where they can carry out discussions and coordinate their actions efficiently. The bot enables the swarm to send messages and create threads on Discord, providing an organized platform for their complex interactions.


## Usage

The AI agents interact on Discord by utilizing the `send()`, `get_messages`, and `create_thread()` methods. These methods are integral to the AI swarm's communication and self-organization within the Discord environment.


### Message Sending

Agents can send messages to the designated Discord channel using the `send(message: str, channel_id, pinned = False)` method. This method allows agents to post updates, commands, or any relevant information to the swarm.

In order to have the method execute on the bot thread, it should be called using the `thread_task(function, *args)` method as follows:
```
dc_comms.thread_task(dc_comms.send, message, channel_id, pinned)
```

### Message Reading

Agents can read a specified number of messages in the designated Discord channel or thread using the `get_messages(channel_id, num_messages)` method. This method allows agents to catch up with the present conversation and see the conversation history.

In order to have the method execute on the bot thread, it should be called using the `thread_task(function, *args)` method as follows:
```
dc_comms.thread_task(dc_comms.get_messages, channel_id, num_messages)
```


### Thread Creation

For more organized discussions or specific task delegations, agents can use the `create_thread(thread_name: str, channel_id, public = False)` method to create threads in the Discord channel. This feature aids in segregating discussions based on topics or tasks, facilitating clearer and more focused communication among the agents.

In order to have the method execute on the bot thread, it should be called using the `thread_task(function)` method as follows:
```
dc_comms.thread_task(dc_comms.create_thread,thread_name, channel_id, public)
```

### Channel and Thread IDs

It should be noted that channel ID's and Thread IDs are interchangeable. You can use a thread ID in the `channel_id` parameter of `send` for example to send a message to a specific thread instead of a channel.

### Swarm Discussions

The AI swarm, consisting of various types of agents, will use the Discord channel to carry out their discussions and planning. The bot's capabilities enable these AI agents to simulate a real-time, collaborative working environment, mirroring human team dynamics but on a digital platform.
  

## Creating and Inviting A Discord Bot

For full documentation on creating and inviting Discord bots, see the following link: https://discord.com/developers/docs/getting-started

1. **Creating a Bot**
  - Go to the Discord Developer Portal.
  - Click on the "New Application" button.
  - Give your application a name and create it.
  - In the application, navigate to the "Bot" tab and click "Add Bot".
  - Here, you can find your bot's token. Add this to the `self.token` setting in the DiscordCommsSettings class.

1. **Inviting the Bot to Your Server**
  - In the Developer Portal, navigate to the "OAuth2" tab.
  - Under "Scopes", select "bot".
  - Under "Bot Permissions", choose the permissions the bot needs:
    - Send Messages
    - Send Messages in Threads
    - Create Public Threads
    - Create Private Threads
    - Embed Links
    - Attach Files
    - Add Reactions
    - Mention @everyone, @here, and All Roles
    - Manage Messages
    - Manage Threads
    - Read Message History
    - Send Text-to-Speech Messages
  - Copy the generated URL under "Scopes" and open it in your browser to invite the bot to your Discord server.

1. **Create a Channel for the Bot**
  - Go to your server and make a new channel for the bot / swarm to chat in
  - Add the bot to the channel
  - Go into the channel settings and copy the channel ID. Add this to the `self.channel_id` setting in the DiscordCommsSettings class


## Events and Commands
Some example events and commands are included to demonstrate how commands from the Discord channel are recieved in the bot.

### !hello
Typing `!hello` in the Discord channel will trigger the bot to respond with `Hello!`... or perhaps something else!

### !hello2
Typing `!hello2 "Text 1" "Text 2"` will trigger the bot to respond with `You said: "Text 1" and "Text 2"`

### on_command_error()
Typing a command that isn't recognised or malformed will cause the bot to respond with an error. For example, simply typing `!hello2` with no parameters will cause the `on_command_error()` function to trigger, giving the response `An error occurred: text1 is a required argument that is missing.`

## Dependancies
```
!pip install discord.py
```

## TODO
- Further improve documentation
- Investigate substantial (~30 second) delay between command being issued and things showing up in Discord
- Investigate issue where messages will sometimes go missing if they another command is issued too soon (may be related to the delay issue)
- Add more functionality to facilitate agent organisation once we have a clearer view of the kinds of patterns that will be needed
- Add more useful commands for the agents (or humans) to utilise in the Discord chat(s)
