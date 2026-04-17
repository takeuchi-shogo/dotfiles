---
date: 2026-04-17
task: Hermes absorb Plan A1 (JSONL secret 監査)
tool: scripts/security/scan-jsonl-secrets.py
scope: ~/.claude/{projects,session-state,skill-data,agent-memory} + dotfiles/.claude/tacit-knowledge
status: 要対処 (HIGH 3 件)
---

# JSONL Secret 監査レポート

## サマリ

| 指標 | 値 |
|------|----|
| スキャン対象ファイル数 | 3,431 |
| スキャン行数 | 260,236 |
| スキャン バイト数 | ~606 MB |
| 総 hit 数 | 157 |

### 重大度別

| Severity | Hits | 内訳 | 判定 |
|----------|------|------|------|
| HIGH | 5 | private_key_block | **3 件要対処 / 2 件 FP** |
| MEDIUM | 89 | sk_token 69, api_key_assignment 17+, bearer_token 3 | ほぼ全て FP |
| LOW | 63 | password_assignment | ほぼ全て FP (local DB credential) |

### パターン別

| パターン | Hits | 主な内容 |
|---------|------|---------|
| `private_key_block` | 5 | RSA PKCS#8 key 3 件 (真) + ドキュメント中のパターン説明 2 件 (FP) |
| `sk_token` | 69 | `risk-analysis.md` の `risk-` と task ID の `task_` への誤マッチ |
| `api_key_assignment` | 17+ | `.env.example` の placeholder, 本レポートの recursive hit |
| `bearer_token` | 3 | 既にマスク済みの `Authorization: '***'` 表示 |
| `password_assignment` | 63 | `POSTGRES_PASSWORD` (docker compose local), gemini auth の空値 |

## 🚨 要対処項目 (HIGH, 真陽性)

### 1. hearable-app transcript に RSA private key が記録

**場所**:
```
~/.claude/projects/-Users-takeuchishougo-dev-app-hearable-app/51de455c-a96f-438f-9779-51ff06b26af9/subagents/
  - agent-a3a3ec5.jsonl:24
  - agent-a88aed6.jsonl:68
  - agent-ad0e617.jsonl:103
```

**内容**: `SURVEY_GRPC_JWT_AUTH_PRIVATE_KEY="\n-----BEGIN ... KEY-----\nMIIJRAIBAD...`

`.env` の内容がサブエージェントの transcript に展開されている。PKCS#8 RSA private key が平文で残留。

**推奨対処** (ユーザー判断):

1. **Rotate**: `SURVEY_GRPC_JWT_AUTH_PRIVATE_KEY` を新しいキーペアに差し替え (対象サービス側で公開鍵更新)
2. **Cleanup**: 該当 3 jsonl を削除 or 該当行のみ削除 (session 継続性より漏洩リスク優先なら削除)
3. **Prevent**: A2 (redactor 統合) + `.env` 内容を読む前にマスクする pre-hook を検討

### 2. (追加の真陽性なし)

## 誤検出 (False Positive) 分析

### sk_token (69/69 FP)

- `tmp/plans/risk-analysis.md` が `sk-analysis` とマッチ
- `"toolUseID":"task_..."` が `sk-...` とマッチ
- **提案**: A2 redactor では `sk-` の前が word boundary `\b` であることを要求する

### api_key_assignment

- `FATHOM_API_KEY=your_fathom_key_here` など .env.example のプレースホルダー
- 本レポート自体の transcript が自己言及で recursive hit

### password_assignment (63/63 FP)

- `POSTGRES_PASSWORD: hearable_local_password` (docker compose, local-only)
- `username: '', password: ''` (空値)
- **提案**: A2 redactor では空値や `_local_` などの明らかな非 secret を除外

### bearer_token (3/3 FP)

- `'Authorization: '***''` など既にマスク済み値
- **提案**: 値が `***` または `REDACTED` を含む場合は skip

## A2 Redactor 改善提案 (このレポートを根拠に)

1. **sk_token**: 先頭に `\b` または非 word 文字を要求 (`(?<![A-Za-z0-9_])sk-[...]`)
2. **password_assignment**: 値が `MASK`/`REDACTED`/空文字なら skip。 `_local_` を含む値は low → ignore tier
3. **api_key_assignment**: `=\s*['"]?(your_|example_|placeholder_|test_)` を含む場合 skip
4. **bearer_token**: 値に `*` を含む場合 skip
5. **private_key_block**: `-----BEGIN [A-Z ]+ KEY-----` 単体は説明文に頻出 → 直後 20 文字以内に base64 (`[A-Za-z0-9+/=]{20,}`) を要求

## 完了条件チェック (plan A1)

- [x] `scripts/security/scan-jsonl-secrets.py` 作成 (read-only, pattern 再利用可能な形)
- [x] `docs/security/2026-04-17-jsonl-secret-audit.md` 作成
- [x] hit 件数分類済み (真陽性 3 / 誤検出 154)
- [ ] **ユーザー対処待ち**: HIGH 3 件の rotate + cleanup 判断

## 次のステップ

A2 (Redactor 統合) に進む前に、HIGH 3 件の対処方針をユーザーに確認する。
Redactor のパターンは本レポート「A2 Redactor 改善提案」を反映する。
