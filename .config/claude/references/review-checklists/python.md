---
status: reference
last_reviewed: 2026-04-23
---

# Python Review Checklist

Python 固有のレビュー観点。`code-reviewer` が `.py` の変更をレビューする際に参照する。

## 命名規約

- 関数・変数: `snake_case`、クラス: `PascalCase`、定数: `UPPER_SNAKE_CASE`
- プライベート: `_leading_underscore`

## PY-1. PEP 8/257 準拠

- 行長: 88文字（Black）or 79文字（PEP 8）
- インポート順序: stdlib → third-party → local
- 空行: トップレベル定義間は2行、メソッド間は1行

## PY-2. 型ヒント — `T | None`

- `must:` 公開関数には型ヒントを付ける
- `Optional[T]` より `T | None`（Python 3.10+）
- `dict[str, Any]` より `TypedDict` や `dataclass`

## PY-3. Pythonic イディオム

- list/dict/set comprehension を活用
- `enumerate()`, `zip()`, `any()`, `all()`
- EAFP パターン

## PY-4. データクラス / Pydantic

- 2つ以上のフィールドを持つ dict/tuple → `@dataclass` に置き換え
- `@dataclass(frozen=True)` で immutability
- 外部入力には Pydantic `BaseModel`

## PY-5. 例外設計 — `except` 広すぎキャッチ防止

- `must:` bare `except:` は絶対禁止
- `must:` `except Exception:` はログ + re-raise しないなら指摘
- 具体的な例外を捕捉: `except (TypeError, ValueError):`

## PY-6. Import 整理

- `isort` 準拠順序
- `from module import *` は禁止
- 型ヒント用は `TYPE_CHECKING` ブロック内で: `from __future__ import annotations`

## PY-7. Mutable デフォルト引数

`must:` `def f(items: list = [])` は禁止。`None` デフォルト + 関数内初期化。

## PY-8. async/await

- `asyncio.gather()` で並列化できるケースの検出
- blocking I/O を async 関数内で呼んでいないか

## PY-9. Context Manager

- `must:` ファイル操作に `with open()` を使っているか
- `contextlib.contextmanager` デコレータの活用

## PY-10. Protocol / ABC

- `Protocol` for structural subtyping
- `ABC` for nominal subtyping
- 暗黙の duck typing を Protocol で型安全にする

## PY-11. pytest パターン

- fixture の適切な使用、parametrize でテストケース増加
- `conftest.py` の配置、assertion メッセージの具体性

## PY-12. セキュリティ — `eval`/`pickle` 禁止

- `must:` `eval()`, `exec()` は原則禁止
- `must:` `pickle` で信頼されないデータをデシリアライズしない
- `must:` `subprocess.shell=True` は避ける
- SQL: raw query ではなく ORM / パラメータバインディング

## PY-13. Performance / N+1 (CC-17 言語別補足)

- `must:` Django ORM では `select_related` (FK / 1-to-1) / `prefetch_related` (M2M / reverse FK) で eager-load
  - NG: `for post in Post.objects.all(): print(post.author.name)`
  - OK: `for post in Post.objects.select_related('author'): print(post.author.name)`
- `must:` SQLAlchemy では `joinedload` (1 クエリで JOIN) / `selectinload` (2 クエリで IN 句) を使う
  - OK: `session.query(Post).options(joinedload(Post.author)).all()`
- `consider:` `.only('id', 'title')` / `.defer('content')` で必要列に限定 (over-fetch 抑制)
- `consider:` 多数 ID 解決は `.filter(id__in=ids)` でバッチ化 (ループ内 `.get(id=...)` 禁止)
- `consider:` `django-debug-toolbar` / `query_count` で実測し、想定外の N+1 を CI で検出する
- 詳細パターン・false positive 抑制: cross-cutting CC-17
