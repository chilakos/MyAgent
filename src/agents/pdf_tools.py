"""
LangChain tools for PDF operations.

This module provides LangChain-compatible tools that wrap the PDFAgent
for use in autonomous agent workflows.
"""

from typing import Optional, List, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from .pdf_agent import PDFAgent, PDFOperationResult


# Pydantic models for tool inputs


class MergePDFInput(BaseModel):
    """Input schema for merging PDFs."""
    input_files: List[str] = Field(
        description="List of PDF file paths to merge"
    )
    output_file: Optional[str] = Field(
        default=None,
        description="Output file name (optional)"
    )


class SplitPDFInput(BaseModel):
    """Input schema for splitting PDFs."""
    input_file: str = Field(description="Path to the PDF file to split")
    pages_per_file: Optional[int] = Field(
        default=None,
        description="Number of pages per output file"
    )
    page_ranges: Optional[List[tuple]] = Field(
        default=None,
        description="List of (start, end) page number tuples for custom splits"
    )
    output_prefix: Optional[str] = Field(
        default=None,
        description="Prefix for output files"
    )


class ExtractTextInput(BaseModel):
    """Input schema for extracting text from PDFs."""
    input_file: str = Field(description="Path to the PDF file")
    page_numbers: Optional[List[int]] = Field(
        default=None,
        description="Specific page numbers to extract (1-indexed). If None, extract all pages."
    )
    use_advanced: bool = Field(
        default=True,
        description="Use advanced text extraction with pdfplumber if available"
    )


class ExtractPagesInput(BaseModel):
    """Input schema for extracting specific pages."""
    input_file: str = Field(description="Path to the PDF file")
    page_numbers: List[int] = Field(
        description="List of page numbers to extract (1-indexed)"
    )
    output_file: Optional[str] = Field(
        default=None,
        description="Output file name (optional)"
    )


class GetMetadataInput(BaseModel):
    """Input schema for getting PDF metadata."""
    input_file: str = Field(description="Path to the PDF file")


class RotatePagesInput(BaseModel):
    """Input schema for rotating PDF pages."""
    input_file: str = Field(description="Path to the PDF file")
    rotation: int = Field(
        description="Rotation angle in degrees (90, 180, or 270)"
    )
    page_numbers: Optional[List[int]] = Field(
        default=None,
        description="Page numbers to rotate (1-indexed). If None, rotate all pages."
    )
    output_file: Optional[str] = Field(
        default=None,
        description="Output file name (optional)"
    )


# LangChain Tool implementations


class MergePDFTool(BaseTool):
    """Tool for merging multiple PDF files."""

    name: str = "merge_pdfs"
    description: str = (
        "Merge multiple PDF files into a single PDF. "
        "Input is a list of PDF file paths. "
        "Returns the path to the merged PDF file."
    )
    args_schema: Type[BaseModel] = MergePDFInput

    def __init__(self, pdf_agent: PDFAgent):
        super().__init__()
        self.pdf_agent = pdf_agent

    def _run(
        self,
        input_files: List[str],
        output_file: Optional[str] = None
    ) -> str:
        """Execute the merge operation."""
        result = self.pdf_agent.merge_pdfs(input_files, output_file)
        if result.success:
            return f"{result.message}\nOutput: {result.output_files[0]}"
        else:
            return f"Error: {result.message}"

    async def _arun(self, *args, **kwargs):
        """Async version (not implemented)."""
        raise NotImplementedError("Async not supported")


class SplitPDFTool(BaseTool):
    """Tool for splitting a PDF into multiple files."""

    name: str = "split_pdf"
    description: str = (
        "Split a PDF into multiple files. "
        "You can split by pages per file, custom page ranges, or one page per file. "
        "Returns the paths to the split PDF files."
    )
    args_schema: Type[BaseModel] = SplitPDFInput

    def __init__(self, pdf_agent: PDFAgent):
        super().__init__()
        self.pdf_agent = pdf_agent

    def _run(
        self,
        input_file: str,
        pages_per_file: Optional[int] = None,
        page_ranges: Optional[List[tuple]] = None,
        output_prefix: Optional[str] = None
    ) -> str:
        """Execute the split operation."""
        result = self.pdf_agent.split_pdf(
            input_file,
            pages_per_file,
            page_ranges,
            output_prefix
        )
        if result.success:
            files_list = "\n".join(f"  - {f}" for f in result.output_files)
            return f"{result.message}\nOutput files:\n{files_list}"
        else:
            return f"Error: {result.message}"

    async def _arun(self, *args, **kwargs):
        """Async version (not implemented)."""
        raise NotImplementedError("Async not supported")


class ExtractTextTool(BaseTool):
    """Tool for extracting text from PDFs."""

    name: str = "extract_text_from_pdf"
    description: str = (
        "Extract text content from a PDF file. "
        "Can extract from all pages or specific pages. "
        "Returns the extracted text and saves it to a text file."
    )
    args_schema: Type[BaseModel] = ExtractTextInput

    def __init__(self, pdf_agent: PDFAgent):
        super().__init__()
        self.pdf_agent = pdf_agent

    def _run(
        self,
        input_file: str,
        page_numbers: Optional[List[int]] = None,
        use_advanced: bool = True
    ) -> str:
        """Execute the text extraction."""
        result = self.pdf_agent.extract_text(input_file, page_numbers, use_advanced)
        if result.success:
            preview = ""
            if result.metadata.get("extracted_text"):
                first_page_key = list(result.metadata["extracted_text"].keys())[0]
                first_page_text = result.metadata["extracted_text"][first_page_key]
                preview = f"\n\nPreview (first 200 chars):\n{first_page_text[:200]}..."

            return (
                f"{result.message}\n"
                f"Total characters: {result.metadata.get('total_characters', 0)}\n"
                f"Saved to: {result.output_files[0]}"
                f"{preview}"
            )
        else:
            return f"Error: {result.message}"

    async def _arun(self, *args, **kwargs):
        """Async version (not implemented)."""
        raise NotImplementedError("Async not supported")


class ExtractPagesTool(BaseTool):
    """Tool for extracting specific pages from a PDF."""

    name: str = "extract_pages_from_pdf"
    description: str = (
        "Extract specific pages from a PDF into a new PDF file. "
        "Input is the file path and a list of page numbers (1-indexed). "
        "Returns the path to the new PDF containing only the specified pages."
    )
    args_schema: Type[BaseModel] = ExtractPagesInput

    def __init__(self, pdf_agent: PDFAgent):
        super().__init__()
        self.pdf_agent = pdf_agent

    def _run(
        self,
        input_file: str,
        page_numbers: List[int],
        output_file: Optional[str] = None
    ) -> str:
        """Execute the page extraction."""
        result = self.pdf_agent.extract_pages(input_file, page_numbers, output_file)
        if result.success:
            return (
                f"{result.message}\n"
                f"Extracted pages: {result.metadata.get('extracted_pages', [])}\n"
                f"Output: {result.output_files[0]}"
            )
        else:
            return f"Error: {result.message}"

    async def _arun(self, *args, **kwargs):
        """Async version (not implemented)."""
        raise NotImplementedError("Async not supported")


class GetPDFMetadataTool(BaseTool):
    """Tool for getting PDF metadata and information."""

    name: str = "get_pdf_metadata"
    description: str = (
        "Get metadata and information about a PDF file, including "
        "title, author, page count, creation date, and page dimensions. "
        "Input is the PDF file path."
    )
    args_schema: Type[BaseModel] = GetMetadataInput

    def __init__(self, pdf_agent: PDFAgent):
        super().__init__()
        self.pdf_agent = pdf_agent

    def _run(self, input_file: str) -> str:
        """Execute the metadata retrieval."""
        result = self.pdf_agent.get_metadata(input_file)
        if result.success:
            metadata_str = "\n".join(
                f"  {key}: {value}"
                for key, value in result.metadata.items()
            )
            return f"{result.message}\n\nMetadata:\n{metadata_str}"
        else:
            return f"Error: {result.message}"

    async def _arun(self, *args, **kwargs):
        """Async version (not implemented)."""
        raise NotImplementedError("Async not supported")


class RotatePagesTool(BaseTool):
    """Tool for rotating PDF pages."""

    name: str = "rotate_pdf_pages"
    description: str = (
        "Rotate pages in a PDF file. "
        "Can rotate all pages or specific pages by 90, 180, or 270 degrees. "
        "Returns the path to the rotated PDF."
    )
    args_schema: Type[BaseModel] = RotatePagesInput

    def __init__(self, pdf_agent: PDFAgent):
        super().__init__()
        self.pdf_agent = pdf_agent

    def _run(
        self,
        input_file: str,
        rotation: int,
        page_numbers: Optional[List[int]] = None,
        output_file: Optional[str] = None
    ) -> str:
        """Execute the rotation operation."""
        result = self.pdf_agent.rotate_pages(
            input_file,
            rotation,
            page_numbers,
            output_file
        )
        if result.success:
            return f"{result.message}\nOutput: {result.output_files[0]}"
        else:
            return f"Error: {result.message}"

    async def _arun(self, *args, **kwargs):
        """Async version (not implemented)."""
        raise NotImplementedError("Async not supported")


def create_pdf_tools(workspace_dir: Optional[str] = None) -> List[BaseTool]:
    """
    Create a list of all PDF tools for use with LangChain agents.

    Args:
        workspace_dir: Directory for PDF output files

    Returns:
        List of LangChain tools for PDF operations
    """
    pdf_agent = PDFAgent(workspace_dir)

    return [
        MergePDFTool(pdf_agent=pdf_agent),
        SplitPDFTool(pdf_agent=pdf_agent),
        ExtractTextTool(pdf_agent=pdf_agent),
        ExtractPagesTool(pdf_agent=pdf_agent),
        GetPDFMetadataTool(pdf_agent=pdf_agent),
        RotatePagesTool(pdf_agent=pdf_agent),
    ]
