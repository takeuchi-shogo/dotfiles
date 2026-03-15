# Readwise × Obsidian セットアップ Playbook

## 概要

Readwise Reader で収集したハイライト・ノートを Obsidian Vault に自動同期する。

## `/digest` との棲み分け

| ソース | ツール | 理由 |
|--------|--------|------|
| YouTube 動画 | NotebookLM → `/digest` | NotebookLM の要約品質が最高 |
| Web 記事 | Readwise → 自動同期 | ハイライト→自動同期が便利 |
| Kindle 本 | Readwise → 自動同期 | ハイライト自動収集の唯一手段 |
| PDF | Claude Code 直接 | 既に読み込み可能 |

## セットアップ手順

### 1. Readwise Reader アカウント作成

1. https://readwise.io/read にアクセス
2. アカウント作成（月額 $7.99〜）
3. ブラウザ拡張をインストール

### 2. Readwise ソース接続

Readwise Reader の Settings → Connections で以下を接続:

- **Kindle**: Amazon アカウント連携（ハイライト自動同期）
- **Twitter/X**: ブックマーク同期
- **RSS フィード**: URL 追加で購読
- **ポッドキャスト**: RSS URL 追加（字幕付きで同期）

### 3. Obsidian プラグインインストール

1. Obsidian → Settings → Community Plugins → Browse
2. 「Readwise Official」を検索・インストール
3. Readwise API トークンを設定
   - Readwise → Settings → Access Token でトークン取得
   - プラグイン設定にトークンを貼り付け

### 4. 同期テンプレート設定

Readwise Official プラグインの Settings → Export format で Jinja2 テンプレートをカスタマイズ。

既存の Literature Note テンプレートに合わせる:

```jinja2
---
created: "{{ date }}"
tags:
  - type/literature
  - "topic/"
source:
  title: "{{ title }}"
  author: "{{ author }}"
  url: "{{ url }}"
  type: "{{ category }}"
---

# {{ title }}

## ハイライト

{% for highlight in highlights %}
- {{ highlight.text }}
{% if highlight.note %}
  - **メモ**: {{ highlight.note }}
{% endif %}
{% endfor %}

## 自分の考え

<!-- 後で追記 -->

## パーマネントノート候補

- [ ]
```

### 5. 同期設定

- **同期先フォルダ**: `05-Literature/readwise/`
- **同期間隔**: 自動（1-24時間で設定可能）
- **ファイル名形式**: Readwise デフォルト（著者名-タイトル）

### 6. 運用ルール

- Readwise で新しいハイライトを追加 → 自動で Obsidian に同期
- 同期されたノートは `05-Literature/readwise/` に入る
- `/obsidian-knowledge` でリンク発見・パーマネントノート生成に活用
- トピックタグは手動で追記するか、Claude Code に依頼
- 定期的に（週次で）Readwise 同期ノートをレビューし、重要なものはパーマネントノートに昇格
