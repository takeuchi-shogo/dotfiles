# Architecture Document Template

`docs/architecture.md` 生成時の構造テンプレート。
document-factory (mode: context) がプロジェクト分析結果に基づいて適用可能セクションを選択する。

---

## セクション構成

全セクションを含めるのではなく、プロジェクトに該当するセクションのみ生成する。

### 1. System Overview

**必須**。プロジェクトの目的と全体像を 3-5 行で記述。

```markdown
## System Overview

{プロジェクトの目的と主要なユースケースを簡潔に}
```

### 2. High-Level Architecture

**必須**。テキストベースの C4 Level 1 図（Context Diagram）。

```markdown
## High-Level Architecture

┌─────────┐     ┌──────────┐     ┌──────────┐
│  Users   │────▶│ Frontend │────▶│ Backend  │
└─────────┘     └──────────┘     └────┬─────┘
                                      │
                              ┌───────▼───────┐
                              │   Database     │
                              └───────────────┘
```

**ルール:**
- ASCII art または Mermaid で記述（プロジェクトが Mermaid 対応の場合）
- 「主要な」コンポーネント間の関係のみ。網羅ではなく概観
- データフローの方向を矢印で明示

### 3. Core Components

**必須**。主要コンポーネントの一覧表。

```markdown
## Core Components

| Component | Purpose | Tech | Key Interface |
|-----------|---------|------|---------------|
| API Server | REST API 提供 | Express.js | `src/api/` |
| Auth | 認証・認可 | Passport.js | `src/auth/` |
| Worker | 非同期ジョブ処理 | Bull Queue | `src/workers/` |
```

**ルール:**
- 各コンポーネントに Purpose（なぜ存在するか）を記述
- ファイルパスで Key Interface を示す（エージェントのナビゲーション支援）
- フレームワーク名は Breadcrumb で十分（説明不要）

### 4. Data Stores

**条件付き**: DB/キャッシュ/メッセージキューが存在する場合のみ。

```markdown
## Data Stores

| Store | Type | Purpose | Key Schema |
|-------|------|---------|------------|
| PostgreSQL | RDB | ユーザー・トランザクション | `prisma/schema.prisma` |
| Redis | Cache | セッション・レート制限 | N/A |
```

**ルール:**
- スキーマ定義ファイルがあればパスを記載
- 「主要テーブル/コレクション」の列挙は不要（スキーマファイルを参照すべき）

### 5. External Integrations

**条件付き**: 外部 API/サービス連携がある場合のみ。

```markdown
## External Integrations

| Service | Purpose | Integration Point |
|---------|---------|-------------------|
| Stripe | 決済処理 | `src/billing/stripe-client.ts` |
| SendGrid | メール送信 | `src/notifications/email.ts` |
```

**ルール:**
- API キーや認証方法の詳細は書かない（セキュリティリスク）
- 統合ポイント（ファイルパス）を明示

### 6. Security Architecture

**条件付き**: 認証/認可/暗号化の仕組みがある場合のみ。

```markdown
## Security Architecture

- **認証**: JWT + Refresh Token（`src/auth/`）
- **認可**: RBAC（Role: admin, user, viewer）
- **暗号化**: TLS 1.3（in-transit）, AES-256（at-rest）
```

**ルール:**
- 方式名のみ記述（Breadcrumb パターン）
- 実装の詳細は書かない（コードを参照）
- OWASP Top 10 への対策状況は `/security-review` の管轄

### 7. Development Setup

**必須**。開発環境のセットアップコマンド。

```markdown
## Development Setup

\`\`\`bash
# 依存インストール
npm install

# 開発サーバー起動
npm run dev

# テスト実行
npm test
\`\`\`

Prerequisites: Node.js >= 20, Docker (for local DB)
```

**ルール:**
- 実際に動作するコマンドのみ記載（検証必須）
- prerequisites は 1 行で

### 8. Architecture Decisions

**条件付き**: L レベル、または既に ADR がある場合。

```markdown
## Architecture Decisions

重要な設計判断は ADR として記録:
- [ADR-001](docs/decisions/001-template.md): {title}
```

**ルール:**
- ADR へのリンクのみ。判断の詳細は ADR 自体に記述
- ADR がまだない場合はこのセクションを省略

---

## 生成ルール

1. **該当セクションのみ生成**: 全セクションを埋めようとしない。DB がなければ Data Stores は省略
2. **Breadcrumb パターン**: フレームワークの説明は不要。`Express.js` と書けば十分
3. **ファイルパスで誘導**: エージェントが次にどのファイルを読むべきか分かるようにパスを含める
4. **網羅より正確性**: 「主要な」コンポーネントに絞る。見つけたもの全てを列挙しない
5. **検証可能な情報のみ**: コマンド、パス、設定はコードベースから検証してから記載
6. **60行以内**: architecture.md 全体で 60 行を超えない。超える場合は `references/subsystems/` に分離

## Anti-Patterns

- ディレクトリツリーの全展開（`tree` コマンドの出力をそのまま貼る）
- フレームワークの説明文（「Express.js は Node.js の...」）
- 将来の予定やロードマップ（コードに存在しないものは書かない）
- API エンドポイントの全列挙（API doc の役割）
- 環境変数やシークレットの記載
