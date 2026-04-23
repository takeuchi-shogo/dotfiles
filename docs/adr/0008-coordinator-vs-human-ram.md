# ADR-0008: Coordinator パターンと Human RAM モデルの調停

## Status

Accepted

## Context

2026-04-23 に取り込んだ「Skill Graphs 2.0」記事は、skill 合成を atom / molecule / compound の 3 層に分類し、「人間は compound を drive し、並列 5 agents を同時に回すことで 100x leverage を得る」という Human RAM モデル を提唱している。

この提唱と、当セットアップの既存規範には衝突点がある:

- **既存規範 (ADR-0001, `references/agent-orchestration-map.md`)**: "Humans steer, agents execute" を前提に、Opus が計画・統合・ユーザー対話を保持し、subagent に作業のみを委譲する。中核教義は **Never delegate understanding**
- **Skill Graphs 2.0 の Human RAM**: 人間が 5 並列で compound を同時に driver すれば、compound=5 / molecule=50 / atom=500 相当の output が得られる、という並列度前提

Human RAM を無条件に採用すると、Coordinator パターンが崩れる。5 並列で compound を回している最中に、人間は個別 compound の `understanding` を保持し続けられない。Codex の批評 (2026-04-23 /absorb Phase 2.5) は「並列 5 agents を同時に drive する想定は Coordinator 原則と衝突する」と指摘した。

一方、記事が提示する **どの skill level を人間が drive すべきか** という問い自体は有用である。`.config/claude/references/context-constitution.md` の P3 (Proactive > Reactive) と `CLAUDE.md` の "Humans steer, agents execute" は方針を与えるが、「atom / molecule / compound のどれを人間が直接指示するか」という粒度レベルの規範は薄い。

ADR を通じて、Human RAM モデルの受容範囲と Coordinator パターンの保持範囲を明文化しないと、将来の skill 追加や orchestrator 設計で方針が揺れる。

## Decision

**Coordinator パターンを維持したうえで、skill level ごとの drive 責任を明文化する**。Human RAM モデルは「並列 5 agents を同時に drive する」形では採用せず、「level ごとに drive 責任を分担する」形に翻訳して取り込む。

### drive 責任のレイヤリング

| Level | 典型例 | 主たる drive 責任 | Coordinator の関与 |
|-------|--------|----------------|------------------|
| **atom** | 単一 Bash/Grep/Read、hook、script | hook / agent-router / 決定的フロー | 人間は通常関与しない。hook が異常を検知したときのみ通知 |
| **simple molecule** | 単一 subagent 呼び出し、review 1 件、build 1 件 | subagent / cmux Worker が autonomous 実行 | 人間は結果を確認、必要なら instruction を追加 |
| **complex molecule** | 複数 atom を跨ぐ workflow (/review, /simplify) | subagent 実行 + 人間が成果物を判断 | 人間が Phase ごとに承認 |
| **compound** | /epd, /rpi, /absorb のような multi-phase orchestrator | **人間が直接 drive**、Opus main session で Coordinator として動く | 人間は毎 Phase の判断点で意思決定する |

### 並列度の扱い

- 並列 5 agents は **「atom / simple molecule の級」に限定**する。/dispatch, cmux race mode が該当
- **compound は並列 drive しない**。compound が 2 本走ると Coordinator の `understanding` が分断されるため、人間は 1 compound を完遂させてから次に移る
- 例外: worktree で完全に分離された compound (filesystem + session 分離済み) は並列化可能だが、その場合も Coordinator context は 1 本ずつ扱う

### 8-molecule ceiling の運用

Gemini の周辺知識調査 (`docs/research/2026-04-23-skill-graphs-2.0-absorb-analysis.md`) によれば、compound が 8-10 molecules を超えると成功率が $0.9^n$ の指数減衰で 43% 以下に落ちる。この ceiling は PLANS.md に記述された compound skill の Success Criteria に反映する (Task 1 参照)。

## Consequences

### Positive

- **中核教義の保持**: Never delegate understanding が明文で守られる
- **判断軸の明確化**: 新規 skill / orchestrator 追加時、「これは compound か molecule か」の粒度判断ができる
- **過剰並列化の抑制**: compound を 5 並列で drive するような Human RAM の過剰採用が予防される
- **記事の有用部分は取り込む**: level ごとの drive 責任分担という視点は設計規範として定着する

### Negative

- **レベル境界の曖昧さ**: /absorb が atom か molecule か compound かはケースバイケース。運用で調整が必要
- **並列度の上限**: compound 1 本ずつという制約は Human RAM の 100x leverage 提案を 5x 相当に縮小する
- **ADR 自体の命脈**: skill 合成パターンが進化すれば 3 層分類自体が古びる可能性あり。Build to Delete 原則下で 6-12 ヶ月後に再評価

### Neutral

- ADR-0001 (hook 4 層分離), ADR-0002 (Progressive Disclosure), ADR-0006 (Hook Philosophy) と補完関係。矛盾はしない
- 既存の /epd, /rpi, /absorb はすでに本 ADR の「compound」定義に合致しており、マイグレーションコストはほぼゼロ
- 将来、新しい compound が追加される際は本 ADR を参照して drive 責任を設計する
