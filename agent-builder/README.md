# Agent Builder

## Description
This script is designed to create assistants using OpenAI's API based on a predefined folder structure. For each agent:
- Create a folder with its name, eg.: Autonomous Swarm Agent Builder
- Create a "instructions.md" file with the custom instructions for that agent.
- If you want to provide files for RAG, create a files folder and place them there.

## Requirements
Python 3.x
Packages:
- openai
- python-dotenv