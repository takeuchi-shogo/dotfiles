---
name: buf-protobuf
description: >
  Buf エコシステム (Buf CLI / BSR / Bufstream) で Protobuf スキーマ設計・コード生成・breaking detection、
  gRPC/ConnectRPC、Kafka 互換ストリームを扱う。Triggers: '.proto', 'buf lint/generate/breaking',
  'bufstream', 'BSR', 'protovalidate'. Not for: Buf 文脈なしの Kafka 運用。
origin: self
metadata:
  pattern: tool-wrapper
---

# Buf Protobuf — エコシステム包括ガイド

Buf エコシステムを使った Protocol Buffers 開発のすべてを支援するスキル。
スキーマ設計からストリーミング基盤まで、3つのレイヤーをカバーする。

## エコシステム概要

```
┌─────────────────────────────────────────────────────┐
│                   Buf Ecosystem                      │
├──────────┬──────────────────┬────────────────────────┤
│ Buf CLI  │ Buf Schema       │ Bufstream              │
│          │ Registry (BSR)   │                        │
│ ローカル │ スキーマの中央   │ Kafka互換メッセージ    │
│ 開発     │ 管理・配布       │ キュー + データ        │
│ ツール   │                  │ レイクハウス            │
├──────────┴──────────────────┴────────────────────────┤
│ Protovalidate: フィールドレベルのセマンティック検証   │
│ ConnectRPC: ブラウザ互換 RPC フレームワーク          │
└─────────────────────────────────────────────────────┘
```

## ワークフロー

ユーザーの意図を判定し、対応する instructions/ ファイルを Read ツールで読み込んでから作業を開始する。
複数の領域にまたがる場合は、必要なファイルを順番に読み込む。

## タスクルーティング

| ユーザーの意図 | Read で読み込むファイル |
|---------------|----------------------|
| .proto ファイルの設計・ベストプラクティス | `instructions/schema-design.md` |
| Protovalidate によるフィールド検証 | `instructions/schema-design.md` |
| buf.yaml / buf.gen.yaml の設定 | `instructions/cli-codegen.md` |
| コード生成（Go, TypeScript 等） | `instructions/cli-codegen.md` |
| リンティング・破壊的変更検出 | `instructions/quality-bsr.md` |
| CI/CD への Buf 統合 | `instructions/quality-bsr.md` |
| BSR へのモジュール公開・依存管理 | `instructions/quality-bsr.md` |
| Bufstream の構築・設定・トピック管理 | `instructions/bufstream.md` |
| セマンティック検証の設定 | `instructions/bufstream.md` |
| Iceberg テーブル連携 | `instructions/bufstream.md` + `references/bufstream-config.md` |
| Kafka 互換性・クライアント設定 | `instructions/bufstream.md` |
| Bufstream のデプロイ（Docker / Helm / クラウド） | `instructions/deployment-ops.md` + `references/bufstream-deploy.md` |
| オブザーバビリティ（メトリクス・ログ・トレース） | `instructions/deployment-ops.md` |
| Kafka vs Bufstream / gRPC vs ConnectRPC の選定 | `instructions/decision-troubleshoot.md` |
| エラー・トラブルシューティング | `instructions/decision-troubleshoot.md` |

## ファイル構成

```
buf-protobuf/
├── SKILL.md                              ← このファイル（オーケストレーター）
├── instructions/
│   ├── schema-design.md                  ← スキーマ設計 + Protovalidate
│   ├── cli-codegen.md                    ← Buf CLI 設定 + コード生成
│   ├── quality-bsr.md                    ← 品質ゲート + BSR 統合
│   ├── bufstream.md                      ← Bufstream 全般 + セマンティック検証 + Iceberg + Kafka互換
│   ├── deployment-ops.md                 ← デプロイメント + オブザーバビリティ
│   └── decision-troubleshoot.md          ← デシジョンツリー + トラブルシューティング
└── references/
    ├── bufstream-config.md               ← Bufstream 設定リファレンス（詳細）
    └── bufstream-deploy.md               ← クラウド別デプロイ手順（詳細）
```
