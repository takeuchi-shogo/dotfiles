---
status: reference
last_reviewed: 2026-04-23
---

# .claudeignore テンプレート

document-factory (mode: constitution) が新プロジェクトの `.claudeignore` を生成する際のベース。
検出された Tech Stack に応じて該当セクションを組み合わせる。

---

## 共通（全プロジェクト）

```
# Build outputs
dist/
build/
out/
.next/
.nuxt/
.output/

# Dependencies (always exclude)
node_modules/
vendor/
.venv/
venv/

# Logs & temp
*.log
tmp/
.tmp/
.cache/

# Coverage & reports
coverage/
.nyc_output/
htmlcov/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Environment (security)
.env
.env.*
!.env.example

# OS
.DS_Store
Thumbs.db
```

## JavaScript / TypeScript

```
# Lock files (large, noisy)
package-lock.json
yarn.lock
pnpm-lock.yaml
bun.lockb

# Generated types
*.d.ts.map
.tsbuildinfo
```

## Python

```
__pycache__/
*.pyc
*.pyo
*.egg-info/
.mypy_cache/
.ruff_cache/
.pytest_cache/
```

## Go

```
# Binary outputs
/bin/
*.exe
*.test
*.out
```

## Rust

```
target/
Cargo.lock
```

## Docker

```
.docker/
```

## Monorepo 追加

```
# Turborepo
.turbo/

# Nx
.nx/
```

---

## 使い方

1. 「共通」セクションは常に含める
2. 検出された言語のセクションを追加
3. プロジェクト固有の大きなディレクトリ（data/, assets/raw/ 等）があれば追記
4. `.gitignore` を参考に、ビルド成果物やキャッシュを確認
