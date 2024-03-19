from abc import ABC, abstractmethod
from .context import Context
from fastapi.responses import JSONResponse
import traceback

class Handler(ABC):
    """Abstract Handler class for building the chain of handlers."""

    _next_handler: "Handler" = None

    def set_next(self, handler: "Handler") -> "Handler":
        self._next_handler = handler
        return handler

    @abstractmethod
    async def handle(self, context: Context):
        if self._next_handler:
            try:
                return await self._next_handler.handle(context)
            except Exception as e:
                _exception_handler: "Handler" = ExceptionHandler()
                # Extract the stack trace and log the exception
                return await _exception_handler.handle(self._next_handler, context, e)


class DefaultCompletionHandler(Handler):
    async def handle(self, context: Context):
        if context.is_normal_chat:
            # Assuming context.client is set and has a method for creating chat completions
            completion = context.client.route(
                messages=context.messages,
                **context.client.clean_params(context.params),
            )
            context.response = completion.model_dump()
            return JSONResponse(content=context.response, status_code=200)

        return await super().handle(context)


class FallbackHandler(Handler):
    async def handle(self, context: Context):
        # This handler does not pass the request further down the chain.
        # It acts as a fallback when no other handler has processed the request.
        if not context.response:
            # The default action when no other handlers have processed the request
            context.response = {"message": "No suitable action found for the request."}
            return JSONResponse(content=context.response, status_code=400)

        # If there's already a response set in the context, it means one of the handlers has processed the request.
        return JSONResponse(content=context.response, status_code=200)


class ExceptionHandler(Handler):
    async def handle(self, handler: Handler, context: Context, exception: Exception):
        print(f"Error processing the request: {str(handler.__class__) } - {exception}")
        # print(traceback.format_exc())
        return JSONResponse(
            content={"error": "An unexpected error occurred, within handler " + str(handler.__class__) + " : " + str(exception)},
            status_code=500,
        )


