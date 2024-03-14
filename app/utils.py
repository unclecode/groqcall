import logging
import os

# To be developed
def create_logger(logger_name: str, log_path: str = ".logs/access.log"):
    log_dir = os.path.dirname(log_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def get_tool_call_response( completion, unresolved_tol_calls, resolved_responses):
    tool_response = {
        "id": "chatcmpl-" + completion.id,
        "object": "chat.completion",
        "created": completion.created,
        "model": completion.model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": unresolved_tol_calls,
                },
                "logprobs": None,
                "finish_reason": "tool_calls",
            }
        ],
        "resolved": resolved_responses,
        "usage": {
            "prompt_tokens": completion.usage.prompt_tokens,
            "completion_tokens": completion.usage.completion_tokens,
            "total_tokens": completion.usage.total_tokens,
        },
        "system_fingerprint": completion.system_fingerprint,
    }    

    return tool_response