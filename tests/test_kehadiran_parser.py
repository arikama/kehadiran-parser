#!/usr/bin/env python3

import pytest
import json
import tempfile
from pathlib import Path
from kehadiran_parser import KehadiranParser

@pytest.fixture
def parser():
    """Create a parser instance for tests."""
    return KehadiranParser()

def test_get_output_json_path(parser):
    """Test JSON output path generation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_path = Path(temp_dir) / "2023-05-24.pdf"
        out_dir = Path(temp_dir) / "output"
        actual = parser.get_output_json_path(out_dir, pdf_path)
        expected = out_dir / "2023-05-24.json"
        assert actual == expected

def test_is_attendees_header(parser):
    """Test attendees header detection."""
    test_lines = ["Ahli-ahli Yang Hadir:", " ahli-ahli yang hadir: "]
    for line in test_lines:
        assert parser.is_attendees_header(line)

def test_is_absentees_header(parser):
    """Test absentees header detection."""
    test_lines = [
        "Ahli-Ahli Yang Tidak Hadir:",
        " ahli-ahli yang tidak hadir: "
    ]
    for line in test_lines:
        assert parser.is_absentees_header(line)
def test_2023_05_24_parsing(parser):
    """Test parsing of 2023-05-24 data."""
    with open("testfiles/2023-05-24.txt", "r", encoding="utf-8") as f:
        content = f.read()
    
    parsed = parser.parse_content(content)
    
    # Test attendees (using normalized ASCII text)
    assert parsed.attendees[0] == "Yang di-Pertua Dewan Rakyat, YB. Dato Johari bin Abdul"
    assert parsed.attendees[1] == "Menteri Pertanian Dan Keterjaminan Makanan, Datuk Seri Haji Mohamad Bin Sabu (Kota Raja)"
    assert parsed.attendees[2] == "Menteri Di Jabatan Perdana Menteri (Undang-Undang Dan Reformasi Institusi), Dato Sri Azalina Othman Said (Pengerang)"
    assert parsed.attendees[36] == "Tuan Tan Kar Hing (Gopeng)"
    assert parsed.attendees[93] == "Tuan Oscar Ling Chai Yew (Sibu)"
    assert parsed.attendees[168] == "Datuk Haji Ahmad Amzad Bin Mohamed @ Hashim (Kuala Terengganu)"
    assert parsed.attendees[177] == "Tuan Hassan Bin Saad (Baling)"
    assert len(parsed.attendees) == 178
    
    # Test absentees (using normalized ASCII text)
    assert parsed.absentees[0] == "Perdana Menteri Dan Menteri Kewangan, Dato Seri Anwar Bin Ibrahim (Tambun)"
    assert parsed.absentees[1] == "Timbalan Perdana Menteri Dan Menteri Kemajuan Desa Dan Wilayah, Dato Seri Dr. Ahmad Zahid Bin Hamidi (Bagan Datuk)"
    assert parsed.absentees[12] == "Menteri Sumber Manusia, Tuan Sivakumar A/L Varatharaju Naidu (Batu Gajah)"
    assert parsed.absentees[14] == "Timbalan Menteri Sains, Teknologi Dan Inovasi, Datuk Arthur Joseph Kurup (Pensiangan)"
    assert parsed.absentees[31] == "Timbalan Menteri Pengangkutan, Datuk Haji Hasbi Bin Haji Habibollah (Limbang)"
    assert parsed.absentees[42] == "Datuk Seri Panglima Gapari Bin Katingan @ Geoffrey Kitingan (Keningau)"
    assert parsed.absentees[44] == "Dr. Siti Mastura Binti Muhammad (Kepala Batas)"
    assert len(parsed.absentees) == 45

def test_2023_05_25_parsing(parser):
    """Test parsing of 2023-05-25 data."""
    with open("testfiles/2023-05-25.txt", "r", encoding="utf-8") as f:
        content = f.read()
    
    parsed = parser.parse_content(content)
    
    # Test attendees (using normalized ASCII text)
    assert parsed.attendees[0] == "Yang di-Pertua Dewan Rakyat, YB. Dato Johari bin Abdul"
    assert parsed.attendees[1] == "Perdana Menteri Dan Menteri Kewangan, Dato Seri Anwar Bin Ibrahim (Tambun)"
    assert parsed.attendees[2] == "Timbalan Perdana Menteri Dan Menteri Perladangan Dan Komoditi, Dato Sri Haji Fadillah Bin Yusof (Petra Jaya)"
    assert parsed.attendees[40] == "Tuan Tan Hong Pin (Bakri)"
    assert parsed.attendees[102] == "Tuan Kesavan A/L Subramaniam (Sungai Siput)"
    assert parsed.attendees[180] == "Tuan Hassan Bin Saad (Baling)"
    assert parsed.attendees[181] == "Menteri Di Jabatan Perdana Menteri (Hal Ehwal Agama), Senator Dato' Setia Dr. Haji Mohd Na'im Bin Haji Mokhtar"
    assert parsed.attendees[183] == "Timbalan Menteri Pembangunan Usahawan Dan Koperasi, Senator Puan Saraswathy A/P Kandasami"
    assert len(parsed.attendees) == 184
    
    # Test absentees (using normalized ASCII text)
    assert parsed.absentees[0] == "Timbalan Perdana Menteri Dan Menteri Kemajuan Desa Dan Wilayah, Dato Seri Dr. Ahmad Zahid Bin Hamidi (Bagan Datuk)"
    assert parsed.absentees[23] == "Dato' Sri Ikmal Hisham Bin Abdul Aziz (Tanah Merah)"
    assert parsed.absentees[27] == "Timbalan Menteri Pengangkutan, Datuk Haji Hasbi Bin Haji Habibollah (Limbang)"
    assert parsed.absentees[41] == "Dr. Siti Mastura Binti Muhammad (Kepala Batas)"
    assert len(parsed.absentees) == 42