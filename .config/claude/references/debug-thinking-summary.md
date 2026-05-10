# Debug Thinking Summary 運用ガイド

`showThinkingSummaries` settings.json key の運用方針。

## 何の設定か

公式 docs (`code.claude.com/docs/en/settings`) より逐語:

> Show extended thinking summaries in interactive sessions. When unset or false (default in interactive mode), thinking blocks are redacted by the API and shown as a collapsed stub. Redaction only changes what you see, not what the model generates: to reduce thinking spend, lower the budget or disable thinking instead. Non-interactive mode (-p) and SDK callers always receive summaries regardless of this setting.

要点:
- redaction は**表示**のみ、モデルの thinking spend は変わらない
- interactive モード default: redacted (collapsed stub のみ表示)
- non-interactive (`-p`) / SDK は常に summary 受信
- 「思考量を減らしたい」なら budget/disable thinking で制御 (`MAX_THINKING_TOKENS=0` or effort level 下げ)

## 運用方針: 常時 OFF (= 未設定)

settings.json には**追加しない**。理由:

| 観点 | 常時 ON のコスト | 常時 OFF (default) の利益 |
|------|----------------|------------------------|
| UI 情報密度 | thinking の全文 verbose 表示で実出力が押し下がる | 必要な出力に集中できる |
| デバッグ精度 | summary は要点のみ抽出 (full chain ではない) | 必要時のみ flag/CLI で full chain 取得 |
| トークンコスト | 変わらない (redaction は表示のみ) | 変わらない |

## いつ ON にするか

以下の状況でのみ一時的に有効化する:

1. **モデルが誤判断した原因を debug したい**: thinking summary を見ると「どの前提を取ったか」が分かる
2. **エージェントの reasoning ループ調査**: subagent の判断 trace を確認したい
3. **prompt engineering**: プロンプトの効き方を thinking で観察

## 一時 ON の方法

### 方法 1: セッション単位 (推奨)

```bash
claude --settings '{"showThinkingSummaries": true}' "query"
```

CLI `--settings` flag は当該セッションのみ override。settings.json は変更しない。

### 方法 2: print mode の場合

`-p` / SDK は default で summary を返す (上記 docs の通り)。設定不要。

### 方法 3: settings.json 一時編集 (非推奨)

settings.json に `"showThinkingSummaries": true` を**一時追加し、debug 終了後に戻す**。忘れがちなので非推奨。

## 関連設定

| key/var | 関係 |
|--------|------|
| `effortLevel` (settings: `xhigh`) | thinking budget の上限。下げると thinking 全体が短くなる (summary も含めて) |
| `CLAUDE_CODE_EFFORT_LEVEL` env var | 上記 settings を session override |
| `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` (settings.json:8) | adaptive 無効化。**ただし Opus 4.7 では no-op** (公式 docs: "Has no effect on Opus 4.7, which always uses adaptive reasoning")。Opus 4.6 / Sonnet 4.6 のみ有効 |
| `MAX_THINKING_TOKENS` env var | fixed budget。`0` で thinking 自体を無効化 |

## 出典

- 公式 docs: `https://code.claude.com/docs/en/settings` (showThinkingSummaries の項)
- 公式 docs: `https://code.claude.com/docs/en/env-vars` (CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING の Opus 4.7 注記)
- 分析: `docs/research/2026-05-10-zodchixquant-15-settings-absorb-analysis.md`
