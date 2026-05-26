# Google eng-practices 深部調査レポート

**調査日**: 2026-05-26
**対象**: https://github.com/google/eng-practices
**前回 absorb**: 2026-05-24 (13件実装済)
**目的**: 前回見落とし・未実装の細部を徹底的に発掘し、dotfiles 改善案を提示

---

## Executive Summary

Google eng-practices は「完璧なコードではなく、継続的に改善するコードベース」という哲学に基づいて設計されたコードレビュー制度設計ドキュメントである。前回 absorb（2026-05-24）で実装した 13 件はすべて確認・整合済みだったが、**developer（PR 作者）視点の指針が全般的に欠落**していることが判明した。

最大の発見：
1. **G-9 (High)**: `handling-comments.md` の developer 側コミュニケーション指針（"Don't Take it Personally" / "Fix the Code" / "Think Collaboratively"）が dotfiles に一切存在しない
2. **G-1 (High)**: PR description の first line に Imperative sentence 原則を適用するチェックが `github-pr` 系ファイルに未実装
3. **G-5 (High)**: "Fix the Code before Explaining" 原則が未実装
4. **AI時代の新知見**: Google の 75% のコードが AI 生成に。コードレビュー expertise の価値は下がらず、むしろ上昇している

---

## 1. Reviewer Guide 完全分析

### 1.1 standard.md — コードレビューの最上位原則

**核心テーゼ**:

> **reviewers should favor approving a CL once it is in a state where it definitely improves the overall code health of the system being worked on, even if the CL isn't perfect.**

「完璧でなくても、コード健全性を確実に改善するなら承認せよ」が最上位原則。"perfect" ではなく "continuous improvement" を目指す。

**3つの反直感的ポイント**:

1. **"Nit:" は「無視してよい許可証」**: 「小さな指摘」ではなく、著者が明示的に無視できるものとして定義されている
   > "they could choose to ignore"
   
2. **教育的コメントも "Nit:" 扱いにする**: purely educational なコメントは critical でない限り "Nit:" または "not mandatory" を付ける

3. **設計選択を「好み」として処理してはならない**:
   > **Aspects of software design are almost never a pure style issue or just a personal preference.**

**エスカレーションパスの順序** (膠着時):
1. より広いチームディスカッション
2. Technical Lead
3. コードのメンテナー
4. Eng Manager

> **Don't let a CL sit around because the author and the reviewer can't come to an agreement.**

---

### 1.2 looking-for.md — レビューで何を見るか

**9つのカテゴリ**: Design → Functionality → Complexity → Tests → Naming → Comments → Style → Consistency → Documentation

**重要な細部**:

#### UI変更・並行処理は「実際に動かして確認」を推奨
> You *can* validate the CL if you want—the time when it's most important for a reviewer to check a CL's behavior is when it has a **UI change**.

#### コメントの "why vs what" の区別が非常に厳格
> usually comments are useful when they **explain why** some code exists, and should not be explaining *what* some code is doing. If the code isn't clear enough to explain itself, then **the code should be made simpler**.

"what" を説明するコメントは「コードを直せ」のサインとして扱う。例外は正規表現と複雑なアルゴリズムのみ。

#### Every Line の例外条件（完全定義）
スキャン許容対象: データファイル・生成コード・大きなデータ構造のみ
「人間が書いた」コードは必ず全て読む。

**複数レビュアー時の例外**（2条件）:
1. 特定のファイルのみレビューを担当
2. 特定の観点（設計、privacy、security 等）のみ

この場合は「どの部分をレビューしたか」をコメントに明記し、"LGTM with comments" を使う。

#### 専門性委譲の義務
> make sure there is a reviewer on the CL who is qualified, particularly for complex issues such as **privacy, security, concurrency, accessibility, internationalization**, etc.

#### 既存不一致への対処（標準手順）
> encourage the author to file a bug and add a TODO for cleaning up existing code.

承認しつつバグ登録 + TODO コメントが標準手順。

#### Good Things セクション（ネガティブ偏重への対抗）
> It's sometimes even more valuable, in terms of mentoring, to tell a developer what they did right than to tell them what they did wrong.

---

### 1.3 navigate.md — CLのナビゲーション方法

**3ステップ手順**:
1. CL description を読む → 方向性確認
2. 主要ファイルを先に見る → 設計問題の早期発見
3. 残りを順に見る

**最重要な反直感的ルール**:
> If you see some major design problems with this part of the CL, you should send those comments immediately, **even if you don't have time to review the rest of the CL right now.**

設計問題発見時は残りのレビューを中断して即座に送信。

**拒否時の礼儀**:
> "Looks like you put some good work into this, thanks! However, we're actually going in the direction of removing the FooWidget system... How about instead you refactor our new BarWidget class?"

代替案なしの拒否は不完全として扱われている。

**テストを先に読む推奨**:
> Sometimes it's also helpful to read the tests first before you read the main code

---

### 1.4 speed.md — レビューのスピード

**核心テーゼ**:
> **At Google, we optimize for the speed at which a team of developers can produce a product together**, as opposed to optimizing for the speed at which an individual developer can write code.

**定量閾値**:
- **最大応答時間: 1 business day**
- タイムゾーン差: 相手の就業時間が終わる前に返す、または翌日の始業前に完了

**スピードの測定単位の定義**（重要）:
> it's even more important for the *individual responses* to come quickly than it is for the whole process to happen rapidly.

全体の完了時間ではなく、**各ラウンドの応答速度**が品質を決定する。

**コーディング中は中断禁止**:
> **If you are in the middle of a focused task, such as writing code, don't interrupt yourself to do a code review.**

**最大の発見: LGTM with Comments の3条件**（既実装だが詳細が欠落）

> This should be done when **at least one of the following** applies:
> 1. The reviewer is confident that the developer will appropriately address all the reviewer's remaining comments.
> 2. The comments don't *have* to be addressed by the developer.
> 3. The suggestions are minor, e.g. sort imports, fix a nearby typo, apply a suggested fix, remove an unused dep, etc.

レビュアーは「どの条件に基づいてLGTM with Commentsにしたか」を明示することが推奨される。

**苦情への対処**:
> **Most complaints about the code review process are actually resolved by making the process faster.**

「厳しすぎる」という苦情は基準を下げるのではなく**応答を速くする**ことで解消される。

---

### 1.5 comments.md — コードレビューコメントの書き方

**コメント重大度ラベルの正確な定義**（4種類）:

| ラベル | 原文定義 | 強制力 | スコープ |
|--------|---------|--------|---------|
| `Nit:` | "minor thing. Technically you should do it, but it won't hugely impact things." | 技術的に正しいが無視可能 | 現在のCL |
| `Optional:` / `Consider:` | "I think this may be a good idea, but it's not strictly required." | 必須ではない | 現在のCL |
| `FYI:` | "I don't expect you to do this in this CL, but you may find this interesting to think about for the future." | 対応を期待しない | 将来の参考 |

**ラベルなしの危険性**:
> without comment labels, authors may interpret all comments as mandatory, even if some comments are merely intended to be informational or optional.

**「コードを直させる」の優先**:
> If you ask a developer to explain a piece of code that you don't understand, that should usually result in them **rewriting the code more clearly**.

**コードレビューツール内の説明は「ほぼ役に立たない」**:
> **Explanations written only in the code review tool are not helpful to future code readers.**

例外: レビュアーが不慣れな領域で、通常の読者は既知の内容を説明する場合のみ。

---

### 1.6 pushback.md — プッシュバックへの対処

**「後でやる」は認めない原則**:
> usually unless the developer does the clean up *immediately* after the present CL, **it never happens.**

**許容できる唯一の条件**:
- 新たな複雑性: 緊急時以外は提出前にクリーンアップ必須
- 既存問題の露出: バグ登録（自分にアサイン）+ 任意でTODOコメント（バグ参照付き）

**厳格さへの苦情が収まるまで**: sometimes months

**コード健全性改善は「小さなステップで起きる」**:
> **Improving code health tends to happen in small steps.**

---

## 2. Developer (CL Author) Guide 完全分析

### 2.1 cl-descriptions.md — CL Description の科学

**First Line の3要件**:
1. 命令文（Imperative sentence）として書く
2. Stand-alone（それだけで意味が完結）
3. 空行で本文と区切る

> "Delete the FizzBuzz RPC and replace it with the new system." ✅
> "Deleting the FizzBuzz RPC..." ❌（-ing 形は NG）

**Body に含めるべき情報の完全リスト**:
1. 解決している問題の概要
2. なぜこのアプローチが最善か
3. アプローチの欠点や限界
4. バグ番号
5. ベンチマーク結果
6. 設計ドキュメントへのリンク
7. コードには現れない意思決定の背景
8. 著者が持っていたコンテキスト

**Chesterton's Fence**（重要概念）:
> "Reading source code may reveal what the software is doing but it may not reveal why it exists, which can make it harder for future developers to know whether they can move Chesterton's fence."

「柵を撤去したいなら、なぜ建てられたかを理解してから」。CL Description に "Why" を書く核心的論拠。

**Bad CL Descriptions（全列挙）**:
- "Fix bug"、"Fix build."、"Add patch."
- "Moving code from A to B."（現在進行形 NG）
- "Phase 1."、"Add convenience functions."、"kill weird URLs."

**Tags のルール**:
- 使用は任意
- First line での長いタグは避ける（内容を埋没させる）
- 複数タグは短ければ可: `#banana #apple: Assemble a fruit basket.`

**提出前の description 再確認義務**:
> It can be worthwhile to review a CL description before submitting the CL, to ensure that the description still reflects what the CL does.

---

### 2.2 small-cls.md — Small CL の分割戦略

**定量閾値**:
- **100 lines = 通常適正**
- **1000 lines = 通常大きすぎる**
- ファイル数も重要: 200 行 in 1 file は OK だが、50 ファイルに分散すると大きすぎる

**7つの分割戦略（詳細）**:

#### 1. Stacking（積み重ね）
最初の CL をレビューに送った直後に、それをベースとした次の CL を書き始める。レビュー待ち中もブロックされない。

#### 2. Splitting by Files
異なるレビュアーが必要なファイルを別 CL に分ける。
例: proto CL + それを使うコードの CL（並行レビュー可能）

#### 3. Splitting Horizontally（水平分割）
技術スタックの**レイヤー**単位で分割。
例: Client / API / Service / Model 層を分ける

#### 4. Splitting Vertically（垂直分割）
**機能（feature）** 単位でフルスタックの縦切り。
例: 乗算 CL + 除算 CL として独立した parallel tracks

#### 5. Splitting Horizontally & Vertically（グリッド）
Layer × Feature のグリッドで各セルを独立した CL にする。

| Layer | Feature: Mult | Feature: Div |
|-------|--------------|-------------|
| Client | Add button | Add button |
| API | Add endpoint | Add endpoint |
| Service | Implement | Share logic |
| Model | Add proto | Add proto |

#### 6. Separate Refactorings
リファクタリングと機能変更を必ず別 CL にする。
例外: ローカル変数名の修正のような小さなクリーンアップは含めてよい。

#### 7. Independent Test Modifications
独立したテスト変更を先行 CL として分離できるケース:
- 既存コードに対して新しいテストを追加（後続リファクタリングの信頼性向上）
- テストコードのリファクタリング（ヘルパー関数の導入等）
- 大きなテストフレームワークの導入

**「大きな CL」が許容される例外**:
- ファイル削除全体（実質1行の変更）
- 信頼できる自動リファクタリングツールによる生成コード

---

### 2.3 handling-comments.md — レビューコメントへの対応（★ dotfiles 最大ギャップ）

**"Don't Take it Personally"**:
> "Ask yourself, 'What is the constructive thing that the reviewer is trying to communicate to me?' and then operate as though that's what they actually said."

**怒りへの対処**:
> "**Never respond in anger to code review comments.** walk away from your computer for a while, or work on something else until you feel calm enough to reply politely."

エスカレーション: 本人 → 対面/ビデオ → プライベートメール → マネージャー

**"Fix the Code before Explaining"（★ 未実装）**:

判断フロー（優先順位付き）:
1. **コード自体を明確にする**（リファクタリング）→ 最優先
2. **コードコメントを追加する** → コードを変えられない場合
3. **レビューツール内で説明する** → 「コメントが無意味に見える場合」のみ（最後の手段）

> "Writing a response in the code review tool doesn't help future code readers, but clarifying your code or adding code comments does help them."

**"Think Collaboratively" の応答テンプレート（★ 未実装）**:

```
Bad:  "No, I'm not going to do that."

Good: "I went with X because of [these pros/cons] with [these tradeoffs].
      My understanding is that using Y would be worse because of [these reasons].
      Are you suggesting that Y better serves the original tradeoffs, that we
      should weigh the tradeoffs differently, or something else?"
```

このテンプレートの3要素:
1. 自分のアプローチの根拠を pros/cons と tradeoffs で説明
2. 相手のアプローチへの懸念を技術的根拠で示す
3. 相手の意図を複数の可能性で問い返す（防御的にならず意図を引き出す）

---

### 2.4 emergencies.md — 緊急時の精密定義

**Emergency の条件**: **small** な変更で以下のいずれか:
- メジャーローンチのロールバック回避
- プロダクション上でユーザーに重大影響を与えているバグの修正
- 緊急の法的問題への対処
- 重大なセキュリティホールの閉塞

**NOT Emergency の全列挙**（重要）:
1. 来週ではなく今週ローンチしたい
2. 開発者が長期間フィーチャーに取り組んでいて「とにかく入れたい」
3. レビュアーが全員別タイムゾーンで夜間または off-site 中
4. 金曜の終業間際で週末前に入れたい
5. マネージャーがソフトデッドラインを理由に今日中にと言っている
6. **テスト失敗やビルドブレークを引き起こしている CL のロールバック**（これが emergency でない点が重要）

**Hard vs Soft Deadline**:
- Hard: "something disastrous would happen" が基準（契約義務、市場完全失敗、年1回のハードウェア出荷締め切り）
- Soft: ほとんどのデッドラインがこれ。重要だがコード健全性を犠牲にする理由にならない

**事後処理義務**（★ 既実装だが詳細不足）:
> "after the emergency is resolved you should look over the emergency CLs again and give them a more thorough review."

緊急時の superficial review は技術的負債として明示的に認識し、解決後の返済が義務付けられている。

---

## 3. 哲学・設計原則の深堀り

### 3.1 対立する価値観のバランス

Google eng-practices は以下の対立を巧みに解決している:

#### 開発速度 vs コード品質
承認基準を「完璧さ」から「正の寄与」へ引き下げることで両立。ただし下限（「healthy を悪化させない」）は絶対禁止。

逆説的発見: 短期的な完璧さを求めることが長期的なcode healthを下げる → 継続的改善の基準採用。

#### 厳格さ vs 開発者モラール
> **Most complaints about the code review process are actually resolved by making the process faster.**

厳格さへの苦情は基準の緩和ではなく応答速度で解消。厳格さ + 速度 = 長期的に品質と速度の両方が上がる。

#### 個人の好み vs 技術的根拠
権威の階層: Technical facts > Style guide（絶対権威）> Design principles > Author preference（等価な場合のみ）> Consistency

「これはスタイルの問題だ」という逃げ道を設計原則の議論から排除。

### 3.2 コード健全性の意図的な「未定義」

注目すべきは Googleが code health を **直接定義していない** ことだ。代わりに多数の属性で輪郭を描く。「定義」すると、それに適合するが本質を外れたコードが生まれるため意図的に属性の集合として提示。

### 3.3 劣化のメカニズムと防衛設計

> codebases degrade through **small decreases** in code health over time, especially when a team is under significant time constraints

時間的プレッシャーによる微小な妥協の累積が劣化を生む。「現在の CL で now に直す」「later は認めない」「バグ登録で借金を明示化」の三層防衛。

### 3.4 教育システムとしてのコードレビュー

4つの教育メカニズム:
1. **ラベリング**: Nit/FYI で「学びの機会」と「ブロッカー」を区別
2. **問題の指摘と解決の委譲**: 解答を与えすぎず、問題提起して開発者が学ぶ
3. **コードの明確化への誘導**: ツール内説明 → コード/コメントの改善に変換
4. **良い点の言語化**: 良い実践の意識化と繰り返し促進

### 3.5 スケーラビリティのための原則ベース設計

原則ベース（vs ルールベース）を選んだ理由: Google規模では新しい言語・ツール・アーキテクチャが常に登場する。ルールは網羅性が必要で例外が複雑になる。「code health を改善するか否か」という単一の問いに帰着できる原則体系であれば、未定義の状況にも適用できる。

---

## 4. dotfiles 実装ギャップ分析

### 4.1 実装済み 13 件の確認結果

**全 13 件確認済み・整合性高**。追加として `agents/code-reviewer.md` に Section G (Mentoring Tone) と `[NITS_REMAIN]` 補助タグが計画外実装されていた。

### 4.2 未実装ギャップ一覧

| ID | トピック | 重大度 | 実装先 |
|----|---------|--------|--------|
| G-1 | PR description の Imperative sentence 原則（First line） | **High** | `skills/github-pr/SKILL.md`, `references/self-review.md` |
| G-5 | "Fix the Code before Explaining" 原則 | **High** | `skills/github-pr/review-response.md`（新規） |
| G-9 | developer 側コミュニケーション指針全般 | **High** | `skills/github-pr/review-response.md`（新規） |
| G-2 | LGTM with Comments の3条件の発動基準 | Medium | `agents/code-reviewer.md` §Verdict |
| G-4 | "Optional:" ラベルと dotfiles `CONSIDER`/`ASK` のマッピング明示 | Medium | `references/review-courtesy-examples.md` |
| G-6 | developer の応答テンプレート "I went with X..." | Medium | `skills/github-pr/review-response.md`（新規） |
| G-7 | Emergency CL のレビュー基準緩和範囲（何が許容されるか） | Medium | `references/emergency-definition.md` |
| G-8 | 分割戦略の適用基準詳細（Horizontal vs Vertical の選択基準） | Low | `references/pr-splitting-patterns.md` |
| G-3 | Cross-timezone SLA | Low | 個人開発のため実用性低 |

### 4.3 最優先実装 2 件

#### G-9: developer コミュニケーション指針（新規ファイル）
`skills/github-pr/review-response.md` に以下を実装:
- Don't Take it Personally（認知的再フレーミング）
- Fix the Code > Add Comment > Explain in tool（優先順序）
- Think Collaboratively テンプレート verbatim
- 怒りへの対処フロー（離席 → 別作業 → 対面/ビデオ → プライベートメール → Manager）

#### G-1: PR description first line チェック
`skills/github-pr/SKILL.md` および `references/self-review.md` の確認チェックリストに:
- First line が命令形（Imperative）か
- Stand-alone（本文なしで意味が通じるか）
- 空行で本文と区切られているか
- タグで内容が埋没していないか

---

## 5. 外部研究 — 業界採用・批判・AI時代の変化

### 5.1 業界採用状況

GitLab、Netlify、Auth0、PayPal、Bitcoin Core が Google eng-practices を参照・採用しているとされる（MEMORY.md 前回absorb記録より）。

[要追加調査] 採用企業の定量データなし。

### 5.2 AI コード生成時代の変化（★ 新発見）

**Google の状況**（WebSearch調査結果）:
- **75% の新規コードが AI 生成**（Sundar Pichai 2025年末発表）
- 18ヶ月前の 2024年初頭は 25%、2025年末に 50% → 2025年末に 75%

**AutoCommenter システム**:
Google は LLM を使って C++/Java/Python/Go のベストプラクティスを自動的に学習・適用するシステムを開発済み。Nit レベルのコメントの自動化が実用段階に。

**DORA 研究の定量データ**:
- コードレビュー時間が短いチームは **50% 良好なソフトウェアデリバリーパフォーマンス**
- AI 採用率が 25% 増加するごとにコードレビュー速度 **+3.1%**、コード品質 **+3.4%** 向上
- 未検証 AI 生成コードを過剰提出した場合: **コードレビュー時間 +12%、バグ密度 +23%**

**eng-practices への示唆**:
- "Nit:" コメントは AI に委譲する方向が加速（AutoCommenter が先行実例）
- **コードレビュー expertise の価値は下がらない**。AI コードの量が増えるほど human oversight の重要性が上昇
- "Fix the Code" 原則は AI 生成コードに対しても同様に適用される。AI への説明ではなく AI プロンプトを修正する、という対応が必要に

### 5.3 批判・反論

[要追加調査] 詳細な批判的文献は今回収集できていない。既知の一般的批判:
- Googleの単一リポジトリ（Monorepo）前提の部分が他組織に適用しにくい
- "1 business day" SLA は規模の小さいチームでは over-prescribed に見える場合がある
- Piper/OWNERS/Critique といった内部ツール前提の暗黙的制約

---

## 6. クロスモデル分析・総合発見

### 6.1 モデル間の合意事項
- Reviewer Guide / Developer Guide の分析: 4サブタスク全て同一の核心原則を発見
- ギャップ分析: developer 視点の欠落を独立して検出（G-9 が最優先）

### 6.2 前回 absorb からの delta

| 項目 | 前回 absorb | 今回新発見 |
|------|-----------|----------|
| CL Description | 参照のみ | Imperative sentence 原則・Chesterton's fence を精密定義（G-1） |
| LGTM with Comments | タグ実装 | 3条件の発動基準が未実装（G-2） |
| Developer 視点 | 未対応 | handling-comments.md 全体が未実装（G-5, G-6, G-9） |
| Emergency | ファイル作成 | 緩和範囲の operationalize が不十分（G-7） |
| AI 時代 | 記録なし | 75% AI 生成・AutoCommenter・+12% review tax のリスク |

### 6.3 哲学的まとめ

Google eng-practices の本質は **コードレビューを人間同士のゲートではなく、コードベースの自己修復システムの一部として設計**したことにある。

- Reviewer は個人として判断するが、判断基準は "code health" という組織的目標に接地される
- Developer は著者としての権限を持つが、技術的根拠を通じてのみ行使できる
- 速度と品質は対立しない——どちらも「長期的なcode health」に奉仕する
- 完璧さは追求しない——継続的改善を追求する

最も深い洞察: **人間の行動を直接制御しようとするのではなく、人間が自然に良い判断を下せる環境を設計する**。ルールを与えるのではなく「このコードはcode healthを改善するか？」という問いを与えることで、無数の個別状況に対して適切な判断が自動的に生まれる。

---

## 7. 推奨アクション（優先順位付き）

### 即実装（High ギャップ）

**A. `skills/github-pr/review-response.md` 新規作成**
- "Don't Take it Personally" 原則
- "Fix the Code > Add Comment > Explain in tool" 優先フロー
- "Think Collaboratively" テンプレート verbatim
- 怒りへの対処手順

**B. `skills/github-pr/SKILL.md` と `references/self-review.md` に PR description チェック追加**
- First line が命令形 (Imperative) か
- Stand-alone 要件
- Chesterton's fence: "Why" を含むか

### 中優先（Medium ギャップ）

**C. `agents/code-reviewer.md` §Verdict に LGTM with Comments 3条件追加**

**D. `references/review-courtesy-examples.md` §Severity マッピング表に "Optional → CONSIDER" 明示**

**E. `references/emergency-definition.md` に緩和範囲の詳細追加**（何が許容されるか具体的に）

### 低優先（Low ギャップ）

**F. `references/pr-splitting-patterns.md` に Horizontal vs Vertical の選択基準詳細追加**

---

## 参照リンク

- [google/eng-practices リポジトリ](https://github.com/google/eng-practices)
- [AI-assisted Assessment of Coding Practices at Google](https://research.google/pubs/ai-assisted-assessment-of-coding-practices-in-industrial-code-review/)
- [AI in software engineering at Google: Progress and the path ahead](https://research.google/blog/ai-in-software-engineering-at-google-progress-and-the-path-ahead/)
- [Gemini Code Assist and GitHub AI code reviews](https://cloud.google.com/blog/products/ai-machine-learning/gemini-code-assist-and-github-ai-code-reviews)
- 前回 absorb: `docs/research/2026-05-24-google-eng-practices-absorb-analysis.md`

---

*分析モデル: Subtask 1-4 = claude-sonnet-4-6 (4サブエージェント並列), Subtask 5 = WebSearch (Gemini quota exhausted)*
*タスクID: tr-2026-05-26-e3cb0d*
