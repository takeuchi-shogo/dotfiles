//! Minimal shell lexer for argv extraction (ptuf-inspired).
//!
//! Splits on `;` / `&&` / `||` / `|`, honours quotes / escapes / heredocs,
//! and surfaces `$(…)` / `` `…` `` bodies for nested analysis.
//! Reference: https://github.com/watany-dev/ptuf (facts/shell) — we keep a
//! smaller subset and expand git aliases / ambient `export` ourselves.

/// One simple command after env peeling.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Command {
    pub env_assignments: Vec<(String, String)>,
    pub head: String,
    pub args: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
enum Token {
    Word(String),
    Semi,
    AndIf,
    OrIf,
    Pipe,
}

/// Parse a bash-like command string into top-level commands plus nested
/// command-substitution bodies (also parsed).
pub fn parse_commands(input: &str) -> Vec<Command> {
    let mut out = Vec::new();
    let (tokens, substitutions) = tokenize(input);
    collect_from_tokens(&tokens, &mut out);
    for inner in substitutions {
        out.extend(parse_commands(&inner));
    }
    out
}

fn collect_from_tokens(tokens: &[Token], out: &mut Vec<Command>) {
    let mut cur: Vec<String> = Vec::new();
    let flush = |words: &mut Vec<String>, out: &mut Vec<Command>| {
        if let Some(cmd) = words_to_command(words) {
            out.push(cmd);
        }
        words.clear();
    };
    for tok in tokens {
        match tok {
            Token::Word(w) => cur.push(w.clone()),
            Token::Semi | Token::AndIf | Token::OrIf | Token::Pipe => {
                flush(&mut cur, out);
            }
        }
    }
    flush(&mut cur, out);
}

fn words_to_command(words: &[String]) -> Option<Command> {
    if words.is_empty() {
        return None;
    }
    let mut env = Vec::new();
    let mut i = 0;
    while i < words.len() {
        if let Some((k, v)) = parse_env_assignment(&words[i]) {
            env.push((k, v));
            i += 1;
        } else {
            break;
        }
    }
    if i >= words.len() {
        // bare assignments / `export KEY=VAL` handled by caller ambient
        if env.is_empty() {
            return None;
        }
        return Some(Command {
            env_assignments: env,
            head: String::new(),
            args: Vec::new(),
        });
    }
    let head = words[i].clone();
    let args = words[i + 1..].to_vec();
    Some(Command {
        env_assignments: env,
        head,
        args,
    })
}

fn parse_env_assignment(word: &str) -> Option<(String, String)> {
    let eq = word.find('=')?;
    if eq == 0 {
        return None;
    }
    let key = &word[..eq];
    if !key.chars().all(|c| c.is_ascii_alphanumeric() || c == '_') {
        return None;
    }
    if key.chars().next()?.is_ascii_digit() {
        return None;
    }
    Some((key.to_string(), word[eq + 1..].to_string()))
}

fn tokenize(input: &str) -> (Vec<Token>, Vec<String>) {
    let bytes = input.as_bytes();
    let mut i = 0;
    let mut tokens = Vec::new();
    let mut substitutions = Vec::new();
    while i < bytes.len() {
        let c = bytes[i];
        if c.is_ascii_whitespace() {
            i += 1;
            continue;
        }
        if c == b';' {
            tokens.push(Token::Semi);
            i += 1;
            continue;
        }
        if c == b'|' {
            if i + 1 < bytes.len() && bytes[i + 1] == b'|' {
                tokens.push(Token::OrIf);
                i += 2;
            } else {
                tokens.push(Token::Pipe);
                i += 1;
            }
            continue;
        }
        if c == b'&' {
            if i + 1 < bytes.len() && bytes[i + 1] == b'&' {
                tokens.push(Token::AndIf);
                i += 2;
            } else {
                // background `&` — ignore
                i += 1;
            }
            continue;
        }
        // Heredoc operator as its own redirect — consume tag + body, no argv word
        if c == b'<' && i + 1 < bytes.len() && bytes[i + 1] == b'<' {
            let (next, body_subs) = consume_heredoc(bytes, i);
            substitutions.extend(body_subs);
            i = next;
            continue;
        }
        let (word, next, mut subs) = read_word(bytes, i);
        substitutions.append(&mut subs);
        if !word.is_empty() || next > i {
            if !word.is_empty() {
                tokens.push(Token::Word(word));
            }
            i = next;
        } else {
            i += 1; // safety forward progress
        }
    }
    (tokens, substitutions)
}

fn consume_heredoc(bytes: &[u8], start: usize) -> (usize, Vec<String>) {
    let mut j = start + 2; // after <<
    if j < bytes.len() && bytes[j] == b'-' {
        j += 1;
    }
    while j < bytes.len() && (bytes[j] == b' ' || bytes[j] == b'\t') {
        j += 1;
    }
    let (tag_raw, after_tag, _) = read_word(bytes, j);
    let tag = strip_quote_chars(&tag_raw);
    j = after_tag;
    if j < bytes.len() && bytes[j] == b'\n' {
        j += 1;
    }
    let body_start = j;
    while j < bytes.len() {
        let line_start = j;
        while j < bytes.len() && bytes[j] != b'\n' {
            j += 1;
        }
        let line = std::str::from_utf8(&bytes[line_start..j]).unwrap_or("");
        let trimmed = line.trim_end_matches('\r');
        if trimmed == tag {
            let body = std::str::from_utf8(&bytes[body_start..line_start]).unwrap_or("");
            let mut subs = Vec::new();
            // nested substitutions inside heredoc body (rare but cheap)
            collect_dollar_subs(body.as_bytes(), &mut subs);
            if j < bytes.len() && bytes[j] == b'\n' {
                j += 1;
            }
            return (j, subs);
        }
        if j < bytes.len() && bytes[j] == b'\n' {
            j += 1;
        }
    }
    (bytes.len(), Vec::new())
}

fn strip_quote_chars(s: &str) -> String {
    if s.len() >= 2 {
        let b = s.as_bytes();
        if (b[0] == b'\'' || b[0] == b'"') && b[0] == b[s.len() - 1] {
            return s[1..s.len() - 1].to_string();
        }
    }
    s.to_string()
}

fn read_word(bytes: &[u8], start: usize) -> (String, usize, Vec<String>) {
    let mut out = String::new();
    let mut subs = Vec::new();
    let mut i = start;
    while i < bytes.len() {
        let c = bytes[i];
        if c.is_ascii_whitespace()
            || c == b';'
            || c == b'|'
            || c == b'&'
            || (c == b'<' && i + 1 < bytes.len() && bytes[i + 1] == b'<')
        {
            break;
        }
        match c {
            b'\\' => {
                i += 1;
                if i < bytes.len() {
                    out.push(bytes[i] as char);
                    i += 1;
                }
            }
            b'\'' => {
                i += 1;
                while i < bytes.len() && bytes[i] != b'\'' {
                    out.push(bytes[i] as char);
                    i += 1;
                }
                if i < bytes.len() {
                    i += 1; // closing '
                }
            }
            b'"' => {
                i += 1;
                while i < bytes.len() && bytes[i] != b'"' {
                    if bytes[i] == b'\\' && i + 1 < bytes.len() {
                        i += 1;
                        out.push(bytes[i] as char);
                        i += 1;
                        continue;
                    }
                    if bytes[i] == b'$' && i + 1 < bytes.len() && bytes[i + 1] == b'(' {
                        let (inner, next) = read_dollar_paren(bytes, i + 2);
                        subs.push(inner.clone());
                        // opaque placeholder so the word stays one argv token
                        out.push_str("$(");
                        out.push_str(&inner);
                        out.push(')');
                        i = next;
                        continue;
                    }
                    out.push(bytes[i] as char);
                    i += 1;
                }
                if i < bytes.len() {
                    i += 1; // closing "
                }
            }
            b'`' => {
                i += 1;
                let body_start = i;
                while i < bytes.len() && bytes[i] != b'`' {
                    i += 1;
                }
                let inner = std::str::from_utf8(&bytes[body_start..i])
                    .unwrap_or("")
                    .to_string();
                subs.push(inner.clone());
                out.push('`');
                out.push_str(&inner);
                out.push('`');
                if i < bytes.len() {
                    i += 1;
                }
            }
            b'$' if i + 1 < bytes.len() && bytes[i + 1] == b'(' => {
                let (inner, next) = read_dollar_paren(bytes, i + 2);
                subs.push(inner.clone());
                out.push_str("$(");
                out.push_str(&inner);
                out.push(')');
                i = next;
            }
            _ => {
                out.push(c as char);
                i += 1;
            }
        }
    }
    (out, i, subs)
}

/// Read `$(…)` body starting *after* `$(`. Handles nested parens, quotes, heredocs.
fn read_dollar_paren(bytes: &[u8], start: usize) -> (String, usize) {
    let mut depth = 1usize;
    let mut i = start;
    let mut out = String::new();
    while i < bytes.len() {
        let c = bytes[i];
        if c == b'\\' {
            out.push('\\');
            i += 1;
            if i < bytes.len() {
                out.push(bytes[i] as char);
                i += 1;
            }
            continue;
        }
        if c == b'\'' {
            out.push('\'');
            i += 1;
            while i < bytes.len() && bytes[i] != b'\'' {
                out.push(bytes[i] as char);
                i += 1;
            }
            if i < bytes.len() {
                out.push('\'');
                i += 1;
            }
            continue;
        }
        if c == b'"' {
            out.push('"');
            i += 1;
            while i < bytes.len() && bytes[i] != b'"' {
                if bytes[i] == b'\\' && i + 1 < bytes.len() {
                    out.push('\\');
                    out.push(bytes[i + 1] as char);
                    i += 2;
                    continue;
                }
                out.push(bytes[i] as char);
                i += 1;
            }
            if i < bytes.len() {
                out.push('"');
                i += 1;
            }
            continue;
        }
        if c == b'<' && i + 1 < bytes.len() && bytes[i + 1] == b'<' {
            // heredoc inside $(): copy operator+tag, then body until tag
            let heredoc_start = i;
            let (after, _) = consume_heredoc(bytes, i);
            out.push_str(std::str::from_utf8(&bytes[heredoc_start..after]).unwrap_or(""));
            i = after;
            continue;
        }
        if c == b'(' {
            depth += 1;
            out.push('(');
            i += 1;
            continue;
        }
        if c == b')' {
            depth -= 1;
            if depth == 0 {
                return (out, i + 1);
            }
            out.push(')');
            i += 1;
            continue;
        }
        out.push(c as char);
        i += 1;
    }
    (out, i)
}

fn collect_dollar_subs(bytes: &[u8], subs: &mut Vec<String>) {
    let mut i = 0;
    while i + 1 < bytes.len() {
        if bytes[i] == b'$' && bytes[i + 1] == b'(' {
            let (inner, next) = read_dollar_paren(bytes, i + 2);
            subs.push(inner);
            i = next;
        } else {
            i += 1;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn splits_on_shell_separators() {
        let cmds = parse_commands("echo a; echo b && echo c | cat");
        assert_eq!(cmds.len(), 4);
        assert_eq!(cmds[0].head, "echo");
        assert_eq!(cmds[0].args, vec!["a"]);
    }

    #[test]
    fn quotes_keep_semicolon_inside_word() {
        let cmds = parse_commands(r#"git commit -m "a; b" --no-verify"#);
        assert_eq!(cmds.len(), 1);
        assert_eq!(cmds[0].head, "git");
        assert_eq!(cmds[0].args, vec!["commit", "-m", "a; b", "--no-verify"]);
    }

    #[test]
    fn strips_quotes_from_flag_tokens() {
        let cmds = parse_commands(r#"git commit '-n' -m x"#);
        assert_eq!(cmds[0].args, vec!["commit", "-n", "-m", "x"]);
        let cmds = parse_commands(r#"git commit "--no-verify" -m x"#);
        assert_eq!(cmds[0].args, vec!["commit", "--no-verify", "-m", "x"]);
    }

    #[test]
    fn env_assignment_and_quoted_value() {
        let cmds = parse_commands(r#"HUSKY="0" git commit -m x"#);
        assert_eq!(cmds[0].env_assignments, vec![("HUSKY".into(), "0".into())]);
        assert_eq!(cmds[0].head, "git");
    }

    #[test]
    fn heredoc_message_with_trailing_no_verify() {
        let cmd = "git commit -m \"$(cat <<'EOF'\nhello\nEOF\n)\" --no-verify";
        let cmds = parse_commands(cmd);
        let git = cmds.iter().find(|c| c.head == "git").expect("git");
        assert!(git.args.iter().any(|a| a == "--no-verify"));
    }
}
