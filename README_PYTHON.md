# Malaysian Parliament Attendance Parser - Python Implementation

This is a Python reimplementation of the Malaysian Parliament attendance parser, originally written in Rust. The tool extracts structured attendance data from Malaysian Parliament meeting PDF files.

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
python tests/kehadiran_parser.py --pdf-dir /path/to/pdfs --out-dir /path/to/output
```

### Example

```bash
python tests/kehadiran_parser.py --pdf-dir testfiles --out-dir output
```

## Dependencies

- **PyPDF2**: For PDF text extraction
- **argparse**: For command-line argument parsing (built-in)
- **re**: For regex pattern matching (built-in)
- **json**: For JSON output (built-in)

## Architecture

### Core Components

- **KehadiranParser**: Main parser class containing the parsing logic
- **ParliamentMeeting**: Data structure holding attendees and absentees lists

### Key Features

- **State Machine**: Processes extracted text using flags to track current parsing state
- **Regex Patterns**: Uses regex to identify section headers and name entries
- **Unicode Support**: Handles Unicode characters in names (including smart quotes)
- **JSON Output**: Generates structured JSON files with attendance data

### Parsing Logic

1. Extract text from PDF files using PyPDF2
2. Process line by line looking for:
   - Attendees header: "ahli-ahli yang hadir:"
   - Absentees header: "ahli-ahli yang tidak hadir:"
   - End marker: "MALAYSIA"
3. Use numbered list regex to identify new person entries
4. Accumulate name words until hitting new entry or section boundary

## Testing

Run all tests with pytest:

```bash
pytest tests/
```

Run specific test files:

```bash
pytest tests/test_kehadiran_parser.py
pytest tests/test_simple.py
pytest tests/test_parser_methods.py
```

Run with verbose output:

```bash
pytest -v tests/
```

## Comparison with Rust Implementation

The Python version produces equivalent output to the original Rust implementation, with some minor formatting differences due to different PDF extraction libraries:

- **Rust**: Uses `pdf-extract` crate
- **Python**: Uses `PyPDF2` library

Both implementations:
- Parse the same data correctly
- Generate identical JSON structure
- Handle the same edge cases
- Support the same CLI interface

## File Structure

```
tests/
  kehadiran_parser.py       # Main parser implementation
  test_kehadiran_parser.py  # Test suite
  simple_test.py           # Basic functionality test
requirements.txt          # Python dependencies
testfiles/               # Sample PDFs and text files for testing
```

## Output Format

The parser generates JSON files with this structure:

```json
{
  "attendees": [
    "Yang di-Pertua Dewan Rakyat, YB. Dato' Johari bin Abdul",
    "Menteri Pertanian Dan Keterjaminan Makanan, Datuk Seri Haji Mohamad Bin Sabu (Kota Raja)",
    ...
  ],
  "absentees": [
    "Perdana Menteri Dan Menteri Kewangan, Dato' Seri Anwar Bin Ibrahim (Tambun)",
    "Timbalan Perdana Menteri Dan Menteri Kemajuan Desa Dan Wilayah, Dato' Seri Dr. Ahmad Zahid Bin Hamidi (Bagan Datuk)",
    ...
  ]
}
```