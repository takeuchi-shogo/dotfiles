---
allowed-tools: Bash(python3 *agentshield-filter.py*), Bash(npx ecc-agentshield *)
description: AgentShield でエージェント設定のセキュリティ監査を実行
---

# Security Scan (AgentShield)

AgentShield (ecc-agentshield) で ~/.claude/ 配下の設定をセキュリティ監査する。
偽陽性フィルタ・重複除去・半自動再現ステージ付きラッパーを使用。

## Pipeline (Logos-shaped)

Cybozu Logos / Horos 概要で読めたステージ形状に合わせる（製品 SAST/DAST の移植ではない）:

1. **product context** — 対象は agent config（CLAUDE.md / hooks / skills / settings.json）
2. **split / scan** — AgentShield がファイルを走査（本コマンドは 1 パス）
3. **dedup + false-positive filter** — `agentshield-filter.py`
4. **reproduction check** — critical/high/medium に半自動チェックリストを付与（攻撃の自動実行はしない）
5. **feedback** — suppressed / deduped / reproductionPending を JSON・レポートに残し次回チューニング

出典: https://blog.cybozu.io/entry/logos-overview / https://blog.cybozu.io/entry/logos-harness-horos  
Caveat: Horos の PSIRT triage・DAST PoC・LLM-Wiki フィードバックは未接続。

Nightly 版: `scripts/runtime/nightly/run-security-scan.sh`

## 引数

$ARGUMENTS

- 引数なし: `~/.claude/` をスキャン（デフォルト）
- `--fix`: auto-fixable な問題を自動修正
- `--format json`: JSON 出力（CI向け）
- `--path /path/to/.claude`: 対象変更
- `--from-json FILE`: AgentShield 生 JSON を再フィルタ（オフライン / テスト）
- `raw`: フィルタなしの生スキャン

## 実行

引数に `raw` が含まれる場合:

```bash
npx ecc-agentshield scan --path ~/.claude
```

それ以外（デフォルト）:

```bash
python3 $HOME/.claude/scripts/policy/agentshield-filter.py --path ~/.claude $ARGUMENTS
```

## スコアの解釈

| Grade | Score | 状態 |
|-------|-------|------|
| A | 90-100 | 堅牢 |
| B | 70-89 | 概ね良好 |
| C | 50-69 | 改善推奨 |
| D | 30-49 | 要対応 |
| F | 0-29 | 重大リスクあり |

## Reproduction（半自動）

JSON 出力の各 finding に `reproduction.status` が付く。

- `pending` — critical/high/medium。チェックリストを人が（または別エージェントが）消化する
- `not_required` — low/info

PoC 攻撃の自動実行は行わない。再現は「引用された file:line / evidence の確認」まで。
