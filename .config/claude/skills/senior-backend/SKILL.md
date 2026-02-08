---
name: senior-backend
description: バックエンドAPI設計・DB最適化・セキュリティのベストプラクティス。Node.js, Express, Go, Python, PostgreSQL, GraphQL対応。
---
# Senior Backend Guide

## API設計
- RESTful: リソース指向URL、適切なHTTPメソッド、バージョニング(/v1/)
- GraphQL: スキーマファースト設計、N+1防止（DataLoader）
- エラーレスポンス: RFC 7807 Problem Details 形式

## データベース
- インデックス設計: クエリパターンから逆算
- N+1問題: JOIN or バッチ取得で解決
- マイグレーション: 後方互換性を維持した段階的変更

## セキュリティ
- 認証: JWT + リフレッシュトークン or セッション
- 認可: RBAC or ABAC
- 入力検証: zod/joi でスキーマバリデーション
- SQLインジェクション: パラメータ化クエリ必須

## パフォーマンス
- キャッシュ戦略: Redis or in-memory（TTL設定）
- 非同期処理: メッセージキュー（BullMQ, SQS）
- 接続プール: DB接続の適切な管理
