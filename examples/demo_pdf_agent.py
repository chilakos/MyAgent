#!/usr/bin/env python3
"""
Interactive demo for the PDF Agent.

This demo shows how to use the PDF agent autonomously with an LLM
to handle various PDF operations through natural language.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.pdf_agent import PDFAgent
from src.agents.pdf_tools import create_pdf_tools
from src.core.llm import create_llm_provider
from src.core.config import Settings

try:
    from langgraph.prebuilt import create_react_agent
    USE_LANGGRAPH = True
except ImportError:
    USE_LANGGRAPH = False

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage


def print_banner():
    """Print a welcome banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║              PDF Agent - Interactive Demo               ║
    ║                                                          ║
    ║  Autonomous PDF operations powered by AI                ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝

    Available Commands:
    ────────────────────────────────────────────────────────────
    merge <file1> <file2> ...  - Merge multiple PDFs
    split <file> [pages/file]  - Split PDF into parts
    extract <file> [pages]     - Extract text from PDF
    pages <file> <page_list>   - Extract specific pages
    info <file>                - Get PDF metadata
    rotate <file> <degrees>    - Rotate PDF pages
    help                       - Show available operations
    demo                       - Run automated demo
    quit/exit                  - Exit the program
    ────────────────────────────────────────────────────────────

    Or just type a natural language request like:
    "Merge documents a.pdf and b.pdf into combined.pdf"
    "Extract pages 1-5 from report.pdf"
    "Get information about my_document.pdf"
    """
    print(banner)


def create_agent_prompt():
    """Create the prompt template for the PDF agent."""
    system_message = """You are an autonomous PDF processing agent with access to tools for manipulating PDF files.

Your capabilities include:
- Merging multiple PDF files
- Splitting PDFs into separate files
- Extracting text content from PDFs
- Extracting specific pages from PDFs
- Getting PDF metadata and information
- Rotating PDF pages

When a user requests a PDF operation:
1. Understand their intent
2. Use the appropriate tool(s) to complete the task
3. Provide clear feedback about what was done
4. Report the output file locations

Important guidelines:
- All output files are saved in the pdf_workspace directory
- Page numbers are 1-indexed (first page is page 1, not 0)
- For file paths, accept both absolute and relative paths
- If a user's request is ambiguous, ask for clarification
- Always confirm successful operations and provide output file paths
- If an error occurs, explain what went wrong clearly

Be helpful, efficient, and precise in your PDF operations."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    return prompt


def run_demo_workflow():
    """Run an automated demo workflow."""
    print("\n" + "=" * 60)
    print("AUTOMATED DEMO MODE")
    print("=" * 60)
    print("\nThis demo will show you how to use the PDF agent.")
    print("It will create sample PDFs and demonstrate operations.\n")

    # Create sample PDFs for demo
    print("Step 1: Creating sample PDF files...")
    from pypdf import PdfWriter

    workspace = Path("./pdf_workspace")
    workspace.mkdir(exist_ok=True)

    # Create sample PDF 1
    pdf1_path = workspace / "sample1.pdf"
    writer1 = PdfWriter()
    writer1.add_blank_page(width=200, height=200)
    writer1.add_blank_page(width=200, height=200)
    with open(pdf1_path, "wb") as f:
        writer1.write(f)
    print(f"  ✓ Created {pdf1_path}")

    # Create sample PDF 2
    pdf2_path = workspace / "sample2.pdf"
    writer2 = PdfWriter()
    writer2.add_blank_page(width=200, height=200)
    writer2.add_blank_page(width=200, height=200)
    writer2.add_blank_page(width=200, height=200)
    with open(pdf2_path, "wb") as f:
        writer2.write(f)
    print(f"  ✓ Created {pdf2_path}")

    # Initialize agent
    pdf_agent = PDFAgent(workspace_dir="./pdf_workspace")

    print("\n" + "-" * 60)
    print("Step 2: Demonstrating PDF operations")
    print("-" * 60)

    # Demo 1: Get metadata
    print("\n📊 Getting metadata from sample1.pdf...")
    result = pdf_agent.get_metadata(str(pdf1_path))
    if result.success:
        print(f"  ✓ {result.message}")
        print(f"    Pages: {result.metadata.get('page_count')}")
        print(f"    Size: {result.metadata.get('file_size_bytes')} bytes")

    # Demo 2: Merge PDFs
    print("\n🔗 Merging sample1.pdf and sample2.pdf...")
    result = pdf_agent.merge_pdfs(
        [str(pdf1_path), str(pdf2_path)],
        output_file="merged_demo.pdf"
    )
    if result.success:
        print(f"  ✓ {result.message}")
        print(f"    Output: {result.output_files[0]}")

    # Demo 3: Split PDF
    print("\n✂️  Splitting merged PDF (2 pages per file)...")
    merged_path = workspace / "merged_demo.pdf"
    result = pdf_agent.split_pdf(
        str(merged_path),
        pages_per_file=2,
        output_prefix="split_demo"
    )
    if result.success:
        print(f"  ✓ {result.message}")
        for output_file in result.output_files[:3]:  # Show first 3
            print(f"    - {Path(output_file).name}")
        if len(result.output_files) > 3:
            print(f"    ... and {len(result.output_files) - 3} more")

    # Demo 4: Extract pages
    print("\n📄 Extracting pages 1-2 from merged PDF...")
    result = pdf_agent.extract_pages(
        str(merged_path),
        page_numbers=[1, 2],
        output_file="extracted_demo.pdf"
    )
    if result.success:
        print(f"  ✓ {result.message}")
        print(f"    Output: {result.output_files[0]}")

    # Demo 5: Rotate pages
    print("\n🔄 Rotating pages in sample1.pdf by 90 degrees...")
    result = pdf_agent.rotate_pages(
        str(pdf1_path),
        rotation=90,
        output_file="rotated_demo.pdf"
    )
    if result.success:
        print(f"  ✓ {result.message}")
        print(f"    Output: {result.output_files[0]}")

    print("\n" + "=" * 60)
    print("DEMO COMPLETE!")
    print("=" * 60)
    print(f"\nAll demo files have been saved to: {workspace.absolute()}")
    print("\nYou can now try the interactive mode to use natural language!")
    print("=" * 60 + "\n")


def run_interactive_mode():
    """Run the interactive PDF agent with LLM."""
    try:
        # Load settings
        settings = Settings()

        # Create LLM provider
        print("Initializing AI agent...")
        llm = create_llm_provider(
            provider_type=settings.llm_provider,
            ollama_base_url=settings.ollama_base_url,
            ollama_model=settings.ollama_model,
            openai_api_key=settings.openai_api_key,
            openai_model=settings.openai_model,
            gemini_api_key=settings.gemini_api_key,
            gemini_model=settings.gemini_model,
        )
        llm.initialize()

        # Create PDF tools
        pdf_tools = create_pdf_tools(workspace_dir="./pdf_workspace")

        # Create agent using langgraph
        agent_executor = create_react_agent(llm.chat_model, pdf_tools)

        print(f"✓ Agent initialized with {settings.llm_provider} ({llm.get_model_info()['model']})")
        print(f"✓ Workspace: ./pdf_workspace/")
        print("\nReady! Type your PDF request or 'help' for commands.\n")

        chat_history = []

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit"]:
                    print("\nGoodbye! 👋")
                    break

                if user_input.lower() == "help":
                    print_banner()
                    continue

                if user_input.lower() == "demo":
                    run_demo_workflow()
                    continue

                # Process with agent
                print("\nAgent: ", end="", flush=True)

                # Add user message to history
                chat_history.append(HumanMessage(content=user_input))

                # Invoke agent with messages
                response = agent_executor.invoke({"messages": chat_history})

                # Get the last message from the agent
                output = response["messages"][-1].content
                print(output)
                print()

                # Update chat history with agent response
                chat_history.append(AIMessage(content=output))

                # Keep history manageable
                if len(chat_history) > 10:
                    chat_history = chat_history[-10:]

            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")
                continue

    except Exception as e:
        print(f"\n❌ Failed to initialize agent: {str(e)}")
        print("\nMake sure you have:")
        print("  1. Installed dependencies: pip install -r requirements.txt")
        print("  2. Set up your .env file with LLM provider credentials")
        print("  3. Have Ollama running (if using Ollama)")
        sys.exit(1)


def main():
    """Main entry point."""
    print_banner()

    # Check if user wants to run demo first
    choice = input("Run automated demo first? (y/n): ").strip().lower()
    if choice in ["y", "yes"]:
        run_demo_workflow()

    # Run interactive mode
    print("\nStarting interactive mode...\n")
    run_interactive_mode()


if __name__ == "__main__":
    main()
