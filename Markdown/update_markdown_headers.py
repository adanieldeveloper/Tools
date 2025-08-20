#!/usr/bin/env python3
"""
Command Line Interface for Markdown Header Processor

Usage:
    python process_markdown.py input.md [output.md]
    
Arguments:
    input.md    - Path to the input markdown file (required)
    output.md   - Path to the output markdown file (optional)
                  If not provided, the input file will be overwritten
                  
Examples:
    python process_markdown.py document.md
    python process_markdown.py document.md processed_document.md
"""

import sys
import argparse
import re
import os
from typing import Optional


class MarkdownHeaderProcessor:
    def __init__(self, max_header_level: int = 6):
        """
        Initialize the processor with a maximum header level.
        
        Args:
            max_header_level: Maximum number of # symbols to treat as regular headers
        """
        self.max_header_level = max_header_level
        self.counters = [0] * 10  # Support up to 10 levels for safety
    
    def reset_counters(self):
        """Reset all counters to 0."""
        self.counters = [0] * 10
    
    def process_header(self, line: str) -> str:
        """
        Process a single header line and return the formatted version.
        
        Args:
            line: A line from the markdown file
            
        Returns:
            The processed line with proper numbering
        """
        # Preserve the original line ending
        original_ending = ''
        if line.endswith('\n'):
            original_ending = '\n'
        elif line.endswith('\r\n'):
            original_ending = '\r\n'
    
        # Match markdown headers
        header_match = re.match(r'^(#{1,})\s*(.*)', line.strip())
        
        if not header_match:
            return line
        
        hash_symbols = header_match.group(1)
        header_text = header_match.group(2).strip()
        header_level = len(hash_symbols)
        
        # Remove any existing XXX.x.x.x numbering from the header text
        # This handles cases where the file is being reprocessed
        cleaned_text = re.sub(r'^XXX(\.\d+)*\s*', '', header_text)
        
        # Update counters based on header level
        self.counters[header_level - 1] += 1
        
        # Reset all deeper level counters
        for i in range(header_level, len(self.counters)):
            self.counters[i] = 0
        
        # Build the numbering string
        if header_level == 1:
            # Main header: # XXX Header
            formatted_line = f"# XXX {cleaned_text}"
        else:
            # Build the number sequence (e.g., XXX.1.2.3)
            number_parts = ["XXX"]
            for i in range(1, header_level):
                if self.counters[i] > 0:
                    number_parts.append(str(self.counters[i]))
            
            number_string = ".".join(number_parts)
            
            # Check if we exceed max header level
            if header_level > self.max_header_level:
                # Use <p class="h7"> format for headers beyond max level
                # Remove the # characters and just use the numbering and text
                formatted_line = f'<p class="h7">{number_string} {cleaned_text}</p>\n\n'
                # Since we're adding our own newlines, we don't need the original ending
                return formatted_line
            else:
                # Regular markdown header format
                formatted_line = f'{"#" * header_level} {number_string} {cleaned_text}'
        
        # Add back the original line ending for regular headers
        return formatted_line + original_ending
    
    def process_file(self, input_file: str, output_file: Optional[str] = None) -> str:
        """
        Process a markdown file and update header numbering.
        
        Args:
            input_file: Path to the input markdown file
            output_file: Path to the output file (if None, overwrites input)
            
        Returns:
            The processed content as a string
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file '{input_file}' not found.")
        
        # Reset counters for each file
        self.reset_counters()
        
        print(f"📖 Reading file: {input_file}")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        processed_lines = []
        header_count = 0
        
        for line in lines:
            processed_line = self.process_header(line)
            if processed_line != line:  # Header was processed
                header_count += 1
            processed_lines.append(processed_line)
        
        processed_content = ''.join(processed_lines)
        
        # Determine output file
        if output_file is None:
            output_file = input_file
            print(f"📝 Overwriting original file: {input_file}")
        else:
            print(f"💾 Writing to new file: {output_file}")
        
        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        
        print(f"✅ Successfully processed {header_count} headers")
        
        return processed_content


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description='Process markdown files to update header numbering format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.md                    # Overwrite the original file
  %(prog)s input.md output.md             # Create a new processed file
  %(prog)s --max-level 4 document.md     # Set maximum header level to 4
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Path to the input markdown file'
    )
    
    parser.add_argument(
        'output_file',
        nargs='?',
        default=None,
        help='Path to the output markdown file (optional, defaults to overwriting input)'
    )
    
    parser.add_argument(
        '--max-level',
        type=int,
        default=6,
        help='Maximum header level to process as regular headers (default: 6)'
    )
    
    parser.add_argument(
        '--preview',
        action='store_true',
        help='Preview the changes without writing to file'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser


def validate_arguments(args) -> bool:
    """Validate command line arguments."""
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"❌ Error: Input file '{args.input_file}' not found.")
        return False
    
    # Check if input file is a markdown file (optional warning)
    if not args.input_file.lower().endswith(('.md', '.markdown')):
        print(f"⚠️  Warning: '{args.input_file}' doesn't appear to be a markdown file")
    
    # Check max level range
    if args.max_level < 1 or args.max_level > 6:
        print(f"❌ Error: --max-level must be between 1 and 6")
        return False
    
    # Check if we can write to output location
    output_file = args.output_file if args.output_file else args.input_file
    output_dir = os.path.dirname(os.path.abspath(output_file))
    
    if not os.access(output_dir, os.W_OK):
        print(f"❌ Error: Cannot write to directory '{output_dir}'")
        return False
    
    return True


def main():
    """Main function to handle command line processing."""
    parser = create_argument_parser()
    
    # Handle no arguments case
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    try:
        args = parser.parse_args()
    except SystemExit:
        return 1
    
    # Validate arguments
    if not validate_arguments(args):
        return 1
    
    try:
        # Create processor with specified max level
        processor = MarkdownHeaderProcessor(max_header_level=args.max_level)
        
        if args.verbose:
            print(f"🔧 Configuration:")
            print(f"   Input file: {args.input_file}")
            print(f"   Output file: {args.output_file or args.input_file + ' (overwrite)'}")
            print(f"   Max header level: {args.max_level}")
            print(f"   Preview mode: {args.preview}")
            print()
        
        # Process the file
        if args.preview:
            # Preview mode - don't write to file
            print("🔍 Preview mode - showing processed content:\n")
            processor.reset_counters()
            
            with open(args.input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                processed_line = processor.process_header(line)
                if processed_line != line:
                    print(f"Line {i}: {line.strip()}")
                    print(f"    ->: {processed_line.strip()}")
                    print()
            
        else:
            # Normal processing mode
            processed_content = processor.process_file(args.input_file, args.output_file)
            
            if args.verbose:
                print("\n📊 Processing summary:")
                lines = processed_content.split('\n')
                header_lines = [line for line in lines if line.strip().startswith('#') or '<p class="h7">' in line]
                
                print(f"   Total lines processed: {len(lines)}")
                print(f"   Headers found: {len(header_lines)}")
                print(f"   File size: {len(processed_content)} characters")
        
        print("\n🎉 Processing completed successfully!")
        return 0
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return 1
    except PermissionError as e:
        print(f"❌ Error: Permission denied - {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
