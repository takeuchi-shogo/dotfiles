# Agentic AI 教科書（和訳 + ビルドブリッジ）

『The Hitchhiker's Guide to Agentic AI: From Foundations to Systems』(Haggai Roitman, 2026-06, v1.2.2, 577p / arXiv:2606.24937) を、**リサーチエージェントを自分で組む**ための教科書に作り変えたもの。原PDFを和訳しつつ、各概念に「自分のスタックでどう作るか」を足す。

## この教科書の使い方

- **読む順:** 章番号順（`15` → `26`、最後に `12`）。各章ファイルは独立して読める。
- **例題の軸:** すべての「使いどころ」は **自己進化型リサーチ/知識収集エージェント**（dotfiles の `ai-tech-researcher` / `knowledge-intake` プラン）に固定。読み通すと、その設計図が下から積み上がる。
- **原PDF:** 各概念の末尾に `§章.節 / p.NNN` を付けてある。数式の完全な導出や図表が要るときだけPDFを開く。

## 概念ブロックの型（Ch16 以降）

各概念は次の6フィールドで書く。これ以上は足さない。

1. **これは何か** — 原文の要約（2-3文）
2. **いつ使う / なぜ要る** — 採否の判断基準
3. **最小実装** — 動く最小コード（Python。UI章のみ TypeScript）
4. **リサーチエージェントでの使いどころ** — 例題の軸への接続
5. **落とし穴** — 実装で踏む地雷
6. **PDF参照** — `§x.y / p.NNN`

## 和訳の取り決め

- 日本語散文。技術用語（ReAct, RAG, MCP 等）とコード識別子は英語のまま。
- AI臭を抜く（「〜することができる」→「できる」、前置き・ヘッジ・機械翻訳調の受動態を排し、行為者を主語に）。

## 深さの2段構成

- **Tier 1（フル: 和訳 + ビルドブリッジ）** — Part V 全章（Ch15-26）+ Ch12。このディレクトリの本体。
- **Tier 2（軽量: 用語集 + 各節1-2文要約）** — Part I-IV（LLM基礎 / RL本体 / 推論 / 評価）+ Part VI（早見表）。Tier 1 完走後に `tier2-reference.md` として追加予定。自分でモデルを学習させる側ではないので、用語が引ければ足りる。

## 進捗

| 章 | テーマ | レイヤー | ファイル | 状態 |
|---|---|---|---|---|
| 15 | Introduction to Agentic AI | 全体地図 | `15-introduction-to-agentic-ai.md` | ✅ |
| 16 | RAG | 知識層 | `16-rag.md` | ✅ |
| 17 | Agentic Memory | 永続層 | `17-agentic-memory.md` | ✅ |
| 18 | Agent Harness | 実行時層 | `18-agent-harness.md` | ✅ |
| 19 | Design Patterns | アーキ層 | `19-design-patterns.md` | ✅ |
| 20 | Environments & Benchmarks | 評価層 | `20-environments-benchmarks.md` | ✅ |
| 21 | MCP | ツール統合 | `21-mcp.md` | ✅ |
| 22 | Agent Skills | 能力層 | `22-agent-skills.md` | ✅ |
| 23 | A2A | エージェント間 | `23-a2a.md` | ✅ |
| 24 | Multi-Agent Systems | 協調層 | `24-multi-agent.md` | ✅ |
| 25 | Agent Frameworks | 実装層 | `25-frameworks.md` | ✅ |
| 26 | Agentic UI | 対話層 | `26-agentic-ui.md` | ✅ |
| 12 | LLM Agentic Training (RL) | 上級・任意 | `12-agentic-training.md` | ✅ |
| — | Tier 2 リファレンス | 基礎用語集 | `tier2-reference.md` | ⬜ |

状態: ✅ 完了 / 🚧 作成中 / ⬜ 未着手
