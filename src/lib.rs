#[macro_use]
extern crate lazy_static;

use regex::Regex;
use serde::{Deserialize, Serialize};
use serde_json;
use std::collections::HashSet;
use std::fs;
use std::fs::File;
use std::io::prelude::*;
use std::path::{Path, PathBuf};

#[derive(Serialize, Deserialize)]
struct ParliamentMeeting {
    attendees: Vec<String>,
    absentees: Vec<String>,
}

const ATTENDEES_HEADER: &str = "ahli-ahli yang hadir:";
const ABSENTEES_HEADER: &str = "ahli-ahli yang tidak hadir:";
const MALAYSIA: &str = "MALAYSIA";

lazy_static! {
    static ref LINE_IGNORES: HashSet<String> = {
        let mut set = HashSet::new();
        set.insert("DR.".to_string());
        set.insert("Ahli-ahli Yang Hadir:".to_string());
        set.insert("Senator Yang Turut Hadir:".to_string());
        set.insert("Ahli-ahli Yang Tidak Hadir:".to_string());
        set.insert("Ahli-Ahli Yang Tidak Hadir:".to_string());
        set.insert("Ahli-Ahli Yang Tidak Hadir Di Bawah Peraturan Mesyuarat 91".to_string());
        set
    };
    static ref DR_REGEX: Regex = Regex::new(r"DR\. +\d{1,2}\.\d{1,2}\.\d{1,4} +\d+").unwrap();
    static ref NUMBERED_LIST_REGEX: Regex = Regex::new(r"^\d+\.\s").unwrap();
    static ref NAME_REGEX: Regex = Regex::new(r"[A-Z()][\w,’'()@/\.\- ]+").unwrap();
}

pub fn run(pdf_dir: &Path, out_dir: &Path) -> Result<(), Box<dyn std::error::Error>> {
    let entries = fs::read_dir(pdf_dir)?;
    for entry in entries {
        let entry = entry?;
        let file_path = entry.path();
        if file_path.is_dir() {
            continue;
        }
        if let Some(ext) = file_path.extension() {
            if ext != "pdf" {
                continue;
            }
        } else {
            continue;
        }
        let bytes = std::fs::read(file_path.display().to_string())?;
        println!("parsing pdf file: pdf_file={}", file_path.display());
        let content = pdf_extract::extract_text_from_mem(&bytes)?;
        let parsed = parse(content);
        let json_string = serde_json::to_string_pretty(&parsed)?;
        let json_file_path = get_out_json_path(out_dir, &file_path).unwrap();
        println!("saving json file: json_file={}", json_file_path.display());
        if let Ok(mut json_file) = File::create(json_file_path) {
            json_file.write_all(json_string.as_bytes())?;
        }
    }
    Ok(())
}

fn parse(content: String) -> ParliamentMeeting {
    // Attendees.
    let mut attendees_process_flag = false;
    let mut attendees_done_flag = false;
    let mut attendees: Vec<String> = Vec::new();

    // Absentees.
    let mut absentees_process_flag = false;
    let mut absentees_done_flag = false;
    let mut absentees: Vec<String> = Vec::new();

    // Current person being processed.
    let mut current_words: Vec<String> = Vec::new();

    for line in content.lines() {
        let line = line.trim();
        if line == "" {
            continue;
        }
        if is_attendees_header(line) && !attendees_done_flag {
            // Mark to start picking up attendees.
            attendees_process_flag = true;
        }
        if is_absentees_header(line) && !absentees_done_flag {
            // Mark to start picking up absentees.
            absentees_process_flag = true;

            // Mark to stop doing attendees.
            attendees_process_flag = false;
            attendees_done_flag = true;

            if current_words.len() > 0 {
                attendees.push(current_words.join(" "));
                current_words = Vec::new()
            }
        }
        if line.contains(MALAYSIA) {
            // Mark to stop doing absentees.
            absentees_process_flag = false;
            absentees_done_flag = true;

            if current_words.len() > 0 {
                absentees.push(current_words.join(" "));
                current_words = Vec::new()
            }
        }

        // Pickup attendees.
        if attendees_process_flag {
            if should_ignore_line(line) {
                continue;
            }
            if is_start_of_new_person(line) {
                if current_words.len() > 0 {
                    attendees.push(current_words.join(" "));
                    current_words = Vec::new()
                }
            }
            current_words.append(&mut get_name_words(line));
        }

        // Pickup absentees.
        if absentees_process_flag {
            if should_ignore_line(line) {
                continue;
            }
            if is_start_of_new_person(line) {
                if current_words.len() > 0 {
                    absentees.push(current_words.join(" "));
                    current_words = Vec::new()
                }
            }
            current_words.append(&mut get_name_words(line));
        }
    }

    ParliamentMeeting {
        attendees,
        absentees,
    }
}

fn should_ignore_line(line: &str) -> bool {
    if DR_REGEX.is_match(line) {
        return true;
    }
    return LINE_IGNORES.contains(line);
}

fn is_attendees_header(line: &str) -> bool {
    let line = line.trim().to_lowercase();
    return line.contains(ATTENDEES_HEADER);
}

fn is_absentees_header(line: &str) -> bool {
    let line = line.trim().to_lowercase();
    return line.contains(ABSENTEES_HEADER);
}

fn is_start_of_new_person(line: &str) -> bool {
    return NUMBERED_LIST_REGEX.is_match(line);
}

fn get_name_words(line: &str) -> Vec<String> {
    match NAME_REGEX.captures(line) {
        Some(captures) => {
            let mut name_words: Vec<String> = Vec::new();
            for word in (&captures[0]).split(" ") {
                if word == "" {
                    continue;
                }

                name_words.push(word.to_string());
            }
            return name_words;
        }
        None => {
            return Vec::new();
        }
    }
}

fn get_out_json_path(out_dir: &Path, file_path: &PathBuf) -> Option<PathBuf> {
    file_path
        .file_name()
        .map(|name| out_dir.join(name).with_extension("json"))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn test_get_out_file_path() {
        let pdf_path = PathBuf::from("/home/cglotr/ws/kehadiran/2023-05-24.pdf");
        let out_dir = PathBuf::from("/home/cglotr/ws/kehadiran-parser/");
        let actual = get_out_json_path(&out_dir, &pdf_path).unwrap();
        assert_eq!(
            actual,
            PathBuf::from("/home/cglotr/ws/kehadiran-parser/2023-05-24.json")
        );
    }

    #[test]
    fn test_is_attendees_header() {
        let lines = vec!["Ahli-ahli Yang Hadir:", " ahli-ahli yang hadir: "];
        for line in lines {
            assert!(is_attendees_header(line))
        }
    }

    #[test]
    fn test_is_absentees_header() {
        let lines = vec![
            "Ahli-Ahli Yang Tidak Hadir:",
            " ahli-ahli yang tidak hadir: ",
        ];
        for line in lines {
            assert!(is_absentees_header(line))
        }
    }

    #[test]
    fn test_2023_05_24() {
        let bytes = std::fs::read("testfiles/2023-05-24.txt").unwrap();
        let content = String::from_utf8(bytes).unwrap();

        let parsed = parse(content);

        // Attendees.
        assert_eq!(
            parsed.attendees[0],
            "Yang di-Pertua Dewan Rakyat, YB. Dato’ Johari bin Abdul"
        );
        assert_eq!(
            parsed.attendees[1],
            "Menteri Pertanian Dan Keterjaminan Makanan, Datuk Seri Haji Mohamad Bin Sabu (Kota Raja)"
        );
        assert_eq!(
            parsed.attendees[2],
            "Menteri Di Jabatan Perdana Menteri (Undang-Undang Dan Reformasi Institusi), Dato’ Sri Azalina Othman Said (Pengerang)"
        );
        assert_eq!(parsed.attendees[36], "Tuan Tan Kar Hing (Gopeng)");
        assert_eq!(parsed.attendees[93], "Tuan Oscar Ling Chai Yew (Sibu)");
        assert_eq!(
            parsed.attendees[168],
            "Datuk Haji Ahmad Amzad Bin Mohamed @ Hashim (Kuala Terengganu)"
        );
        assert_eq!(parsed.attendees[177], "Tuan Hassan Bin Saad (Baling)");
        assert_eq!(parsed.attendees.len(), 178);

        // Absentees.
        assert_eq!(
            parsed.absentees[0],
            "Perdana Menteri Dan Menteri Kewangan, Dato’ Seri Anwar Bin Ibrahim (Tambun)"
        );
        assert_eq!(
            parsed.absentees[1],
            "Timbalan Perdana Menteri Dan Menteri Kemajuan Desa Dan Wilayah, Dato’ Seri Dr. Ahmad Zahid Bin Hamidi (Bagan Datuk)"
        );
        assert_eq!(
            parsed.absentees[12],
            "Menteri Sumber Manusia, Tuan Sivakumar A/L Varatharaju Naidu (Batu Gajah)"
        );
        assert_eq!(
            parsed.absentees[14],
            "Timbalan Menteri Sains, Teknologi Dan Inovasi, Datuk Arthur Joseph Kurup (Pensiangan)"
        );
        assert_eq!(
            parsed.absentees[31],
            "Timbalan Menteri Pengangkutan, Datuk Haji Hasbi Bin Haji Habibollah (Limbang)"
        );
        assert_eq!(
            parsed.absentees[42],
            "Datuk Seri Panglima Gapari Bin Katingan @ Geoffrey Kitingan (Keningau)"
        );
        assert_eq!(
            parsed.absentees[44],
            "Dr. Siti Mastura Binti Muhammad (Kepala Batas)"
        );
        assert_eq!(parsed.absentees.len(), 45);
    }

    #[test]
    fn test_2023_05_25() {
        let bytes = std::fs::read("testfiles/2023-05-25.txt").unwrap();
        let content = String::from_utf8(bytes).unwrap();

        let parsed = parse(content);

        // Attendees.
        assert_eq!(
            parsed.attendees[0],
            "Yang di-Pertua Dewan Rakyat, YB. Dato’ Johari bin Abdul"
        );
        assert_eq!(
            parsed.attendees[1],
            "Perdana Menteri Dan Menteri Kewangan, Dato’ Seri Anwar Bin Ibrahim (Tambun)"
        );
        assert_eq!(
            parsed.attendees[2],
            "Timbalan Perdana Menteri Dan Menteri Perladangan Dan Komoditi, Dato’ Sri Haji Fadillah Bin Yusof (Petra Jaya)"
        );
        assert_eq!(parsed.attendees[40], "Tuan Tan Hong Pin (Bakri)");
        assert_eq!(
            parsed.attendees[102],
            "Tuan Kesavan A/L Subramaniam (Sungai Siput)"
        );
        assert_eq!(parsed.attendees[180], "Tuan Hassan Bin Saad (Baling)");
        assert_eq!(
            parsed.attendees[181],
            "Menteri Di Jabatan Perdana Menteri (Hal Ehwal Agama), Senator Dato' Setia Dr. Haji Mohd Na'im Bin Haji Mokhtar");
        assert_eq!(
            parsed.attendees[183],
            "Timbalan Menteri Pembangunan Usahawan Dan Koperasi, Senator Puan Saraswathy A/P Kandasami");
        assert_eq!(parsed.attendees.len(), 184);

        // Absentees.
        assert_eq!(
            parsed.absentees[0],
            "Timbalan Perdana Menteri Dan Menteri Kemajuan Desa Dan Wilayah, Dato’ Seri Dr. Ahmad Zahid Bin Hamidi (Bagan Datuk)"
        );
        assert_eq!(
            parsed.absentees[23],
            "Dato' Sri Ikmal Hisham Bin Abdul Aziz (Tanah Merah)"
        );
        assert_eq!(
            parsed.absentees[27],
            "Timbalan Menteri Pengangkutan, Datuk Haji Hasbi Bin Haji Habibollah (Limbang)"
        );
        assert_eq!(
            parsed.absentees[41],
            "Dr. Siti Mastura Binti Muhammad (Kepala Batas)"
        );
        assert_eq!(parsed.absentees.len(), 42);
    }
}
