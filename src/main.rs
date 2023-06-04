use std::{path::PathBuf, str::FromStr};

use clap::Parser;

/// Simple program to greet a person
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Name of the person to greet
    #[arg(short, long)]
    pdf_dir: String,

    /// Number of times to greet
    #[arg(short, long)]
    out_dir: String,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = Args::parse();
    let pdf_dir = PathBuf::from_str(&args.pdf_dir)?;
    let out_dir = PathBuf::from_str(&args.out_dir)?;

    if !pdf_dir.is_dir() {
        return Err("pdf_dir must be a directory".into());
    }

    if !out_dir.is_dir() {
        return Err("out_dir must be a directory".into());
    }

    println!(
        "pdf_dir:{} out_dir:{}",
        pdf_dir.display(),
        out_dir.display()
    );

    kehadiran_parser::run(&pdf_dir, &out_dir)?;
    Ok(())
}
