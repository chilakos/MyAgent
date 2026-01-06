# PDF Agent Documentation

## Overview

The PDF Agent is an autonomous AI-powered tool for handling various PDF operations. It can merge, split, extract text, rotate pages, and more - all through natural language commands or direct API calls.

## Features

- **Merge PDFs**: Combine multiple PDF files into a single document
- **Split PDFs**: Divide a PDF into separate files (by page count, page ranges, or individual pages)
- **Extract Text**: Extract text content from PDFs with advanced parsing
- **Extract Pages**: Extract specific pages into a new PDF
- **Get Metadata**: Retrieve PDF information (title, author, page count, dimensions, etc.)
- **Rotate Pages**: Rotate pages by 90, 180, or 270 degrees
- **Autonomous Processing**: Use natural language to describe PDF tasks

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `pypdf` - Core PDF manipulation library
- `pdfplumber` - Advanced text extraction
- `langchain` - LLM integration for natural language processing

### 2. Configure LLM Provider

Create a `.env` file in the project root:

```bash
# Choose your LLM provider (ollama, openai, or gemini)
LLM_PROVIDER=ollama

# Ollama settings (for local/offline use)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# OpenAI settings (for production use)
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4

# Gemini settings
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-pro
```

## Quick Start

### Interactive Demo

Run the interactive demo to see the PDF agent in action:

```bash
python examples/demo_pdf_agent.py
```

This will:
1. Offer to run an automated demo showing all capabilities
2. Start an interactive session where you can use natural language

### Using the Demo

**Automated Demo:**
```
Run automated demo first? (y/n): y
```

**Interactive Mode - Natural Language:**
```
You: Merge report1.pdf and report2.pdf into final_report.pdf
Agent: Successfully merged 2 PDFs
       Output: ./pdf_workspace/final_report.pdf

You: Extract pages 1-5 from final_report.pdf
Agent: Successfully extracted 5 pages
       Output: ./pdf_workspace/final_report_pages_1_2_3_4_5.pdf

You: Get information about final_report.pdf
Agent: Successfully retrieved PDF metadata
       Page count: 10
       Size: 45230 bytes
       ...
```

**Interactive Mode - Quick Commands:**
```
merge <file1> <file2> ...  - Merge multiple PDFs
split <file> [pages/file]  - Split PDF into parts
extract <file> [pages]     - Extract text from PDF
pages <file> <page_list>   - Extract specific pages
info <file>                - Get PDF metadata
rotate <file> <degrees>    - Rotate PDF pages
```

## Programmatic Usage

### Basic Operations

```python
from src.agents.pdf_agent import PDFAgent

# Initialize agent
agent = PDFAgent(workspace_dir="./my_pdfs")

# Merge PDFs
result = agent.merge_pdfs(
    input_files=["doc1.pdf", "doc2.pdf", "doc3.pdf"],
    output_file="merged.pdf"
)
if result.success:
    print(f"Merged PDF saved to: {result.output_files[0]}")

# Split PDF (2 pages per file)
result = agent.split_pdf(
    input_file="large_document.pdf",
    pages_per_file=2,
    output_prefix="chapter"
)
print(f"Created {len(result.output_files)} files")

# Split by custom page ranges
result = agent.split_pdf(
    input_file="report.pdf",
    page_ranges=[(1, 5), (6, 10), (11, 15)]
)

# Extract text from all pages
result = agent.extract_text(
    input_file="document.pdf",
    use_advanced=True  # Use pdfplumber for better extraction
)
print(result.metadata["extracted_text"]["page_1"])

# Extract specific pages
result = agent.extract_text(
    input_file="book.pdf",
    page_numbers=[1, 5, 10]  # Only these pages
)

# Extract pages to new PDF
result = agent.extract_pages(
    input_file="presentation.pdf",
    page_numbers=[1, 3, 5, 7],
    output_file="slides_excerpt.pdf"
)

# Get PDF metadata
result = agent.get_metadata("document.pdf")
print(f"Pages: {result.metadata['page_count']}")
print(f"Author: {result.metadata['author']}")
print(f"Size: {result.metadata['file_size_bytes']} bytes")

# Rotate pages
result = agent.rotate_pages(
    input_file="scanned.pdf",
    rotation=90,  # or 180, 270
    page_numbers=[2, 4, 6]  # Only specific pages
)
```

### Using with LangChain Tools

```python
from src.agents.pdf_tools import create_pdf_tools
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from src.core.llm import create_llm_provider

# Create LLM
llm = create_llm_provider(provider_type="ollama")
llm.initialize()

# Create PDF tools
pdf_tools = create_pdf_tools(workspace_dir="./pdfs")

# Create agent prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a PDF processing assistant..."),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Create agent
agent = create_tool_calling_agent(llm.chat_model, pdf_tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=pdf_tools, verbose=True)

# Process natural language requests
response = agent_executor.invoke({
    "input": "Merge all PDFs in the reports folder and extract text from the result"
})
print(response["output"])
```

## API Reference

### PDFAgent Class

#### `__init__(workspace_dir: Optional[str] = None)`
Initialize the PDF agent with a workspace directory for output files.

**Parameters:**
- `workspace_dir` (str, optional): Directory for output files. Defaults to `./pdf_workspace`

---

#### `merge_pdfs(input_files: List[str], output_file: Optional[str] = None) -> PDFOperationResult`
Merge multiple PDF files into one.

**Parameters:**
- `input_files` (List[str]): List of PDF file paths to merge
- `output_file` (str, optional): Output filename (auto-generated if None)

**Returns:** `PDFOperationResult` with merged PDF path

---

#### `split_pdf(input_file: str, pages_per_file: Optional[int] = None, page_ranges: Optional[List[tuple]] = None, output_prefix: Optional[str] = None) -> PDFOperationResult`
Split a PDF into multiple files.

**Parameters:**
- `input_file` (str): Input PDF path
- `pages_per_file` (int, optional): Pages per output file
- `page_ranges` (List[tuple], optional): Custom ranges like `[(1,5), (6,10)]`
- `output_prefix` (str, optional): Prefix for output filenames

**Returns:** `PDFOperationResult` with list of output files

---

#### `extract_text(input_file: str, page_numbers: Optional[List[int]] = None, use_advanced: bool = True) -> PDFOperationResult`
Extract text content from PDF.

**Parameters:**
- `input_file` (str): Input PDF path
- `page_numbers` (List[int], optional): Specific pages (1-indexed). All pages if None.
- `use_advanced` (bool): Use pdfplumber for better extraction

**Returns:** `PDFOperationResult` with extracted text in metadata

---

#### `extract_pages(input_file: str, page_numbers: List[int], output_file: Optional[str] = None) -> PDFOperationResult`
Extract specific pages to a new PDF.

**Parameters:**
- `input_file` (str): Input PDF path
- `page_numbers` (List[int]): Pages to extract (1-indexed)
- `output_file` (str, optional): Output filename

**Returns:** `PDFOperationResult` with new PDF path

---

#### `get_metadata(input_file: str) -> PDFOperationResult`
Get PDF metadata and information.

**Parameters:**
- `input_file` (str): Input PDF path

**Returns:** `PDFOperationResult` with metadata dict

**Metadata includes:**
- `title`, `author`, `subject`, `creator`, `producer`
- `creation_date`, `modification_date`
- `page_count`, `file_size_bytes`
- `page_width`, `page_height`

---

#### `rotate_pages(input_file: str, rotation: int, page_numbers: Optional[List[int]] = None, output_file: Optional[str] = None) -> PDFOperationResult`
Rotate pages in a PDF.

**Parameters:**
- `input_file` (str): Input PDF path
- `rotation` (int): Rotation angle (90, 180, or 270)
- `page_numbers` (List[int], optional): Pages to rotate. All pages if None.
- `output_file` (str, optional): Output filename

**Returns:** `PDFOperationResult` with rotated PDF path

---

#### `process_task(task_description: str, **kwargs) -> PDFOperationResult`
Process a natural language task description.

**Parameters:**
- `task_description` (str): Natural language description
- `**kwargs`: Additional arguments for the operation

**Returns:** `PDFOperationResult` with task outcome

**Example:**
```python
agent.process_task(
    "merge these files",
    input_files=["a.pdf", "b.pdf"]
)
```

### PDFOperationResult

Result object returned by all PDF operations.

**Attributes:**
- `success` (bool): Whether the operation succeeded
- `message` (str): Human-readable message
- `output_files` (List[str]): Paths to created files
- `metadata` (Dict[str, Any]): Additional operation-specific data

## LangChain Tools

The following tools are available for LangChain agent integration:

1. **merge_pdfs** - Merge multiple PDFs
2. **split_pdf** - Split PDF into parts
3. **extract_text_from_pdf** - Extract text content
4. **extract_pages_from_pdf** - Extract specific pages
5. **get_pdf_metadata** - Get PDF information
6. **rotate_pdf_pages** - Rotate pages

Create all tools:
```python
from src.agents.pdf_tools import create_pdf_tools
tools = create_pdf_tools(workspace_dir="./pdfs")
```

## Architecture

```
src/agents/
├── pdf_agent.py      # Core PDFAgent class with operations
└── pdf_tools.py      # LangChain tool wrappers

examples/
└── demo_pdf_agent.py # Interactive demo

tests/unit/
└── test_pdf_agent.py # Unit tests (30 tests)
```

### Design Principles

1. **Autonomous**: Agent handles complex multi-step operations
2. **Safe**: Validates inputs, handles errors gracefully
3. **Flexible**: Direct API or natural language interface
4. **Tested**: Comprehensive unit test coverage
5. **Extensible**: Easy to add new PDF operations

## Workspace Directory

All output files are saved to the workspace directory (default: `./pdf_workspace`).

**Structure:**
```
pdf_workspace/
├── merged_output.pdf
├── split_part1.pdf
├── split_part2.pdf
├── extracted_text.txt
└── rotated_output.pdf
```

## Error Handling

All operations return `PDFOperationResult` with success status:

```python
result = agent.merge_pdfs(["a.pdf", "missing.pdf"])
if not result.success:
    print(f"Error: {result.message}")
    # Error: Input file not found: missing.pdf
else:
    print(f"Success: {result.output_files[0]}")
```

## Testing

Run unit tests:
```bash
pytest tests/unit/test_pdf_agent.py -v
```

**Test Coverage:**
- ✅ 30 unit tests
- ✅ All PDF operations (merge, split, extract, rotate, metadata)
- ✅ Error handling (missing files, invalid inputs)
- ✅ Edge cases (page ranges, out of bounds)

## Performance Tips

1. **Text Extraction**: Set `use_advanced=True` for better results with pdfplumber
2. **Large PDFs**: Split operations are I/O bound - SSD recommended
3. **Batch Operations**: Process multiple PDFs in parallel using threading
4. **Memory**: Large PDFs are loaded into memory - ensure sufficient RAM

## Common Use Cases

### 1. Batch Merge Documents
```python
agent = PDFAgent()
result = agent.merge_pdfs(
    input_files=["chapter1.pdf", "chapter2.pdf", "chapter3.pdf"],
    output_file="full_book.pdf"
)
```

### 2. Extract Specific Chapters
```python
result = agent.extract_pages(
    input_file="textbook.pdf",
    page_numbers=list(range(50, 101)),  # Pages 50-100
    output_file="chapter3.pdf"
)
```

### 3. Search PDF Content
```python
result = agent.extract_text("document.pdf")
text = result.metadata["extracted_text"]["page_1"]
if "keyword" in text:
    print("Found keyword on page 1")
```

### 4. Prepare for Printing
```python
# Rotate landscape pages to portrait
agent.rotate_pages(
    input_file="mixed_orientation.pdf",
    rotation=90,
    page_numbers=[2, 4, 6, 8]
)
```

## Troubleshooting

### Issue: "pypdf not found"
**Solution:** Install dependencies
```bash
pip install pypdf pdfplumber
```

### Issue: Poor text extraction quality
**Solution:** Enable advanced extraction
```python
result = agent.extract_text(file, use_advanced=True)
```

### Issue: "Permission denied" when writing
**Solution:** Check workspace directory permissions
```bash
chmod 755 ./pdf_workspace
```

### Issue: LLM not responding
**Solution:** Check `.env` configuration and LLM availability
```bash
# For Ollama
ollama list  # Check if models are installed
ollama run mistral  # Test model

# For OpenAI
echo $OPENAI_API_KEY  # Verify API key is set
```

## Future Enhancements

Planned features:
- [ ] Add watermarks to PDFs
- [ ] Compress PDFs to reduce file size
- [ ] Convert images to PDF
- [ ] OCR for scanned documents
- [ ] Encrypt/decrypt PDFs
- [ ] Form field extraction
- [ ] Batch processing CLI

## License

This PDF Agent is part of the MyAgent project.

## Contributing

To add new PDF operations:

1. Add method to `PDFAgent` class in `src/agents/pdf_agent.py`
2. Create corresponding LangChain tool in `src/agents/pdf_tools.py`
3. Add unit tests in `tests/unit/test_pdf_agent.py`
4. Update this documentation

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review unit tests for usage examples
3. Examine `examples/demo_pdf_agent.py` for reference
4. Open an issue on the project repository
