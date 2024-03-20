import logging
import os
import replicate
import base64
from io import BytesIO


# To be developed
def create_logger(logger_name: str, log_path: str = ".logs/access.log", show_on_shell: bool = False):
    log_dir = os.path.dirname(log_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    if show_on_shell:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        shell_formatter = logging.Formatter(
            "%(levelname)s (%(name)s)   %(message)s"
        )
        stream_handler.setFormatter(shell_formatter)
        logger.addHandler(stream_handler)    
    return logger


def get_tool_call_response(tool_calls_result, unresolved_tol_calls, resolved_responses):
    last_completion = tool_calls_result["last_completion"]
    tool_response = {
        "id": "chatcmpl-" + last_completion.id if last_completion else None,
        "object": "chat.completion",
        "created": last_completion.created if last_completion else None,
        "model": last_completion.model if last_completion else None,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "", # None,
                    "tool_calls": unresolved_tol_calls,
                },
                "logprobs": None,
                "finish_reason": "tool_calls",
            }
        ],
        "resolved": resolved_responses,
        "usage": tool_calls_result["usage"],
        "system_fingerprint": last_completion.system_fingerprint if last_completion else None,
    }
    return tool_response

def describe(prompt: str, image_url_or_base64 : str, **kwargs) -> str:
    logger = create_logger("vision", ".logs/access.log", True)
    try:
        if image_url_or_base64.startswith("data:image/"):
            # If the input is a base64 string
            image_data = base64.b64decode(image_url_or_base64.split(",")[1])
            image_file = BytesIO(image_data)
        else:
            # If the input is a URL
            image_file = image_url_or_base64
        
        model_params = {
            "top_p": 1,
            "max_tokens": 1024,
            "temperature": 0.2
        }
        model_params.update(kwargs)

        logger.info("Running the model")
        output = replicate.run(
            "yorickvp/llava-13b:01359160a4cff57c6b7d4dc625d0019d390c7c46f553714069f114b392f4a726",
            input={
                "image": image_file,
                "prompt": prompt, #"Describe the image in detail.",
                **model_params
            }
        )
        
        description = ""
        for item in output:
            if not description:
                logger.info("Streaming...")
            description += item
        
        return description.strip()
    except Exception as e:
        logger.error( f"Vision model, An error occurred: {e}")
    return None



    # describe("Describe the image in detail.", "https://replicate.delivery/pbxt/KRULC43USWlEx4ZNkXltJqvYaHpEx2uJ4IyUQPRPwYb8SzPf/view.jpg")