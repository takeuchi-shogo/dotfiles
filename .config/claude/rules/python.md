---
paths:
  - "**/*.py"
  - "**/pyproject.toml"
---

# Python Rules

PEP 8・Effective Python・Fluent Python に基づく。

## プロジェクト構造

### src layout を採用する

```
project/
├── src/my_project/   # 再利用可能なコード
│   └── __init__.py
├── tests/            # pytest
├── pyproject.toml    # プロジェクト定義
└── uv.lock           # 依存ロック
```

ML/データサイエンスプロジェクトでは以下を追加:

```
project/
├── configs/          # 設定ファイル（YAML/TOML）
├── scripts/          # エントリポイント（種類別に整理）
│   ├── data/         # データ前処理
│   ├── training/     # 学習実行
│   ├── evaluation/   # 評価・分析
│   └── plots/        # 可視化
├── src/my_project/
└── ...
```

- `scripts/` はエントリポイント。再利用可能なロジックは `src/` に分離する
- 学習ロジックと可視化を1ファイルに混ぜない — 責務ごとにスクリプトを分ける

### パッケージ管理

- `uv` を推奨（pip/poetry より高速、ロックファイル標準対応）
- `pyproject.toml` に依存を集約する（`setup.py` / `requirements.txt` は非推奨）
- `uv.lock` をバージョン管理に含める — 再現性の担保

## 設定の外部化

ハードコードされたパラメータを設定ファイルに分離する:

```python
# NG: ハードコード
learning_rate = 0.001
batch_size = 32

# OK: 設定ファイルから読み込む
from omegaconf import OmegaConf

cfg = OmegaConf.load("configs/train.yaml")
learning_rate = cfg.learning_rate
batch_size = cfg.batch_size
```

- `omegaconf`: YAML ベースの階層的設定管理（CLIオーバーライド対応）
- `pydantic-settings`: 環境変数 + .env + バリデーション統合
- 設定クラスには型ヒントを付ける — 不正な値を起動時に検出する

## 型ヒント

### 公開関数には型ヒントを必須とする

```python
# NG: 型ヒントなし
def process(data, threshold):
    return [d for d in data if d > threshold]

# OK: 入出力の意図が明確
def process(data: list[float], threshold: float) -> list[float]:
    return [d for d in data if d > threshold]
```

- `T | None`（Python 3.10+）を `Optional[T]` より優先する
- `dict[str, Any]` より `TypedDict` や `@dataclass` を使う
- 型ヒント専用 import は `TYPE_CHECKING` ブロック内に:
  ```python
  from __future__ import annotations
  from typing import TYPE_CHECKING
  if TYPE_CHECKING:
      from heavy_module import HeavyClass
  ```

## データモデル

### dataclass / Pydantic を dict より優先する

```python
# NG: 素の dict
config = {"lr": 0.001, "epochs": 100, "name": "exp1"}

# OK: 型安全なデータクラス
@dataclass(frozen=True)
class TrainConfig:
    lr: float = 0.001
    epochs: int = 100
    name: str = "exp1"
```

- `@dataclass(frozen=True)` でデフォルト immutable
- 外部入力（API/ファイル/ユーザー入力）には Pydantic `BaseModel` でバリデーション
- 2つ以上のフィールドを持つ dict/tuple は dataclass に置き換える

## エラーハンドリング

- bare `except:` は絶対禁止
- `except Exception:` はログ + re-raise を必ず伴う
- 具体的な例外を捕捉する: `except (TypeError, ValueError):`
- ファイル操作には `with` 文（context manager）を必ず使う

## Pythonic イディオム

- list/dict/set comprehension を活用する
- `enumerate()`, `zip()`, `any()`, `all()` を明示的ループより優先する
- EAFP（Easier to Ask Forgiveness than Permission）パターンを許容する

## Import 規約

- 順序: stdlib → third-party → local（`isort` 準拠）
- `from module import *` は禁止
- mutable デフォルト引数は禁止: `def f(items: list = [])` → `def f(items: list | None = None):`

## セキュリティ

- `eval()`, `exec()` は原則禁止
- `pickle` で信頼されないデータをデシリアライズしない
- `subprocess` では `shell=True` を避ける
- SQL は ORM / パラメータバインディングを使う

## テスト

- pytest を使用する
- `@pytest.mark.parametrize` でテストケースを増やす
- fixture と `conftest.py` を適切に配置する
- assertion メッセージを具体的に書く
