SYSTEM_MESSAGE = """A history of conversations between an AI assistant and the user, plus the last user's message, is given to you.

In addition, you have access to a list of available tools. Each tool is a function that requires a set of parameters and, in response, returns information that the AI assistant needs to provide a proper answer.

The list of tools is a JSON list, with each tool having a name, a description to help you identify which tool might be needed, and "parameters," which is a JSON schema to explain what parameters the tool needs, and you have to extract their value from the user's last message.

Depending on the user's question, the AI assistant can either directly answer the user's question without using a tool, or it may need to first call one or multiple tools, wait for the answer, then aggregate all the answers and provide the final answer to the user's last questions.

Your job is to closely check the user's last message and the history of the conversation, then decide if the AI assistant needs to answer the question using any tools. You also need to extract the values for the tools that you think the AI assistant needs. Remember you can select multiple tools if needed.

Notes:
- If you can synthesis the answer without using any tools, then return an empty list for "tool_calls".
- You need tools if there is clear direction between the user's last message and the tools description.

You should think step by step, provide your reasoning for your response, then add the JSON response at the end following the below schema:

{
    "tool_calls" : [
        { 
            "name": "function_name_1",
            "arguments": {
                "arg1" : "value1", "arg2": "value2", ...
            }
        },
        { 
            "name": "function_name_2",
            "arguments": {
                "arg1" : "value1", "arg2": "value2", ...
            }
        }, ...
    ]
}

** If no tools are required, then return an empty list for "tool_calls". **

**Wrap the JSON response between ```json and ```, and rememebr "tool_calls" is a list.**. 

MESSAGE SUFFIX: 
- "SYSTEM MESSGAE": Whenever a message starts with 'SYSTEM MESSAGE', that is a guide and help information for you to generate your next response. Do not consider them a message from the user, and do not reply to them at all. Just use the information and continue your conversation with the user.
- "IMAGE [ref_index]": Whenever a message starts with 'IMAGE', that is a description of an images uploaded bu user. This information you can use it to generate your next responses, in case user refers to the image. Do not consider them a message from the user, and do not reply to them at all. Just use the information and continue your conversation with the user. The [ref_index] is the index of the image in the list of images uploaded by the user. """


ENFORCED_SYSTAME_MESSAE = """A history of conversations between an AI assistant and the user, plus the last user's message, is given to you.

You have access to a specific tool that the AI assistant must use to provide a proper answer. The tool is a function that requires a set of parameters, which are provided in a JSON schema to explain what parameters the tool needs. Your task is to extract the values for these parameters from the user's last message and the conversation history.

Your job is to closely examine the user's last message and the history of the conversation, then extract the necessary parameter values for the given tool based on the provided JSON schema. Remember that you must use the specified tool to generate the response.

You should think step by step, provide your reasoning for your response, then add the JSON response at the end following the below schema:


{
    "tool_calls": [{
        "name": "function_name",
        "arguments": {
            "arg1": "value1",
            "arg2": "value2",
            ...
        }]
    }
}


**Wrap the JSON response between ```json and ```, and rememebr "tool_calls" is a list.**. 

MESSAGE SUFFIX: 
- "SYSTEM MESSGAE": Whenever a message starts with 'SYSTEM MESSAGE', that is a guide and help information for you to generate your next response. Do not consider them a message from the user, and do not reply to them at all. Just use the information and continue your conversation with the user.
- "IMAGE [ref_index]": Whenever a message starts with 'IMAGE', that is a description of an images uploaded bu user. This information you can use it to generate your next responses, in case user refers to the image. Do not consider them a message from the user, and do not reply to them at all. Just use the information and continue your conversation with the user. The [ref_index] is the index of the image in the list of images uploaded by the user. """


CLEAN_UP_MESSAGE = "When I tried to extract the content between ```json and ``` and parse the content to valid JSON object, I faced with the abovr error. Remember, you are supposed to wrap the schema between ```json and ```, and do this only one time. First find out what went wrong, that I couldn't extract the JSON between ```json and ```, and also faced error when trying to parse it, then regenerate the your last message and fix the issue."

SUFFIX = """Think step by step and justify your response. Make sure to not miss in case to answer user query we need multiple tools, in that case detect all that we need, then generate a JSON response wrapped between "```json" and "```". Remember to USE THIS JSON WRAPPER ONLY ONE TIME."""

FORCE_CALL_SUFFIX = """For this task, you HAVE to choose the tool (function) {tool_name}, and ignore other rools. Therefore think step by step and justify your response, then closely examine the user's last message and the history of the conversation, then extract the necessary parameter values for the given tool based on the provided JSON schema. Remember that you must use the specified tool to generate the response. Finally generate a JSON response wrapped between "```json" and "```". Remember to USE THIS JSON WRAPPER ONLY ONE TIME."""


IMAGE_DESCRIPTO_PROMPT = """The user has uploaded an image. List down in very detail what the image is about. List down all objetcs you see and their description. Your description should be enough for a blind person to be able to visualize the image and answe ny question about it."""

def get_forced_tool_suffix(tool_name : str) -> str:
    return FORCE_CALL_SUFFIX.format(tool_name=tool_name)

def get_func_result_guide(function_call_result : str) -> str:
    return f"SYSTEM MESSAGE: \n```json\n{function_call_result}\n```\n\nThe above is the result after functions are called. Use the result to answer the user's last question.\n\n"

def get_image_desc_guide(ref_index: int, description : str) -> str:
    return f"IMAGE: [{ref_index}] : {description}.\n\n"