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
