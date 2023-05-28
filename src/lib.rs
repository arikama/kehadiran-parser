use std::fs;

pub fn run(pdf_dir: String, out_dir: String) -> i32 {
    println!("running: pdf_dir={}, out_dir={}", pdf_dir, out_dir);
    if let Ok(entries) = fs::read_dir(pdf_dir) {
        for entry in entries {
            if let Ok(entry) = entry {
                let file_path = entry.path();
                println!("file: {}", file_path.display());
                let bytes = std::fs::read(file_path.display().to_string()).unwrap();
                let out = pdf_extract::extract_text_from_mem(&bytes).unwrap();
                println!("file content: {}", out);
            }
        }
    }
    0
}
