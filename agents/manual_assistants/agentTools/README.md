# Functions

[OpenAI functions](https://platform.openai.com/docs/guides/gpt/function-calling) for all models that support it.

Multiple functions may be attached to an agent.

The example configuration below assumes you want to add a new function called `test_function`.

Tools are assigned to an agent by including them in the `tools` property.

```yaml
- name: "Boss" 
  tools: ["test_function"]
```

## Creating functions.

Functions are created as callable Python classes, that inherit from the base `Function` class.

The class name must be the camel-cased version of the snake-cased function name, so `test_function` becomes `TestFunction`.

There is one required method to implement, `__call__`, its return value can techincally be anything, including no return,
but is generally a dict necessary to return a tool call.

```python
from function import Function

class TestFunction(Function):
    def __call__(self, word: str, repeats: int, enclose_with: str = '') -> dict:
        """
        Repeat the provided word a number of times.

        :param word: The word to repeat.
        :type content: str
        :param repeats: The number of times to repeat the word.
        :type repeats: int
        :param enclose_with: Optional string to enclose the final content.
        :type enclose_with: str, optional
        :return: A dictionary containing the repeated content.
        :rtype: dict
        """
        action_id = self.execution.actionId
        try:
            repeated_content = " ".join([word] * repeats)
            enclosed_content = f"{enclose_with}{repeated_content}{enclose_with}"
            output = {
                "tool_call_id": action_id,
                'output': enclosed_content,
            }
            output = {
            }
        except Exception as e:
            output = {
                "tool_call_id": action_id,
                'output': f"ERROR: {str(e)}",
            }
        return output
```

The file should be named `[function_name].py`, e.g. `test_function.py`, and be placed in the `agentTools/functions` directory.

## Providing the function definition

In the example above, notice both the type hints in the function signature (e.g. `word: str`),
and the reStructured text documentation of the method arguments.
This is the default method for providing the function definition to the OpenAI API.

Alternatively, you may provide the function definition by creating a `[function_name].config.yaml` file in the same location as the
`[function_name].py` file, e.g. `test_function.config.yaml` -- if provided, its contents will be used instead of the default
method.

Finally, for full control, you may override the `get_config()` method of the base `Function` class, and return
a dictionary of the function definition. This approach allows passing much more robust function definitions to the LLM.

## Support for Langchain tools

[Langchain](https://docs.langchain.com) has many useful [tools](https://python.langchain.com/docs/modules/agents/tools/)
that can be used in function calls.

To use a Langchain tool as function:

1. Find the name of the tool class, e.g. `MoveFileTool` or `ShellTool`.
2. Prefix that class name with `Langchain-`
3. Add it to the `functions` list for the agent:

```yaml
- name: "Boss" 
  tools: ["Langchain-ShellTool"]
```
