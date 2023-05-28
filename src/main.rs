use config::Config;

fn main() {
    let settings = Config::builder()
        .add_source(config::File::with_name("config.yaml"))
        .build()
        .unwrap();
    let run = kehadiran_parser::run(
        settings.get_string("pdf_dir").unwrap(),
        settings.get_string("out_dir").unwrap(),
    );
    std::process::exit(run)
}
