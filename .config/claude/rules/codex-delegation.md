# Codex CLI 委譲ルール

Codex CLI は設計判断、深い推論、複雑なデバッグを担当する。以下の場面で Codex への委譲を検討せよ。

## 委譲すべきケース

- **Spec/Plan Gate（批評）**: Spec/Plan 作成後、実装前に Codex で批評する → `codex-plan-reviewer` エージェント。Spec の抜け漏れ・Plan の妥当性・潜在リスクを統合的にレビュー。M規模以上で必須
- **セキュリティ深掘り調査**: 潜在的脆弱性の根本原因分析、攻撃ベクトル評価、セキュリティアーキテクチャレビュー → `codex exec -p security`（xhigh reasoning + read-only）。`security-reviewer` エージェントの表面チェックを Codex の深い推論で補完する
- **設計判断**: アーキテクチャ選定、モジュール構造、API設計、技術選定
- **トレードオフ分析**: 「AとBどちらが良いか」という比較・評価
- **複雑なデバッグ**: 通常の debugger エージェントで原因特定が困難な場合 → `codex-debugger` エージェント
- **コードレビュー（セカンドオピニオン）**: S規模以上の変更で `codex-reviewer` エージェントを並列起動
- **Debate（マルチモデル議論）**: `/debate` スキルで Gemini と並列に独立した視点を提供
- **リファクタリング計画**: 大規模な構造変更の計画策定

## 委譲方法

- **Spec/Plan 批評**: `codex-plan-reviewer` エージェント（read-only、CREATE 後 → Implement 前で起動）
- **セキュリティ分析**: `codex exec --skip-git-repo-check -m gpt-5.5 -p security "..."` — profiles.security で xhigh + read-only が自動適用
- **分析・レビュー**: `codex-debugger` エージェント（read-only）
- **コードレビュー**: `codex-reviewer` エージェント（read-only、他レビューアーと並列起動）
- **スキル実行**: `codex` スキル or `codex-review` スキル（手動実行用）
- **直接呼び出し**: `codex exec --skip-git-repo-check -m gpt-5.5 --sandbox read-only "..." 2>/dev/null`
- **レビュー/セキュリティは必ず xhigh**: セキュリティ分析には `-p security` を使用（profiles.security で xhigh + read-only が自動適用）。通常レビューは `--config model_reasoning_effort="xhigh"` を指定

## Codex 深掘り分析の使い分け

| タイミング | エージェント | reasoning_effort | 目的 |
|---|---|---|---|
| Spec/Plan 作成後（M/L 規模） | `codex-plan-reviewer` | xhigh | Spec 批評 + Plan 批評 + リスク分析の統合レビュー |
| コード完成後（S 規模以上） | `codex-reviewer` | xhigh | 7項目検査（6項目 + Plan 整合性）|
| セキュリティ調査 | `codex exec -p security` | xhigh | 脆弱性の深掘り分析・攻撃ベクトル評価 |
| エラー発生時 | `codex-debugger` | high | 根本原因の深い分析 |

## 編集指示のベストプラクティス

Codex (GPT系) は `apply_patch` 形式に最適化されているが、`str_replace` の正確な再現は苦手な傾向がある（"The Harness Problem" ベンチマーク: patch failure rate が高い）。委譲時は以下を意識する:

- **行番号ベースの指示を優先**: 「L42-L55 を以下に置換」のように行範囲で指定する
- **古いコンテンツの正確な再現を求めない**: 変更箇所の特定にはファイルパス + 関数名 + 行番号を使う
- **大きな変更はファイル全体の書き換えを許容**: 400行以下のファイルでは全書き換えの方が精度が高い場合がある
- **空白・インデントの厳密な一致に依存しない**: コンテキストの意味的な一致で指示する

## トークン予算による実装委譲

長時間セッションや並列セッションで Claude のトークン消費が大きい場合、重い実装タスクを Codex に委譲してトークンを分散する。

| 状況 | アクション |
|------|----------|
| セッション後半で大きな実装が残っている | `codex exec` で実装を委譲し、Claude はレビュー・統合に集中 |
| 並列セッションが 3+ 同時稼働中 | 新規の実装タスクは Codex に委譲を優先 |
| Plan は完成、実装が機械的 | Plan を `codex exec -p` に渡して実装を委譲 |
| **新規実装が100行超の見込み** | Codex に委譲を優先（Claude の3-4倍のトークン消費を回避） |
| **テストコード生成が主タスク** | Codex が得意領域（Terminal-Bench 77.3%）。テスト生成は委譲優先 |

**コスト根拠**: 同一タスクで Claude は Codex の3〜4倍のトークンを消費する（Figmaプラグイン: 4.2倍、API統合: 3.6倍）。Rate Limit 制では実装オフロードの効果が特に大きい。

### 委譲方法

```bash
# Plan ファイルを渡して実装を委譲
codex exec --skip-git-repo-check -m gpt-5.5 \
  "Read tmp/plans/{plan}.md and implement all tasks. Follow the acceptance criteria exactly."
```

Claude はプラン策定・レビュー・統合の上流/下流を担当し、Codex は中間の実装を担当する分業モデル。

## タスク性質別の委譲ガイダンス

> context-and-impact のタスク分類器の知見を応用。タスクの性質に応じて最適なモデルにルーティングする。

| タスク性質 | 推奨先 | 理由 |
|-----------|--------|------|
| fix / debug / root-cause | Codex | 深い推論が必要。reasoning effort: high〜xhigh |
| feat / refactor / large-scope | Gemini | 広いコンテキストが必要。1M ウィンドウ活用 |
| review / security | Codex + Claude | 多角的検証。異種シグナルの組み合わせ |
| docs / config / small-edit | Claude 直接 | 委譲のオーバーヘッドが利益を上回る |

**既存ルーティングとの関係**: `agent-router.py` のキーワードベースルーティングと競合しない。agent-router は特定エージェントへの振り分け、このガイダンスはモデル選択の指針。両方を組み合わせて使う。

## Codex 実装失敗時のフォールバック

Codex に実装を委譲した場合、以下のルールで回復する:

| 失敗回数 | アクション |
|----------|-----------|
| 1回目 | エラー内容を補足情報として付与し、Codex に再実行を指示 |
| 2回目 | Claude が直接実装にフォールバック。Codex の出力を参考情報として活用 |

**根拠**: 記事調査により、Codex は実行ごとに結果が変わりうるため、1回の再試行は有効。ただし2回連続失敗は構造的な問題を示唆するため、Claude の会話型軌道修正能力で回復する方が効率的。

## Codex の Instruction Fragment 設計哲学

> 出典: wquguru/harness-books Book 2 Ch2 — Codex のソースコード分析に基づく

Codex は instruction を「自然語テキストの連結」ではなく「型・境界・包裹規則を持つ構造化片段」として扱う。

| 概念 | Codex の実装 | Claude Code との違い |
|------|-------------|---------------------|
| **Fragment** | `fragment.rs` で instruction に型・起止境界・包裹規則を定義 | CC は動態拼装（条件注入で組み立て） |
| **AGENTS.md** | 作用域と優先度の継承関係を明示。`child_agents_md` で階層的 | CC の `CLAUDE.md` は「現場公告板」的 |
| **User Instructions** | `user_instructions.rs` で目録と境界標記付きメッセージに序列化 | CC は system prompt に自然語として注入 |
| **ExecPolicy** | `execpolicy/src/lib.rs` で宣言的ツール実行ポリシー | CC は `bashPermissions.ts` で現場判定 |

### Codex に委譲する際の含意

- Codex は **明確な境界を持つ指示** に最適化されている。曖昧な自然語指示より、構造化された要件が精度を上げる
- `AGENTS.md` の階層的規則システムは、Codex がプロジェクト固有の制約を理解する主要な入口
- instruction が「識別可能な一等オブジェクト」であるため、何がプロンプトに入っているかの可調試性が高い

---

## 委譲しないケース

- 単純なコード編集、git操作、ファイル作成
- 大規模コードベース分析（→ Gemini）
- 外部リサーチ、ドキュメント検索（→ Gemini）
- マルチモーダル処理（→ Gemini）

## 性格傾向バイアス

Codex (GPT系) は指示に忠実で、失敗データに対しても比較的ニュートラル。ただし「精度を上げろ」等の曖昧な指示には教科書的な定番施策のみ提案する傾向がある。**具体的な仮説や方向性を含む指示**を与えることで提案の質が上がる。

## Safety Claim を過信しない

外部記事には「Codex は deny by default で安全」という一般化された主張が多いが、当 dotfiles は `codex-best-practice/README.md` の `trusted` profile (workspace-write + on-request approval) で運用している。**profile 設計を確認せず Codex の安全性を仮定しない**。実際に有効な safety boundary は (1) profile 設定 (`development` / `trusted` / `security`) と (2) lefthook pre-commit / commit-msg、(3) `protect-linter-config` 等の hook 群で構成される。

## Expertise Map

ドメイン別の expertise score は `references/model-expertise-map.md` を参照。`/debate` の重み付けに使用。

## 言語プロトコル

Codex への指示は英語。結果はユーザーの言語（日本語）で報告。
