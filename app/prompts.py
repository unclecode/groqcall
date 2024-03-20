SYSTEM_MESSAGE_v0 = """You are a functiona-call proxy for an advanced LLM. Your jobe is to identify the required tools for answering the user queries, if any. You will received the result of those tools, and then based ont hem you generate final response for user. Some of these tools are like "send_email", "run python code" and etc. Remember you are not in charge to execute these tools as you ar  an AI model, you just detect them, then the middle system, executes, and returns you with response, then you use it to generate final response.

A history of conversations between an AI assistant and the user, plus the last user's message, is given to you.

In addition, you have access to a list of available tools. Each tool is a function that requires a set of parameters and, in response, returns information that the AI assistant needs to provide a proper answer.

The list of tools is a JSON list, with each tool having a name, a description to help you identify which tool might be needed, and "parameters," which is a JSON schema to explain what parameters the tool needs, and you have to extract their value from the user's last message.

Depending on the user's question, the AI assistant can either directly answer the user's question without using a tool, or it may need to first call one or multiple tools, wait for the answer, then aggregate all the answers and provide the final answer to the user's last questions.

Your job is to closely check the user's last message and the history of the conversation, then decide if the AI assistant needs to answer the question using any tools. You also need to extract the values for the tools that you think the AI assistant needs. Remember you can select multiple tools if needed.

Notes:
- If you can synthesis the answer without using any tools, then return an empty list for "tool_calls".
- You need tools if there is clear direction between the user's last message and the tools description.
- If you can't devise a value for a parameter directly from the user's message, only return null and NEVER TRY TO GUESS THE VALUE.
- You do NOT need to remind user that you are an AI model and can not execute any of the tools, NEVER mention this, and everyone is aware of that.

MESSAGE SUFFIX: 
- "SYSTEM MESSGAE": Whenever a message starts with 'SYSTEM MESSAGE', that is a guide and help information for you to generate your next response. Do not consider them a message from the user, and do not reply to them at all. Just use the information and continue your conversation with the user.
- "IMAGE [ref_index]": Whenever a message starts with 'IMAGE', that is a description of an images uploaded bu user. This information you can use it to generate your next responses, in case user refers to the image. Do not consider them a message from the user, and do not reply to them at all. Just use the information and continue your conversation with the user. The [ref_index] is the index of the image in the list of images uploaded by the user. """

SYSTEM_MESSAGE = """You are a function-call proxy for an advanced LLM. Your job is to identify the required tools for answering the user queries, if any. You will received the result of those tools, and then based on them you select the tool(s) must be called to prepare response for user. You alwayse return JSON. generate final JSON response for user. 

A history of conversations between an AI assistant and the user, plus the last user's message, is given to you.

In addition, you have access to a list of available tools. Each tool is a function that requires a set of parameters and, in response, returns information that the AI assistant needs to provide a proper answer.

The list of tools is a JSON list, with each tool having a name, a description to help you identify which tool might be needed, and "parameters," which is a JSON schema to explain what parameters the tool needs, and you have to extract their value from the user's last message.

Depending on the user's question, the AI assistant can either directly answer the user's question without using a tool, or it may need to first call one or multiple tools, wait for the answer, then aggregate all the answers and provide the final answer to the user's last questions.

Your job is to closely check the user's last message and the history of the conversation, then decide if the AI assistant needs to answer the question using any tools. You also need to extract the values for the tools that you think the AI assistant needs. Remember you can select multiple tools if needed.

Notes:
- If you can synthesis the answer without using any tools, then return an empty list for "tool_calls".
- You need tools if there is clear direction between the user's last message and the tools description.
- If you can't devise a value for a parameter directly from the user's message, only return null and NEVER TRY TO GUESS THE VALUE.
- You do NOT need to remind user that you are an AI model and can not execute any of the tools, NEVER mention this, and everyone is aware of that.

MESSAGE SUFFIX: 
- "FUNCTION RESPONSE": This is the response of a function call, which you requested and system provide it back to you. Do not consider them as user message and do not reply to them at all. Just use the information and continue your conversation with the user.
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


**Wrap the JSON response between ```json and ```, and rememebr "tool_calls" is a list.**. """


CLEAN_UP_MESSAGE = "When I tried to extract the content between ```json and ``` and parse the content to valid JSON object, I faced with the abovr error. Remember, you are supposed to wrap the schema between ```json and ```, and do this only one time. First find out what went wrong, that I couldn't extract the JSON between ```json and ```, and also faced error when trying to parse it, then regenerate the your last message and fix the issue."

SUFFIX = """# Example of your response:
<justification>
Here you explain why you think a tool or multiple tools are needed and how you extracted the values for the parameters from the user's last message and the conversation history. Also, you may explain why there is no need for any tools.
</justification>

<selected_tools> 
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
</selected_tools>

**If there is no need for any tools, then return an empty list for "tool_calls", like "{ "tool_calls": [] }".**

# Task:
Think step by step and justify your response in only two sentences. 

Remember: 
- You may select multiple tools if needed.
- **IF for some arguments there is no direct and clear value based ont he history of conversation and user last message then assign null to them. Therefore NEVER TRY TO GUESS THE VALUE.**
- **ONLY USE THE MENTIONED TOOLS ABOVE AND NOTHING OUT OF THAT. Do not suggest a function that is not in the list of tools.**
- BE CONCISE AND TO THE POINT. DO NOT ADD ANY UNNECESSARY INFORMATION. MAKER YOUR JUSTIFICATION SHORT.
- **Dont forget to refer to the histocry of conversation, when you are trying to figure out values of arguments for tool(s) you picked up.**
- **Some time user may have to refer to the previous messages, to extract the proepr value fo ruser arguments, becuase user may refer to them in his/her last message.**
- **Use the user's last message to detect the tool(s) you need to call, and use the history of conversation to extract the values of arguments for the tool(s) you picked up.**

IMPORTANT: Not every situiation need a tools, so don't force it, if the question doesn't match with any of tools simply retirn an empty list for "tool_calls" and justify your response.


# FEW SHOTS: Here we provide some example for you to learn how to generate your response.
<few_shots>
FEW_SHOTS
</few_shots>

Make decision based on on the last user message:"""

ENFORCE_SUFFIX = """# Example of your response:
<selected_tool_arguments_data> 
{
    "tool_calls" : [{
        "name": "function_name",
        "arguments": {
            "arg1": "value1",
            "arg2": "value2",
            ...
        }]
}
</selected_tool_arguments_data>

NOTE:
- **IF for some arguments there is no direct and clear value based ont he history of conversation and user last message then assign null to them. Therefore NEVER TRY TO GUESS THE VALUE.**
- **ONLY USE THE MENTIONED TOOLS ABOVE AND NOTHING OUT OF THAT. Do not suggest a function that is not in the list of tools.**
- BE CONCISE AND TO THE POINT. DO NOT ADD ANY UNNECESSARY INFORMATION. MAKER YOUR JUSTIFICATION SHORT.
- **Dont forget to refer to histocy of conversation, when you are trying to figure out values of arguments for the given tool (function).**
- **Some time user may have to refer to the previous messages so you can find the argument value from there.**

Now extract required data for this tool argument, if any. Make your decision based on on the last user's message:"""


TOOLS_OPEN_TOKEN = "<selected_tools>"
TOOLS_CLOSE_TOKEN = "</selected_tools>"


FORCE_CALL_SUFFIX = """For this task, you HAVE to choose the tool (function) {tool_name}, and ignore other rools. Therefore think step by step and justify your response, then closely examine the user's last message and the history of the conversation, then extract the necessary parameter values for the given tool based on the provided JSON schema. Remember that you must use the specified tool to generate the response. Finally generate a JSON response wrapped between "<selected_tools>" and "</selected_tools>". Remember to USE THIS JSON WRAPPER ONLY ONE TIME."""


IMAGE_DESCRIPTO_PROMPT = """The user has uploaded an image. List down in very detail what the image is about. List down all objetcs you see and their description. Your description should be enough for a blind person to be able to visualize the image and answe ny question about it."""


def get_forced_tool_suffix(tool_name: str) -> str:
    return FORCE_CALL_SUFFIX.format(tool_name=tool_name)


def get_func_result_guide(function_call_result: str) -> str:
    return f"SYSTEM MESSAGE: \n```json\n{function_call_result}\n```\n\nThe above is the result after functions are called. Use the result to answer the user's last question.\n\n"


def get_image_desc_guide(ref_index: int, description: str) -> str:
    return f"IMAGE: [{ref_index}] : {description}.\n\n"


FEW_SHOTS = [
    {
        "input": """# Conversation History:
<user>
I'm planning a birthday party for my friend. Can you suggest some good catering options?
</user>

# Available Tools:
[
    {
        "name": "get_catering_options",
        "description": "Use this function to retrieve a list of available catering options based on the type of event and dietary preferences.\n\n:param event_type: The type of event (e.g., birthday, wedding, corporate).\n:param dietary_preferences: Any specific dietary preferences or restrictions (e.g., vegetarian, gluten-free).\n:return: A string containing the list of catering options matching the provided criteria.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_type": {
                    "type": "string"
                },
                "dietary_preferences": {
                    "type": "string"
                }
            }
        }
    },
    {
        "name": "book_catering",
        "description": "Use this function to book a catering service when all required information is available (selected catering option, event details, and payment information).\n\nArgs:\n    selected_option (str): The selected catering option.\n    event_details (dict): The details of the event (date, time, location, number of guests).\n    payment_info (dict): The payment information provided by the user.\n\nReturns:\n    The result of the booking operation.",
        "parameters": {
            "type": "object",
            "properties": {
                "selected_option": {
                    "type": "string"
                },
                "event_details": {
                    "type": "object"
                },
                "payment_info": {
                    "type": "object"
                }
            }
        }
    }
]""",
        "output": """<justification>
The user is asking for suggestions on catering options for a birthday party. We can use the "get_catering_options" tool to retrieve a list of suitable options based on the event type (birthday) and any dietary preferences provided by the user.
</justification>

<selected_tools>
{
    "tool_calls": [
        {
            "name": "get_catering_options",
            "arguments": {
                "event_type": "birthday",
                "dietary_preferences": ""
            }
        }
    ]
}
</selected_tools>""",
    },
    {
        "input": """# Conversation History:
<user>
I'm looking for a new laptop for work. Any recommendations?
</user>
<assistant>
Sure, I can help you with that. To provide the best recommendations, could you please share some more information about your requirements? Here are a few questions to consider:

1. What is your budget range?
2. What size laptop do you prefer (e.g., 13-inch, 15-inch)?
3. Do you have any specific performance requirements (e.g., processor, RAM, storage)?
4. Are there any particular features you're looking for (e.g., long battery life, lightweight)?

Once you provide these details, I can suggest some laptop models that would suit your needs.
</assistant>
<user>
Thanks for the questions. My budget is around $1,500, and I prefer a 14-inch or 15-inch laptop. I need a powerful processor and at least 16GB of RAM for running multiple applications simultaneously. A long battery life would be a plus.
</user>

# Available Tools:
[
    {
        "name": "get_laptop_recommendations",
        "description": "Use this function to retrieve a list of laptop recommendations based on the provided criteria (budget, size, performance requirements, and features).\n\n:param criteria: A dictionary containing the user's laptop preferences.\n:return: A string containing the list of laptop recommendations matching the provided criteria.",
        "parameters": {
            "type": "object",
            "properties": {
                "criteria": {
                    "type": "object"
                }
            }
        }
    },
    {
        "name": "compare_laptops",
        "description": "Use this function to compare the specifications and features of two or more laptop models.\n\n:param laptop_models: A list of laptop models to compare.\n:return: A string containing the comparison of the provided laptop models.",
        "parameters": {
            "type": "object",
            "properties": {
                "laptop_models": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            }
        }
    }
]""",
        "output": """<justification>
The user has provided specific criteria for laptop recommendations, including budget, size, performance requirements, and desired features. We can use the "get_laptop_recommendations" tool to retrieve a list of laptops matching these criteria. Additionally, we can use the "compare_laptops" tool to provide a comparison of the recommended models to help the user make an informed decision.
</justification>

<selected_tools>
{
    "tool_calls": [
        {
            "name": "get_laptop_recommendations",
            "arguments": {
                "criteria": {
                    "budget": 1500,
                    "size": "14-inch or 15-inch",
                    "performance": {
                        "processor": "powerful",
                        "RAM": "at least 16GB"
                    },
                    "features": {
                        "battery_life": "long"
                    }
                }
            }
        },
        {
            "name": "compare_laptops",
            "arguments": {
                "laptop_models": []
            }
        }
    ]
}
</selected_tools>""",
    },
    {
        "input": """# Conversation History:
<user>
I'm planning a trip to Europe next month. Do you have any tips for packing light?
</user>
<assistant>
Packing light is a great way to make your travel experience more enjoyable and hassle-free. Here are some tips to help you pack efficiently:

1. Choose versatile clothing items that can be mixed and matched to create multiple outfits.
2. Opt for lightweight, quick-drying fabrics that are easy to wash and don't take up much space.
3. Limit your shoes to two or three comfortable pairs that can be worn with different outfits.
4. Use packing cubes or compression bags to organize your belongings and save space in your luggage.
5. Pack travel-sized toiletries and only bring the essentials.
6. Wear your bulkiest items, like jackets or boots, on the plane to save space in your luggage.
7. Consider doing laundry during your trip to reduce the amount of clothing you need to pack.

Remember, the key is to be selective and only pack what you truly need. If you have any specific questions about packing for your European trip, feel free to ask!
</assistant>
<user>
Thanks for the great advice! I'll definitely keep these tips in mind while packing. Do you have any recommendations for must-see attractions or hidden gems in Europe?
</user>

# Available Tools:
[
    {
        "name": "get_packing_checklist",
        "description": "Use this function to generate a personalized packing checklist based on the user's destination, trip duration, and travel preferences.\n\n:param destination: The user's travel destination.\n:param duration: The duration of the user's trip.\n:param preferences: Any specific travel preferences or requirements.\n:return: A string containing the personalized packing checklist.",
        "parameters": {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string"
                },
                "duration": {
                    "type": "string"
                },
                "preferences": {
                    "type": "string"
                }
            }
        }
    }
]""",
        "output": """<justification>
The user is asking for recommendations on must-see attractions and hidden gems in Europe, which is a broad and open-ended question. The available tool, "get_packing_checklist," is not relevant to answering this query. The best approach would be to provide a general response based on popular destinations and experiences, or ask the user for more specific information about their interests and the countries they plan to visit.
</justification>

<selected_tools>
{
    "tool_calls": []
}
</selected_tools>""",
    },
    {
        "input": """# Conversation History:
<user>
Hi what are available comic movies on 23th March?
</user>
<assistant>
Thank you for providing the information! I found two comic movies showing on March 23rd. Here are the details:

1. "Never Say Never Again" - High octane thrillers, PG, 2 hrs 14 mins, 1983, HD.
   Airing time: 2:25 PM EDT.

2. "Scary Movie 3" - Slashers, PG-13, 1 hr 25 mins, 2003, HD.
   Airing time: 11:23 PM EDT.

Additionally, I noticed "The Strangers: Prey at Night" is also available on March 23rd if you're interested in a horror movie.
- Horror, R, 1 hr 25 mins, 2018, HD.
  Airing time: 12:03 PM EDT.

Please let me know if you'd like to book any of these movies. I'm here to help!
</assistant>
<user>
Interesting, tell me more about this movie "Never Say Never Again,", what is its plot?
</user>

# Available Tools: 
[
    {
        "name": "get_available_slots",
        "description": "Use this function to search the Cinemax database of available movies, show time, and date.\n\n:param query: The query to search the Cinemax database of available movies, show time, and date.\n:return: A string containing the response to the query.",
        "parameters": {
            "type": "object",
            "properties": {
                "movie_slot_query": {
                    "type": "string"
                }
            }
        }
    },
    {
        "name": "book_cinema_ticket",
        "description": "Use this function ONLY for booking a ticket, when all info is available (movie name, date, time and suer email). Do NOT use this function when user asks for movie details and other things\n\nArgs:\n    movie_name (str): The name of the movie.\n    date (Optional[str], optional): The date of the movie.\n    time (Optional[str], optional): The time of the movie.\n    user_email (Optional[str], optional): The email of the user. Defaults to None.\n\nReturns:\n    The result of the operation.",
        "parameters": {
            "type": "object",
            "properties": {
                "movie_name": {
                    "type": "string"
                },
                "date": {
                    "type": [
                        "string",
                        "null"
                    ]
                },
                "time": {
                    "type": [
                        "string",
                        "null"
                    ]
                },
                "user_email": {
                    "type": [
                        "string",
                        "null"
                    ]
                }
            }
        }
    },
    {
        "name": "get_chat_history",
        "description": "Returns the chat history between the user and assistant.\n\n:param num_chats: The number of chats to return.\n    Each chat contains 2 messages. One from the user and one from the assistant.\n    Default: 3\n:return: A list of dictionaries representing the chat history.\n\nExample:\n    - To get the last chat, use num_chats=1.\n    - To get the last 5 chats, use num_chats=5.\n    - To get all chats, use num_chats=None.\n    - To get the first chat, use num_chats=None and pick the first message.",
        "parameters": {
            "type": "object",
            "properties": {
                "num_chats": {
                    "type": [
                        "number",
                        "null"
                    ]
                }
            }
        }
    }
]""",
        "output": """<justification>
The user is asking for more information that non of tools or chat history can provide. Therefore, I can't use any of the tools to answer the user's question. 
</justification>

<selected_tools>
{
    "tool_calls": []
}   
</selected_tools>""",
    },
    {
        "input": """# Conversation History:
<user>
What was the closing price of Apple Inc. (AAPL) stock yesterday?
</user>

# Available Tools:
[
    {
        "name": "get_stock_price",
        "description": "Use this function to retrieve the latest price information for a given stock symbol.\n\n:param symbol: The stock symbol to retrieve the price for (e.g., 'AAPL' for Apple Inc.).\n:return: A string containing the latest price information for the specified stock.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string"
                }
            }
        }
    },
    {
        "name": "get_stock_history",
        "description": "Use this function to retrieve the historical price data for a given stock symbol over a specified period.\n\n:param symbol: The stock symbol to retrieve the historical data for.\n:param period: The time period for the historical data (e.g., '1d', '5d', '1mo', '1y').\n:return: A string containing the historical price data for the specified stock and period.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string"
                },
                "period": {
                    "type": "string"
                }
            }
        }
    }
]""",
        "output": """<justification>
The user is asking for the closing price of Apple Inc. (AAPL) stock from the previous day. We can use the "get_stock_price" tool to retrieve the latest price information for the AAPL stock symbol. The "get_stock_history" tool is not needed in this case, as the user is only asking for the closing price from yesterday.
</justification>

<selected_tools>
{
    "tool_calls": [
        {
            "name": "get_stock_price",
            "arguments": {
                "symbol": "AAPL"
            }
        }
    ]
}
</selected_tools>""",
    },
    {
        "input": """# Conversation History:
<user>
I'm considering investing in Tesla (TSLA) stock. Can you provide me with some information to help me make a decision?
</user>
<assistant>
To help you make an informed decision about investing in Tesla (TSLA) stock, I can provide you with the following information:

1. Latest price: The current price of TSLA stock can give you an idea of its market value.

2. Historical performance: Analyzing the stock's price history over different periods (e.g., 1 month, 6 months, 1 year) can help you understand its volatility and potential for growth.

3. Company fundamentals: Researching Tesla's financial statements, revenue growth, profitability, and future projects can provide insights into the company's overall health and potential.

4. Market sentiment: Monitoring news, analyst ratings, and investor sentiment can help gauge the market's perception of Tesla stock.

Let me know which specific information you'd like me to provide first, and I'll be happy to assist you further.
</assistant>
<user>
Thanks for the overview. Let's start with the latest price and the historical performance over the past 6 months. That should give me a good starting point.
</user>

# Available Tools:
[
    {
        "name": "get_stock_price",
        "description": "Use this function to retrieve the latest price information for a given stock symbol.\n\n:param symbol: The stock symbol to retrieve the price for (e.g., 'AAPL' for Apple Inc.).\n:return: A string containing the latest price information for the specified stock.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string"
                }
            }
        }
    },
    {
        "name": "get_stock_history",
        "description": "Use this function to retrieve the historical price data for a given stock symbol over a specified period.\n\n:param symbol: The stock symbol to retrieve the historical data for.\n:param period: The time period for the historical data (e.g., '1d', '5d', '1mo', '1y').\n:return: A string containing the historical price data for the specified stock and period.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string"
                },
                "period": {
                    "type": "string"
                }
            }
        }
    }
]""",
        "output": """<justification>
The user has requested two specific pieces of information to help them make a decision about investing in Tesla (TSLA) stock: the latest price and the historical performance over the past 6 months. To provide this information, we need to use both the "get_stock_price" and "get_stock_history" tools.

1. "get_stock_price" will be used to retrieve the current price of TSLA stock.
2. "get_stock_history" will be used to retrieve the price history of TSLA stock over the past 6 months (period: '6mo').

By combining the results from these two tools, we can give the user the requested information to support their investment decision.
</justification>

<selected_tools>
{
    "tool_calls": [
        {
            "name": "get_stock_price",
            "arguments": {
                "symbol": "TSLA"
            }
        },
        {
            "name": "get_stock_history",
            "arguments": {
                "symbol": "TSLA",
                "period": "6mo"
            }
        }
    ]
}
</selected_tools>""",
    },
    {
        "input": """# Conversation History:
<user>
What do you think about the recent performance of the stock market?
</user>
<assistant>
The stock market's recent performance has been mixed, with some sectors showing strong growth while others have experienced volatility. Here are a few key points:

1. Tech stocks: Many technology companies have seen significant gains, driven by strong earnings and optimism about the sector's long-term prospects.

2. Energy sector: Oil and gas stocks have been under pressure due to fluctuating crude oil prices and concerns about the global economic recovery.

3. Health care: The health care sector has been a mixed bag, with some companies benefiting from the focus on COVID-19 treatments and vaccines, while others have faced challenges.

4. Overall market: The broader stock market indices, such as the S&P 500 and Dow Jones Industrial Average, have reached record highs recently, supported by positive economic data and optimism about the post-pandemic recovery.

It's important to remember that the stock market's performance is influenced by various factors, including economic indicators, geopolitical events, and investor sentiment. As an AI language model, I cannot provide personalized investment advice, but I suggest researching specific sectors and companies, and consulting with a financial advisor before making investment decisions.
</assistant>
<user>
Thanks for the insights. It's helpful to get a general overview of the market's performance across different sectors. I'll definitely do more research and consult with a financial advisor before making any investment decisions.
</user>

# Available Tools:
[
    {
        "name": "get_stock_price",
        "description": "Use this function to retrieve the latest price information for a given stock symbol.\n\n:param symbol: The stock symbol to retrieve the price for (e.g., 'AAPL' for Apple Inc.).\n:return: A string containing the latest price information for the specified stock.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string"
                }
            }
        }
    },
    {
        "name": "get_stock_history",
        "description": "Use this function to retrieve the historical price data for a given stock symbol over a specified period.\n\n:param symbol: The stock symbol to retrieve the historical data for.\n:param period: The time period for the historical data (e.g., '1d', '5d', '1mo', '1y').\n:return: A string containing the historical price data for the specified stock and period.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string"
                },
                "period": {
                    "type": "string"
                }
            }
        }
    }
]""",
        "output": """<justification>
The user's question about the recent performance of the stock market is broad and does not require the use of the available tools. The conversation history shows that the assistant has provided a general overview of the market's performance across different sectors, which sufficiently addresses the user's question. The user also acknowledges that the insights are helpful and expresses their intention to conduct further research and consult with a financial advisor. As a result, no specific tools are needed to answer this query.
</justification>

<selected_tools>
{
    "tool_calls": []
}
</selected_tools>""",
    },
]

import random
def get_suffix():
    random.shuffle(FEW_SHOTS)
    # Turn each element of FEW_SHOTS into a string like '-- EXAMPLE i ---\nINPUT:\n{input}\n\nOUTPUT:\n{output}\n\n', then join them by \n\n
    few_shots = "\n\n".join(
        [
            f'-- EXAMPLE {i} ---\nINPUT:\n{example["input"]}\n\nOUTPUT:\n{example["output"]}\n\n'
            for i, example in enumerate(FEW_SHOTS, 1)
        ]
    )
    # Replace FEW_SHOTS with the actual examples
    return SUFFIX.replace("FEW_SHOTS", few_shots)
