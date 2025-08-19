#!/usr/bin/env python3

import os
import json
import re
import argparse
import unicodedata
from pathlib import Path
from typing import List, Dict, Set
import PyPDF2

class ParliamentMeeting:
    def __init__(self):
        self.attendees: List[str] = []
        self.absentees: List[str] = []
    
    def to_dict(self) -> Dict:
        return {
            "attendees": self.attendees,
            "absentees": self.absentees
        }

class KehadiranParser:
    def __init__(self):
        # Constants
        self.ATTENDEES_HEADER = "ahli-ahli yang hadir:"
        self.ABSENTEES_HEADER = "ahli-ahli yang tidak hadir:"
        self.MALAYSIA = "MALAYSIA"
        
        # Line ignores set
        self.LINE_IGNORES: Set[str] = {
            "DR.",
            "Ahli-ahli Yang Hadir:",
            "Senator Yang Turut Hadir:",
            "Ahli-ahli Yang Tidak Hadir:",
            "Ahli-Ahli Yang Tidak Hadir:",
            "Ahli-Ahli Yang Tidak Hadir Di Bawah Peraturan Mesyuarat 91"
        }
        
        # Compiled regex patterns
        self.DR_REGEX = re.compile(r"DR\. +\d{1,2}\.\d{1,2}\.\d{1,4} +\d+")
        self.NUMBERED_LIST_REGEX = re.compile(r"^\d+\.\s")
        self.NAME_REGEX = re.compile(r"[A-Z()][^0-9]*", re.UNICODE)
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    def normalize_text(self, text: str) -> str:
        """Normalize unicode text to ASCII equivalents."""
        # Common unicode to ASCII mappings
        replacements = {
            ''': "'",  # Smart apostrophe to regular apostrophe
            ''': "'",  # Smart apostrophe to regular apostrophe
            '"': '"',  # Smart quote to regular quote
            '"': '"',  # Smart quote to regular quote
            '–': '-',  # En dash to hyphen
            '—': '-',  # Em dash to hyphen
            '…': '...',  # Ellipsis to three dots
        }
        
        # Apply specific replacements first
        for unicode_char, ascii_char in replacements.items():
            text = text.replace(unicode_char, ascii_char)
        
        # More aggressive apostrophe normalization  
        # Replace all variants of apostrophes with regular ASCII apostrophe
        import re
        # Pattern to match various apostrophe-like characters
        apostrophe_pattern = re.compile(r'[''`´]')
        text = apostrophe_pattern.sub("'", text)
        
        # Pattern to match various quote-like characters
        quote_pattern = re.compile(r'[""„«»]')
        text = quote_pattern.sub('"', text)
        
        # Then try to normalize remaining characters to ASCII
        normalized = unicodedata.normalize('NFKD', text)
        ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
        
        return ascii_text
    
    def should_ignore_line(self, line: str) -> bool:
        """Check if line should be ignored."""
        if self.DR_REGEX.search(line):
            return True
        return line in self.LINE_IGNORES
    
    def is_attendees_header(self, line: str) -> bool:
        """Check if line is attendees header."""
        line_lower = line.strip().lower()
        return self.ATTENDEES_HEADER in line_lower
    
    def is_absentees_header(self, line: str) -> bool:
        """Check if line is absentees header."""
        line_lower = line.strip().lower()
        return self.ABSENTEES_HEADER in line_lower
    
    def is_numbered_list(self, line: str) -> bool:
        """Check if line starts a numbered list entry."""
        return bool(self.NUMBERED_LIST_REGEX.match(line))
    
    def is_start_of_new_person(self, line: str) -> bool:
        """Check if line starts a new person entry."""
        return self.is_numbered_list(line)
    
    def get_name_words(self, line: str) -> List[str]:
        """Extract name words from line using regex."""
        match = self.NAME_REGEX.search(line)
        if match:
            name_words = []
            for word in match.group(0).split():
                if word.strip():
                    name_words.append(word)
            return name_words
        return []
    
    def parse_content(self, content: str) -> ParliamentMeeting:
        """Parse extracted PDF content and return ParliamentMeeting."""
        meeting = ParliamentMeeting()
        
        # Attendees state
        attendees_process_flag = False
        attendees_done_flag = False
        
        # Absentees state  
        absentees_process_flag = False
        absentees_done_flag = False
        
        # Current person being processed
        current_words = []
        
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Normalize unicode characters to ASCII
            line = self.normalize_text(line)
            
            # Check for attendees header
            if self.is_attendees_header(line) and not attendees_done_flag:
                attendees_process_flag = True
            
            # Check for absentees header
            if self.is_absentees_header(line) and not absentees_done_flag:
                absentees_process_flag = True
                attendees_process_flag = False
                attendees_done_flag = True
                
                if current_words:
                    meeting.attendees.append(self.normalize_text(" ".join(current_words)))
                    current_words = []
            
            # Check for MALAYSIA marker (end of absentees)
            if self.MALAYSIA in line:
                absentees_process_flag = False
                absentees_done_flag = True
                
                if current_words:
                    meeting.absentees.append(self.normalize_text(" ".join(current_words)))
                    current_words = []
            
            # Process attendees
            if attendees_process_flag:
                if self.should_ignore_line(line):
                    continue
                if self.is_start_of_new_person(line):
                    if current_words:
                        meeting.attendees.append(self.normalize_text(" ".join(current_words)))
                        current_words = []
                current_words.extend(self.get_name_words(line))
            
            # Process absentees
            if absentees_process_flag:
                if self.should_ignore_line(line):
                    continue
                if self.is_start_of_new_person(line):
                    if current_words:
                        meeting.absentees.append(self.normalize_text(" ".join(current_words)))
                        current_words = []
                current_words.extend(self.get_name_words(line))
        
        return meeting
    
    def extract_name_from_line(self, line: str) -> str:
        """Extract name from a line, removing numbered list prefix if present."""
        if self.is_numbered_list(line):
            # Remove the numbered list prefix (e.g., "1. ")
            return self.NUMBERED_LIST_REGEX.sub("", line)
        return line
    
    def is_malaysia_marker(self, line: str) -> bool:
        """Check if line contains Malaysia marker."""
        line_clean = line.strip().lower()
        malaysia_lower = self.MALAYSIA.lower()
        
        # Check if line is exactly "MALAYSIA" or "MALAYSIA" as a complete word
        import re
        # Use word boundary to ensure "MALAYSIA" is a complete word
        pattern = r'\b' + re.escape(malaysia_lower) + r'\b'
        return bool(re.search(pattern, line_clean))
    
    def get_output_json_path(self, out_dir: Path, pdf_path: Path) -> Path:
        """Get output JSON file path."""
        return out_dir / f"{pdf_path.stem}.json"
    
    def run(self, pdf_dir: str, out_dir: str) -> None:
        """Main processing function."""
        pdf_path = Path(pdf_dir)
        output_path = Path(out_dir)
        
        if not pdf_path.is_dir():
            raise ValueError("pdf_dir must be a directory")
        
        if not output_path.is_dir():
            raise ValueError("out_dir must be a directory")
        
        print(f"pdf_dir:{pdf_path} out_dir:{output_path}")
        
        # Process all PDF files in directory
        for file_path in pdf_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() == '.pdf':
                print(f"parsing pdf file: pdf_file={file_path}")
                
                # Extract text from PDF
                content = self.extract_text_from_pdf(str(file_path))
                if not content:
                    continue
                
                # Parse content
                parsed_meeting = self.parse_content(content)
                
                # Convert to JSON
                json_data = json.dumps(parsed_meeting.to_dict(), indent=2, ensure_ascii=False)
                
                # Write to output file
                json_file_path = self.get_output_json_path(output_path, file_path)
                print(f"saving json file: json_file={json_file_path}")
                
                with open(json_file_path, 'w', encoding='utf-8') as json_file:
                    json_file.write(json_data)

def main():
    parser = argparse.ArgumentParser(
        description="Program to parse PDF of Malaysian MPs attendance"
    )
    parser.add_argument(
        "-p", "--pdf-dir",
        required=True,
        help="Path to the PDF directory"
    )
    parser.add_argument(
        "-o", "--out-dir", 
        required=True,
        help="Path to the output directory"
    )
    
    args = parser.parse_args()
    
    try:
        kehadiran_parser = KehadiranParser()
        kehadiran_parser.run(args.pdf_dir, args.out_dir)
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())