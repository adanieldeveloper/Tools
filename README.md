# Tools

Date: 2025-08-20

## Description

This repository contains a collection of tools designed to assist with various tasks. Each tool is implemented in a separate file, and they can be used independently or together as needed.

## Markdown Tools

- [markdown_processor.py](Markdown/markdown_processor.py): A tool that adds numbers to each markdown headers.
  - For example it converts: '# Header' to '# XXX Header', and '## Header' to '## XXX.1' Header, where XXX is the number of the header in the file.
- [update_markdown_headers](Markdown/update_markdown_headers.py): A tool that updates markdown headers in a file.
  - It can be used to add or modify headers in markdown files, ensuring consistency and clarity in documentation. It is used by the `markdown_processor.py` tool.