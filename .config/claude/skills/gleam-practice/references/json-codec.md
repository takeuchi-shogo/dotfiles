# Gleam JSON Codec

`/gleam-practice` skill の JSON Codec セクションを切り出した詳細実装。
SKILL.md からは要約のみ参照され、ここで完全な decode / encode サンプルを保持する。

---

## JSON Codec (`gleam/dynamic/decode` + `gleam/json`)

Gleam's JSON API tends to shift between versions (`gleam_json` v2+). Current idiomatic usage:

### Decode

```gleam
import gleam/dynamic/decode
import gleam/json

pub type NewTodo { NewTodo(title: String, priority: Int) }

pub fn new_todo_decoder() -> decode.Decoder(NewTodo) {
  use title <- decode.field("title", decode.string)
  use priority <- decode.optional_field("priority", 0, decode.int)
  decode.success(NewTodo(title:, priority:))
}

// Inside a Wisp handler
case decode.run(body, new_todo_decoder()) {
  Ok(nt) -> // ... use nt
  Error(errors) -> wisp.bad_request("invalid json: " <> string.inspect(errors))
}
```

`decode.field` is required; `decode.optional_field(key, default, decoder)` is optional. For nested objects use `decode.field("user", user_decoder())`.

### Encode

```gleam
pub fn encode_todo(t: Todo) -> json.Json {
  json.object([
    #("id", json.int(t.id)),
    #("title", json.string(t.title)),
    #("done", json.bool(t.done)),
  ])
}

// Return it from Wisp
wisp.json_response(json.to_string_tree(encode_todo(t)), 201)
```

Lists: `json.array(items, of: encode_todo)`.

**LSP Code Action**: `gleam-language-server` v1.2+ ships a "Generate JSON encoder/decoder" feature. Place the cursor on the `Todo` type and invoke the Code Action to auto-generate `encode_todo` / `todo_decoder`. More accurate than writing them by hand.