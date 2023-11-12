# Send message
{
  "name": "sendMessage",
  "description": "Send a message to another agent",
  "parameters": {
    "type": "object",
    "properties": {
      "recipient": {
        "type": "string",
        "description": "Agent name to send the message to"
      },
      "message": {
        "type": "string",
        "description": "Message to send"
      }
    },
    "required": [
      "recipient", "message"
    ]
  }
}

# Broadcast
{
  "name": "broadcast",
  "description": "Broadcast a message on a channel",
  "parameters": {
    "type": "object",
    "properties": {
      "channel": {
        "type": "string",
        "description": "Channel name to broadcast the message to"
      },
      "message": {
        "type": "string",
        "description": "Message to broadcast"
      }
    },
    "required": [
      "channel", "message"
    ]
  }
}

# Assign task
{
  "name": "assignTask",
  "description": "Assign a task to the worker agents",
  "parameters": {
    "type": "object",
    "properties": {
      "assignee": {
        "type": "string",
        "description": "Name of the agent assigned to this task"
      },
      "task": {
        "type": "string",
        "description": "Description of the task"
      }
    },
    "required": [
      "description"
    ]
  }
}

# Resolve task
{
  "name": "resolveTask",
  "description": "Send final task results to the boss agent",
  "parameters": {
    "type": "object",
    "properties": {
      "id": {
        "type": "string",
        "description": "Task id provided when the task was assigned"
      },
      "result": {
        "type": "string",
        "description": "Result of the task"
      }
    },
    "required": [
      "description"
    ]
  }
}