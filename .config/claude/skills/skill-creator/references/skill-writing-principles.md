# スキル執筆原則

hamelsmu/evals-skills (meta-skill.md) から適応した、スキル品質を高める 7 つの原則。
スキル作成・改善時に SKILL.md を通すチェックリストとして使用する。

## 1. 指示を書け、知恵を書くな (Write directives, not wisdom)

エージェントには「何をするか」を指示する。「なぜ重要か」の説明は最小限に。

**Bad:** "ドメインエキスパートに生の JSON を読ませないことが重要です。これはアノテーションのボトルネックの最大の原因です。ドメインエキスパートはエンジニアではありません。"

**Good:** "すべてのデータをドメインに最も読みやすい表現でフォーマットする。"

**Bad:** "ROUGE スコアを主要な評価指標として使用することは問題があります。なぜなら表面的なテキスト重複を測定するからです..."

**Good:** "特定の失敗モードに基づく binary pass/fail 評価を使用する。ROUGE, BERTScore, cosine similarity を主要指標にしない。"

**例外**: 指示に従わないと重大な結果を招く場合のみ、1文の「なぜ」を添える。

## 2. 一般知識を削れ (Cut general knowledge)

エージェントが既に知っていることは書かない。ドメイン固有の手順・テンプレート・閾値のみ残す。

**削除対象:**
- 定義（「トレースとは完全な記録で...」）
- 重要性の説明（「エラー分析は最もROIの高い活動で...」）
- フレームワーク一覧（「FastHTML, Streamlit, Gradio, ...が使えます」）
- 動機づけ（「スプレッドシートは失敗します、なぜなら...」）
- 学術引用

**残す対象:**
- ドメイン固有の手順（エージェントが知り得ないもの）
- 具体例付きテンプレート
- 数式と閾値
- ドメイン固有のアンチパターン

## 3. ビルドタスクにスコープを絞れ (Scope to the build task)

スキルがアノテーションアプリ構築なら、全文がそのアプリ構築に役立つべき。

**削除対象:**
- プロセス助言（「週次レビューセッションを設定する」）
- 組織ガイダンス（「3-5人のアノテーターチームを編成する」）
- プロジェクト管理（「開発時間の60-80%をエラー分析に充てる」）

**テスト:** 「この文はエージェントの仕事（何かを構築する or ユーザーをプロセスに導く）に役立つか？」 No なら削除。

## 3.5. スキル化の閾値 (When to create a skill)

**5ステップ以上 × 2回以上の再発** をスキル化の閾値とする。

- 5ステップ未満: memory のメモや references/ のチェックリストで十分
- 5ステップ以上でも1回きり: スキル化のコスト（作成・保守）に見合わない
- 閾値を超えたら: `/skill-creator` で形式化し、再利用可能にする

## 4. 良いデフォルトから始めよ (Start with good defaults)

最もシンプルで正しいアプローチを最初に提示する。高度なテクニックは前提条件を明示してから。

**Bad:** ランダムサンプリング、不確実性サンプリング、失敗駆動サンプリングを同等の選択肢として列挙。

**Good:** "ランダムサンプルから始める。自動評価器がある場合は不確実性サンプリングを追加（評価器が一致しないトレース）。本番監視がある場合は失敗駆動サンプリングを追加（ガードレールやユーザー苦情がトリガーされたトレース）。"

## 5. 具体的に書け (Be concrete)

曖昧な指示は無意味。良い例を示す。

**Bad:** "明確な pass/fail 基準を書け。"

**Good:**
```
Pass: メールがクライアントを名前で呼び、保存済み検索から
少なくとも1つの物件を参照している。
Fail: メールが汎用的な挨拶（「お客様各位」）を使用するか、
クライアントの保存済み検索の物件に一切言及していない。
```

## 6. 警告は指示かアンチパターンに変換せよ (Convert warnings)

「やってはいけないこと」セクションの長い説明は、2つのアプローチに変換する:

**アプローチ A — 本文中の指示に統合:**
- "Binary ラベルを使え、Likert スケールではなく"（フィードバック収集セクション内）
- "最終出力だけでなくフルトレースを表示せよ"（データ表示セクション内）

**アプローチ B — 末尾の簡潔なアンチパターンリスト:**
- ROUGE や cosine similarity を主要評価指標として使用する
- トレースで観察していない失敗モードの評価器を構築する
- 1-5 スケールで評価する（binary pass/fail ではなく）

**アンチパターンは1行ずつ。** 段落が必要なら、それは「知恵」—指示に変換して本文に入れる。

## 7. 参照は1階層まで (No nested references)

SKILL.md → reference.md は OK。reference.md → detail.md は禁止。

- SKILL.md は 500 行以下を目標
- 超えたら reference/ に分割（1階層まで）
- 大きな参照ファイル（300行超）には目次を含める
- 参照ファイルからさらに別ファイルへの参照は作らない

## Anti-Patterns セクションの標準化

全スキルの SKILL.md に `## Anti-Patterns` セクションを含めることを推奨する。

**形式（デフォルト: ❌/✅ 対比テーブル）:**

```markdown
## Anti-Patterns

| # | ❌ Don't | ✅ Do Instead |
|---|---------|--------------|
| 1 | エラー分析を完了する前に評価器を構築する | まずトレースを分析し失敗モードを特定する |
| 2 | Likert スケール (1-5) で評価する | binary pass/fail を使用する |
```

**テーブル形式のメリット:**
- Bad → Good の対比で「代わりに何をすべきか」が明確
- 番号付きで参照しやすい
- 箇条書きより情報密度が高い

**適用判断:**
- 繰り返し違反されるルールには Good/Bad 例を併記（feedback_bad_example_pattern.md 参照）
- 1回の観察のみの場合はアンチパターンに追加しない

## Metadata フィールド

frontmatter の `metadata` セクションに以下のフィールドを含めることを推奨する。

**必須フィールド:**
- `pattern`: スキルの設計パターン（pipeline, reviewer, generator 等）

**推奨フィールド:**
- `version`: セマンティックバージョニング（例: `1.0.0`）。破壊的変更時にメジャーを上げる
- `category`: スキルの分類。以下から選択:
  - `workflow` — epd, spike, rpi, autonomous
  - `quality` — review, validate, verification-before-completion
  - `generation` — spec, frontend-design, autocover
  - `research` — research, absorb, debate, gemini
  - `operations` — morning, daily-report, weekly-review, timekeeper
  - `tooling` — codex, codex-review, webapp-testing
  - `architecture` — senior-architect, senior-backend, senior-frontend
  - `knowledge` — obsidian-*, digest, eureka, continuous-learning
  - `security` — careful, freeze, security-review
  - `meta` — skill-creator, skill-audit, ai-workflow-audit, improve

**オプショナルフィールド:**
- `sources`: スキルの知識ソース（例: `"Harrison Chase: Builder or Reviewer"`）

## Decision Table ガイダンス

類似スキルとの使い分けが曖昧な場合、`## Decision: X vs Y vs Z` セクションを追加する。

**形式:**

```markdown
## Decision: spike vs rpi vs epd

| 状況 | 推奨 | 理由 |
|------|------|------|
| 仕様が曖昧、実現可能性が不明 | `/spike` | 最小実装で検証 |
| 仕様は明確、複雑度が中程度 | `/rpi` | Research→Plan→Implement |
```

**配置ルール:**
- Anti-Patterns セクションの直前、または Shortcuts セクションの直前に配置
- テーブルは 3-5 行に収める（多すぎると判断が遅くなる）
- 推奨列はコマンド名を使う（`/spike` 等）

## 8. 出力を自己スコアリングせよ (Self-score your output)

スキルの出力品質を継続的に測定するため、出力末尾に自己評価を付与する。
このスコアは `skill-executions.jsonl` に記録され、AutoEvolve の改善ループで使用される。

**形式:**
```
Score: [1-10]
Reason: [1文 — 何が良かったか、何が不足か、次回改善点]
```

**スコア基準:**
- 9-10: スキルの stated criteria を完全に満たし、追加価値も提供
- 7-8: criteria をほぼ満たす。軽微な改善余地あり
- 5-6: criteria の一部を満たすが、明確な欠落がある
- 3-4: criteria の大半を満たせていない
- 1-2: ほぼ失敗。根本的な問題あり

**適用ルール:**
- 新規作成・改善するスキルに段階的に導入する（既存スキルの一斉変更はしない）
- Pipeline 型スキル（/improve, /epd 等）の最終出力に付与する
- Guard 型スキル（/freeze, /careful 等）は対象外（pass/fail で十分）
- Score は `scoring-config.json` の `outputSignal.thresholds` で信号分類される
