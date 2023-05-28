use serde::{Deserialize, Serialize};
use serde_json;
use std::fs;
use std::fs::File;
use std::io::prelude::*;

#[derive(Serialize, Deserialize)]
struct ParliamentMeeting {
    members: Vec<String>,
    attendees: Vec<String>,
    absentees: Vec<String>,
}

pub fn run(pdf_dir: String, out_dir: String) -> i32 {
    println!("running: pdf_dir={}, out_dir={}", pdf_dir, out_dir);
    if let Ok(entries) = fs::read_dir(pdf_dir) {
        for entry in entries {
            if let Ok(entry) = entry {
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
                println!("pdf_file: {}", file_path.display());
                let bytes = std::fs::read(file_path.display().to_string()).unwrap();
                let content = pdf_extract::extract_text_from_mem(&bytes).unwrap();
                let json_file_path = file_path
                    .display()
                    .to_string()
                    .trim_end_matches(".pdf")
                    .clone()
                    .to_owned()
                    + ".json";
                if let Ok(mut json_file) = File::create(json_file_path) {
                    let parsed = parse(content);
                    let json_string = serde_json::to_string(&parsed).unwrap();
                    if let Ok(()) = json_file.write_all(json_string.as_bytes()) {}
                }
            }
        }
    }
    0
}

fn parse(_content: String) -> ParliamentMeeting {
    ParliamentMeeting {
        members: Vec::new(),
        attendees: Vec::new(),
        absentees: Vec::new(),
    }
}
