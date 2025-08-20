"""
Markdown File Processor

This module provides functionality to process markdown files by:
1. Identifying headers (H1-H7)
2. Adding automatic numbering to headers using MarkdownHeaderProcessor
3. Ensuring proper spacing around headers
4. Preserving original content while updating headers

The processor works by extracting headers from the original file, processing them
through the MarkdownHeaderProcessor for numbering, and then replacing the original
headers with the numbered versions while maintaining proper formatting.

Author: Generated for ASP.NET Core Web API Documentation Project
Version: 1.0.0
Dependencies: update_markdown_headers.MarkdownHeaderProcessor

Usage Examples:
    # Process an existing markdown file
    python markdown_processor.py document.md
    
    # Create a sample file for testing
    python -c "from markdown_processor import create_sample_file; create_sample_file()"
    
    # Process the sample file
    python markdown_processor.py sample.md
    
    # Use programmatically
    from markdown_processor import MarkdownFileProcessor
    processor = MarkdownFileProcessor()
    processor.process_markdown_file('my_document.md')
"""

import re
import os
import sys
import tempfile
from typing import List, Tuple

# Add parent directory to path to import from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Markdown.update_markdown_headers import MarkdownHeaderProcessor

class MarkdownFileProcessor:
    """
    A comprehensive markdown file processor that handles header numbering and formatting.
    
    This class provides methods to:
    - Read and parse markdown files
    - Identify headers at all levels (H1-H7)
    - Process headers through MarkdownHeaderProcessor for automatic numbering
    - Ensure proper spacing around headers
    - Write updated content back to the original file
    
    Attributes:
        processor (MarkdownHeaderProcessor): Instance of the header numbering processor
    
    Example:
        processor = MarkdownFileProcessor()
        processor.process_markdown_file('document.md')
    """
    
    def __init__(self):
        """
        Initialize the MarkdownFileProcessor.
        
        Creates an instance of MarkdownHeaderProcessor for handling header numbering.
        """
        self.processor = MarkdownHeaderProcessor()
    
    def read_markdown_file(self, file_path: str) -> str:
        """
        Read the markdown file and return its content.
        
        Args:
            file_path (str): Path to the markdown file to read
            
        Returns:
            str: The complete content of the markdown file
            
        Raises:
            FileNotFoundError: If the specified file doesn't exist
            Exception: If there's an error reading the file
            
        Example:
            content = processor.read_markdown_file('document.md')
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Markdown file not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading file {file_path}: {str(e)}")
    
    def identify_headers(self, content: str) -> List[Tuple[int, str, int]]:
        """
        Identify all headers in the content and return their details.
        
        Scans the content for markdown headers (lines starting with 1-7 hash symbols)
        and returns information about each header found.
        
        Args:
            content (str): The markdown content to scan for headers
            
        Returns:
            List[Tuple[int, str, int]]: List of tuples containing:
                - line_number (int): Zero-based line number where header was found
                - original_header (str): The complete header text including hash symbols
                - level (int): Header level (1-7 corresponding to H1-H7)
                
        Example:
            headers = processor.identify_headers(content)
            # Returns: [(0, '# Main Title', 1), (5, '## Subtitle', 2), ...]
        """
        headers = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Match headers with 1 to 7 hash symbols
            match = re.match(r'^(#{1,7})\s+(.+)', line)
            if match:
                level = len(match.group(1))
                headers.append((i, line, level))
        
        return headers
    
    def create_temporary_file_with_headers_only(self, headers: List[Tuple[int, str, int]]) -> str:
        """
        Create a temporary file containing only the headers for processing.
        
        This method extracts just the header lines and writes them to a temporary file
        that can be processed by MarkdownHeaderProcessor without affecting the original content.
        
        Args:
            headers (List[Tuple[int, str, int]]): List of header information tuples
            
        Returns:
            str: Path to the created temporary file
            
        Raises:
            Exception: If there's an error creating or writing to the temporary file
            
        Example:
            temp_path = processor.create_temporary_file_with_headers_only(headers)
        """
        try:
            # Create a temporary file
            temp_fd, temp_path = tempfile.mkstemp(suffix='.md', text=True)
            
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as temp_file:
                # Write headers to the temporary file
                for _, header_text, level in headers:
                    temp_file.write(header_text + '\n')
            
            return temp_path
        except Exception as e:
            raise Exception(f"Error creating temporary file: {str(e)}")
    
    def ensure_header_spacing(self, content: str) -> str:
        """
        Ensure exactly one blank line before and after each header.
        
        This method processes the content to maintain consistent spacing around headers
        while avoiding multiple consecutive blank lines elsewhere in the document.
        
        Args:
            content (str): The markdown content to format
            
        Returns:
            str: The content with proper header spacing applied
            
        Example:
            formatted_content = processor.ensure_header_spacing(content)
        """
        lines = content.split('\n')
        result_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if current line is a header (1-7 hash symbols)
            is_header = re.match(r'^#{1,7}\s+', line)
            
            if is_header:
                # Add blank line before header (if not at start and previous line isn't blank)
                if result_lines and result_lines[-1].strip() != '':
                    result_lines.append('')
                
                # Add the header
                result_lines.append(line)
                
                # Add blank line after header (if next line exists and isn't blank)
                if i < len(lines) - 1 and lines[i + 1].strip() != '':
                    result_lines.append('')
            else:
                # For non-header lines, avoid multiple consecutive blank lines
                if line.strip() == '':
                    # Only add blank line if previous line wasn't blank
                    if result_lines and result_lines[-1].strip() != '':
                        result_lines.append(line)
                else:
                    result_lines.append(line)
            
            i += 1
        
        return '\n'.join(result_lines)
    
    def replace_headers_in_original(self, original_content: str, original_headers: List[Tuple[int, str, int]], 
                                  updated_headers: List[str]) -> str:
        """
        Replace the original headers with updated numbered headers in the original content.
        
        This method preserves all the original content while only updating the header lines
        with their numbered versions from the MarkdownHeaderProcessor.
        
        Args:
            original_content (str): The original markdown content
            original_headers (List[Tuple[int, str, int]]): Information about original headers
            updated_headers (List[str]): The processed headers with numbering
            
        Returns:
            str: The original content with headers replaced by numbered versions
            
        Example:
            updated_content = processor.replace_headers_in_original(
                original_content, headers, numbered_headers
            )
        """
        lines = original_content.split('\n')
        
        # Create a mapping of line numbers to updated headers
        header_updates = {}
        for i, (line_num, _, _) in enumerate(original_headers):
            if i < len(updated_headers):
                header_updates[line_num] = updated_headers[i].strip()
        
        # Replace headers in the original content
        for line_num, updated_header in header_updates.items():
            if line_num < len(lines):
                lines[line_num] = updated_header
        
        return '\n'.join(lines)
    
    def write_updated_content(self, file_path: str, content: str):
        """
        Write the updated content back to the original file.
        
        Args:
            file_path (str): Path to the file to write to
            content (str): The updated content to write
            
        Raises:
            Exception: If there's an error writing to the file
            
        Example:
            processor.write_updated_content('document.md', updated_content)
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
        except Exception as e:
            raise Exception(f"Error writing to file {file_path}: {str(e)}")
    
    def process_markdown_file(self, file_path: str):
        """
        Main method to process a markdown file according to requirements.
        
        This method orchestrates the entire processing workflow:
        1. Reads the original markdown file
        2. Identifies all headers (H1-H7)
        3. Creates a temporary file with just the headers
        4. Processes headers through MarkdownHeaderProcessor for numbering
        5. Replaces original headers with numbered versions
        6. Ensures proper spacing around headers
        7. Writes the updated content back to the original file
        8. Cleans up temporary files
        
        Args:
            file_path (str): Path to the markdown file to process
            
        Raises:
            Exception: If any step in the processing fails
            
        Example:
            processor = MarkdownFileProcessor()
            processor.process_markdown_file('my_document.md')
        """
        print(f"Processing markdown file: {file_path}")
        
        try:
            # Step 1: Read the markdown file
            print("Step 1: Reading markdown file...")
            original_content = self.read_markdown_file(file_path)
            
            # Step 2: Identify all headers (1-7 hash symbols)
            print("Step 2: Identifying headers...")
            headers = self.identify_headers(original_content)
            print(f"Found {len(headers)} headers:")
            for line_num, header_text, level in headers:
                print(f"  Line {line_num + 1}: H{level} - {header_text}")
            
            if not headers:
                print("No headers found in the file. Nothing to process.")
                return
            
            # Step 3: Create temporary file with ONLY the original headers
            print("Step 3: Creating temporary file with headers only...")
            temp_file_path = self.create_temporary_file_with_headers_only(headers)
            print(f"Temporary file created with {len(headers)} headers: {temp_file_path}")
            
            # Debug: Show temp file content
            with open(temp_file_path, 'r', encoding='utf-8') as f:
                temp_content = f.read()
                print("Temporary file content:")
                print(repr(temp_content))
            
            try:
                # Step 4: Process the temporary file using MarkdownHeaderProcessor
                print("Step 4: Processing headers with numbering using MarkdownHeaderProcessor...")
                
                # Process the temporary file (this modifies the file in place)
                self.processor.process_file(temp_file_path)
                
                # Now read the processed content from the temporary file
                with open(temp_file_path, 'r', encoding='utf-8') as f:
                    processed_headers_content = f.read()
                
                print("Processed content from temp file:")
                print(repr(processed_headers_content))
                
                # Split the processed content into individual headers
                updated_headers = [line for line in processed_headers_content.split('\n') if line.strip()]
                
                print(f"Updated {len(updated_headers)} headers:")
                for i, header in enumerate(updated_headers):
                    print(f"  {i + 1}: {header}")
                
                # Step 5: Replace headers in original content
                print("Step 5: Replacing headers in original content...")
                content_with_updated_headers = self.replace_headers_in_original(
                    original_content, headers, updated_headers
                )
                
                # Step 6: Ensure proper spacing around headers
                print("Step 6: Ensuring proper header spacing...")
                final_content = self.ensure_header_spacing(content_with_updated_headers)
                
                # Step 7: Write updated content back to original file
                print("Step 7: Writing updated content to original file...")
                self.write_updated_content(file_path, final_content)
                
                print("✅ Markdown file processing completed successfully!")
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                    print(f"Temporary file cleaned up: {temp_file_path}")
                except Exception as e:
                    print(f"Warning: Could not clean up temporary file: {e}")
                    
        except Exception as e:
            print(f"❌ Error processing markdown file: {str(e)}")
            raise

def create_sample_file():
    """Create a sample markdown file for demonstration purposes"""
    sample_content = """# CORS in ASP.NET Core Web API

## Introduction

Cross-Origin Resource Sharing (CORS) is a standard mechanism that allows servers to specify who can access their resources and how.

### The Same-Origin Policy

The Same-Origin Policy is a security mechanism enforced by browsers.

#### Same-Origin Request

This is a same-origin request example.

Some content here.

##### Detailed Example

More detailed content here.

###### Implementation Notes

Implementation details here.

####### Enable CORS for Specific Endpoints

To enable CORS for specific endpoints, you can use the `[EnableCors]` attribute on your controllers or actions.

Some code example here.

### How Does CORS Work?

CORS works through several steps that ensure security.

## Enable CORS in ASP.NET Core

When developing applications where the client and server are hosted on different domains.

### Enable CORS Globally

Modify the Program.cs file as follows.

Some code example here.
"""
    
    sample_file = "sample.md"
    with open(sample_file, "w", encoding="utf-8") as f:
        f.write(sample_content)
    
    print(f"Created {sample_file} for testing.")
    return sample_file

def main():
    """Main function to handle command-line arguments"""
    processor = MarkdownFileProcessor()
    
    # Check if a file path was provided as command-line argument
    if len(sys.argv) > 1:
        markdown_file = sys.argv[1]
        
        if os.path.exists(markdown_file):
            try:
                processor.process_markdown_file(markdown_file)
            except Exception as e:
                print(f"Failed to process {markdown_file}: {e}")
                sys.exit(1)
        else:
            print(f"❌ Error: File '{markdown_file}' not found.")
            sys.exit(1)
    else:
        # No argument provided, show usage
        print("❌ Error: No file specified.")
        print("Usage: python markdown_processor.py <filename.md>")
        print("\nTo create a sample file for testing, you can call:")
        print("  create_sample_file()")
        sys.exit(1)

if __name__ == "__main__":
    main()
