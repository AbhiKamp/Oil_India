"""Optional local OCR through Poppler and Tesseract command-line tools."""

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


MAX_OCR_PAGES = 10
MAX_OCR_CHARS = 2_000_000
PDFTOPPM_TIMEOUT_SECONDS = 30
TESSERACT_TIMEOUT_SECONDS = 20


class OCRUnavailableError(RuntimeError):
    """One or both system OCR tools are unavailable."""


class OCRLimitError(ValueError):
    """The document exceeds bounded OCR limits."""


class OCRExecutionError(RuntimeError):
    """An OCR subprocess failed or exceeded its time limit."""


class OCRParser:
    def __init__(self, tesseract_cmd: str = "tesseract", pdftoppm_cmd: str = "pdftoppm"):
        self.tesseract_cmd = tesseract_cmd
        self.pdftoppm_cmd = pdftoppm_cmd

    def extract_scanned_text(self, image_or_pdf_path: str,
                             page_numbers: list[int] | None = None) -> dict[str, Any]:
        pdf_path = Path(image_or_pdf_path)
        if page_numbers is None:
            try:
                from pypdf import PdfReader
                page_numbers = list(range(1, len(PdfReader(pdf_path, strict=True).pages) + 1))
            except Exception as exc:
                raise OCRExecutionError("Unable to read PDF for OCR") from exc
        if not page_numbers:
            return {"source": pdf_path.name, "engine": "tesseract", "extraction_method": "ocr",
                    "pages": [], "extracted_text": ""}
        if len(page_numbers) > MAX_OCR_PAGES or any(page < 1 for page in page_numbers):
            raise OCRLimitError(f"Automatic OCR is limited to {MAX_OCR_PAGES} pages")

        pdftoppm = shutil.which(self.pdftoppm_cmd)
        tesseract = shutil.which(self.tesseract_cmd)
        missing = [name for name, executable in (("pdftoppm", pdftoppm), ("tesseract", tesseract))
                   if executable is None]
        if missing:
            raise OCRUnavailableError("OCR unavailable: missing " + " and ".join(missing))

        results = []
        total_chars = 0
        with tempfile.TemporaryDirectory(prefix="nwis-ocr-") as temporary_dir:
            temp = Path(temporary_dir)
            for page_number in page_numbers:
                image_prefix = temp / f"page-{page_number}"
                try:
                    subprocess.run(
                        [pdftoppm, "-f", str(page_number), "-l", str(page_number), "-singlefile",
                         "-scale-to", "2500", "-png", str(pdf_path), str(image_prefix)],
                        check=True, capture_output=True, timeout=PDFTOPPM_TIMEOUT_SECONDS,
                    )
                    image_path = image_prefix.with_suffix(".png")
                    completed = subprocess.run(
                        [tesseract, str(image_path), "stdout", "-l", "eng", "--psm", "6"],
                        check=True, capture_output=True, timeout=TESSERACT_TIMEOUT_SECONDS,
                    )
                except subprocess.TimeoutExpired as exc:
                    tool = "pdftoppm" if exc.cmd and str(pdftoppm) in str(exc.cmd) else "tesseract"
                    raise OCRExecutionError(f"{tool} exceeded its {exc.timeout}s timeout") from exc
                except (subprocess.CalledProcessError, OSError) as exc:
                    raise OCRExecutionError("Local OCR command failed") from exc
                text = completed.stdout.decode("utf-8", errors="replace").strip()
                total_chars += len(text)
                if total_chars > MAX_OCR_CHARS:
                    raise OCRLimitError(f"OCR output exceeds {MAX_OCR_CHARS} characters")
                results.append({"page_number": page_number, "text": text, "extraction_method": "ocr"})

        return {"source": pdf_path.name, "engine": "tesseract", "extraction_method": "ocr",
                "pages": results, "extracted_text": "\n\n".join(page["text"] for page in results)}
