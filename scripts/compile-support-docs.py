#!/usr/bin/env python3
"""
Compile Support Docs Script

Aggregates all Mintlify documentation into a single text file for use as
context in the support chatbot.

Usage:
    python compile-support-docs.py

Output:
    ../../../marketing/support-docs.txt (relative to this script)
    Publicly accessible at https://www.getchatads.com/support-docs.txt

The script:
1. Finds all .mdx files in the /docs directory
2. Excludes snippets and non-content files
3. Extracts content, stripping frontmatter and JSX components
4. Outputs with clear section separators
"""

import re
import glob
from pathlib import Path


def get_script_dir() -> Path:
    """Get the directory where this script is located."""
    return Path(__file__).parent.resolve()


def get_docs_dir() -> Path:
    """Get the docs directory (parent of scripts/)."""
    return get_script_dir().parent


def get_output_path() -> Path:
    """Get the output file path in the marketing directory."""
    docs_dir = get_docs_dir()
    # Navigate from /docs to /marketing
    return docs_dir.parent / "marketing" / "support-docs.txt"


def extract_frontmatter_title(content: str, filepath: Path) -> str:
    """
    Extract title from YAML frontmatter, or derive from filename.

    Frontmatter format:
    ---
    title: "Page Title"
    description: "..."
    ---
    """
    # Match frontmatter block
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)

    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        # Extract title field
        title_match = re.search(r'^title:\s*["\']?([^"\'\n]+)["\']?\s*$', frontmatter, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()

    # Fallback: derive from filename
    return filepath.stem.replace('-', ' ').replace('_', ' ').title()


def strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter from the beginning of the content."""
    return re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)


def strip_mdx_components(content: str) -> str:
    """
    Strip JSX/MDX components while preserving text content.

    Handles:
    - Self-closing tags: <Card ... />
    - Tag pairs with content: <Warning>text</Warning>
    - Nested components: <CardGroup><Card>...</Card></CardGroup>
    - Multi-line components
    """
    # Remove self-closing JSX tags (e.g., <Card ... />)
    content = re.sub(r'<[A-Z][a-zA-Z]*\s+[^>]*/>', '', content)

    # Remove opening tags with attributes (e.g., <Card title="..." icon="...">)
    # Keep the text content between tags
    content = re.sub(r'<[A-Z][a-zA-Z]*(?:\s+[^>]*)?>', '', content)

    # Remove closing tags (e.g., </Card>, </Warning>)
    content = re.sub(r'</[A-Z][a-zA-Z]*>', '', content)

    # Clean up any remaining JSX-style tags that might be malformed
    content = re.sub(r'<[A-Z][a-zA-Z]*\s*/>', '', content)

    return content


def clean_whitespace(content: str) -> str:
    """Clean up excessive whitespace while preserving code blocks."""
    # Preserve code blocks
    code_blocks = []

    def save_code_block(match):
        code_blocks.append(match.group(0))
        return f'__CODE_BLOCK_{len(code_blocks) - 1}__'

    # Save code blocks temporarily
    content = re.sub(r'```[\s\S]*?```', save_code_block, content)

    # Collapse multiple blank lines to single blank line
    content = re.sub(r'\n{3,}', '\n\n', content)

    # Remove trailing whitespace from lines
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)

    # Restore code blocks
    for i, block in enumerate(code_blocks):
        content = content.replace(f'__CODE_BLOCK_{i}__', block)

    return content.strip()


def process_mdx_file(filepath: Path, docs_dir: Path) -> tuple[str, str]:
    """
    Process a single MDX file and return (title, cleaned_content).
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title before stripping frontmatter
    title = extract_frontmatter_title(content, filepath)

    # Strip frontmatter
    content = strip_frontmatter(content)

    # Strip MDX/JSX components
    content = strip_mdx_components(content)

    # Clean up whitespace
    content = clean_whitespace(content)

    # Get relative path for SOURCE field
    relative_path = filepath.relative_to(docs_dir)

    return title, str(relative_path), content


def should_include_file(filepath: Path, docs_dir: Path) -> bool:
    """
    Determine if a file should be included in the output.

    Excludes:
    - Files in snippets/ directory (reusable fragments, not standalone docs)
    - Non-content files
    """
    relative_path = filepath.relative_to(docs_dir)
    relative_str = str(relative_path)

    # Exclude snippets directory
    if relative_str.startswith('snippets/') or relative_str.startswith('snippets\\'):
        return False

    return True


def compile_docs() -> str:
    """
    Compile all documentation into a single string.
    """
    docs_dir = get_docs_dir()

    # Find all MDX files
    mdx_pattern = docs_dir / "**" / "*.mdx"
    mdx_files = sorted(glob.glob(str(mdx_pattern), recursive=True))

    sections = []
    processed_count = 0
    skipped_count = 0
    failed_files = []

    for mdx_path in mdx_files:
        filepath = Path(mdx_path)

        if not should_include_file(filepath, docs_dir):
            skipped_count += 1
            continue

        try:
            title, source, content = process_mdx_file(filepath, docs_dir)

            section = f"""================================================================================
SECTION: {title}
SOURCE: {source}
================================================================================

{content}
"""
            sections.append(section)
            processed_count += 1

        except Exception as e:
            print(f"Warning: Failed to process {filepath}: {e}")
            failed_files.append(str(filepath))

    # Add header with metadata
    header = f"""ChatAds Documentation
Generated for Support Chatbot Context
================================================================================

This file contains the complete ChatAds documentation compiled from {processed_count} pages.
Use this as context when answering user questions about ChatAds.

"""

    output = header + "\n\n".join(sections)

    print(f"Processed {processed_count} files, skipped {skipped_count} files")
    if failed_files:
        print(f"Failed to process {len(failed_files)} files:")
        for f in failed_files:
            print(f"  - {f}")

    return output


def main() -> None:
    """Main entry point."""
    import sys

    print("Compiling ChatAds documentation for support chatbot...")
    print()

    # Compile documentation
    output = compile_docs()

    # Get output path
    output_path = get_output_path()

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write output file with error handling
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
    except (IOError, OSError) as e:
        print(f"\nCRITICAL: Failed to write to output file {output_path}.")
        print(f"Error: {e}")
        sys.exit(1)

    print()
    print(f"Output written to: {output_path}")
    print(f"File size: {len(output):,} characters")

    # Verify it's accessible (just check the path)
    if output_path.exists():
        print("File exists and is ready for deployment")
        print("Will be accessible at: https://www.getchatads.com/support-docs.txt")


if __name__ == "__main__":
    main()
