mod events;
mod io;
mod post_any;
mod post_bash;
mod post_edit;
mod pre_tool;
mod user_prompt;

fn main() {
    let raw = io::read_stdin();
    let data: serde_json::Value = match serde_json::from_str(&raw) {
        Ok(v) => v,
        Err(_) => {
            print!("{}", raw);
            return;
        }
    };

    let args: Vec<String> = std::env::args().collect();
    let subcmd = args.get(1).map(|s| s.as_str()).unwrap_or("");

    let result = match subcmd {
        "post-any" => post_any::run(&raw, &data),
        "post-bash" => post_bash::run(&raw, &data),
        "post-edit" => post_edit::run(&raw, &data),
        "pre-edit" => pre_tool::pre_edit(&raw, &data),
        "pre-bash" => pre_tool::pre_bash(&data),
        "pre-search" => pre_tool::pre_search(&data),
        "pre-websearch" => pre_tool::pre_websearch(&raw, &data),
        "pre-commit" => pre_tool::pre_commit(&raw, &data),
        "user-prompt" => user_prompt::run(&raw, &data),
        _ => {
            eprintln!("[claude-hooks] unknown subcommand: {}", subcmd);
            print!("{}", raw);
            Ok(())
        }
    };

    if let Err(e) = result {
        eprintln!("[claude-hooks] error: {}", e);
        print!("{}", raw);
    }
}
