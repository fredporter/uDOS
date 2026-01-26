"""
PDF OCR Service for Wizard Server
==================================

Converts PDF files to Markdown using Mistral AI OCR technology.
Wrapper around pdf-ocr-obsidian library for Wizard Server integration.

Features:
- Single file extraction: EXTRACT {file.pdf}
- Batch processing: EXTRACT (no args) - processes inbox folder
- Automatic image extraction and linking
- Output to /memory/sandbox/outbox/

Example:
    service = PDFOCRService()
    success, output_path, message = await service.extract("invoice.pdf")
    # or
    success, files, message = await service.extract_batch()
"""

import asyncio
import subprocess
import os
import json
import shutil
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime
from wizard.services.logging_manager import get_logging_manager
from wizard.services.path_utils import get_repo_root


class PDFOCRService:
    """Extract text and images from PDFs using Mistral OCR."""

    def __init__(self):
        self.logger = get_logging_manager().get_logger("pdf-ocr")
        self.repo_root = get_repo_root()
        self.library_path = self.repo_root / "library" / "pdf-ocr"
        self.inbox_path = self.repo_root / "memory" / "sandbox" / "inbox"
        self.outbox_path = self.repo_root / "memory" / "sandbox" / "outbox"
        
        # Create directories if needed
        self.inbox_path.mkdir(parents=True, exist_ok=True)
        self.outbox_path.mkdir(parents=True, exist_ok=True)
        
        # API key from environment
        self.api_key = os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            self.logger.warning("[WIZ] MISTRAL_API_KEY not set in environment")

    def _validate_setup(self) -> Tuple[bool, str]:
        """Validate that pdf-ocr library is available and configured."""
        if not self.library_path.exists():
            return False, f"pdf-ocr library not found at {self.library_path}"
        
        if not self.api_key:
            return False, "MISTRAL_API_KEY not configured (required for OCR)"
        
        # Check if mistralai is installed
        try:
            import mistralai  # noqa
        except ImportError:
            return False, "mistralai package not installed: pip install mistralai"
        
        return True, "Setup valid"

    def _get_pdf_files(self, directory: Path) -> List[Path]:
        """Get all PDF files in a directory."""
        if not directory.exists():
            return []
        return sorted(directory.glob("*.pdf"))

    async def extract(
        self,
        pdf_path: Optional[str] = None,
        page_separator: str = "---"
    ) -> Tuple[bool, Optional[Path], str]:
        """
        Extract text and images from a single PDF.
        
        Args:
            pdf_path: Full path to PDF file. Can be relative to inbox or absolute.
            page_separator: Text to insert between pages (default: "---")
            
        Returns:
            (success, output_path, message)
        """
        # Validate setup
        valid, setup_msg = self._validate_setup()
        if not valid:
            self.logger.error(f"[WIZ] Setup validation failed: {setup_msg}")
            return False, None, setup_msg
        
        # Resolve PDF path
        if pdf_path is None:
            return False, None, "PDF path required (or use extract_batch for inbox)"
        
        # Try to find PDF
        pdf_file = None
        if Path(pdf_path).is_absolute():
            pdf_file = Path(pdf_path)
        else:
            # Check inbox first
            candidate = self.inbox_path / pdf_path
            if candidate.exists():
                pdf_file = candidate
            else:
                # Try as-is
                candidate = Path(pdf_path)
                if candidate.exists():
                    pdf_file = candidate
        
        if not pdf_file or not pdf_file.exists():
            return False, None, f"PDF file not found: {pdf_path}"
        
        if pdf_file.suffix.lower() != ".pdf":
            return False, None, f"File is not a PDF: {pdf_file.suffix}"
        
        try:
            self.logger.info(f"[WIZ] Extracting PDF: {pdf_file.name}")
            
            # Use subprocess to run Python OCR processing
            # This isolates Mistral API calls from the event loop
            result = await asyncio.to_thread(
                self._process_pdf_sync,
                str(pdf_file),
                page_separator
            )
            
            if result["success"]:
                output_path = Path(result["markdown_path"])
                msg = f"✅ Extracted {pdf_file.name} to {output_path.relative_to(self.repo_root)}"
                self.logger.info(f"[WIZ] {msg}")
                return True, output_path, msg
            else:
                return False, None, result["error"]
        
        except Exception as e:
            error_msg = f"Extraction error: {e}"
            self.logger.error(f"[WIZ] {error_msg}")
            return False, None, error_msg

    def _process_pdf_sync(self, pdf_path: str, page_separator: str) -> Dict[str, Any]:
        """
        Synchronously process PDF using the pdf-ocr library.
        
        This runs in a thread to avoid blocking the event loop.
        """
        try:
            from mistralai import Mistral, DocumentURLChunk
            from mistralai.models import OCRResponse
            from werkzeug.utils import secure_filename
        except ImportError as e:
            return {"success": False, "error": f"Import error: {e}"}
        
        pdf_path = Path(pdf_path)
        pdf_base = pdf_path.stem
        pdf_base_sanitized = secure_filename(pdf_base)
        
        # Create output directory
        pdf_output_dir = self.outbox_path / pdf_base_sanitized
        counter = 1
        while pdf_output_dir.exists():
            pdf_base_sanitized = f"{secure_filename(pdf_base)}_{counter}"
            pdf_output_dir = self.outbox_path / pdf_base_sanitized
            counter += 1
        
        pdf_output_dir.mkdir(parents=True, exist_ok=True)
        images_dir = pdf_output_dir / "images"
        images_dir.mkdir(exist_ok=True)
        
        try:
            # Initialize Mistral client
            client = Mistral(api_key=self.api_key)
            
            # Upload PDF
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            
            uploaded_file = client.files.upload(
                file={"file_name": pdf_path.name, "content": pdf_bytes},
                purpose="ocr"
            )
            
            # Get signed URL
            signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=60)
            
            # Process OCR
            message = client.ocr.process(
                model="pixtral-12b-2409",
                document=DocumentURLChunk(
                    type="document_url",
                    document_url=signed_url.url,
                ),
            )
            
            ocr_response = message
            
            # Extract text
            pages_md = []
            image_mapping = {}
            image_count = 1
            
            for page in ocr_response.pages:
                page_content = []
                
                if page.text:
                    page_content.append(page.text)
                
                # Extract images
                if page.images:
                    for img_idx, image in enumerate(page.images):
                        if hasattr(image, "image_base64"):
                            img_name = f"{pdf_base_sanitized}_img_{image_count}.jpeg"
                            img_path = images_dir / img_name
                            
                            # Decode and save image
                            import base64
                            img_bytes = base64.b64decode(image.image_base64)
                            with open(img_path, "wb") as img_file:
                                img_file.write(img_bytes)
                            
                            # Add wikilink to content
                            page_content.append(f"![[{img_name}]]")
                            image_mapping[f"image_{image_count}"] = img_name
                            image_count += 1
                
                if page_content:
                    pages_md.append("\n".join(page_content))
            
            # Combine pages with separator
            markdown_content = f"\n{page_separator}\n".join(pages_md) if pages_md else ""
            
            # Add metadata header
            timestamp = datetime.now().isoformat()
            metadata = f"""---
title: {pdf_base_sanitized}
source_file: {pdf_path.name}
extracted_at: {timestamp}
format: pdf-ocr-mistral
image_count: {image_count - 1}
---

"""
            
            # Write markdown
            markdown_file = pdf_output_dir / "output.md"
            with open(markdown_file, "w", encoding="utf-8") as f:
                f.write(metadata)
                f.write(markdown_content)
            
            # Save OCR response as JSON for reference
            ocr_json_file = pdf_output_dir / "ocr_response.json"
            with open(ocr_json_file, "w") as f:
                json.dump({
                    "pdf": pdf_path.name,
                    "extracted_at": timestamp,
                    "pages": len(ocr_response.pages),
                    "images": image_count - 1,
                }, f, indent=2)
            
            return {
                "success": True,
                "markdown_path": str(markdown_file),
                "images_count": image_count - 1,
                "pages": len(ocr_response.pages)
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"OCR processing error: {e}"
            }

    async def extract_batch(
        self,
        page_separator: str = "---"
    ) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Batch extract all PDFs from inbox directory.
        
        Returns:
            (success, results_list, summary_message)
            where results_list contains dicts with: filename, output_path, images_count
        """
        # Validate setup
        valid, setup_msg = self._validate_setup()
        if not valid:
            self.logger.error(f"[WIZ] Setup validation failed: {setup_msg}")
            return False, [], setup_msg
        
        # Find PDFs in inbox
        pdf_files = self._get_pdf_files(self.inbox_path)
        
        if not pdf_files:
            msg = f"No PDFs found in {self.inbox_path.relative_to(self.repo_root)}"
            self.logger.info(f"[WIZ] {msg}")
            return True, [], msg
        
        self.logger.info(f"[WIZ] Found {len(pdf_files)} PDFs to process")
        
        results = []
        failed = []
        
        for pdf_file in pdf_files:
            self.logger.info(f"[WIZ] Processing {pdf_file.name}...")
            
            try:
                result = await asyncio.to_thread(
                    self._process_pdf_sync,
                    str(pdf_file),
                    page_separator
                )
                
                if result["success"]:
                    output_path = Path(result["markdown_path"])
                    results.append({
                        "filename": pdf_file.name,
                        "output_path": str(output_path.relative_to(self.repo_root)),
                        "images": result.get("images_count", 0),
                        "pages": result.get("pages", 0)
                    })
                    self.logger.info(f"[WIZ] ✅ {pdf_file.name}")
                else:
                    failed.append((pdf_file.name, result["error"]))
                    self.logger.error(f"[WIZ] ❌ {pdf_file.name}: {result['error']}")
            
            except Exception as e:
                failed.append((pdf_file.name, str(e)))
                self.logger.error(f"[WIZ] ❌ {pdf_file.name}: {e}")
        
        # Summary
        summary = f"✅ Processed {len(results)} PDFs"
        if failed:
            summary += f", ❌ Failed {len(failed)}"
        
        return True, results, summary


# Singleton instance
_service: Optional[PDFOCRService] = None


def get_pdf_ocr_service() -> PDFOCRService:
    """Get or create PDF OCR service instance."""
    global _service
    if _service is None:
        _service = PDFOCRService()
    return _service
