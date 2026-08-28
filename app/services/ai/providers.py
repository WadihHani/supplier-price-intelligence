import json
from abc import ABC, abstractmethod
from urllib.error import URLError
from urllib.request import Request, urlopen

from app.core.config import settings


PROCUREMENT_SYSTEM_PROMPT = """You are a procurement analyst.

Explain the provided supplier analysis using ONLY the supplied facts.
Do not invent information.
Do not change scores.
Do not perform currency conversion.
Do not claim information that is not provided.

Explain which supplier is recommended, why it is recommended, the important
price difference, relevant reliability and delivery information, and any
important caveats. Keep the response concise and professional."""


class AIProvider(ABC):

    @abstractmethod
    def generate_procurement_explanation(self, analysis: dict) -> str:
        pass


class MockAIProvider(AIProvider):

    def generate_procurement_explanation(self, analysis: dict) -> str:
        recommendation = analysis["recommendation"]

        return (
            f"{recommendation['supplier_name']} is recommended based on the "
            f"highest overall supplier score of "
            f"{recommendation['final_score']}. Its unit price is "
            f"{recommendation['unit_price']} {analysis['currency']} with a "
            f"reliability score of {recommendation['reliability_score']} and "
            f"delivery score of {recommendation['delivery_score']}."
        )


class OpenAIProvider(AIProvider):

    def __init__(
        self,
        api_key: str | None,
        model: str,
    ):
        self.api_key = api_key
        self.model = model

    def generate_procurement_explanation(self, analysis: dict) -> str:
        if not self.api_key:
            raise RuntimeError("AI API key is not configured.")

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": PROCUREMENT_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": json.dumps(analysis),
                },
            ],
        }
        request = Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (URLError, TimeoutError) as error:
            raise RuntimeError("AI provider request failed.") from error

        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, AttributeError) as error:
            raise RuntimeError("AI provider returned an invalid response.") from error


class UnavailableAIProvider(AIProvider):

    def generate_procurement_explanation(self, analysis: dict) -> str:
        raise RuntimeError("Configured AI provider is not available.")


def get_ai_provider() -> AIProvider:
    if settings.ai_provider.lower() == "mock":
        return MockAIProvider()

    if settings.ai_provider.lower() == "openai":
        return OpenAIProvider(
            api_key=settings.ai_api_key,
            model=settings.ai_model,
        )

    return UnavailableAIProvider()
