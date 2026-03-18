# Acceptance Criteria Extraction Guide

## Supported Formats

| Format | Pattern | Example |
|--------|---------|---------|
| YAML frontmatter | `acceptance_criteria:` list | spec の frontmatter |
| Markdown checklist | `- [ ]` under "Acceptance Criteria" | spec 本文 |
| Given/When/Then | `Given ... When ... Then ...` | BDD 形式 |
| Numbered list | `1. ` under criteria heading | 番号付きリスト |

## Extraction Steps

1. spec ファイルを Read で読み込む
2. `acceptance_criteria` セクションを探す
3. 上記フォーマットのいずれかでパース
4. 各 criteria を独立した検証項目として扱う

## Verification Methods

| Criteria Type | Verification |
|--------------|-------------|
| UI/UX behavior | webapp-testing / ui-observer で確認 |
| API response | Bash で curl/httpie 実行 |
| Data integrity | DB query or file check |
| Performance | benchmark 実行 |
| Error handling | 異常系テスト実行 |
