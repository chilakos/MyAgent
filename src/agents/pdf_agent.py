"""
PDF Agent for autonomous PDF operations.

This module provides a comprehensive PDF agent that can:
- Merge multiple PDFs
- Split PDFs into separate files
- Extract text from PDFs
- Extract specific pages
- Get PDF metadata
- Rotate pages
- Add watermarks
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass
import logging

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    raise ImportError(
        "pypdf is required for PDF operations. Install it with: pip install pypdf"
    )

try:
    import pdfplumber
except ImportError:
    pdfplumber = None
    logging.warning("pdfplumber not installed. Advanced text extraction will be limited.")


logger = logging.getLogger(__name__)


@dataclass
class PDFOperationResult:
    """Result of a PDF operation."""
    success: bool
    message: str
    output_files: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.output_files is None:
            self.output_files = []
        if self.metadata is None:
            self.metadata = {}


class PDFAgent:
    """
    Autonomous PDF agent for handling various PDF operations.

    This agent can handle complex PDF tasks including merging, splitting,
    text extraction, and more.
    """

    def __init__(self, workspace_dir: Optional[str] = None):
        """
        Initialize the PDF agent.

        Args:
            workspace_dir: Directory for output files. Defaults to ./pdf_workspace
        """
        self.workspace_dir = Path(workspace_dir or "./pdf_workspace")
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"PDF Agent initialized with workspace: {self.workspace_dir}")

    def merge_pdfs(
        self,
        input_files: List[str],
        output_file: Optional[str] = None
    ) -> PDFOperationResult:
        """
        Merge multiple PDF files into a single PDF.

        Args:
            input_files: List of PDF file paths to merge
            output_file: Output file path. If None, auto-generated

        Returns:
            PDFOperationResult with success status and output file
        """
        try:
            # Validate input files
            for file in input_files:
                if not Path(file).exists():
                    return PDFOperationResult(
                        success=False,
                        message=f"Input file not found: {file}"
                    )

            # Generate output filename if not provided
            if output_file is None:
                output_file = str(self.workspace_dir / "merged_output.pdf")
            else:
                output_file = str(self.workspace_dir / Path(output_file).name)

            # Merge PDFs using PdfWriter
            writer = PdfWriter()
            for pdf_file in input_files:
                reader = PdfReader(pdf_file)
                for page in reader.pages:
                    writer.add_page(page)

            with open(output_file, "wb") as f:
                writer.write(f)

            logger.info(f"Successfully merged {len(input_files)} PDFs into {output_file}")

            return PDFOperationResult(
                success=True,
                message=f"Successfully merged {len(input_files)} PDFs",
                output_files=[output_file],
                metadata={"input_count": len(input_files)}
            )

        except Exception as e:
            logger.error(f"Error merging PDFs: {str(e)}")
            return PDFOperationResult(
                success=False,
                message=f"Error merging PDFs: {str(e)}"
            )

    def split_pdf(
        self,
        input_file: str,
        pages_per_file: Optional[int] = None,
        page_ranges: Optional[List[tuple]] = None,
        output_prefix: Optional[str] = None
    ) -> PDFOperationResult:
        """
        Split a PDF into multiple files.

        Args:
            input_file: Input PDF file path
            pages_per_file: Number of pages per output file (mutually exclusive with page_ranges)
            page_ranges: List of (start, end) tuples for custom splits
            output_prefix: Prefix for output files

        Returns:
            PDFOperationResult with success status and output files
        """
        try:
            if not Path(input_file).exists():
                return PDFOperationResult(
                    success=False,
                    message=f"Input file not found: {input_file}"
                )

            reader = PdfReader(input_file)
            total_pages = len(reader.pages)

            output_files = []
            base_name = Path(input_file).stem
            prefix = output_prefix or f"{base_name}_split"

            # Split by pages per file
            if pages_per_file:
                for i in range(0, total_pages, pages_per_file):
                    writer = PdfWriter()
                    end_page = min(i + pages_per_file, total_pages)

                    for page_num in range(i, end_page):
                        writer.add_page(reader.pages[page_num])

                    output_file = str(self.workspace_dir / f"{prefix}_part{i//pages_per_file + 1}.pdf")
                    with open(output_file, "wb") as f:
                        writer.write(f)
                    output_files.append(output_file)

            # Split by page ranges
            elif page_ranges:
                for idx, (start, end) in enumerate(page_ranges, 1):
                    writer = PdfWriter()

                    # Adjust for 0-indexing
                    start_idx = max(0, start - 1)
                    end_idx = min(end, total_pages)

                    for page_num in range(start_idx, end_idx):
                        writer.add_page(reader.pages[page_num])

                    output_file = str(self.workspace_dir / f"{prefix}_range{idx}_p{start}-{end}.pdf")
                    with open(output_file, "wb") as f:
                        writer.write(f)
                    output_files.append(output_file)

            # Default: one file per page
            else:
                for page_num in range(total_pages):
                    writer = PdfWriter()
                    writer.add_page(reader.pages[page_num])

                    output_file = str(self.workspace_dir / f"{prefix}_page{page_num + 1}.pdf")
                    with open(output_file, "wb") as f:
                        writer.write(f)
                    output_files.append(output_file)

            logger.info(f"Successfully split PDF into {len(output_files)} files")

            return PDFOperationResult(
                success=True,
                message=f"Successfully split PDF into {len(output_files)} files",
                output_files=output_files,
                metadata={"total_pages": total_pages, "output_count": len(output_files)}
            )

        except Exception as e:
            logger.error(f"Error splitting PDF: {str(e)}")
            return PDFOperationResult(
                success=False,
                message=f"Error splitting PDF: {str(e)}"
            )

    def extract_text(
        self,
        input_file: str,
        page_numbers: Optional[List[int]] = None,
        use_advanced: bool = True
    ) -> PDFOperationResult:
        """
        Extract text from a PDF.

        Args:
            input_file: Input PDF file path
            page_numbers: Specific pages to extract (1-indexed). If None, extract all
            use_advanced: Use pdfplumber for better text extraction if available

        Returns:
            PDFOperationResult with extracted text in metadata
        """
        try:
            if not Path(input_file).exists():
                return PDFOperationResult(
                    success=False,
                    message=f"Input file not found: {input_file}"
                )

            extracted_text = {}

            # Use pdfplumber if available and requested
            if use_advanced and pdfplumber:
                with pdfplumber.open(input_file) as pdf:
                    pages_to_extract = page_numbers or list(range(1, len(pdf.pages) + 1))

                    for page_num in pages_to_extract:
                        if 1 <= page_num <= len(pdf.pages):
                            page = pdf.pages[page_num - 1]
                            text = page.extract_text() or ""
                            extracted_text[f"page_{page_num}"] = text
            else:
                # Fallback to pypdf
                reader = PdfReader(input_file)
                total_pages = len(reader.pages)
                pages_to_extract = page_numbers or list(range(1, total_pages + 1))

                for page_num in pages_to_extract:
                    if 1 <= page_num <= total_pages:
                        page = reader.pages[page_num - 1]
                        text = page.extract_text() or ""
                        extracted_text[f"page_{page_num}"] = text

            # Save extracted text to file
            output_file = str(self.workspace_dir / f"{Path(input_file).stem}_extracted.txt")
            with open(output_file, "w", encoding="utf-8") as f:
                for page, text in extracted_text.items():
                    f.write(f"\n=== {page.upper()} ===\n")
                    f.write(text)
                    f.write("\n")

            total_chars = sum(len(text) for text in extracted_text.values())

            logger.info(f"Extracted text from {len(extracted_text)} pages")

            return PDFOperationResult(
                success=True,
                message=f"Successfully extracted text from {len(extracted_text)} pages",
                output_files=[output_file],
                metadata={
                    "extracted_text": extracted_text,
                    "total_characters": total_chars,
                    "page_count": len(extracted_text)
                }
            )

        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return PDFOperationResult(
                success=False,
                message=f"Error extracting text: {str(e)}"
            )

    def extract_pages(
        self,
        input_file: str,
        page_numbers: List[int],
        output_file: Optional[str] = None
    ) -> PDFOperationResult:
        """
        Extract specific pages from a PDF into a new PDF.

        Args:
            input_file: Input PDF file path
            page_numbers: List of page numbers to extract (1-indexed)
            output_file: Output file path

        Returns:
            PDFOperationResult with success status and output file
        """
        try:
            if not Path(input_file).exists():
                return PDFOperationResult(
                    success=False,
                    message=f"Input file not found: {input_file}"
                )

            reader = PdfReader(input_file)
            total_pages = len(reader.pages)
            writer = PdfWriter()

            extracted_pages = []
            for page_num in page_numbers:
                if 1 <= page_num <= total_pages:
                    writer.add_page(reader.pages[page_num - 1])
                    extracted_pages.append(page_num)
                else:
                    logger.warning(f"Page {page_num} out of range (1-{total_pages})")

            if not extracted_pages:
                return PDFOperationResult(
                    success=False,
                    message="No valid pages to extract"
                )

            if output_file is None:
                pages_str = "_".join(map(str, extracted_pages))
                output_file = str(self.workspace_dir / f"{Path(input_file).stem}_pages_{pages_str}.pdf")
            else:
                output_file = str(self.workspace_dir / Path(output_file).name)

            with open(output_file, "wb") as f:
                writer.write(f)

            logger.info(f"Extracted {len(extracted_pages)} pages to {output_file}")

            return PDFOperationResult(
                success=True,
                message=f"Successfully extracted {len(extracted_pages)} pages",
                output_files=[output_file],
                metadata={"extracted_pages": extracted_pages}
            )

        except Exception as e:
            logger.error(f"Error extracting pages: {str(e)}")
            return PDFOperationResult(
                success=False,
                message=f"Error extracting pages: {str(e)}"
            )

    def get_metadata(self, input_file: str) -> PDFOperationResult:
        """
        Get metadata from a PDF file.

        Args:
            input_file: Input PDF file path

        Returns:
            PDFOperationResult with metadata information
        """
        try:
            if not Path(input_file).exists():
                return PDFOperationResult(
                    success=False,
                    message=f"Input file not found: {input_file}"
                )

            reader = PdfReader(input_file)
            metadata = reader.metadata

            info = {
                "title": metadata.get("/Title", "N/A") if metadata else "N/A",
                "author": metadata.get("/Author", "N/A") if metadata else "N/A",
                "subject": metadata.get("/Subject", "N/A") if metadata else "N/A",
                "creator": metadata.get("/Creator", "N/A") if metadata else "N/A",
                "producer": metadata.get("/Producer", "N/A") if metadata else "N/A",
                "creation_date": metadata.get("/CreationDate", "N/A") if metadata else "N/A",
                "modification_date": metadata.get("/ModDate", "N/A") if metadata else "N/A",
                "page_count": len(reader.pages),
                "file_size_bytes": Path(input_file).stat().st_size,
            }

            # Add page dimensions for first page
            if reader.pages:
                first_page = reader.pages[0]
                mediabox = first_page.mediabox
                info["page_width"] = float(mediabox.width)
                info["page_height"] = float(mediabox.height)

            logger.info(f"Retrieved metadata for {input_file}")

            return PDFOperationResult(
                success=True,
                message="Successfully retrieved PDF metadata",
                metadata=info
            )

        except Exception as e:
            logger.error(f"Error getting metadata: {str(e)}")
            return PDFOperationResult(
                success=False,
                message=f"Error getting metadata: {str(e)}"
            )

    def rotate_pages(
        self,
        input_file: str,
        rotation: int,
        page_numbers: Optional[List[int]] = None,
        output_file: Optional[str] = None
    ) -> PDFOperationResult:
        """
        Rotate pages in a PDF.

        Args:
            input_file: Input PDF file path
            rotation: Rotation angle (90, 180, 270)
            page_numbers: Pages to rotate (1-indexed). If None, rotate all
            output_file: Output file path

        Returns:
            PDFOperationResult with success status and output file
        """
        try:
            if not Path(input_file).exists():
                return PDFOperationResult(
                    success=False,
                    message=f"Input file not found: {input_file}"
                )

            if rotation not in [90, 180, 270, -90, -180, -270]:
                return PDFOperationResult(
                    success=False,
                    message=f"Invalid rotation angle: {rotation}. Use 90, 180, or 270"
                )

            reader = PdfReader(input_file)
            writer = PdfWriter()
            total_pages = len(reader.pages)

            pages_to_rotate = page_numbers or list(range(1, total_pages + 1))

            for page_num in range(1, total_pages + 1):
                page = reader.pages[page_num - 1]
                if page_num in pages_to_rotate:
                    page.rotate(rotation)
                writer.add_page(page)

            if output_file is None:
                output_file = str(self.workspace_dir / f"{Path(input_file).stem}_rotated.pdf")
            else:
                output_file = str(self.workspace_dir / Path(output_file).name)

            with open(output_file, "wb") as f:
                writer.write(f)

            logger.info(f"Rotated {len(pages_to_rotate)} pages by {rotation} degrees")

            return PDFOperationResult(
                success=True,
                message=f"Successfully rotated {len(pages_to_rotate)} pages",
                output_files=[output_file],
                metadata={"rotation": rotation, "pages_rotated": len(pages_to_rotate)}
            )

        except Exception as e:
            logger.error(f"Error rotating pages: {str(e)}")
            return PDFOperationResult(
                success=False,
                message=f"Error rotating pages: {str(e)}"
            )

    def process_task(self, task_description: str, **kwargs) -> PDFOperationResult:
        """
        Process a natural language task description.

        This is the main entry point for autonomous task handling.

        Args:
            task_description: Natural language description of the PDF task
            **kwargs: Additional arguments specific to the operation

        Returns:
            PDFOperationResult with task outcome
        """
        task_lower = task_description.lower()

        # Determine the operation type
        if "merge" in task_lower or "combine" in task_lower:
            input_files = kwargs.get("input_files", [])
            output_file = kwargs.get("output_file")
            return self.merge_pdfs(input_files, output_file)

        elif "split" in task_lower:
            input_file = kwargs.get("input_file", "")
            pages_per_file = kwargs.get("pages_per_file")
            page_ranges = kwargs.get("page_ranges")
            return self.split_pdf(input_file, pages_per_file, page_ranges)

        elif "extract text" in task_lower or "extract content" in task_lower:
            input_file = kwargs.get("input_file", "")
            page_numbers = kwargs.get("page_numbers")
            return self.extract_text(input_file, page_numbers)

        elif "extract page" in task_lower:
            input_file = kwargs.get("input_file", "")
            page_numbers = kwargs.get("page_numbers", [])
            output_file = kwargs.get("output_file")
            return self.extract_pages(input_file, page_numbers, output_file)

        elif "metadata" in task_lower or "info" in task_lower:
            input_file = kwargs.get("input_file", "")
            return self.get_metadata(input_file)

        elif "rotate" in task_lower:
            input_file = kwargs.get("input_file", "")
            rotation = kwargs.get("rotation", 90)
            page_numbers = kwargs.get("page_numbers")
            return self.rotate_pages(input_file, rotation, page_numbers)

        else:
            return PDFOperationResult(
                success=False,
                message=f"Unknown task: {task_description}"
            )
