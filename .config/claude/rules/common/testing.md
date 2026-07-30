---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
  - "**/*.go"
  - "**/*.py"
  - "**/*.rs"
  - "**/*.test.*"
  - "**/*.spec.*"
  - "**/*_test.*"
---

# Testing Requirements

## Test Coverage Target: 80%+

Test Types (all required for production code):
1. **Unit Tests** — Individual functions, utilities, components
2. **Integration Tests** — API endpoints, database operations
3. **E2E Tests** — Critical user flows

## Test-Driven Development

Preferred workflow:
1. Write test first (RED)
2. Run test — it should FAIL
3. Write minimal implementation (GREEN)
4. Run test — it should PASS
5. Refactor (IMPROVE)
6. Verify coverage

### 後から書いたテストは識別力を確認する

TDD の RED は「先に書く」場合しかカバーしない。既存コードに後からテストを足したときは、
**仕様を壊す代表的な defect を対象に一時的に入れて、赤くなるのを見てから戻す**。
壊れたコードでも通るテストは、意図した対象とは別の何かをテストしている。

適用範囲は、誤った値を静かに返しうる対象に限る（変換・バリデータ・境界計算・設定解釈）。
自明な getter や型で保証済みの経路には要求しない。

### テストを書く順序は「どれだけ静かに失敗するか」で決める

例外を投げる関数は自分で失敗を報告する。怖いのは、それらしい誤った値を返すものの方で、
これはユーザーが気づくまで見えない。カバレッジのギャップを埋めるときは次の順で潰す。

1. 例外を投げずに誤った値・意図しない副作用を返しうる経路 — off-by-one、バイト数と文字数の
   取り違え、ずれた日付、大文字小文字の扱いを誤った拡張子判定、ゆるすぎるバリデータ
2. 公開 API / エクスポート関数（利用者に影響）
3. ビジネスロジック
4. 例外を投げるエラーパス（失敗が自己申告されるぶん検出は早い）
5. ユーティリティ関数

1 つの関数が複数に該当するときは、先に「静かに誤るか」を判定する。該当すれば 1 に置き、
残りを 2-5 に振り分ける。

## Test Quality Rules

- Tests should be independent and isolated
- No shared mutable state between tests
- Use descriptive test names that explain the scenario
- Arrange-Act-Assert pattern
- Mock external dependencies, not internal logic
- Test edge cases and error paths

### Few-shot Examples

```typescript
// NG: 不明瞭なテスト名
test("test1", () => { ... });

// OK: シナリオを説明する名前
test("should return validation error when email is empty", () => { ... });
```

```typescript
// NG: Arrange-Act-Assert が混在し、複数の振る舞いを1テストに詰め込む
test("user creation", () => {
  const user = createUser("alice");
  expect(user.name).toBe("alice");
  user.activate();
  expect(user.isActive).toBe(true);
});

// OK: 1テスト1振る舞い、AAA を明確に分離
test("should create user with given name", () => {
  // Arrange
  const name = "alice";
  // Act
  const user = createUser(name);
  // Assert
  expect(user.name).toBe("alice");
});

test("should activate user", () => {
  const user = createUser("alice");
  user.activate();
  expect(user.isActive).toBe(true);
});
```

## Test Comments (前提・事前条件・検証項目)

> 出典: erukiti「実践フルAIコーディングのための考え方とノウハウ」(Zenn 2024-12) — AI が書くテストはコメントを省略しがちで、後で読んだ AI も人間も「何を検証しているか」が読み取れなくなる。

テストには以下 3 要素を **TSDoc / docstring / コメント** で明示する。言語非依存の汎用ルール:

| 要素 | 内容 |
|------|------|
| **前提条件** | 環境・データの初期状態 (例: DB に user A が存在、外部 API は mock 済み) |
| **事前条件** | テスト対象の関数を呼ぶ直前の状態 (例: user A はログイン済みかつ未認証フラグ) |
| **検証項目** | 何が成立すれば pass か (例: 戻り値が { ok: false, code: "AUTH_REQUIRED" } である) |

**粒度の基準**: 「**プロジェクト外の慣れていないエンジニアが読んで、このテストが何を保証しているか分かる**」水準。テスト名だけで全部書こうとせず、コメントに逃がす。

### Few-shot Example (TypeScript / vitest)

```typescript
// NG: 何を保証するテストか不明
test("should fail", () => {
  const r = login("a", "wrong");
  expect(r.ok).toBe(false);
});

// OK: 前提・事前・検証項目が読み取れる
/**
 * 前提: user "a" は DB に存在し、password ハッシュは "correct" 由来。
 * 事前: ログイン試行は初回（rate limit に未到達）。
 * 検証: 誤パスワード時は { ok: false, code: "INVALID_CREDENTIALS" } を返し、
 *       失敗カウンタは 1 増えること。
 */
test("returns INVALID_CREDENTIALS and increments failure count on wrong password", () => {
  const before = getFailureCount("a");
  const r = login("a", "wrong");
  expect(r).toEqual({ ok: false, code: "INVALID_CREDENTIALS" });
  expect(getFailureCount("a")).toBe(before + 1);
});
```

## Troubleshooting Test Failures

1. Use **test-engineer** agent for test strategy
2. Use **debugger** agent for root cause analysis
3. Fix implementation, not tests (unless tests are wrong)
4. Check test isolation — failing in CI but passing locally?
