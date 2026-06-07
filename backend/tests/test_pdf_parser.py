from unittest.mock import patch

import pytest

from app.services.pdf_parser import pdf_parser


class TestPdfParser:
    @pytest.mark.asyncio
    async def test_extract_text_pymupdf(self):
        with patch("app.services.pdf_parser.PdfParser._extract_with_pymupdf") as mock:
            mock.return_value = "Extracted text from PyMuPDF parser correctly"
            result = await pdf_parser.extract_text(b"fake_pdf_bytes")
            assert result == "Extracted text from PyMuPDF parser correctly"

    @pytest.mark.asyncio
    async def test_extract_text_fallback(self):
        with patch("app.services.pdf_parser.PdfParser._extract_with_pymupdf") as mock_pymupdf:
            mock_pymupdf.return_value = None
            with patch("app.services.pdf_parser.PdfParser._extract_with_pypdf") as mock_pypdf:
                mock_pypdf.return_value = "Extracted text from PyPDF fallback parser here"
                result = await pdf_parser.extract_text(b"fake_pdf_bytes")
                assert result == "Extracted text from PyPDF fallback parser here"

    @pytest.mark.asyncio
    async def test_extract_text_ocr_fallback(self):
        with patch("app.services.pdf_parser.PdfParser._extract_with_pymupdf") as mock_pymupdf:
            mock_pymupdf.return_value = None
            with patch("app.services.pdf_parser.PdfParser._extract_with_pypdf") as mock_pypdf:
                mock_pypdf.return_value = None
                with patch("app.services.pdf_parser.PdfParser._extract_with_ocr") as mock_ocr:
                    mock_ocr.return_value = "Extracted via OCR engine fallback"
                    result = await pdf_parser.extract_text(b"fake_pdf_bytes")
                    assert result == "Extracted via OCR engine fallback"

    @pytest.mark.asyncio
    async def test_extract_text_all_fail(self):
        with patch("app.services.pdf_parser.PdfParser._extract_with_pymupdf") as mock_pymupdf:
            mock_pymupdf.return_value = None
            with patch("app.services.pdf_parser.PdfParser._extract_with_pypdf") as mock_pypdf:
                mock_pypdf.return_value = None
                with patch("app.services.pdf_parser.PdfParser._extract_with_ocr") as mock_ocr:
                    mock_ocr.return_value = None
                    result = await pdf_parser.extract_text(b"fake_pdf_bytes")
                    assert result == ""
