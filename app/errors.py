class GatewayError(Exception):
      """Base class for gateway-controlled errors."""


class ModelNotFoundError(GatewayError):
    """Raised when the requested public model is not registered."""

    def __init__(self, model: str) -> None:
        self.model = model
        super().__init__(f"Model not found: {model}")

class StreamingNotSupportedError(GatewayError):
    """Raised when streaming is requested before streaming support exists."""

    def __init__(self) -> None:
        super().__init__("Streaming is not supported in this milestone")

class ProviderError(GatewayError):
      """Raised when a downstream provider fails."""

      def __init__(self, message: str = "Provider request failed") -> None:
          super().__init__(message)