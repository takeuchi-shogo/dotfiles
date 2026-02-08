---
name: senior-frontend
description: React/Next.js開発のベストプラクティスガイド。コンポーネント設計、パフォーマンス最適化、状態管理、アクセシビリティ。
---
# Senior Frontend Guide

## コンポーネント設計
- hooks, context, composition パターンで再利用可能なコンポーネントを構築
- Mobile-first レスポンシブデザイン（Tailwind CSS）
- Semantic HTML + ARIA で WCAG 準拠

## パフォーマンス最適化
- React.memo, useMemo, useCallback で不要な再レンダリングを防止
- Dynamic imports + React.lazy でコード分割
- Image最適化（next/image, srcset）

## 状態管理
- ローカル状態: useState/useReducer
- グローバル状態: Zustand or Context API
- サーバー状態: TanStack Query / SWR

## TypeScript統合
- Props には明示的な型定義（interface推奨）
- Generic components で再利用性を確保
- strict モードを常に有効化
