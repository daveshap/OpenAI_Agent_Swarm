## Function calling
Learn how to connect large language models to external tools.

Introduction
In an API call, you can describe functions and have the model intelligently choose to output a JSON object containing arguments to call one or many functions. The Chat Completions API does not call the function; instead, the model generates JSON that you can use to call the function in your code.

The latest models (gpt-3.5-turbo-1006 and gpt-4-1106-preview) have been trained to both detect when a function should to be called (depending on the input) and to respond with JSON that adheres to the function signature more closely than previous models. With this capability also comes potential risks. We strongly recommend building in user confirmation flows before taking actions that impact the world on behalf of users (sending an email, posting something online, making a purchase, etc).

This guide is focused on function calling with the Chat Completions API, for details on function calling in the Assistants API, please see the Assistants Tools page.
Common use cases
Function calling allows you to more reliably get structured data back from the model. For example, you can:

Create assistants that answer questions by calling external APIs (e.g. like ChatGPT Plugins)
e.g. define functions like send_email(to: string, body: string), or get_current_weather(location: string, unit: 'celsius' | 'fahrenheit')
Convert natural language into API calls
e.g. convert "Who are my top customers?" to get_customers(min_revenue: int, created_before: string, limit: int) and call your internal API
Extract structured data from text
e.g. define a function called extract_data(name: string, birthday: string), or sql_query(query: string)
...and much more!

The basic sequence of steps for function calling is as follows:

Call the model with the user query and a set of functions defined in the functions parameter.
The model can choose to call one or more functions; if so, the content will be a stringified JSON object adhering to your custom schema (note: the model may hallucinate parameters).
Parse the string into JSON in your code, and call your function with the provided arguments if they exist.
Call the model again by appending the function response as a new message, and let the model summarize the results back to the user.
Supported models
Not all model versions are trained with function calling data. Function calling is supported with the following models:

gpt-4
gpt-4-1106-preview
gpt-4-0613
gpt-3.5-turbo
gpt-3.5-turbo-1106
gpt-3.5-turbo-0613
In addition, parallel function calls is supported on the following models:

gpt-4-1106-preview
gpt-3.5-turbo-1106
Parallel function calling
Parallel function call is helpful for cases where you want to call multiple functions in one turn. For example, you may want to call functions to get the weather in 3 different locations at the same time. In this case, the model will call multiple functions in a single response. And you can pass back the results of each function call by referencing the tool_call_id in the response matching the ID of each tool call.

In this example, we define a single function get_current_weather. The model calls the function multiple times, and after sending the function response back to the model, we let it decide the next step. It responded with a user-facing message which was telling the user the temperature in Boston, San Francisco, and Tokyo. Depending on the query, it may choose to call a function again.

If you want to force the model to call a specific function you can do so by setting tool_choice with a specific function name. You can also force the model to generate a user-facing message by setting tool_choice: "none". Note that the default behavior (tool_choice: "auto") is for the model to decide on its own whether to call a function and if so which function to call.

Example with one function called in parallel

```python
python
import openai
import json

# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": location, "temperature": "10", "unit": "celsius"})
    elif "san francisco" in location.lower():
        return json.dumps({"location": location, "temperature": "72", "unit": "fahrenheit"})
    else:
        return json.dumps({"location": location, "temperature": "22", "unit": "celsius"})

def run_conversation():
    # Step 1: send the conversation and available functions to the model
    messages = [{"role": "user", "content": "What's the weather like in San Francisco, Tokyo, and Paris?"}]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
        }
    ]
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_current_weather": get_current_weather,
        }  # only one function in this example, but you can have multiple
        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                location=function_args.get("location"),
                unit=function_args.get("unit"),
            )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        second_response = openai.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages,
        )  # get a new response from the model where it can see the function response
        return second_response
print(run_conversation())
```
You can find more examples of function calling in the OpenAI cookbook:
Function calling
Learn from more examples demonstrating function calling
Tokens
Under the hood, functions are injected into the system message in a syntax the model has been trained on. This means functions count against the model's context limit and are billed as input tokens. If running into context limits, we suggest limiting the number of functions or the length of documentation you provide for function parameters.

It is also possible to use fine-tuning to reduce the number of tokens used if you have many functions defined.









##Text generation models
New capabilities launched at DevDay

Text generation models are now capable of JSON mode and Reproducible outputs. We also launched the Assistants API to enable you to build agent-like experiences on top of our text-generation models.
OpenAI's text generation models (often called generative pre-trained transformers or large language models) have been trained to understand natural language, code, and images. The models provide text outputs in response to their inputs. The inputs to these models are also referred to as "prompts". Designing a prompt is essentially how you “program” a large language model model, usually by providing instructions or some examples of how to successfully complete a task.

Using OpenAI's text generation models, you can build applications to:

Draft documents
Write computer code
Answer questions about a knowledge base
Analyze texts
Give software a natural language interface
Tutor in a range of subjects
Translate languages
Simulate characters for games
With the release of gpt-4-vision-preview, you can now build systems that also process and understand images.

Explore GPT-4 with image inputs
Check out the vision guide for more detail.
To use one of these models via the OpenAI API, you’ll send a request containing the inputs and your API key, and receive a response containing the model’s output. Our latest models, gpt-4 and gpt-3.5-turbo, are accessed through the chat completions API endpoint.

MODEL FAMILIES	API ENDPOINT
Newer models (2023–)	gpt-4, gpt-3.5-turbo	https://api.openai.com/v1/chat/completions
Updated base models (2023)	babbage-002, davinci-002	https://api.openai.com/v1/completions
Legacy models (2020–2022)	text-davinci-003, text-davinci-002, davinci, curie, babbage, ada	https://api.openai.com/v1/completions
You can experiment with various models in the chat playground. If you’re not sure which model to use, then use gpt-3.5-turbo or gpt-4.

Chat Completions API
Chat models take a list of messages as input and return a model-generated message as output. Although the chat format is designed to make multi-turn conversations easy, it’s just as useful for single-turn tasks without any conversation.

An example Chat Completions API call looks like the following:

```python
from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Who won the world series in 2020?"},
    {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
    {"role": "user", "content": "Where was it played?"}
  ]
)
```
To learn more, you can view the full API reference documentation for the Chat API.

The main input is the messages parameter. Messages must be an array of message objects, where each object has a role (either "system", "user", or "assistant") and content. Conversations can be as short as one message or many back and forth turns.

Typically, a conversation is formatted with a system message first, followed by alternating user and assistant messages.

The system message helps set the behavior of the assistant. For example, you can modify the personality of the assistant or provide specific instructions about how it should behave throughout the conversation. However note that the system message is optional and the model’s behavior without a system message is likely to be similar to using a generic message such as "You are a helpful assistant."

The user messages provide requests or comments for the assistant to respond to. Assistant messages store previous assistant responses, but can also be written by you to give examples of desired behavior.

Including conversation history is important when user instructions refer to prior messages. In the example above, the user’s final question of "Where was it played?" only makes sense in the context of the prior messages about the World Series of 2020. Because the models have no memory of past requests, all relevant information must be supplied as part of the conversation history in each request. If a conversation cannot fit within the model’s token limit, it will need to be shortened in some way.

To mimic the effect seen in ChatGPT where the text is returned iteratively, set the stream parameter to true.
Chat Completions response format
An example Chat Completions API response looks as follows:

```json
{
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "message": {
        "content": "The 2020 World Series was played in Texas at Globe Life Field in Arlington.",
        "role": "assistant"
      }
    }
  ],
  "created": 1677664795,
  "id": "chatcmpl-7QyqpwdfhqwajicIEznoc6Q47XAyW",
  "model": "gpt-3.5-turbo-0613",
  "object": "chat.completion",
  "usage": {
    "completion_tokens": 17,
    "prompt_tokens": 57,
    "total_tokens": 74
  }
}
```
The assistant’s reply can be extracted with:

```python
response['choices'][0]['message']['content']
```

Every response will include a finish_reason. The possible values for finish_reason are:

stop: API returned complete message, or a message terminated by one of the stop sequences provided via the stop parameter
length: Incomplete model output due to max_tokens parameter or token limit
function_call: The model decided to call a function
content_filter: Omitted content due to a flag from our content filters
null: API response still in progress or incomplete
Depending on input parameters, the model response may include different information.

JSON mode New
A common way to use Chat Completions is to instruct the model to always return JSON in some format that makes sense for your use case, by providing a system message. This works well, but occasionally the models may generate output that does not parse to valid JSON.

To prevent these errors and improve model performance, when calling gpt-4-1106-preview or gpt-3.5-turbo-1106, you can set response_format to { type: "json_object" } to enable JSON mode. When JSON mode is enabled, the model is constrained to only generate strings that parse into valid JSON.

Important notes:

When using JSON mode, always instruct the model to produce JSON via some message in the conversation, for example via your system message. If you don't include an explicit instruction to generate JSON, the model may generate an unending stream of whitespace and the request may run continually until it reaches the token limit. To help ensure you don't forget, the API will throw an error if the string "JSON" does not appear somewhere in the context.
The JSON in the message the model returns may be partial (i.e. cut off) if finish_reason is length, which indicates the generation exceeded max_tokens or the conversation exceeded the token limit. To guard against this, check finish_reason before parsing the response.
JSON mode will not guarantee the output matches any specific schema, only that it is valid and parses without errors.
Note that JSON mode is always enabled when the model is generating arguments as part of function calling.

Reproducible outputs Beta
Chat Completions are non-deterministic by default (which means model outputs may differ from request to request). That being said, we offer some control towards deterministic outputs by giving you access to the seed parameter and the system_fingerprint response field.

To receive (mostly) deterministic outputs across API calls, you can:

Set the seed parameter to any integer of your choice and use the same value across requests you'd like deterministic outputs for.
Ensure all other parameters (like prompt or temperature) are the exact same across requests.
Sometimes, determinism may be impacted due to necessary changes OpenAI makes to model configurations on our end. To help you keep track of these changes, we expose the system_fingerprint field. If this value is different, you may see different outputs due to changes we've made on our systems.

Deterministic outputs
Explore the new seed parameter in the OpenAI cookbook
Managing tokens
Language models read and write text in chunks called tokens. In English, a token can be as short as one character or as long as one word (e.g., a or apple), and in some languages tokens can be even shorter than one character or even longer than one word.

For example, the string "ChatGPT is great!" is encoded into six tokens: ["Chat", "G", "PT", " is", " great", "!"].

The total number of tokens in an API call affects:

How much your API call costs, as you pay per token
How long your API call takes, as writing more tokens takes more time
Whether your API call works at all, as total tokens must be below the model’s maximum limit (4097 tokens for gpt-3.5-turbo)
Both input and output tokens count toward these quantities. For example, if your API call used 10 tokens in the message input and you received 20 tokens in the message output, you would be billed for 30 tokens. Note however that for some models the price per token is different for tokens in the input vs. the output (see the pricing page for more information).

To see how many tokens are used by an API call, check the usage field in the API response (e.g., response['usage']['total_tokens']).

Chat models like gpt-3.5-turbo and gpt-4 use tokens in the same way as the models available in the completions API, but because of their message-based formatting, it's more difficult to count how many tokens will be used by a conversation.

DEEP DIVE
Counting tokens for chat API calls
To see how many tokens are in a text string without making an API call, use OpenAI’s tiktoken Python library. Example code can be found in the OpenAI Cookbook’s guide on how to count tokens with tiktoken.

Each message passed to the API consumes the number of tokens in the content, role, and other fields, plus a few extra for behind-the-scenes formatting. This may change slightly in the future.

If a conversation has too many tokens to fit within a model’s maximum limit (e.g., more than 4097 tokens for gpt-3.5-turbo), you will have to truncate, omit, or otherwise shrink your text until it fits. Beware that if a message is removed from the messages input, the model will lose all knowledge of it.

Note that very long conversations are more likely to receive incomplete replies. For example, a gpt-3.5-turbo conversation that is 4090 tokens long will have its reply cut off after just 6 tokens.

Parameter details
Frequency and presence penalties

The frequency and presence penalties found in the Chat Completions API and Legacy Completions API can be used to reduce the likelihood of sampling repetitive sequences of tokens. They work by directly modifying the logits (un-normalized log-probabilities) with an additive contribution.

```
mu[j] -> mu[j] - c[j] * alpha_frequency - float(c[j] > 0) * alpha_presence
```

Where:

mu[j] is the logits of the j-th token
c[j] is how often that token was sampled prior to the current position
float(c[j] > 0) is 1 if c[j] > 0 and 0 otherwise
alpha_frequency is the frequency penalty coefficient
alpha_presence is the presence penalty coefficient
As we can see, the presence penalty is a one-off additive contribution that applies to all tokens that have been sampled at least once and the frequency penalty is a contribution that is proportional to how often a particular token has already been sampled.

Reasonable values for the penalty coefficients are around 0.1 to 1 if the aim is to just reduce repetitive samples somewhat. If the aim is to strongly suppress repetition, then one can increase the coefficients up to 2, but this can noticeably degrade the quality of samples. Negative values can be used to increase the likelihood of repetition.

Completions API Legacy
The completions API endpoint received its final update in July 2023 and has a different interface than the new chat completions endpoint. Instead of the input being a list of messages, the input is a freeform text string called a prompt.

An example API call looks as follows:

```python
from openai import OpenAI
client = OpenAI()

response = client.completions.create(
  model="gpt-3.5-turbo-instruct",
  prompt="Write a tagline for an ice cream shop."
)
```
See the full API reference documentation to learn more.

Token log probabilities
The completions API can provide a limited number of log probabilities associated with the most likely tokens for each output token. This feature is controlled by using the logprobs field. This can be useful in some cases to assess the confidence of the model in its output.

Inserting text
The completions endpoint also supports inserting text by providing a suffix in addition to the standard prompt which is treated as a prefix. This need naturally arises when writing long-form text, transitioning between paragraphs, following an outline, or guiding the model towards an ending. This also works on code, and can be used to insert in the middle of a function or file.

DEEP DIVE
Inserting text
Completions response format
An example completions API response looks as follows:

```json
{
  "choices": [
    {
      "finish_reason": "length",
      "index": 0,
      "logprobs": null,
      "text": "\n\n\"Let Your Sweet Tooth Run Wild at Our Creamy Ice Cream Shack"
    }
  ],
  "created": 1683130927,
  "id": "cmpl-7C9Wxi9Du4j1lQjdjhxBlO22M61LD",
  "model": "gpt-3.5-turbo-instruct",
  "object": "text_completion",
  "usage": {
    "completion_tokens": 16,
    "prompt_tokens": 10,
    "total_tokens": 26
  }
}
```
In Python, the output can be extracted with response['choices'][0]['text'].

The response format is similar to the response format of the Chat Completions API but also includes the optional field logprobs.

Chat Completions vs. Completions
The Chat Completions format can be made similar to the completions format by constructing a request using a single user message. For example, one can translate from English to French with the following completions prompt:

```
Translate the following English text to French: "{text}"
```

And an equivalent chat prompt would be:

```
[{"role": "user", "content": 'Translate the following English text to French: "{text}"'}]
```

Likewise, the completions API can be used to simulate a chat between a user and an assistant by formatting the input accordingly.

The difference between these APIs is the underlying models that are available in each. The chat completions API is the interface to our most capable model (gpt-4), and our most cost effective model (gpt-3.5-turbo).

Which model should I use?
We generally recommend that you use either gpt-4 or gpt-3.5-turbo. Which of these you should use depends on the complexity of the tasks you are using the models for. gpt-4 generally performs better on a wide range of evaluations. In particular, gpt-4 is more capable at carefully following complex instructions. By contrast gpt-3.5-turbo is more likely to follow just one part of a complex multi-part instruction. gpt-4 is less likely than gpt-3.5-turbo to make up information, a behavior known as "hallucination". gpt-4 also has a larger context window with a maximum size of 8,192 tokens compared to 4,096 tokens for gpt-3.5-turbo. However, gpt-3.5-turbo returns outputs with lower latency and costs much less per token.

We recommend experimenting in the playground to investigate which models provide the best price performance trade-off for your usage. A common design pattern is to use several distinct query types which are each dispatched to the model appropriate to handle them.

Prompt engineering
An awareness of the best practices for working with OpenAI models can make a significant difference in application performance. The failure modes that each exhibit and the ways of working around or correcting those failure modes are not always intuitive. There is an entire field related to working with language models which has come to be known as "prompt engineering", but as the field has progressed its scope has outgrown merely engineering the prompt into engineering systems that use model queries as components. To learn more, read our guide on prompt engineering which covers methods to improve model reasoning, reduce the likelihood of model hallucinations, and more. You can also find many useful resources including code samples in the OpenAI Cookbook.

FAQ
How should I set the temperature parameter?
Lower values for temperature result in more consistent outputs, while higher values generate more diverse and creative results. Select a temperature value based on the desired trade-off between coherence and creativity for your specific application.

Is fine-tuning available for the latest models?
Yes, for some. Currently, you can only fine-tune gpt-3.5-turbo and our updated base models (babbage-002 and davinci-002). See the fine-tuning guide for more details on how to use fine-tuned models.

Do you store the data that is passed into the API?
As of March 1st, 2023, we retain your API data for 30 days but no longer use your data sent via the API to improve our models. Learn more in our data usage policy. Some endpoints offer zero retention.

How can I make my application more safe?
If you want to add a moderation layer to the outputs of the Chat API, you can follow our moderation guide to prevent content that violates OpenAI’s usage policies from being shown.

Should I use ChatGPT or the API?
ChatGPT offers a chat interface to the models in the OpenAI API and a range of built-in features such as integrated browsing, code execution, plugins, and more. By contrast, using OpenAI’s API provides more flexibility.












## Assistants API Beta
The Assistants API allows you to build AI assistants within your own applications. An Assistant has instructions and can leverage models, tools, and knowledge to respond to user queries. The Assistants API currently supports three types of tools: Code Interpreter, Retrieval, and Function calling. In the future, we plan to release more OpenAI-built tools, and allow you to provide your own tools on our platform.

You can explore the capabilties of the Assitants API using the Assistants playground or by building a step-by-step integration outlined in this guide. At a high level, a typical integration of the Assistants API has the following flow:

Create an Assistant in the API by defining it custom instructions and picking a model. If helpful, enable tools like Code Interpreter, Retrieval, and Function calling.
Create a Thread when a user starts a conversation.
Add Messages to the Thread as the user ask questions.
Run the Assistant on the Thread to trigger responses. This automatically calls the relevant tools.
The Assistants API is in beta and we are actively working on adding more functionality. Share your feedback in our Developer Forum!
This starter guide walks through the key steps to create and run an Assistant that uses Code Interpreter.

Step 1: Create an Assistant
An Assistant represents an entity that can be configured to respond to users’ Messages using several parameters like:

Instructions: how the Assistant and model should behave or respond
Model: you can specify any GPT-3.5 or GPT-4 models, including fine-tuned models. The Retrieval tool requires gpt-3.5-turbo-1106 and gpt-4-1106-preview models.
Tools: the API supports Code Interpreter and Retrieval that are built and hosted by OpenAI.
Functions: the API allows you to define custom function signatures, with similar behavior as our function calling feature.
In this example, we're creating an Assistant that is a personal math tutor, with the Code Interpreter tool enabled:

Calls to the Assistants API require that you pass a beta HTTP header. This is handled automatically if you’re using OpenAI’s official Python and Node.js SDKs.
OpenAI-Beta: assistants=v1


```python
assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a personal math tutor. Write and run code to answer math questions.",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4-1106-preview"
)
Step 2: Create a Thread
A Thread represents a conversation. We recommend creating one Thread per user as soon as the user initiates the conversation. Pass any user-specific context and files in this thread by creating Messages.
```


thread = client.beta.threads.create()
Threads don’t have a size limit. You can pass as many Messages as you want to a Thread. The API will ensure that requests to the model fit within the maximum context window, using relevant optimization techniques such as truncation.

Step 3: Add a Message to a Thread
A Message contains the user's text, and optionally, any files that the user uploads. Image files aren't supported today, but we plan to add support for them in the coming months.

```python
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="I need to solve the equation `3x + 11 = 14`. Can you help me?"
)
```
Now if you list Messages in Thread, you will see that this message is added to the thread on creation:

```json
{
  "object": "list",
  "data": [
    {
      "created_at": 1696995451,
      "id": "msg_4rb1Skx3XgQZEe4PHVRFQhr0",
      "object": "thread.message",
      "thread_id": "thread_34p0sfdas0823smfv",
      "role": "user",
      "content": [{
        "type": "text",
        "text": {
          "value": "I need to solve the equation `3x + 11 = 14`. Can you help me?",
          "annotations": []
        }
          }],
        ...
```
Step 4: Run the Assistant
For the Assistant to respond to the user message, you need to create a Run. This makes the Assistant read the Thread and decide whether to call tools or simply use the model to best answer the user query. As the run progresses, the assistant appends Messages to the thread with the role="assistant" .

You can optionally pass additional instructions to the Assistant while creating the Run:



```python
run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id,
  instructions="Please address the user as Jane Doe. The user has a premium account."
)
```
Step 5: Display the Assistant's Response
This creates a Run in a queued status. You can periodically retrieve the Run to check on its status to see if it has moved to completed.


```python
run = client.beta.threads.runs.retrieve(
  thread_id=thread.id,
  run_id=run.id
)
```
Once the Run completes, you can retrieve the Messages added by the Assistant to the Thread.


```python
messages = client.beta.threads.messages.list(
  thread_id=thread.id
)
```
And finally, display them to the user! During this Run, the Assistant added two new Messages to the Thread.

ROLE	CONTENT
user	I need to solve the equation 3x + 11 = 14. Can you help me?
assistant	Certainly, Jane Doe. To solve the equation (3x + 11 = 14) for (x), you'll want to isolate (x) on one side of the equation. Here's how you can do that:
Subtract 11 from both sides of the equation to get (3x = 3).
Then, divide both sides by 3 to solve for (x).
Let me calculate the value of (x) for you.
assistant	The solution to the equation (3x + 11 = 14) is (x = 1).
You can also retrieve the Run Steps of this Run if you'd like to explore or display the inner workings of the Assistant and its tools.


## How Assistants work Beta
The Assistants API is designed to help developers build powerful AI assistants capable of performing a variety of tasks.

The Assistants API is in beta and we are actively working on adding more functionality. Share your feedback in our Developer Forum!
Assistants can call OpenAI’s models with specific instructions to tune their personality and capabilities.
Assistants can access multiple tools in parallel. These can be both OpenAI-hosted tools — like Code interpreter and Knowledge retrieval — or tools you build / host (via Function calling).
Assistants can access persistent Threads. Threads simplify AI application development by storing message history and truncating it when the conversation gets too long for the model’s context length. You create a Thread once, and simply append Messages to it as your users reply.
Assistants can access Files in several formats — either as part of their creation or as part of Threads between Assistants and users. When using tools, Assistants can also create files (e.g., images, spreadsheets, etc) and cite files they reference in the Messages they create.
Objects
Assistants object architecture diagram

OBJECT	WHAT IT REPRESENTS
Assistant	Purpose-built AI that uses OpenAI’s models and calls tools
Thread	A conversation session between an Assistant and a user. Threads store Messages and automatically handle truncation to fit content into a model’s context.
Message	A message created by an Assistant or a user. Messages can include text, images, and other files. Messages stored as a list on the Thread.
Run	An invocation of an Assistant on a Thread. The Assistant uses it’s configuration and the Thread’s Messages to perform tasks by calling models and tools. As part of a Run, the Assistant appends Messages to the Thread.
Run Step	A detailed list of steps the Assistant took as part of a Run. An Assistant can call tools or create Messages during it’s run. Examining Run Steps allows you to introspect how the Assistant is getting to it’s final results.
Creating Assistants
We recommend using OpenAI’s latest models with the Assistants API for best results and maximum compatibility with tools.
To get started, creating an Assistant only requires specifying the model to use. But you can further customize the behavior of the Assistant:

Use the instructions parameter to guide the personality of the Assistant and define it’s goals. Instructions are similar to system messages in the Chat Completions API.
Use the tools parameter to give the Assistant access to up to 128 tools. You can give it access to OpenAI-hosted tools like code_interpreter and retrieval, or call a third-party tools via a function calling.
Use the file_ids parameter to give the tools like code_interpreter and retrieval access to files. Files are uploaded using the File upload endpoint and must have the purpose set to assistants to be used with this API.
For example, to create an Assistant that can create data visualization based on a .csv file, first upload a file.

```python
file = client.files.create(
  file=open("speech.py", "rb"),
  purpose='assistants'
)
```
And then create the Assistant with the uploaded file.

```python
assistant = client.beta.assistants.create(
  name="Data visualizer",
  description="You are great at creating beautiful data visualizations. You analyze data present in .csv files, understand trends, and come up with data visualizations relevant to those trends. You also share a brief text summary of the trends observed.",
  model="gpt-4-1106-preview",
  tools=[{"type": "code_interpreter"}],
  file_ids=[file.id]
)
```
You can attach a maximum of 20 files per Assistant, and they can be at most 512 MB each. In addition, the size of all the files uploaded by your organization should not exceed 100GB. You can request an increase in this storage limit using our help center.

You can also use the AssistantFile object to create, delete, or view associations between Assistant and File objects. Note that deleting an AssistantFile doesn’t delete the original File object, it simply deletes the association between that File and the Assistant. To delete a File, use the File delete endpoint instead.

Managing Threads and Messages
Threads and Messages represent a conversation session between an Assistant and a user. There is no limit to the number of Messages you can store in a Thread. Once the size of the Messages exceeds the context window of the model, the Thread smartly truncates them to fit. You can create a Thread with an initial list of Messages like this:


```python
thread = client.beta.threads.create(
  messages=[
    {
      "role": "user",
      "content": "Create 3 data visualizations based on the trends in this file.",
      "file_ids": [file.id]
    }
  ]
)
```
Messages can contain text, images, or files. At the moment, user-created Messages cannot contain image files but we plan to add support for this in the future.

Message annotations

Messages created by Assistants may contain annotations within the content array of the object. Annotations provide information around how you should annotate the text in the Message.

There are two types of Annotations:

file_citation: File citations are created by the retrieval tool and define references to a specific quote in a specific file that was uploaded and used by the Assistant to generate the response.
file_path: File path annotations are created by the code_interpreter tool and contain references to the files generated by the tool.
When annotations are present in the Message object, you'll see illegible model-generated substrings in the text that you should replace with the annotations. These strings may look something like 【13†source】 or sandbox:/mnt/data/file.csv. Here’s an example python code snippet that replaces these strings with information present in the annotations.

```python
# Retrieve the message object
message = client.beta.threads.messages.retrieve(
  thread_id="...",
  message_id="..."
)

# Extract the message content
message_content = message.content[0].text
annotations = message_content.annotations
citations = []

# Iterate over the annotations and add footnotes
for index, annotation in enumerate(annotations):
    # Replace the text with a footnote
    message_content.value = message_content.value.replace(annotation.text, f' [{index}]')

    # Gather citations based on annotation attributes
    if (file_citation := getattr(annotation, 'file_citation', None)):
        cited_file = client.files.retrieve(file_citation.file_id)
        citations.append(f'[{index}] {file_citation.quote} from {cited_file.filename}')
    elif (file_path := getattr(annotation, 'file_path', None)):
        cited_file = client.files.retrieve(file_path.file_id)
        citations.append(f'[{index}] Click <here> to download {cited_file.filename}')
        # Note: File download functionality not implemented above for brevity

# Add footnotes to the end of the message before displaying to user
message_content.value += '\n' + '\n'.join(citations)
```
Runs and Run Steps
When you have all the context you need from your user in the Thread, you can run the Thread with an Assistant of your choice.


```python
run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id
)
```
By default, a Run will use the model and tools configuration specified in Assistant object, but you can override most of these when creating the Run for added flexibility:


```python
run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id,
  model="gpt-4-1106-preview",
  instructions="additional instructions",
  tools=[{"type": "code_interpreter"}, {"type": "retrieval"}]
)
```
Note: file_ids associated with the Assistant cannot be overridden during Run creation. You must use the modify Assistant endpoint to do this.

Run lifecycle

Run objects can have multiple statuses.

Run lifecycle - diagram showing possible status transitions

STATUS	DEFINITION
queued	When Runs are first created or when you complete the required_action, they are moved to a queued status. They should almost immediately move to in_progress.
in_progress	While in_progress, the Assistant uses the model and tools to perform steps. You can view progress being made by the Run by examining the Run Steps.
completed	The Run successfully completed! You can now view all Messages the Assistant added to the Thread, and all the steps the Run took. You can also continue the conversation by adding more user Messages to the Thread and creating another Run.
requires_action	When using the Function calling tool, the Run will move to a required_action state once the model determines the names and arguments of the functions to be called. You must then run those functions and submit the outputs before the run proceeds. If the outputs are not provided before the expires_at timestamp passes (roughly 10 mins past creation), the run will move to an expired status.
expired	This happens when the function calling outputs were not submitted before expires_at and the run expires. Additionally, if the runs take too long to execute and go beyond the time stated in expires_at, our systems will expire the run.
cancelling	You can attempt to cancel an in_progress run using the Cancel Run endpoint. Once the attempt to cancel succeeds, status of the Run moves to cancelled. Cancellation is attempted but not guaranteed.
cancelled	Run was successfully cancelled.
failed	You can view the reason for the failure by looking at the last_error object in the Run. The timestamp for the failure will be recorded under failed_at.
Polling for updates

In order to keep the status of your run up to date, you will have to periodically retrieve the Run object. You can check the status of the run each time you retrieve the object to determine what your application should do next. We plan to add support for streaming to make this simpler in the near future.

Thread locks

When a Run is in_progress and not in a terminal state, the Thread is locked. This means that:

New Messages cannot be added to the Thread.
New Runs cannot be created on the Thread.
Run steps

Run steps lifecycle - diagram showing possible status transitions

Run step statuses have the same meaning as Run statuses.

Most of the interesting detail in the Run Step object lives in the step_details field. There can be two types of step details:

message_creation: This Run Step is created when the Assistant creates a Message on the Thread.
tool_calls: This Run Step is created when the Assistant calls a tool. Details around this are covered in the relevant sections of the Tools guide.
Data access guidance
Currently, assistants, threads, messages, and files created via the API are scoped to the entire organization. As such, any person with API key access to the organization is able to read or write assistants, threads, messages, and files in the organization.

We strongly recommend the following data access controls:

Implement authorization. Before performing reads or writes on assistants, threads, messages, and files, ensure that the end-user is authorized to do so. For example, store in your database the object IDs that the end-user has access to, and check it before fetching the object ID with the API.
Restrict API key access. Carefully consider who in your organization should have API keys and periodically audit this list. API keys enable a wide range of operations including reading and modifying sensitive information, such as messages and files.
Create separate accounts. Consider creating separate accounts / organizations for different applications in order to isolate data across multiple applications.
Limitations
During this beta, there are several known limitations we are looking to address in the coming weeks and months. We will publish a changelog on this page when we add support for additional functionality.









## Tools Beta
Give Assistants access to OpenAI-hosted tools like Code Interpreter and Knowledge Retrieval, or build your own tools using Function calling.

The Assistants API is in beta and we are actively working on adding more functionality. Share your feedback in our Developer Forum!
Code Interpreter
Code Interpreter allows the Assistants API to write and run Python code in a sandboxed execution environment. This tool can process files with diverse data and formatting, and generate files with data and images of graphs. Code Interpreter allows your Assistant to run code iteratively to solve challenging code and math problems. When your Assistant writes code that fails to run, it can iterate on this code by attempting to run different code until the code execution succeeds.

Enabling Code Interpreter
Pass the code_interpreterin the tools parameter of the Assistant object to enable Code Interpreter:

```python
assistant = client.beta.assistants.create(
  instructions="You are a personal math tutor. When asked a math question, write and run code to answer the question.",
  model="gpt-4-1106-preview",
  tools=[{"type": "code_interpreter"}]
)
```
The model then decides when to invoke Code Interpreter in a Run based on the nature of the user request. This behavior can be promoted by prompting in the Assistant's instructions (e.g., “write code to solve this problem”).

Passing files to Code Interpreter
Code Interpreter can parse data from files. This is useful when you want to provide a large volume of data to the Assistant or allow your users to upload their own files for analysis.

Files that are passed at the Assistant level are accessible by all Runs with this Assistant:

```python
# Upload a file with an "assistants" purpose
file = client.files.create(
  file=open("speech.py", "rb"),
  purpose='assistants'
)

# Create an assistant using the file ID
assistant = client.beta.assistants.create(
  instructions="You are a personal math tutor. When asked a math question, write and run code to answer the question.",
  model="gpt-4-1106-preview",
  tools=[{"type": "code_interpreter"}],
  file_ids=[file.id]
)
```
Files can also be passed at the Thread level. These files are only accessible in the specific Thread. Upload the File using the File upload endpoint and then pass the File ID as part of the Message creation request:

```python
thread = client.beta.threads.create(
  messages=[
    {
      "role": "user",
      "content": "I need to solve the equation `3x + 11 = 14`. Can you help me?",
      "file_ids": [file.id]
    }
  ]
)
```
Files have a maximum size of 512 MB. Code Interpreter supports a variety of file formats including .csv, .pdf, .json and many more. More details on the file extensions (and their corresponding MIME-types) supported can be found in the Supported files section below.

Reading images and files generated by Code Interpreter
Code Interpreter in the API also outputs files, such as generating image diagrams, CSVs, and PDFs. There are two types of files that are generated:

Images
Data files (e.g. a csv file with data generated by the Assistant)
When Code Interpreter generates an image, you can look up and download this file in the file_id field of the Assistant Message response:

```json
{
    "id": "msg_OHGpsFRGFYmz69MM1u8KYCwf",
    "object": "thread.message",
    "created_at": 1698964262,
    "thread_id": "thread_uqorHcTs46BZhYMyPn6Mg5gW",
    "role": "assistant",
    "content": [
    {
      "type": "image_file",
      "image_file": {
        "file_id": "file-WsgZPYWAauPuW4uvcgNUGcb"
      }
    }
  ]
  # ...
}
```
The file content can then be downloaded by passing the file ID to the Files API:

```python
content = client.files.retrieve_content(file.id)
```
When Code Interpreter references a file path (e.g., ”Download this csv file”), file paths are listed as annotations. You can convert these annotations into links to download the file:

```json
{
  "id": "msg_3jyIh3DgunZSNMCOORflDyih",
  "object": "thread.message",
  "created_at": 1699073585,
  "thread_id": "thread_ZRvNTPOoYVGssUZr3G8cRRzE",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": {
        "value": "The rows of the CSV file have been shuffled and saved to a new CSV file. You can download the shuffled CSV file from the following link:\n\n[Download Shuffled CSV File](sandbox:/mnt/data/shuffled_file.csv)",
        "annotations": [
          {
            "type": "file_path",
            "text": "sandbox:/mnt/data/shuffled_file.csv",
            "start_index": 167,
            "end_index": 202,
            "file_path": {
              "file_id": "file-oSgJAzAnnQkVB3u7yCoE9CBe"
            }
          }
          ...
```
Input and output logs of Code Interpreter
By listing the steps of a Run that called Code Interpreter, you can inspect the code input and outputs logs of Code Interpreter:

```python
run_steps = client.beta.threads.runs.steps.list(
  thread_id=thread.id,
  run_id=run.id
)
{
  "object": "list",
  "data": [
    {
      "id": "step_DQfPq3JPu8hRKW0ctAraWC9s",
      "object": "assistant.run.step",
      "type": "tool_calls",
      "run_id": "run_kme4a442kme4a442",
      "thread_id": "thread_34p0sfdas0823smfv",
      "status": "completed",
      "step_details": {
        "type": "tool_calls",
        "tool_calls": [
          {
            "type": "code",
            "code": {
              "input": "# Calculating 2 + 2\nresult = 2 + 2\nresult",
              "outputs": [
                {
                  "type": "logs",
                  "logs": "4"
                }
                        ...
 }
```
Knowledge Retrieval
Retrieval augments the Assistant with knowledge from outside its model, such as proprietary product information or documents provided by your users. Once a file is uploaded and passed to the Assistant, OpenAI will automatically chunk your documents, index and store the embeddings, and implement vector search to retrieve relevant content to answer user queries.

Enabling Retrieval
Pass the retrieval in the tools parameter of the Assistant to enable Retrieval:

```python
assistant = client.beta.assistants.create(
  instructions="You are a customer support chatbot. Use your knowledge base to best respond to customer queries.",
  model="gpt-4-1106-preview",
  tools=[{"type": "retrieval"}]
)
```
How it works
The model then decides when to retrieve content based on the user Messages. The Assistants API automatically chooses between two retrieval techniques:

it either passes the file content in the prompt for short documents, or
performs a vector search for longer documents
Retrieval currently optimizes for quality by adding all relevant content to the context of model calls. We plan to introduce other retrieval strategies to enable developers to choose a different tradeoff between retrieval quality and model usage cost.

Uploading files for retrieval
Similar to Code Interpreter, files can be passed at the Assistant-level or at the Thread-level

```python
# Upload a file with an "assistants" purpose
file = client.files.create(
  file=open("knowledge.pdf", "rb"),
  purpose='assistants'
)

# Add the file to the assistant
assistant = client.beta.assistants.create(
  instructions="You are a customer support chatbot. Use your knowledge base to best respond to customer queries.",
  model="gpt-4-1106-preview",
  tools=[{"type": "retrieval"}],
  file_ids=[file.id]
)
```
Files can also be added to a Message in a Thread. These files are only accessible within this specific thread. After having uploaded a file, you can pass the ID of this File when creating the Message:

```python
message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content="I can't find in the PDF manual how to turn off this device.",
  file_ids=[file.id]
)
```
Maximum file size is 512MB. Retrieval supports a variety of file formats including .pdf, .md, .docx and many more. More details on the file extensions (and their corresponding MIME-types) supported can be found in the Supported files section below.

Deleting files
To remove a file from the assistant, you can detach the file from the assistant:

```python
file_deletion_status = client.beta.assistants.files.delete(
  assistant_id=assistant.id,
  file_id=file.id
)
```
Detaching the file from the assistant removes the file from the retrieval index as well.

File citations
When Code Interpreter outputs file paths in a Message, you can convert them to corresponding file downloads using the annotations field. See the Annotations section for an example of how to do this.

```json
{
    "id": "msg_3jyIh3DgunZSNMCOORflDyih",
    "object": "thread.message",
    "created_at": 1699073585,
    "thread_id": "thread_ZRvNTPOoYVGssUZr3G8cRRzE",
    "role": "assistant",
    "content": [
      {
        "type": "text",
        "text": {
          "value": "The rows of the CSV file have been shuffled and saved to a new CSV file. You can download the shuffled CSV file from the following link:\n\n[Download Shuffled CSV File](sandbox:/mnt/data/shuffled_file.csv)",
          "annotations": [
            {
              "type": "file_path",
              "text": "sandbox:/mnt/data/shuffled_file.csv",
              "start_index": 167,
              "end_index": 202,
              "file_path": {
                "file_id": "file-oSgJAzAnnQkVB3u7yCoE9CBe"
              }
            }
          ]
        }
      }
    ],
    "file_ids": [
      "file-oSgJAzAnnQkVB3u7yCoE9CBe"
    ],
        ...
  },
```
Function calling
Similar to the Chat Completions API, the Assistants API supports function calling. Function calling allows you to describe functions to the Assistants and have it intelligently return the functions that need to be called along with their arguments. The Assistants API will pause execution during a Run when it invokes functions, and you can supply the results of the function call back to continue the Run execution.

Defining functions
First, define your functions when creating an Assistant:

```python
assistant = client.beta.assistants.create(
  instructions="You are a weather bot. Use the provided functions to answer questions.",
  model="gpt-4-1106-preview",
  tools=[{
      "type": "function",
    "function": {
      "name": "getCurrentWeather",
      "description": "Get the weather in location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {"type": "string", "description": "The city and state e.g. San Francisco, CA"},
          "unit": {"type": "string", "enum": ["c", "f"]}
        },
        "required": ["location"]
      }
    }
  }, {
    "type": "function",
    "function": {
      "name": "getNickname",
      "description": "Get the nickname of a city",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {"type": "string", "description": "The city and state e.g. San Francisco, CA"},
        },
        "required": ["location"]
      }
    } 
  }]
)
```
Reading the functions called by the Assistant
When you initiate a Run with a user Message that triggers the function, the Run will enter a requires_action status. The model can provide multiple functions to call at once via the parallel function calling feature:

```json
{
  "id": "run_3HV7rrQsagiqZmYynKwEdcxS",
  "object": "thread.run",
  "assistant_id": "asst_rEEOF3OGMan2ChvEALwTQakP",
  "thread_id": "thread_dXgWKGf8Cb7md8p0wKiMDGKc",
  "status": "requires_action",
  "required_action": {
    "type": "submit_tool_outputs",
    "submit_tool_outputs": {
      "tool_calls": [
        {
          "tool_call_id": "call_Vt5AqcWr8QsRTNGv4cDIpsmA",
          "type": "function",
          "function": {
            "name": "getCurrentWeather",
            "arguments": "{\"location\":\"San Francisco\"}"
          }
        },
        {
          "tool_call_id": "call_45y0df8230430n34f8saa",
          "type": "function",
          "function": {
            "name": "getNickname",
            "arguments": "{\"location\":\"Los Angeles\"}"
          }
        }
      ]
    }
  },
...
```
Submitting functions outputs
You can then complete the Run by submitting the output from the function(s) you call. Pass the tool_call_id referenced in the required_action object above to match output to each function call.

```python
run = client.beta.threads.runs.submit_tool_outputs(
  thread_id=thread.id,
  run_id=run.id,
  tool_outputs=[
      {
        "tool_call_id": call_ids[0],
        "output": "22C",
      },
      {
        "tool_call_id": call_ids[1],
        "output": "LA",
      },
    ]
)
```
After submitting outputs, the run will enter the queued state before it continues it’s execution.

Supported files
For text/ MIME types, the encoding must be one of utf-8, utf-16, or ascii.

FILE FORMAT	MIME TYPE	CODE INTERPRETER	RETRIEVAL
.c	text/x-c		
.cpp	text/x-c++		
.csv	application/csv		
.docx	application/vnd.openxmlformats-officedocument.wordprocessingml.document		
.html	text/html		
.java	text/x-java		
.json	application/json		
.md	text/markdown		
.pdf	application/pdf		
.php	text/x-php		
.pptx	application/vnd.openxmlformats-officedocument.presentationml.presentation		
.py	text/x-python		
.py	text/x-script.python		
.rb	text/x-ruby		
.tex	text/x-tex		
.txt	text/plain		
.css	text/css		
.jpeg	image/jpeg		
.jpg	image/jpeg		
.js	text/javascript		
.gif	image/gif		
.png	image/png		
.tar	application/x-tar		
.ts	application/typescript		
.xlsx	application/vnd.openxmlformats-officedocument.spreadsheetml.sheet		
.xml	application/xml or "text/xml"		
.zip	application/zip		
Was this page useful?
