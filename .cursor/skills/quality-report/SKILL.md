---
name: quality-report
description: プロジェクトの品質メトリクス（静的解析警告、コード複雑度、重複密度）をレポートする。MSR'26 論文の3指標を計測。
---

# Quality Report Skill

## When to Use

- プロジェクトの品質状態を把握したい時
- 品質劣化の傾向を検出したい時
- リファクタリングの優先度を決めたい時

## Metrics (MSR '26 Paper Indicators)

1. **Static Analysis Warnings**: lint 警告数（reliability, maintainability, security）
2. **Code Complexity**: ファイル別の行数、関数の最大行数、ネスト深度
3. **Duplicate Line Density**: 重複コードブロックの割合

## Workflow

1. lint を実行し警告を集計:
   - TypeScript: `npx eslint . --format json` or `npx biome check .`
   - Python: `ruff check . --output-format json`
   - Go: `golangci-lint run --out-format json`
   - Rust: `cargo clippy --message-format json`
2. ファイル別の行数と複雑度を分析:
   - 400行以上のファイルをリストアップ
   - 50行以上の関数をリストアップ
3. 重複コードを検出（利用可能なツールがあれば）
4. レポートを生成:
   ```
   # Quality Report — [Date]
   ## Summary
   - Total warnings: N (reliability: X, maintainability: Y, security: Z)
   - Files over 400 lines: N
   - Functions over 50 lines: N
   - Estimated duplicate density: X%
   ## Top Issues
   ## Trend (vs previous report)
   ```
5. プロジェクトの `docs/quality/` に保存
6. 前回レポートが存在すれば差分を表示し、劣化があれば警告
