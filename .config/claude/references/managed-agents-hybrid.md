# Managed Agents × Custom Harness — Hybrid Architecture

## 概要

Claude Managed Agents（クラウド基盤）と Custom Harness（ローカル dotfiles）を併用するアーキテクチャ。
それぞれの強みを活かし、弱みを補完する。

## アーキテクチャ

```
┌─────────────────────────────┐
│  Managed Agents 層          │  計画・推論・スケジュール実行
│  (クラウド基盤)              │  Event-triggered / Scheduled / Fire-and-forget
├─────────────────────────────┤
│  Custom Harness 層          │  コード変更・ビルド・テスト・検証
│  (ローカル dotfiles)         │  hooks, skills, agents, worktree 隔離
├─────────────────────────────┤
│  ローカル環境               │  成果物・秘匿データ・OS 操作
│  (zsh, gh, kubectl, etc.)   │
└─────────────────────────────┘
```

## 使い分け基準

### Managed Agents を選ぶ場面

| 条件 | 理由 |
|------|------|
| チーム規模で同一タスク反復 | インフラ保守をベンダーに委託 |
| Scheduled / Event-triggered | クラウド基盤の信頼性（launchd 停止リスク回避） |
| Fire-and-forget（Slack/Teams 経由） | 外部サービス連携が組み込み済み |
| ハーネス更新の追従コストが高い | Managed Agents はモデル進化に自動追従 |

### Custom Harness を維持する場面

| 条件 | 理由 |
|------|------|
| OS 密着操作（zshrc, gh, kubectl） | サンドボックス制約を回避 |
| 厳格な検証ゲート（Codex Review Gate） | カスタム品質基準の強制 |
| 秘匿データのローカル保持 | ベンダーサーバーに預けない |
| 任意言語・バイナリ統合 | サンドボックスの制限なし |
| 高速な短時間タスク | コールドスタート 3-8秒を回避 |

## トレードオフ（注意事項）

### コスト管理

- **ハード予算キャップ必須**: 長期タスクの自律再試行で一晩数千ドルの事例あり
- トークン上限をエージェントごとに設定
- 段階的実行: 大規模タスクは小分けにして段階実行

### コールドスタート

- 環境セットアップ: 3-8秒
- 短時間タスク × 多数並列では無視できない
- → 短時間タスクは Custom Harness（即座に起動）を優先

### ベンダーロックイン

- Agent 設定/学習履歴のポータビリティが低い
- 対策: `references/agent-portability.md` 参照
- Decision Journal で設計決定を記録し、移行時に再現可能にする

### 推論品質 ≠ 実装品質

- Managed Agents の計画・推論は高品質だが、実装の検証は Custom Harness が担う
- 既存の Codex Review Gate + verification-before-completion で補完

## マルチモデルルーティングとの統合

既存のルーティング（CLAUDE.md）に Managed Agents を追加:

| モデル/基盤 | 得意領域 | 委譲タスク例 |
|------------|----------|-------------|
| **Managed Agents** | クラウド実行・スケジュール・外部連携 | 日次ブリーフ、Event-triggered PR、Slack 応答 |
| Sonnet | 高速実装・定型作業 | ファイル探索、コード実装、テスト作成 |
| Haiku | 軽量な情報取得 | WebFetch+要約、フォーマット変換 |
| Codex | 異視点の深い推論 | 設計の壁打ち、リスク分析、コードレビュー |
| Gemini | 1Mコンテキスト | コードベース全体分析、外部リサーチ |

## 関連ドキュメント

- `references/agent-config-standard.md` — Agent 定義の標準化
- `references/managed-agents-scheduling.md` — スケジュール実行の移行検討
- `references/agent-portability.md` — ベンダーロックイン回避
- `docs/agent-harness-contract.md` — 既存ハーネスの設計契約
