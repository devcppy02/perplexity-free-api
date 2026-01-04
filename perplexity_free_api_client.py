import json
import random
import uuid
from typing import List, Literal, Optional

from curl_cffi.requests import AsyncSession
from curl_cffi.requests.impersonate import BrowserTypeLiteral
from curl_cffi.requests.cookies import CookieTypes


class PerplexityFreeAPIClient:
    SUPPORTED_BLOCKS = [
        "answer_modes",
        "media_items",
        "knowledge_cards",
        "inline_entity_cards",
        "place_widgets",
        "finance_widgets",
        "prediction_market_widgets",
        "sports_widgets",
        "flight_status_widgets",
        "news_widgets",
        "shopping_widgets",
        "jobs_widgets",
        "search_result_widgets",
        "inline_images",
        "inline_assets",
        "placeholder_cards",
        "diff_blocks",
        "inline_knowledge_cards",
        "entity_group_v2",
        "refinement_filters",
        "canvas_mode",
        "maps_preview",
        "answer_tabs",
        "price_comparison_widgets",
        "preserve_latex",
    ]

    def __init__(
        self,
        cookies: Optional[CookieTypes] = None,
        timezone: str = "America/New_York",
        language: str = "en-US",
        version: str = "2.18",
        impersonate: BrowserTypeLiteral = "chrome120",
    ):
        self.session = AsyncSession(impersonate=impersonate)
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Content-Type": "application/json",
        }
        self.cookies = cookies

        self.frontend_uuid = str(uuid.uuid4())
        self.timezone = timezone
        self.language = language
        self.version = version

    async def get_no_acc_cookies(self):
        response = await self.session.get(
            "https://www.perplexity.ai/", headers=self.headers
        )
        if response.status_code == 200:
            self.cookies = response.cookies

    async def ask(
        self,
        message: str,
        search_focus: Literal["internet", "writing"] = "internet",
        sources: Optional[List[Literal["web", "scholar", "social", "edgar"]]] = ["web"],
        model_preference: Optional[Literal["turbo", "pplx_pro", "experimental", "gpt52", "gpt52_thinking", "gemini30pro", "gemini30flash", "gemini30flash_high", "grok41nonreasoning", "grok41reasoning", "kimik2thinking", "claude45sonnet", "claude45sonnetthinking"]] = "turbo",
        context_uuid: Optional[str] = None,
    ):
        """
        Asking perplexity.ai

        :param message: Message text
        :param search_focus: Search mode
        :param sources: List of sources
        :param context_uuid: Chat ID, If None, a new chat will be created
        """
        if self.cookies is None:
            await self.get_no_acc_cookies()

        current_context_uuid = context_uuid if context_uuid else str(uuid.uuid4())

        base_reaction = random.randint(800, 1200)
        char_speed = random.randint(150, 250)
        typing_time = len(message) * char_speed
        time_typing = base_reaction + typing_time

        payload = {
            "params": {
                "always_search_override": False,
                "attachments": [],
                "browser_agent_allow_once_from_toggle": False,
                "client_coordinates": None,
                "is_incognito": False,
                "is_nav_suggestions_disabled": False,
                "is_related_query": False,
                "is_sponsored": False,
                "local_search_enabled": False,
                "mentions": [],
                "mode": "concise",
                "model_preference": model_preference,
                "override_no_search": False,
                "prompt_source": "user",
                "query_source": "home",
                "search_recency_filter": None,
                "send_back_text_in_streaming_api": False,
                "should_ask_for_mcp_tool_confirmation": True,
                "skip_search_enabled": True,
                "supported_block_use_cases": self.SUPPORTED_BLOCKS,
                "supported_features": ["browser_agent_permission_banner_v1.1"],
                "use_schematized_api": True,
                "timezone": self.timezone,
                "language": self.language,
                "version": self.version,
                "frontend_uuid": self.frontend_uuid,
                "dsl_query": message,
                "frontend_context_uuid": current_context_uuid,
                "search_focus": search_focus,
                "sources": sources,
                "time_from_first_type": time_typing,
            },
            "query_str": message,
        }

        response = await self.session.post(
            "https://www.perplexity.ai/rest/sse/perplexity_ask",
            headers=self.headers,
            cookies=self.cookies,
            json=payload,
            stream=True,
        )

        final_answer = ""

        async for line in response.aiter_lines():
            if not line.startswith(b"data: "):
                continue

            try:
                json_str = line[6:].decode("utf-8")
                if json_str.strip() == "{}":
                    continue

                data = json.loads(json_str)

                blocks = data.get("blocks", [])
                for block in blocks:
                    if block.get("intended_usage") == "ask_text":
                        if "markdown_block" in block:
                            final_answer = block["markdown_block"].get("answer", "")

                        elif "diff_block" in block:
                            patches = block["diff_block"].get("patches", [])
                            for patch in patches:
                                if patch.get("path") == "/answer":
                                    current_text = patch.get("value", "")
                                    final_answer = current_text

            except json.JSONDecodeError:
                pass

        return current_context_uuid, final_answer
