#!/usr/bin/env python3

import pytest
from kehadiran_parser import KehadiranParser, ParliamentMeeting


@pytest.fixture
def parser():
    """Create a parser instance for tests."""
    return KehadiranParser()


class TestParserMethods:
    """Test individual parser methods."""
    
    def test_parliament_meeting_to_dict(self):
        """Test ParliamentMeeting to_dict conversion."""
        meeting = ParliamentMeeting()
        meeting.attendees = ["John Doe", "Jane Smith"]
        meeting.absentees = ["Bob Johnson"]
        
        expected = {
            "attendees": ["John Doe", "Jane Smith"],
            "absentees": ["Bob Johnson"]
        }
        assert meeting.to_dict() == expected

    def test_is_attendees_header_variations(self, parser):
        """Test different attendees header variations."""
        valid_headers = [
            "Ahli-ahli Yang Hadir:",
            " ahli-ahli yang hadir: ",
            "AHLI-AHLI YANG HADIR:",
            "  Ahli-Ahli Yang Hadir:  "
        ]
        for header in valid_headers:
            assert parser.is_attendees_header(header)
        
        invalid_headers = [
            "Ahli-ahli Yang Tidak Hadir:",
            "Random text",
            "ahli yang hadir"
        ]
        for header in invalid_headers:
            assert not parser.is_attendees_header(header)

    def test_is_absentees_header_variations(self, parser):
        """Test different absentees header variations."""
        valid_headers = [
            "Ahli-Ahli Yang Tidak Hadir:",
            " ahli-ahli yang tidak hadir: ",
            "AHLI-AHLI YANG TIDAK HADIR:",
            "  Ahli-Ahli Yang Tidak Hadir:  "
        ]
        for header in valid_headers:
            assert parser.is_absentees_header(header)
        
        invalid_headers = [
            "Ahli-ahli Yang Hadir:",
            "Random text",
            "ahli yang tidak"
        ]
        for header in invalid_headers:
            assert not parser.is_absentees_header(header)

    def test_is_numbered_list(self, parser):
        """Test numbered list detection."""
        valid_lists = [
            "1. John Doe",
            "25. Jane Smith (Constituency)",
            "123. Bob Johnson",
            "9. Short"
        ]
        for line in valid_lists:
            assert parser.is_numbered_list(line)
        
        invalid_lists = [
            "John Doe",
            "a. Invalid",
            ". Invalid",
            "1 Invalid",
            " 1. Invalid"  # Leading space
        ]
        for line in invalid_lists:
            assert not parser.is_numbered_list(line)

    def test_should_ignore_line(self, parser):
        """Test line ignoring logic."""
        ignored_lines = [
            "DR.",
            "Ahli-ahli Yang Hadir:",
            "Senator Yang Turut Hadir:",
            "Ahli-ahli Yang Tidak Hadir:",
            "Ahli-Ahli Yang Tidak Hadir:",
            "Ahli-Ahli Yang Tidak Hadir Di Bawah Peraturan Mesyuarat 91"
        ]
        for line in ignored_lines:
            assert parser.should_ignore_line(line.strip())
        
        valid_lines = [
            "Dato' Sri Someone",
            "Tuan John Doe",
            "1. Valid Entry"
        ]
        for line in valid_lines:
            assert not parser.should_ignore_line(line.strip())

    def test_extract_name_from_line(self, parser):
        """Test name extraction from lines."""
        test_cases = [
            ("1. Dato' Sri John Doe (Constituency)", "Dato' Sri John Doe (Constituency)"),
            ("25. Jane Smith", "Jane Smith"),
            ("Simple Name", "Simple Name"),
            ("Name With (Brackets)", "Name With (Brackets)")
        ]
        
        for line, expected in test_cases:
            result = parser.extract_name_from_line(line)
            assert result == expected

    def test_is_malaysia_marker(self, parser):
        """Test Malaysia marker detection."""
        assert parser.is_malaysia_marker("MALAYSIA")
        assert parser.is_malaysia_marker(" MALAYSIA ")
        assert parser.is_malaysia_marker("malaysia")
        # These should match because they contain "MALAYSIA" as a word
        assert parser.is_malaysia_marker("NEW MALAYSIA")
        assert parser.is_malaysia_marker("MALAYSIA BARU")
        # This should not match because it's not a complete word
        assert not parser.is_malaysia_marker("MALAYSIAN")