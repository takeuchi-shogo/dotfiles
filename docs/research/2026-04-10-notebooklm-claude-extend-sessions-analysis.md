---
title: "I want to extend my Claude sessions (full guide)"
source: "(URL 未記録、個人ブログ)"
authors: 不明（参考元: Jack Roberts, Chase, Universe of AI, Teng Ling）
date_analyzed: 2026-04-10
type: article
tags: [notebooklm, session-extension, memory, workflow, dbs, skill-writing, harness]
status: integrated
---

# NotebookLM × Claude セッション拡張ガイド — 分析レポート

## Source Summary

### 記事の核心主張

Claude Pro plan ($20/month) のユーザーがトークン枯渇（30-45分/日しか生産的に使えない）という痛みを抱えている前提で、開発者 Teng Ling が作成した非公式 CLI ツール `notebooklm-py`（GitHub: teng-lin/notebooklm-py）を Claude Code と統合することで、トークン制限の回避と永続メモリを実現する 4 つのワークフローを提案している。

### 4 ワークフロー

| Workflow | 名称 | 概要 |
|----------|------|------|
| A | Zero-Token Research | 30+ 資料解析を NotebookLM にオフロード。Claude はサマリのみ受け取る |
| B | Deep Research → DBS → skill-creator | Web 調査 → Direction/Blueprints/Solutions 3分類 → スキル自動生成 |
| C | Master Brain 永続メモリ | `/wrap-up` ritual で session summary を NotebookLM に upload。CLAUDE.md に「回答前照会せよ」と記載 |
| D | Obsidian Vault 統合 | Vault ルートで Claude 起動、CLAUDE.md で folder/metadata/linking ルール定義 |

### DBS 分類原則（Workflow B の核心）

- **Direction**: 戦略・判断・優先度の定義（CLAUDE.md / references/）
- **Blueprints**: 設計・構造・フロー（skills/SKILL.md、plan ファイル）
- **Solutions**: 具体的な実装・コード・スクリプト（scripts/、実装ファイル）

### 前提条件と限界

- 記事の痛みの対象: Claude Pro plan ($20/month) のトークン枯渇
- `notebooklm-py` は Google の内部プロトコルを reverse-engineering した非公式ツール
- UK/EU GDPR データ越境リスクに言及あり
- Cookie 保護・非公式 API 破壊リスクに言及あり

---

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | notebooklm-py CLI 導入 | Optional Experiment | /research + /digest でカバー範囲が重複。非公式 API を production harness に入れるリスクが価値を上回る |
| 2 | DBS rubric 明文化 | Partial | skill-writing-guide に記載なし。Directory/Script/Markdown の分類はあるが DBS として体系化されていない |
| 3 | /wrap-up 独立スキル | N/A | /checkpoint + continuous-learning で目的は達成済み。重複スキルは避ける |
| 4 | Master Brain 専用ノートブック方式 | N/A (defer) | canonical は Obsidian + MEMORY.md。将来 read-only 補助索引として再検討余地はあるが即採用不可 |
| 5 | Workflow A: 30+ ソース集約能力 | Partial | /research は並列マルチモデルで部分対応。audio/slide/mindmap 生成は代替不能。ただし非公式 API 依存 |
| 6 | Vault ルートで Claude 起動 playbook | Partial | docs/playbooks/ に未記載。process 改善として有効だが低優先度 |
| 7 | 【新規発見】データ分類ゲート | Gap | 外部サービスに何を送ってよいかの classification rubric が未整備 |

---

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|-------------|---------------|--------|------|
| S1 | /digest に NotebookLM 出力の手動統合フロー | NotebookLM API の直接呼び出し統合 | 非公式 API 依存 → **却下** | 却下 |
| S2 | /research にマルチモデル並列リサーチ | NotebookLM バックエンドを追加 | 非公式 API 依存 → **却下** | 却下 |
| S3 | CLAUDE.md に指示コスト評価済み | 「記憶の照合前参照」ルール追加 | Context Constitution P3 で既存。重複 → **保留** | 保留 |
| S4 | skill-writing-guide の構造ガイド | DBS 原則が未明文化 | DBS rubric セクション追加 → **採用** | 採用 |
| S5 | docs/playbooks/ に各種 playbook | Vault ルート起動の手順なし | claude-in-vault.md 追加 → 低優先度 | 低優先度 |
| S6 | references/credential-hygiene.md | 外部サービスへのデータ送信基準なし | データ分類ゲートと統合 → Gap #7 と同一課題 | Gap #7 へ統合 |

---

## Refine (Phase 2.5)

### Codex 批評の主要指摘

- **痛みの再定義**: 記事は Pro plan ($20/month) 前提だが、Max plan ユーザーは token 節約ではなく synthesis capability（audio/slide/mindmap 自動生成）で評価すべき。評価軸が変わる
- **非公式 API リスクは blocker 級**: reverse-engineering ツールは Google 側変更で無予告破壊される。Production harness への組み込みは不可
- **DBS は「新機能」ではなく「rubric 明文化」**: 実体はドキュメント配置ポリシーの体系化。低コストで高効果
- **データ分類ゲートの漏れ**: 外部サービス（NotebookLM, Gemini API等）に何を送ってよいかの classification rubric が分析から脱落していた。独立した未解決課題として記録すべき
- **Verdict（Codex）**: 採用は 1 つのみ — skill-writing-guide への DBS チェックリスト追加

### Gemini 補足（予測ベース、要検証）

- `notebooklm-py` は非公式 API ラッパー。Google 側の API 変更で無予告破壊リスクが高い
- NotebookLM 利用規約は reverse-engineering を通常禁止領域に含む
- GDPR データ越境は blocker 候補（EU/UK ユーザーは特に注意）
- 記事の「Pro plan で 30-45分/日」という主張は誇張の可能性あり（実際の制限はより柔軟）

---

## Integration Decisions (Phase 3 Triage)

ユーザー選択: **DBS rubric のみ採用**（Codex 推奨に従う）

### 採用

| # | 項目 | 対象ファイル | 理由 |
|---|------|------------|------|
| S4 | DBS rubric 明文化 | `skill-creator/instructions/skill-writing-guide.md` | 低コスト・高効果。スキル設計の判断軸が明確になる |

### 却下

| # | 項目 | 却下理由 |
|---|------|---------|
| 1 | notebooklm-py CLI 導入 | 非公式 API 依存。Production harness への組み込みは blocker 級リスク |
| 3 | /wrap-up 独立スキル | /checkpoint + continuous-learning で十分。重複スキルを避ける |
| 4 | Master Brain 専用ノートブック | canonical は Obsidian + MEMORY.md。将来の read-only 補助索引として再検討 |
| S1, S2 | /digest, /research への NotebookLM 統合 | 非公式 API 依存 |

### 保留（将来課題として記録）

| # | 項目 | 将来の再評価条件 |
|---|------|--------------|
| 5 | 30+ ソース集約・audio 生成 | Google が公式 NotebookLM API を公開した場合 |
| 6 | Vault ルート起動 playbook | docs/playbooks/ 整理のタイミングで追加 |
| 7 | データ分類ゲート | /research や /digest 拡張時に再浮上。`references/credential-hygiene.md` と統合 |

---

## Plan

### Task 1: DBS Rubric を skill-writing-guide に追加（採用済み）

- **Files**: `.config/claude/skills/skill-creator/instructions/skill-writing-guide.md`
- **Changes**: Anatomy of a Skill の直後、Progressive Disclosure の直前に「DBS Rubric — どこに書くかの分類原則」セクションを追加
- **内容**:
  - Direction/Blueprints/Solutions の 3 分類表
  - アンチパターン（判断を scripts に埋める、決定論的処理を SKILL.md に書く、静的参照を本文に混ぜる）
  - Atomic Skill Design Principles の Self-containment との関連明記
- **Size**: S

---

## 学んだこと / 残された課題

### 今回の分析から

1. **非公式 API の誘惑パターン**: 記事の主張を無批判に採用すると、非公式 API を production harness に組み込む誘惑が生まれる。Codex 批評が blocker として機能した。マルチモデル批評（Codex + Gemini）は採用判断の安全装置として有効
2. **DBS は新機能ではなく rubric 明文化**: 新しい仕組みを入れるより、既存の設計判断を体系化する方がコスト対効果が高いケースがある。「機能追加」と「文書化・体系化」を区別して評価すべき
3. **評価軸の前提確認**: 記事は Pro plan ユーザーを対象としており、Max plan ユーザーには評価軸が変わる。前提条件の確認は分析の最初に行う

### 未解決課題

- **データ分類ゲート**: 外部サービス（NotebookLM, Gemini API, Brave Search 等）への送信可否を判定する classification rubric が未整備。`/research` や `/digest` の拡張時に再浮上する。`references/credential-hygiene.md` との統合が望ましい
- **NotebookLM synthesis capability の将来性**: audio/slide/mindmap 自動生成は /research では代替不能な機能。Google が公式 API を提供した場合は即座に再評価する価値がある

---

## 関連ドキュメント

- `.config/claude/skills/skill-creator/instructions/skill-writing-guide.md` — DBS rubric 追加先
- `.config/claude/references/context-constitution.md` — P3: Proactive > Reactive（Master Brain 相当機能の既存実装）
- `docs/research/2026-04-04-letta-memory-as-harness-analysis.md` — Memory-as-harness の文脈
- `docs/research/2026-03-16-notebooklm-obsidian-claude-integration.md` — 先行する NotebookLM 統合分析
- `.config/claude/skills/digest/SKILL.md` — NotebookLM 出力の手動統合フロー
- `.config/claude/skills/research/SKILL.md` — マルチモデル並列リサーチ
- `references/credential-hygiene.md` — データ分類ゲート統合候補
