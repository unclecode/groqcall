from importlib import import_module
from fastapi.responses import JSONResponse
from prompts import *
from .base_handler import Handler
from .context import Context

class ProviderSelectionHandler(Handler):
    @staticmethod
    def provider_exists(provider: str) -> bool:
        module_name = f"app.providers"
        class_name = f"{provider.capitalize()}Provider"
        try:
            provider_module = import_module(module_name)
            provider_class = getattr(provider_module, class_name)
            return bool(provider_class)
        except ImportError:
            return False

    async def handle(self, context: Context):
        # Construct the module path and class name based on the provider
        module_name = f"app.providers"
        class_name = f"{context.provider.capitalize()}Provider"

        try:
            # Dynamically import the module and class
            provider_module = import_module(module_name)
            provider_class = getattr(provider_module, class_name)

            if provider_class:
                context.client = provider_class(
                    api_key=context.api_token
                )  # Assuming an api_key parameter
                return await super().handle(context)
            else:
                raise ValueError(
                    f"Provider class {class_name} could not be found in {module_name}."
                )
        except ImportError as e:
            # Handle import error (e.g., module or class not found)
            print(f"Error importing {class_name} from {module_name}: {e}")
            context.response = {
                "error": f"An error occurred while trying to load the provider: {e}"
            }
            return JSONResponse(content=context.response, status_code=500)

