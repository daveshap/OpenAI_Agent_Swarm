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
