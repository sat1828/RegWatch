from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)


class PdfParser:
    async def extract_text(self, pdf_bytes: bytes) -> str:
        text = await self._extract_with_pymupdf(pdf_bytes)
        if text and len(text.strip()) > 20:
            return text

        text = await self._extract_with_pypdf(pdf_bytes)
        if text and len(text.strip()) > 20:
            return text

        text = await self._extract_with_ocr(pdf_bytes)
        return text or ""

    @staticmethod
    async def _extract_with_pymupdf(pdf_bytes: bytes) -> str | None:
        try:
            import fitz

            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = "\n".join(page.get_text() for page in doc)
            doc.close()
            return text.strip()
        except Exception as e:
            logger.debug("pymupdf_extract_failed", error=str(e))
            return None

    @staticmethod
    async def _extract_with_pypdf(pdf_bytes: bytes) -> str | None:
        try:
            from io import BytesIO

            from pypdf import PdfReader

            reader = PdfReader(BytesIO(pdf_bytes))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return text.strip()
        except Exception as e:
            logger.debug("pypdf_extract_failed", error=str(e))
            return None

    @staticmethod
    async def _extract_with_ocr(pdf_bytes: bytes) -> str | None:
        try:
            import pytesseract
            from pdf2image import convert_from_bytes

            images = convert_from_bytes(pdf_bytes)
            text = "\n".join(
                pytesseract.image_to_string(img, lang="eng+hin") for img in images
            )
            return text.strip()
        except Exception as e:
            logger.debug("ocr_extract_failed", error=str(e))
            return None


pdf_parser = PdfParser()
