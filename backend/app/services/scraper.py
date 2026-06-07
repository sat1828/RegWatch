from __future__ import annotations

import hashlib
from typing import Any, Optional

import structlog
from bs4 import BeautifulSoup

from app.core.config import settings

logger = structlog.get_logger(__name__)


class ScrapeResult:
    def __init__(
        self,
        url: str,
        html: str = "",
        text: str = "",
        pdf_bytes: bytes | None = None,
        links: list[dict[str, str]] | None = None,
        success: bool = False,
        error: str | None = None,
    ) -> None:
        self.url = url
        self.html = html
        self.text = text
        self.pdf_bytes = pdf_bytes
        self.links = links or []
        self.success = success
        self.error = error

    @property
    def content_hash(self) -> str:
        content = self.text or self.html
        return hashlib.sha256(content.encode()).hexdigest()


class PlaywrightScraper:
    def __init__(self) -> None:
        self._browser: Any = None

    async def _ensure_browser(self) -> Any:
        if self._browser is not None:
            return self._browser
        try:
            from playwright.async_api import async_playwright

            p = await async_playwright().start()
            self._browser = await p.chromium.launch(
                headless=settings.playwright_headless,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ],
            )
        except Exception as e:
            logger.warning("playwright_launch_failed", error=str(e))
            self._browser = None
        return self._browser

    async def scrape(self, url: str, timeout: int | None = None) -> ScrapeResult:
        browser = await self._ensure_browser()
        if not browser:
            return ScrapeResult(url=url, success=False, error="Playwright not available")

        try:
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                )
            )
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle", timeout=timeout or 30000)
            html = await page.content()
            text = await page.inner_text("body")
            await context.close()

            links = self._extract_links(html, url)

            return ScrapeResult(
                url=url,
                html=html,
                text=text,
                links=links,
                success=True,
            )
        except Exception as e:
            logger.error("playwright_scrape_error", url=url, error=str(e))
            return ScrapeResult(url=url, success=False, error=str(e))

    async def fetch_pdf_bytes(self, url: str) -> bytes | None:
        browser = await self._ensure_browser()
        if not browser:
            return None
        try:
            context = await browser.new_context()
            page = await context.new_page()
            resp = await page.goto(url, wait_until="networkidle")
            if resp and resp.ok:
                content = await resp.body()
                await context.close()
                return content
            await context.close()
            return None
        except Exception as e:
            logger.error("pdf_fetch_error", url=url, error=str(e))
            return None

    @staticmethod
    def _extract_links(html: str, base_url: str) -> list[dict[str, str]]:
        soup = BeautifulSoup(html, "html.parser")
        links: list[dict[str, str]] = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            title = a.get_text(strip=True)
            if title and href and not href.startswith("#") and not href.startswith("javascript:"):
                from urllib.parse import urljoin

                full_url = urljoin(base_url, href)
                links.append({"title": title, "url": full_url})
        return links

    async def close(self) -> None:
        if self._browser:
            try:
                await self._browser.close()
            except Exception:
                pass


class SimpleHttpScraper:
    async def scrape(self, url: str, timeout: int | None = None) -> ScrapeResult:
        try:
            import httpx

            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=httpx.Timeout(timeout or settings.scrapyd_timeout_seconds),
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/125.0.0.0 Safari/537.36"
                    )
                },
            ) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                content_type = resp.headers.get("content-type", "")

                if "pdf" in content_type:
                    return ScrapeResult(
                        url=url,
                        pdf_bytes=resp.content,
                        success=True,
                    )

                html = resp.text
                soup = BeautifulSoup(html, "html.parser")
                text = soup.get_text(separator="\n", strip=True)
                links = PlaywrightScraper._extract_links(html, url)

                return ScrapeResult(
                    url=url,
                    html=html,
                    text=text,
                    links=links,
                    success=True,
                )
        except Exception as e:
            logger.error("http_scrape_error", url=url, error=str(e))
            return ScrapeResult(url=url, success=False, error=str(e))


class ScraperFactory:
    def __init__(self) -> None:
        self.playwright = PlaywrightScraper()
        self.http = SimpleHttpScraper()

    async def scrape(self, url: str, use_playwright: bool = True) -> ScrapeResult:
        if use_playwright:
            result = await self.playwright.scrape(url)
            if result.success:
                return result
        return await self.http.scrape(url)

    async def fetch_document_content(self, url: str) -> ScrapeResult:
        if url.lower().endswith(".pdf"):
            result = await self.playwright.scrape(url)
            if result.success and result.text:
                return result
            pdf_bytes = await self.playwright.fetch_pdf_bytes(url)
            if pdf_bytes:
                return ScrapeResult(url=url, pdf_bytes=pdf_bytes, success=True)
            return await self.http.scrape(url)
        return await self.scrape(url)

    async def close(self) -> None:
        await self.playwright.close()


scraper_factory = ScraperFactory()
