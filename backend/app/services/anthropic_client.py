from __future__ import annotations

import json
import re
from typing import Any

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class AnthropicClient:
    def __init__(self) -> None:
        self.api_key = settings.anthropic_api_key
        self.model = settings.anthropic_model
        self._client: Any = None

    async def _ensure_client(self) -> Any:
        if self._client is not None:
            return self._client
        if self.api_key and self.api_key.get_secret_value():
            try:
                import anthropic

                self._client = anthropic.AsyncAnthropic(
                    api_key=self.api_key.get_secret_value()
                )
            except Exception as e:
                logger.warning("anthropic_import_failed", error=str(e))
                self._client = None
        return self._client

    async def extract_structured(
        self, system_prompt: str, user_prompt: str, json_schema: dict[str, Any]
    ) -> dict[str, Any] | None:
        client = await self._ensure_client()
        if not client:
            return await self._mock_extraction(system_prompt, user_prompt, json_schema)

        try:
            response = await client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                tools=[
                    {
                        "name": "extract_structured_data",
                        "description": "Extract structured data from regulatory text",
                        "input_schema": json_schema,
                    }
                ],
                tool_choice={"type": "tool", "name": "extract_structured_data"},
            )

            for block in response.content:
                if block.type == "tool_use":
                    return block.input

            text = response.content[0].text if response.content else ""
            return self._parse_fallback_json(text)

        except Exception as e:
            logger.error("anthropic_extract_error", error=str(e))
            return await self._mock_extraction(system_prompt, user_prompt, json_schema)

    async def generate_text(
        self, system_prompt: str, user_prompt: str, max_tokens: int = 2048
    ) -> str | None:
        client = await self._ensure_client()
        if not client:
            return f"[Mock response for: {user_prompt[:100]}...]"

        try:
            response = await client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return response.content[0].text if response.content else None
        except Exception as e:
            logger.error("anthropic_generate_error", error=str(e))
            return None

    @staticmethod
    def _parse_fallback_json(text: str) -> dict[str, Any] | None:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return None

    @staticmethod
    async def _mock_extraction(
        system_prompt: str, user_prompt: str, json_schema: dict[str, Any]
    ) -> dict[str, Any]:
        mock: dict[str, Any] = {
            "obligations": [
                {
                    "obligation_text": "Maintain accurate records of all transactions",
                    "obligation_category": "record_keeping",
                    "severity": "HIGH",
                    "deadline": None,
                    "regulation_reference": "SEBI Regulation 15",
                    "is_mandatory": True,
                }
            ],
            "compliance_gaps": [
                {
                    "gap_type": "missing_policy",
                    "gap_description": "No policy for transaction record keeping",
                    "severity": "HIGH",
                    "confidence_score": 0.85,
                    "recommendation": "Create a record keeping policy",
                }
            ],
            "summary": "Mock analysis for testing purposes",
            "risk_factors": ["Regulatory complexity", "Penalty exposure"],
        }
        return mock


anthropic_client = AnthropicClient()
