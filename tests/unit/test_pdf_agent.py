"""
Unit tests for PDF Agent functionality.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from pypdf import PdfWriter
from src.agents.pdf_agent import PDFAgent, PDFOperationResult


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def pdf_agent(temp_workspace):
    """Create a PDF agent with temporary workspace."""
    return PDFAgent(workspace_dir=temp_workspace)


@pytest.fixture
def sample_pdf_1(temp_workspace):
    """Create a sample PDF with 2 pages."""
    pdf_path = Path(temp_workspace) / "sample1.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.add_blank_page(width=200, height=200)
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return str(pdf_path)


@pytest.fixture
def sample_pdf_2(temp_workspace):
    """Create a sample PDF with 3 pages."""
    pdf_path = Path(temp_workspace) / "sample2.pdf"
    writer = PdfWriter()
    for _ in range(3):
        writer.add_blank_page(width=200, height=200)
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return str(pdf_path)


class TestPDFAgent:
    """Test suite for PDFAgent class."""

    def test_initialization(self, temp_workspace):
        """Test PDF agent initialization."""
        agent = PDFAgent(workspace_dir=temp_workspace)
        assert agent.workspace_dir == Path(temp_workspace)
        assert agent.workspace_dir.exists()

    def test_initialization_default_workspace(self):
        """Test PDF agent initialization with default workspace."""
        agent = PDFAgent()
        assert agent.workspace_dir == Path("./pdf_workspace")

    def test_merge_pdfs_success(self, pdf_agent, sample_pdf_1, sample_pdf_2):
        """Test successful PDF merging."""
        result = pdf_agent.merge_pdfs([sample_pdf_1, sample_pdf_2])

        assert isinstance(result, PDFOperationResult)
        assert result.success is True
        assert len(result.output_files) == 1
        assert Path(result.output_files[0]).exists()
        assert result.metadata["input_count"] == 2

    def test_merge_pdfs_with_output_file(self, pdf_agent, sample_pdf_1, sample_pdf_2):
        """Test PDF merging with custom output filename."""
        result = pdf_agent.merge_pdfs(
            [sample_pdf_1, sample_pdf_2],
            output_file="custom_merge.pdf"
        )

        assert result.success is True
        assert "custom_merge.pdf" in result.output_files[0]

    def test_merge_pdfs_missing_file(self, pdf_agent, sample_pdf_1):
        """Test PDF merging with missing input file."""
        result = pdf_agent.merge_pdfs([sample_pdf_1, "nonexistent.pdf"])

        assert result.success is False
        assert "not found" in result.message.lower()

    def test_split_pdf_by_pages_per_file(self, pdf_agent, sample_pdf_2):
        """Test splitting PDF by pages per file."""
        result = pdf_agent.split_pdf(sample_pdf_2, pages_per_file=2)

        assert result.success is True
        assert len(result.output_files) == 2  # 3 pages, 2 per file = 2 files
        assert result.metadata["total_pages"] == 3
        assert all(Path(f).exists() for f in result.output_files)

    def test_split_pdf_by_page_ranges(self, pdf_agent, sample_pdf_2):
        """Test splitting PDF by custom page ranges."""
        result = pdf_agent.split_pdf(
            sample_pdf_2,
            page_ranges=[(1, 2), (3, 3)]
        )

        assert result.success is True
        assert len(result.output_files) == 2
        assert all(Path(f).exists() for f in result.output_files)

    def test_split_pdf_one_per_page(self, pdf_agent, sample_pdf_1):
        """Test splitting PDF into one file per page."""
        result = pdf_agent.split_pdf(sample_pdf_1)

        assert result.success is True
        assert len(result.output_files) == 2  # 2 pages = 2 files
        assert result.metadata["total_pages"] == 2

    def test_split_pdf_missing_file(self, pdf_agent):
        """Test splitting nonexistent PDF."""
        result = pdf_agent.split_pdf("nonexistent.pdf")

        assert result.success is False
        assert "not found" in result.message.lower()

    def test_extract_text(self, pdf_agent, sample_pdf_1):
        """Test text extraction from PDF."""
        result = pdf_agent.extract_text(sample_pdf_1)

        assert result.success is True
        assert len(result.output_files) == 1
        assert Path(result.output_files[0]).exists()
        assert "extracted_text" in result.metadata
        assert result.metadata["page_count"] == 2

    def test_extract_text_specific_pages(self, pdf_agent, sample_pdf_2):
        """Test text extraction from specific pages."""
        result = pdf_agent.extract_text(sample_pdf_2, page_numbers=[1, 3])

        assert result.success is True
        assert result.metadata["page_count"] == 2
        assert "page_1" in result.metadata["extracted_text"]
        assert "page_3" in result.metadata["extracted_text"]
        assert "page_2" not in result.metadata["extracted_text"]

    def test_extract_text_missing_file(self, pdf_agent):
        """Test text extraction from nonexistent PDF."""
        result = pdf_agent.extract_text("nonexistent.pdf")

        assert result.success is False
        assert "not found" in result.message.lower()

    def test_extract_pages(self, pdf_agent, sample_pdf_2):
        """Test extracting specific pages to new PDF."""
        result = pdf_agent.extract_pages(sample_pdf_2, page_numbers=[1, 3])

        assert result.success is True
        assert len(result.output_files) == 1
        assert Path(result.output_files[0]).exists()
        assert result.metadata["extracted_pages"] == [1, 3]

    def test_extract_pages_out_of_range(self, pdf_agent, sample_pdf_1):
        """Test extracting pages with some out of range."""
        result = pdf_agent.extract_pages(sample_pdf_1, page_numbers=[1, 99])

        assert result.success is True
        assert result.metadata["extracted_pages"] == [1]

    def test_extract_pages_all_invalid(self, pdf_agent, sample_pdf_1):
        """Test extracting only invalid pages."""
        result = pdf_agent.extract_pages(sample_pdf_1, page_numbers=[99, 100])

        assert result.success is False
        assert "no valid pages" in result.message.lower()

    def test_extract_pages_missing_file(self, pdf_agent):
        """Test extracting pages from nonexistent PDF."""
        result = pdf_agent.extract_pages("nonexistent.pdf", page_numbers=[1])

        assert result.success is False
        assert "not found" in result.message.lower()

    def test_get_metadata(self, pdf_agent, sample_pdf_1):
        """Test getting PDF metadata."""
        result = pdf_agent.get_metadata(sample_pdf_1)

        assert result.success is True
        assert "page_count" in result.metadata
        assert result.metadata["page_count"] == 2
        assert "file_size_bytes" in result.metadata
        assert "page_width" in result.metadata
        assert "page_height" in result.metadata

    def test_get_metadata_missing_file(self, pdf_agent):
        """Test getting metadata from nonexistent PDF."""
        result = pdf_agent.get_metadata("nonexistent.pdf")

        assert result.success is False
        assert "not found" in result.message.lower()

    def test_rotate_pages_all(self, pdf_agent, sample_pdf_1):
        """Test rotating all pages."""
        result = pdf_agent.rotate_pages(sample_pdf_1, rotation=90)

        assert result.success is True
        assert len(result.output_files) == 1
        assert Path(result.output_files[0]).exists()
        assert result.metadata["rotation"] == 90
        assert result.metadata["pages_rotated"] == 2

    def test_rotate_pages_specific(self, pdf_agent, sample_pdf_2):
        """Test rotating specific pages."""
        result = pdf_agent.rotate_pages(sample_pdf_2, rotation=180, page_numbers=[1, 3])

        assert result.success is True
        assert result.metadata["rotation"] == 180
        assert result.metadata["pages_rotated"] == 2

    def test_rotate_pages_invalid_rotation(self, pdf_agent, sample_pdf_1):
        """Test rotating with invalid angle."""
        result = pdf_agent.rotate_pages(sample_pdf_1, rotation=45)

        assert result.success is False
        assert "invalid rotation" in result.message.lower()

    def test_rotate_pages_missing_file(self, pdf_agent):
        """Test rotating nonexistent PDF."""
        result = pdf_agent.rotate_pages("nonexistent.pdf", rotation=90)

        assert result.success is False
        assert "not found" in result.message.lower()

    def test_process_task_merge(self, pdf_agent, sample_pdf_1, sample_pdf_2):
        """Test process_task with merge operation."""
        result = pdf_agent.process_task(
            "merge these PDFs",
            input_files=[sample_pdf_1, sample_pdf_2]
        )

        assert result.success is True
        assert len(result.output_files) == 1

    def test_process_task_split(self, pdf_agent, sample_pdf_1):
        """Test process_task with split operation."""
        result = pdf_agent.process_task(
            "split this PDF",
            input_file=sample_pdf_1,
            pages_per_file=1
        )

        assert result.success is True
        assert len(result.output_files) == 2

    def test_process_task_extract_text(self, pdf_agent, sample_pdf_1):
        """Test process_task with extract text operation."""
        result = pdf_agent.process_task(
            "extract text from PDF",
            input_file=sample_pdf_1
        )

        assert result.success is True
        assert "extracted_text" in result.metadata

    def test_process_task_metadata(self, pdf_agent, sample_pdf_1):
        """Test process_task with metadata operation."""
        result = pdf_agent.process_task(
            "get PDF info",
            input_file=sample_pdf_1
        )

        assert result.success is True
        assert "page_count" in result.metadata

    def test_process_task_rotate(self, pdf_agent, sample_pdf_1):
        """Test process_task with rotate operation."""
        result = pdf_agent.process_task(
            "rotate PDF",
            input_file=sample_pdf_1,
            rotation=90
        )

        assert result.success is True
        assert result.metadata["rotation"] == 90

    def test_process_task_unknown(self, pdf_agent):
        """Test process_task with unknown operation."""
        result = pdf_agent.process_task("do something weird")

        assert result.success is False
        assert "unknown task" in result.message.lower()


class TestPDFOperationResult:
    """Test suite for PDFOperationResult dataclass."""

    def test_creation_minimal(self):
        """Test creating result with minimal parameters."""
        result = PDFOperationResult(success=True, message="Test")

        assert result.success is True
        assert result.message == "Test"
        assert result.output_files == []
        assert result.metadata == {}

    def test_creation_full(self):
        """Test creating result with all parameters."""
        result = PDFOperationResult(
            success=True,
            message="Test",
            output_files=["file1.pdf", "file2.pdf"],
            metadata={"key": "value"}
        )

        assert result.success is True
        assert result.message == "Test"
        assert len(result.output_files) == 2
        assert result.metadata["key"] == "value"
