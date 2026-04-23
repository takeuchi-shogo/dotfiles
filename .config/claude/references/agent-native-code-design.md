---
status: reference
last_reviewed: 2026-04-23
---

# Agent-Native Code Design Guide

エージェントが効率的にコードベースを理解・修正できるよう設計する5原則。
出典: Factory.ai, every.to "Agent-Native Architectures", 逆瀬川 "Coding Agent Workflow 2026"

## 1. Grep-able 命名

エージェントの主要な探索手段は `grep`, `glob`, `cat`。検索で見つかる命名が効率を決定的に左右する。

- **named export を強制**: `export default` より `export function fetchUser()` を優先
- **一貫したエラー型**: `XxxError` の命名規約で grep 一発で全エラーを列挙可能にする
- **マジックストリングの排除**: 定数に名前を付け、grep で参照箇所を追跡可能にする
- **ファイル名 = 主要 export 名**: `userService.ts` → `export class UserService`

## 2. Collocated Tests

テストをソースの隣に配置し、`ls` 一回でテストの有無を確認できるようにする。

- **配置**: `src/auth/login.ts` → `src/auth/__tests__/login.test.ts`
- **命名規約**: `{SourceName}.test.{ext}` を統一
- **効果**: エージェントがテストの存在を即座に判定でき、テストなしコードの検出が容易

## 3. 機能単位モジュール化

水平スライス（`services/`, `controllers/`, `models/`）ではなく、機能単位で凝集する。

- **NG**: `services/user.ts`, `controllers/user.ts`, `models/user.ts`（3ディレクトリにジャンプ）
- **OK**: `features/user/service.ts`, `features/user/controller.ts`, `features/user/model.ts`（1ディレクトリで完結）
- **効果**: エージェントのディレクトリジャンプを最小化し、関連ファイルの見落としを防止

## 4. テスト = 報酬信号

テスト合格/不合格がエージェントの実装の正否を判定する唯一の信頼できる信号。

- テストのないコードパスはエージェントにとって **品質保証不能**
- 新機能追加時はテストを先に書く（TDD）か、最低でも同時に書く
- テストカバレッジが低い領域は、エージェントが変更する前に `/autocover` でテストを補強

## 5. API 境界の明確化

マルチエージェント並列実行の前提条件。モジュール間のインターフェースを先に合意する。

- **型定義を先に**: `types.ts` / `interface.go` でモジュール間契約を定義
- **API 契約 = 並列の境界**: 契約が安定していればエージェントは独立に実装可能
- **変更の伝播を限定**: 内部実装の変更がインターフェースに漏れない設計（カプセル化）

## Inner Loop / Outer Loop

導入は2段階で行う:

1. **Inner Loop** (IDE内): compile → test → debug の規律確立。ここが Agent-Native の基盤
2. **Outer Loop** (CI/CD): Issue → PR → Review → Merge のガバナンス。Inner Loop が安定してから

## 適用指針

- これらは **新規プロジェクト設計時** の原則。既存コードの全面リファクタリングを推奨するものではない
- 既存コードへの適用は、変更対象のモジュールから段階的に行う
- code-reviewer エージェントのチェックリストに反映して、レビュー時に自然に適用される
