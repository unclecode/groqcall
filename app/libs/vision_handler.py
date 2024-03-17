from prompts import *
from utils import describe
from .context import Context
from .base_handler import Handler


class ImageMessageHandler(Handler):
    async def handle(self, context: Context):
        new_messages = []
        image_ref = 1
        for message in context.messages:
            if message["role"] == "user":
                if isinstance(message["content"], list):
                    prompt = None
                    for content in message["content"]:
                        if content["type"] == "text":
                            # new_messages.append({"role": message["role"], "content": content["text"]})
                            prompt = content["text"]
                        elif content["type"] == "image_url":
                            image_url = content["image_url"]["url"]
                            try:
                                prompt = prompt or IMAGE_DESCRIPTO_PROMPT
                                description = describe(prompt, image_url)
                                if description:
                                    description = get_image_desc_guide(image_ref, description)
                                    new_messages.append(
                                        {"role": message["role"], "content": description}
                                    )
                                    image_ref += 1
                                else:
                                    pass
                            except Exception as e:
                                print(f"Error describing image: {e}")
                                continue
                else:
                    new_messages.append(message)
            else:
                new_messages.append(message)

        context.messages = new_messages
        return await super().handle(context)
    

class ImageLLavaMessageHandler(Handler):
    async def handle(self, context: Context):
        new_messages = []
        image_ref = 1
        for message in context.messages:
            new_messages.append(message)
            if message["role"] == "user":
                if isinstance(message["content"], list):
                    for content in message["content"]:
                        if content["type"] == "text":
                            prompt = content["text"]
                        elif content["type"] == "image_url":
                            image_url = content["image_url"]["url"]
                            try:
                                description = describe(prompt, image_url)
                                new_messages.append(
                                    {"role": "assistant", "content": description}
                                )
                                image_ref += 1
                            except Exception as e:
                                print(f"Error describing image: {e}")
                                continue
        context.messages = new_messages
        return await super().handle(context)

