#!/usr/bin/env python3

import pytest
from kehadiran_parser import KehadiranParser


def test_basic_parser_functionality():
    """Test basic parser functionality."""
    parser = KehadiranParser()
    
    with open('testfiles/2023-05-24.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    parsed = parser.parse_content(content)
    
    # Test basic functionality
    assert len(parsed.attendees) > 0, "Should have attendees"
    assert len(parsed.absentees) > 0, "Should have absentees"
    assert len(parsed.attendees) == 178, f"Expected 178 attendees, got {len(parsed.attendees)}"
    assert len(parsed.absentees) == 45, f"Expected 45 absentees, got {len(parsed.absentees)}"
    
    # Check first entry matches expected format
    first_attendee = parsed.attendees[0]
    assert "Yang di-Pertua Dewan Rakyat" in first_attendee, f"Unexpected first attendee: {first_attendee}"