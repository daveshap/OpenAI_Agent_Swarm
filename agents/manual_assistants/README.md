# Objective
This folder includes some initial tests on how function calling may enable HAAS communication and cognition. A network with a limited number of agents is created as a test to identify issues and help guide the architecture: one boss talking to three worker agents.

# Observations
## Choosing what to propagate
The simplest approach when connecting multiple agents is to have the downstream agents get all the messages from their source nodes. This limits the capacity of the model greatly.
Instead it is possible to give the agents the possibility to decide which messages to propagate, by instructing them to call a *sendMessage* function.

## Function specificity
There's value in having more specific and meaningful functions instead of general all-purpose ones. Eg.: assignTask vs sendMessage
Advantages:
- Semantic cues for the model directly in the function declaration. More lightweight system prompts.
- Easier to program custom behaviours for different functions. No need to switch based on parameters.

## Channels
There's value on a basic "sendMessage" function. But the moment multiple agents need to work on a task it makes sense to introduce the concept of *channels* which agents may be part of and to which they may broadcast messages.
Note: all agents of a channel will receive messages queued there EXCEPT the one that sent it.

## Peer chatter and race conditions
With a basic boss-worker x3 topology it was clear that the workers had trouble having effective communication. They often step on each other and take a long time to further the discussion, making this system very token inefficient.
To prevent that, some prompt engineering strategies can be employed, eg.: *If you receive a message from other workers don't reply back unless necessary. Keep the worker channel as free from noise as possible. Share results in the channel to advance the mission, but do not send acknowledgements.*

However, once the system prompt gets to a certain level of complexity it is hard to ensure that the agents will follow the rules consistently. In that sense some effort has been put in analysing off-model strategies to improve the communication.

## Blocking communication
The boss agent originally used *sendMessage* to pass the tasks to the workers. As it suffered from similar issues, *assignTask* was created. It functions almost identically to *sendMessage* except by the fact that it waits for the actual response before unblocking the run.
There's limitations to this approach such as the run expiry time, however it has proven very effective so far with simple tasks.

Following that pattern, one may modify the *broadcast* function so it waits for a response from one of the peers. 

## Raise hand function and queue
The key issue behind the miscommunication between peer agents is that race conditions during model executions make it so some agents may broadcast a response before they've catched up with all the new messages in the channel. Effectively introducing lag in the conversation.

To combat that a "raise hand" system can be used. Implemented as a multi-thread semaphore, only one agent may send messages to the channel at a certain time.

Any agent may request to be put into the *raised hands queue*. An agent may only appear once in the queue.
Once an agent turn is reached, it will first be given all the new messages in the channel, thus ensuring there's no lag in the conversation. Only then will it be allowed to broadcast its message.
That will require some delicate work with the functions and the prompts, as it's a mandatory hybrid model+framework functionality: the framework can't do it without the model collaboration and vice-versa. 

This will allow for many options down the road. Mixing concepts from telecom and psychology it may be interesting to configure agents with different messaging priorities, ie.: able to jump places in the queue. So we would be modelling more "pushy" agent personalities by giving them access to use high priority messaging.

## Thinking functions
By introducing a *thinking* function, agents may indicate they’re not ready to provide an answer. The introduction of self-prompting provides breathing room to the model and reduces the chances of subpar messages propagating through the network. 
From the framework side it will be be seen as an initial function call (*thinking*) which will be immediately answered with an ACK. Afterwards a that thread would be prompted to *continue working*.