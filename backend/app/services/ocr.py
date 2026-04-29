from dataclasses import dataclass, field
from pathlib import Path

from app.core.config import get_settings


@dataclass
class OcrResult:
    text: str
    engine: str | None = None
    metadata: dict = field(default_factory=dict)
    warnings: list[dict] = field(default_factory=list)


class OcrService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def ocr_image(self, path: Path) -> OcrResult:
        if not self.settings.ocr_enabled:
            return OcrResult(text="", warnings=[{"code": "ocr_disabled", "message": "OCR is disabled"}])
        try:
            from PIL import Image
            import pytesseract
        except ImportError:
            return OcrResult(
                text="",
                warnings=[
                    {
                        "code": "ocr_dependency_missing",
                        "message": "Install pillow and pytesseract, plus the Tesseract binary, to enable image OCR",
                    }
                ],
            )

        try:
            image = Image.open(path)
            text = pytesseract.image_to_string(image, lang=self.settings.ocr_languages)
            return OcrResult(
                text=text.strip(),
                engine="tesseract",
                metadata={"ocr_languages": self.settings.ocr_languages, "image_size": list(image.size)},
            )
        except Exception as exc:
            return OcrResult(text="", warnings=[{"code": "ocr_failed", "message": str(exc)}])

    def ocr_pdf(self, path: Path) -> OcrResult:
        if not self.settings.ocr_enabled:
            return OcrResult(text="", warnings=[{"code": "ocr_disabled", "message": "OCR is disabled"}])
        try:
            import fitz
            from PIL import Image
            import pytesseract
        except ImportError:
            return OcrResult(
                text="",
                warnings=[
                    {
                        "code": "ocr_dependency_missing",
                        "message": "Install pymupdf, pillow and pytesseract, plus the Tesseract binary, to enable PDF OCR",
                    }
                ],
            )

        pages = []
        warnings = []
        try:
            document = fitz.open(str(path))
            max_pages = min(len(document), self.settings.ocr_max_pdf_pages)
            for page_index in range(max_pages):
                page = document.load_page(page_index)
                pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
                page_text = pytesseract.image_to_string(image, lang=self.settings.ocr_languages)
                if page_text.strip():
                    pages.append(page_text.strip())
                else:
                    warnings.append({"code": "ocr_empty_page", "message": f"OCR found no text on page {page_index + 1}"})
            return OcrResult(
                text="\n\n".join(pages).strip(),
                engine="tesseract+pymupdf",
                metadata={"ocr_pages": max_pages, "ocr_languages": self.settings.ocr_languages},
                warnings=warnings,
            )
        except Exception as exc:
            return OcrResult(text="", warnings=[{"code": "ocr_failed", "message": str(exc)}])
