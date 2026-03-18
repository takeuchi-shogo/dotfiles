---
name: senior-frontend
description: >
  React/Next.js のフロントエンドアーキテクチャ意思決定ガイド。コンポーネント設計、状態管理選定、
  アクセシビリティ計画。Use when making frontend architecture decisions: component design,
  state management selection, or accessibility planning.
  Do NOT use for specific React performance optimization — use react-best-practices skill instead.
allowed-tools: "Read, Grep, Glob"
metadata:
  pattern: tool-wrapper
---

# Senior Frontend — 設計意思決定ガイド

フロントエンド設計に関する判断を支援するガイド。パフォーマンス最適化の詳細は react-best-practices スキルに委譲。

## デシジョンツリー

### 1. Server Component vs Client Component (Next.js App Router)

```
データフェッチのみ          → Server Component
インタラクティブ要素あり    → Client Component
SEO が重要                 → Server Component
ブラウザ API 使用          → Client Component
```

| 判断基準 | Server Component | Client Component |
|----------|-----------------|-----------------|
| データフェッチ | 直接 DB/API アクセス可 | useEffect / TanStack Query |
| バンドルサイズ | JS に含まれない | バンドルに追加 |
| インタラクション | 不可 | useState, onClick 等 |
| SEO | 最適 | 追加設定が必要 |

**原則**: デフォルトは Server Component。`"use client"` は必要な場合のみ。

### 2. 状態管理選定

| データの種類 | 推奨 | 理由 |
|-------------|------|------|
| UI状態（モーダル開閉等） | useState | コンポーネントローカルで十分 |
| フォーム状態 | React Hook Form | バリデーション・パフォーマンス最適化込み |
| 複雑なローカル状態 | useReducer | 状態遷移が明確になる |
| グローバルUI状態 | Zustand | 軽量、ボイラープレート少 |
| テーマ / 言語 | Context API | 低頻度更新に最適 |
| サーバーデータ | TanStack Query | キャッシュ・再検証・楽観的更新 |

**アンチパターン**: サーバーデータを Zustand/Redux に入れない → TanStack Query に任せる。

### 3. コンポーネント抽出の判断

以下のいずれかに該当したら抽出:

- **再利用**: 2箇所以上で同じ構造が出現
- **複雑さ**: 100行を超える JSX
- **責務**: 1つのコンポーネントが2つ以上の責務を持つ
- **テスタビリティ**: 単体テストしたいロジックがある

**抽出しない**: 1箇所でしか使わない短い JSX は inline のままでOK。

### 4. テスト戦略

| テスト層 | ツール | 対象 |
|----------|--------|------|
| Unit | Vitest | ユーティリティ関数、カスタムフック |
| Integration | Testing Library | コンポーネントの振る舞い |
| E2E | Playwright | ユーザーフロー全体 |
| Visual | Storybook + Chromatic | UIの見た目の変化検出 |

**テストの優先順位**: Integration > Unit > E2E > Visual

## アクセシビリティチェックリスト (WCAG 2.1 AA)

### キーボード操作
- [ ] すべてのインタラクティブ要素が Tab でフォーカス可能
- [ ] フォーカス順序が論理的
- [ ] モーダル内でフォーカストラップが機能
- [ ] Escape でモーダル / ドロップダウンが閉じる

### スクリーンリーダー
- [ ] 画像に適切な alt テキスト（装飾画像は `alt=""`）
- [ ] フォーム要素に label が紐付いている
- [ ] 動的コンテンツ変更に aria-live が設定
- [ ] ランドマーク（nav, main, aside）が適切に使用

### ビジュアル
- [ ] テキストと背景のコントラスト比 4.5:1 以上
- [ ] フォーカスインジケーターが視認可能
- [ ] 色だけに依存しない情報伝達
- [ ] テキストが 200% まで拡大可能

## コンポーネントパターン選定

| パターン | いつ使う |
|----------|---------|
| Compound Component | 親子関係のある UI（Tabs, Accordion） |
| Render Props | 描画ロジックの柔軟な委譲 |
| Headless UI | ロジックのみ提供、スタイルは利用側 |
| HOC | クロスカッティング（認証ラップ等）— hooks で代替可能なら hooks |

詳細なパターン集は `references/component-patterns.md` を参照。

## Gotchas

- **over-memoization**: useMemo/useCallback の乱用は可読性を下げ、効果も薄い。プロファイラで計測してから適用
- **state scope creep**: グローバル state に何でも入れると再レンダリング地獄。コンポーネントローカル state を優先
- **hydration mismatch**: SSR/SSG で server と client の出力が異なると hydration エラー。動的コンテンツは useEffect 内で
- **bundle size 盲点**: 依存追加時に bundle analyzer で影響を確認。tree-shaking が効かないライブラリに注意
- **アクセシビリティ後付け**: 設計段階で ARIA/keyboard navigation を組み込む。後から付けると手戻りが大きい
