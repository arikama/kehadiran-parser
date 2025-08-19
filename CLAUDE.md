# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Rust CLI tool that parses PDF files containing Malaysian Parliament attendance records and extracts structured data about attendees and absentees. The tool processes PDF files from a directory and outputs JSON files with parsed attendance data.

## Common Commands

### Development
- **Build**: `cargo build`
- **Build for release**: `cargo build --release` 
- **Run tests**: `cargo test`
- **Run the program**: `cargo run -- --pdf-dir=/path/to/pdfs --out-dir=/path/to/output`

### Testing
The project includes comprehensive integration tests in `src/lib.rs` that use test files in the `testfiles/` directory. Tests validate the parsing logic against real parliament attendance data from specific dates.

## Architecture

### Core Components
- **main.rs**: CLI entry point using `clap` for argument parsing. Validates input/output directories and calls the main parsing logic.
- **lib.rs**: Contains the core parsing engine with regex-based text extraction logic.

### Key Data Structures
- **ParliamentMeeting**: Main struct containing `attendees` and `absentees` vectors
- **Args**: CLI argument structure for PDF input directory and JSON output directory

### Parsing Logic
The parser uses a state machine approach to process extracted PDF text:
1. Looks for attendance section headers ("ahli-ahli yang hadir:")
2. Switches to absentee processing when encountering absentee headers ("ahli-ahli yang tidak hadir:")
3. Stops processing when encountering "MALAYSIA" marker
4. Uses regex patterns to identify new person entries (numbered lists) and extract names
5. Filters out irrelevant lines using predefined ignore patterns

### Dependencies
- `clap`: Command-line argument parsing
- `pdf-extract`: PDF text extraction
- `regex`: Text pattern matching for parsing
- `serde`/`serde_json`: JSON serialization
- `lazy_static`: Static regex compilation

### Test Data
The `testfiles/` directory contains sample data:
- PDF files: Original parliament documents
- TXT files: Extracted text for testing
- JSON files: Expected output for validation

The parsing logic is specifically tuned for Malaysian Parliament document formats and uses Malay language headers and markers.