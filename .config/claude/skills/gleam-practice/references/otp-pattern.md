# Gleam OTP Pattern

`/gleam-practice` skill の OTP Pattern セクションを切り出した詳細実装。
SKILL.md からは要約のみ参照され、ここで完全な actor wrapper / supervision tree / guidelines を保持する。

---

## OTP Pattern

The basic shape is two layers: `pure state` and `server`.

**Important**: `gleam_otp` is a statically-typed wrapper over Erlang's `gen_server`, and **its API is not compatible with `gen_server`**. Do not call `:gen_server.call` / `:gen_server.cast` directly. Keep everything inside the `Subject` and `actor.Message` world.

### pure state

```gleam
pub opaque type State {
  State(hits: Dict(String, Int), limit: Int)
}

pub fn new(limit: Int) -> State {
  State(hits: dict.new(), limit: limit)
}

pub fn incr(state: State, key: String) -> #(State, Bool) {
  let n = dict.get(state.hits, key) |> result.unwrap(0) + 1
  #(State(..state, hits: dict.insert(state.hits, key, n)), n <= state.limit)
}
```

### actor wrapper (concrete example)

```gleam
import gleam/erlang/process.{type Subject}
import gleam/otp/actor
import gleam/otp/supervision

pub opaque type Message {
  Check(key: String, reply_to: Subject(Bool))
  Reset(key: String)
}

pub opaque type Server { Server(subject: Subject(Message)) }

pub fn start(limit: Int) -> Result(Server, actor.StartError) {
  actor.new(new(limit))
  |> actor.on_message(handle)
  |> actor.start
  |> result.map(fn(started) { Server(subject: started.data) })
}

pub fn supervised(limit: Int) -> supervision.ChildSpecification(Server) {
  supervision.worker(fn() { start(limit) })
}

fn handle(state: State, msg: Message) -> actor.Next(State, Message) {
  case msg {
    Check(key, reply_to) -> {
      let #(next, ok) = incr(state, key)
      process.send(reply_to, ok)
      actor.continue(next)
    }
    Reset(key) ->
      actor.continue(State(..state, hits: dict.delete(state.hits, key)))
  }
}

// sync call pattern: the caller creates a reply subject and passes it in
pub fn check(s: Server, key: String) -> Bool {
  let reply = process.new_subject()
  process.send(s.subject, Check(key, reply))
  process.receive(reply, 1000) |> result.unwrap(False)
}

pub fn reset(s: Server, key: String) -> Nil {
  process.send(s.subject, Reset(key))
}
```

### Three kinds of supervision trees

`gleam_otp` splits supervisors across three modules by use case.

| Kind | Module | When to use |
|---|---|---|
| **static** | `gleam/otp/static_supervisor` | Child processes are fixed at startup (DB pool, pre-configured actors). Handles restarts only. |
| **factory** | `gleam/otp/supervisor_factory` | Spawn the same spec dynamically with IDs (e.g. session-per-user). `start_child(name, arg)` |
| **dynamic** | `gleam/otp/supervisor_dynamic` | Add/remove arbitrary specs dynamically (e.g. job worker pool). `start_child(name, spec)` / `terminate_child` |

The exact API names vary by version. Check the official `gleam_otp` hex docs each time. The template below assumes v0.16+:

```gleam
// src/my_app/app.gleam
import gleam/otp/static_supervisor as sup
import my_app/db_pool
import my_app/rate_limiter

pub fn start() -> Result(Nil, actor.StartError) {
  sup.new(sup.OneForOne)
  |> sup.restart_tolerance(intensity: 3, period: 60)  // allow up to 3 restarts in 60s
  |> sup.add(db_pool.supervised())                    // static child
  |> sup.add(rate_limiter.supervised(limit: 100))     // static child
  |> sup.start
  |> result.replace(Nil)
}
```

How to pick a restart strategy:
- **`Permanent`**: always restart on exit (infrastructure like DB pools or auth servers).
- **`Transient`**: normal exits are fine, restart only on abnormal exits (job workers).
- **`Temporary`**: never restart (one-shot work).

When `restart_intensity` (default 3) over `period` (default 5 seconds) is exceeded, the supervisor itself crashes and propagates upward.

### Guidelines

- Keep `Server` opaque (do not let callers manipulate the Subject directly).
- Do not touch state directly from HTTP (always go through the actor).
- Collect the supervision tree inside `app.gleam`.
- Start with `OneForOne` as the restart strategy, and use `static_supervisor` at the top level.
- Use named actors to make testing easier.
- Use the right supervisor kind for the job: `static` (fixed), `factory` (same spec, dynamic), `dynamic` (arbitrary spec, dynamic).