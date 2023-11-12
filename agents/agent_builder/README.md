# Agent Builder

This preliminary experiment has to do with getting the OpenAI Assistant endpoint to create other Assistants (agents). This is the primary thing we need to figure out: agents that build agents in a structured, hierarchical manner. This will allow us to create agent swarms of arbitrary size and purpose.

Given the current API, there are just a few primary parameters to work with. 

## Parameters

1. **Instructions:** This is similar to the SYSTEM window of the ChatGPT API or the Custome Instructions in ChatGPT web interface. The latest model seems incredibly responsive to personas, archetypes, and so on. This needs to be dynamically defined at instantiation based upon `context`.

2. **Functions:** These are the "tools" that each agent will have. The first tools are the ability to create and destroy other agents. The second tools are the abilities to make more tools, depending upon `context` and `mission`. Other functions will eventually include API calls to other systems, such as cloud platforms, robots, data access points, and so on.

3. **File Retrieval:** This will serve as each agent's internal KB (knowledge base) including knowledge about the HAAS system, morality, code base, API documentation, and so on. Basically this is the "user manual" for the agent. 

**Code Interpreter** will likely be needed by most agents, but as of right now it's not clear how it may be used. 

## Instructions

The instructions will need to include enough `context` such as about the HAAS system overall, as well as a few other bits of information.

1. **Archetype or Persona:** The latest models demonstrate the ability to adopt personas very well. This is further exmplified by ChatDev where the model can adopt personas such as "marketer" or "CEO". Furthermore, we can adopt mythic archetypes capable of moral reasoning, executive judgment, ethical debate, and prosecution of mission. This is critical for the SOB (supreme oversight board) as it will be tasked with making executive decisions, judgments, debating over morality and ethics, and overall steering the rest of the ship.

2. **Context:** Context needs to include enough information about what the agent is supposed to do and what it is part of. 

3. **Mission:** Every agent must be instantiated with an individualized mission or purpose. At the highest level, the SOB's mission is to steer the rest of the swarm. At the lowest level, an agent's purpose may be something as simple as "Fix this software bug" or "send an email to Jeff Bezos"

## Functions

The functions are the tools given to the agent at instantiation. This includes data tools (internal ability to manipulate data), coding tools (ability to write and execute code), access tools (ability to communicate with external APIs, and probably a few other categories, but these are likely the main ones. 

1. **Internal Data Tools:** This includes the ability to perform RAG, search for and manipulate data, such as with the BSHR loop, organizing and so on. 

2. **Internal Coding Tools:** This includes the ability to write, test, execute, and read code for internal use or saving to external repositories. 

3. **External API Calls:** This includes all external tools such as calls to vendor and cloud platforms, robotic endpoints, and so on.

## Retrieval

This includes the list of files to be included with the agent at instantiation. There are likely some standard documents that should be included with all agents, such as a baseline HAAS document that includes basics of operation (sort of like an Employee Handbook and SOPs). Each agent should also be equipped with any unique or distinct information needed for its `mission` such as software specifications and documentation. 

1. **Agent Handbook:** This is a standard document that all agents should be equipped with. This document should define HAAS at a high level, as well as SOPs (standard operating procedures) to ensure consistency across the entire swarm.

2. **Software Specifications:** For agents meant to build anything software related, it should get specifications such as definition of done and other critical components so it knows what to build.

3. **Relevant Documentation:** This should be API documentation, procedural documentation, and other relevant stuff to the agent's particular `mission` and `functions`. 


## Chat Functions

The primary method of interaction with the agents is via chat dialog similar to the ChatGPT API. The USER (input) could be anything from directives from other agents (like a supervisor or manager) as well as chat logs or messages from groups of agents, telemetry from various sources, and so on. The output, likewise, is something that can be recorded and "sent up the chain"

### USER Input

The USER, in this case, is a stand in for the rest of the HAAS swarm. It could be a direct supervisor agent (manager) or something else. Here are some ideas:

1. **Supervisor Directives:** We will need to have supervisor or manager agents telling other agents what to do. 
2. **Group Chats:** As demonstrated with ChatDev and other "chatroom" style usecases of agents. 
3. **Telemetry:** This can include logs and feedback from other systems to provide updated context. 

### Agent Output

By and large, agent output will probably be consumed by other agents, message queues, and system buses. It is not yet clear how we'll structure this. It could get very noisy very fast.
