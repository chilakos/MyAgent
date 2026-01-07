#!/usr/bin/env python3
"""
Simple PDF Agent Usage Example

This script demonstrates basic PDF operations using the PDFAgent class.
Shows how to merge PDFs, get metadata, split files, and extract pages.
"""

import sys
from pathlib import Path

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.pdf_agent import PDFAgent


def main():
    """Demonstrate basic PDF agent operations."""

    # Initialize the agent with a workspace directory
    # All output files will be saved here
    agent = PDFAgent(workspace_dir="./pdf_output")

    print("=" * 60)
    print("PDF Agent - Simple Usage Examples")
    print("=" * 60)

    # Example 1: Merge multiple PDFs
    print("\n1. Merging PDFs...")
    result = agent.merge_pdfs(
        input_files=["doc1.pdf", "doc2.pdf"],
        output_file="combined.pdf"
    )
    if result.success:
        print(f"   ✓ {result.message}")
        print(f"   Output: {result.output_files[0]}")
    else:
        print(f"   ✗ {result.message}")

    # Example 2: Get PDF metadata
    print("\n2. Getting PDF metadata...")
    result = agent.get_metadata("doc1.pdf")
    if result.success:
        print(f"   ✓ {result.message}")
        print(f"   Pages: {result.metadata['page_count']}")
        print(f"   Size: {result.metadata['file_size_bytes']} bytes")
    else:
        print(f"   ✗ {result.message}")

    # Example 3: Split a PDF (2 pages per file)
    print("\n3. Splitting PDF...")
    result = agent.split_pdf(
        input_file="large_document.pdf",
        pages_per_file=2,
        output_prefix="chapter"
    )
    if result.success:
        print(f"   ✓ {result.message}")
        print(f"   Created {len(result.output_files)} files")
    else:
        print(f"   ✗ {result.message}")

    # Example 4: Extract specific pages
    print("\n4. Extracting specific pages...")
    result = agent.extract_pages(
        input_file="document.pdf",
        page_numbers=[1, 3, 5],
        output_file="selected_pages.pdf"
    )
    if result.success:
        print(f"   ✓ {result.message}")
        print(f"   Output: {result.output_files[0]}")
    else:
        print(f"   ✗ {result.message}")

    # Example 5: Rotate pages
    print("\n5. Rotating pages...")
    result = agent.rotate_pages(
        input_file="scanned.pdf",
        rotation=90,
        page_numbers=[1, 2]  # Rotate only pages 1 and 2
    )
    if result.success:
        print(f"   ✓ {result.message}")
        print(f"   Output: {result.output_files[0]}")
    else:
        print(f"   ✗ {result.message}")

    # Example 6: Extract text content
    print("\n6. Extracting text from PDF...")
    result = agent.extract_text(
        input_file="document.pdf",
        page_numbers=[1],  # Extract from page 1 only
        use_advanced=True
    )
    if result.success:
        print(f"   ✓ {result.message}")
        print(f"   Characters extracted: {result.metadata['total_characters']}")
    else:
        print(f"   ✗ {result.message}")

    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
