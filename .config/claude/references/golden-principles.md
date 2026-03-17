# Golden Principles（自動検証用）

rules/ はエージェント向けの指示。このファイルは hooks による自動検証用のパターン集。
golden-check.py が参照し、コード変更時に逸脱を軽量検出する。

---

## GP-001: 共有ユーティリティ優先

- **原則**: 同一ロジックの重複より共有ユーティリティを使う
- **検出パターン**: 新規ファイルで既存 utils/ や helpers/ に類似関数がある場合
- **キーワード**: `function`, `def`, `const.*=.*=>`（新規関数定義）
- **例**: NG: 新規 `formatDate()` を定義 → OK: 既存 `utils/date.ts` を import して使用

## GP-002: バウンダリでバリデーション

- **原則**: 外部入力を受け取る関数では入力をバリデーションする
- **検出パターン**: API handler, CLI parser で raw input を直接使用
- **キーワード**: `req.body`, `req.query`, `req.params`, `sys.argv`, `os.Args`（バリデーションなし）
- **例**: NG: `req.body.email` を直接使用 → OK: schema validation ライブラリで validate してから使用

## GP-003: 退屈な技術を好む

- **原則**: 新しいライブラリの追加は慎重に。安定した技術を優先
- **検出パターン**: package.json, go.mod, Cargo.toml, requirements.txt への新規依存追加
- **ファイル**: `package.json`, `go.mod`, `Cargo.toml`, `requirements.txt`, `pyproject.toml`
- **例**: NG: 新 dep 追加理由なし → OK: 既存 dep で解決可能か検証済み、不可の根拠をコメント

## GP-004: エラーを握り潰さない

- **原則**: catch/recover ブロックで空の処理やログのみは避ける
- **検出パターン**: `catch` ブロック内が空、または `console.log` のみ
- **キーワード**: `catch`, `except`, `recover`

## GP-005: 型安全性の維持

- **原則**: any/interface{} の多用を避け、具体的な型を使う
- **検出パターン**: `any` 型の新規使用、`interface{}` の新規使用
- **キーワード**: `: any`, `as any`, `interface{}`

> **注意**: GP-006〜008 は静的解析での自動検出が困難なため、
> code-reviewer によるレビュー観点として参照する。golden-check.py のスキャン対象外。

## GP-006: 開放閉鎖原則 (OCP)

- **原則**: 既存コードの変更ではなく、新規追加で機能を拡張する
- **検出パターン**: 既存関数への条件分岐追加（if/switch の肥大化）、既存クラスの責務拡大
- **キーワード**: 既存関数内の `if.*type`, `switch`, `case` の追加（5分岐以上）

## GP-007: インターフェース分離 (ISP)

- **原則**: クライアントが使わないメソッドへの依存を強制しない。巨大インターフェースより小さい特化型
- **検出パターン**: 10+ メソッドの interface 定義、空実装や `not implemented` を含むメソッド
- **キーワード**: `interface`, `trait`, `protocol`（メソッド数が多い定義）

## GP-008: 依存性逆転 (DIP)

- **原則**: 上位モジュールは下位モジュールの具体実装に依存しない。抽象（interface）に依存する
- **検出パターン**: 関数内での具体クラスの直接インスタンス化、テスト困難な密結合
- **キーワード**: `new `, `import` で具体実装を直接参照（DI コンテナや factory を経由していない）

## GP-009: ゴーストファイル防止

- **原則**: 既存ファイルを修正せず、同名・類似名の新規ファイルを作成しない
- **検出パターン**: Write ツールでの新規ファイル作成時、同ディレクトリに類似ファイルが存在
- **キーワード**: 新規ファイル作成（Write ツール、`file_path` が既存ファイルと名前が似ている）
- **背景**: OX Security/Snyk 調査で AI 生成コードの主要アンチパターンとして報告
- **例**: NG: `userService2.ts` を新規作成 → OK: 既存 `userService.ts` を Edit で修正

## GP-010: コメント過多防止

- **原則**: コメントはコードが「なぜ」そうなっているかを説明する。「何を」しているかはコード自体で表現する
- **検出パターン**: ファイル内のコメント行比率が 40% を超える場合に警告
- **キーワード**: `//`, `#`, `/* */`, `"""`（コメント行が多すぎる）
- **背景**: AI リポジトリの 90-100% で "Comments Everywhere" パターンが報告（OX Security）
- **例**: NG: 全行に `// increment i` 式の自明なコメント → OK: 非自明なビジネスロジックのみコメント

## GP-011: Breaking Change 防止

- **原則**: export された関数・型のシグネチャを変更する場合、呼び出し元への影響を確認する
- **検出パターン**: `export` された関数・型の引数・戻り値が Edit で変更された場合
- **キーワード**: `export function`, `export const`, `export type`, `export interface`, `export class`, `export enum`, `export default` の diff 内変更（現在: TS/JS のみ）
- **背景**: SWE-CI ベンチマーク (arXiv:2603.03823) で regression の主要原因。75% のモデルがシグネチャ変更時に呼び出し元を壊す
