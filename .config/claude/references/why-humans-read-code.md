---
name: why-humans-read-code
description: 人間が全コードを読む工程を harness で置き換えない理由と、その方針を見直す条件
type: reference
last_reviewed: 2026-07-27
---

# なぜ人間がコードを読み続けるのか

dotfiles は "Humans steer, agents execute" を前提に組まれている。この文書はその **why** と、**何が変われば前提を見直すか**を書く。理由が書かれていない方針は教義になり、条件が変わっても更新されない。

> 出典: Dex Horthy (HumanLayer) "Harness Engineering is not Enough: Why Software Factories Fail" (AI Engineer, 2026-07-27 absorb。字幕全文 4,045 語を一次ソースとして使用)

## 理由: 報酬の構造上、モデルは保守性を学習していない

coding model は SWE-bench 系のベンチマークに対して強化学習される。その報酬は概ね次の binary である:

- 対象のテストが通ったか
- 他のテストを壊さなかったか

この構造には**プログラム設計の劣化にペナルティを与える経路がない**。不要な try-catch で握り潰しても、型を無理にキャストしても、テストが通れば報酬が出る。実際 SWE-bench Multilingual のタスクはモデルの変更のうちテストファイルへの変更を巻き戻したうえで golden test patch を当てて判定する設計で、「テストを通す」以外の軸を持たない。

さらに悪いことに、**bad architecture のコスト関数は月〜年の単位で測られる**。ある変更が設計を痛めたと分かるのは数ヶ月後で、その信号を学習時の報酬として遡って伝播させることが極めて難しい。

> (verbatim) "if you can't verify the maintainability of the code, it gets way harder to train on this stuff" / "the cost function of bad architecture is measured in months and years"

したがってこれは **scale の問題ではなく model training の問題**であり、harness の loop を増やしても、reviewer bot に adversarial review と書き足しても解けない。「もっとトークンを使え」「使い方が悪い」で片付く話ではない。

## 帰結: harness を品質保証の代替物にしない

講演は harness 投資そのものを否定していない。否定しているのは **harness を人間のレビューの代替とみなす前提**である。dotfiles における具体的な線引き:

| やってはいけない | 理由 |
|---|---|
| `ralph-loop` / max-loop の完走を「レビュー不要」の根拠にする | ループの完走はテストが通ったことしか意味しない |
| completion-gate の binary PASS を「読まなくてよい」の根拠に昇格させる | gate は形式条件であって設計品質の判定ではない |
| reviewer agent の `ok=true` / PASS verdict を人間レビューの代わりにする | reviewer もモデルであり、同じ報酬構造の制約を受ける |
| 成功率・テスト通過率だけを見て harness を改善する | 測っていない軸 (保守性) が劣化しても指標は上がる |

逆に、**探索・計画・検証証跡・レビューを読みやすくする harness は講演と整合する**。それは全行レビューを可能にするための投資だからである。dotfiles の Plan / Codex Gate / review synthesis / scope-governor はこちら側に属する。

## 対処: 事前設計でレビューを軽くする

読む工程を残したまま速く動くには、レビューに入る前の手戻り確率を下げる。講演の順序:

1. **product review** — 何の問題を解くか、望ましい挙動、モックアップ
2. **system architecture** — component contract、データモデル、制約
3. **program design** — 型、メソッドシグネチャ、プログラムレイアウト、call graph
4. **vertical slices** — 実装順序と、各単位で何を検証するか

3 が最も過小評価されていると講演は言う。「アーキテクチャさえ決まればモデルが実装できる」は成り立たない。dotfiles では `PLANS.md` の `## Program Design（該当時のみ）` がこれに当たる。

小さい変更にこの層は要らない。講演も "small stuff still just goes straight to the agent" と明言している。

## 見直し条件

この方針は**モデルの訓練構造に依存しており、恒久的な原則ではない**。次が満たされたら見直す:

> **代表的な変更に対して、設計の劣化を高い再現率で検出できる verifier が実証されたとき。**

ベンチマーク名そのものは撤退条件ではなく**観測対象**として扱う。講演が挙げていた進行中の取り組み:

- SWE Marathon (Abundant AI) — 400 時間規模のタスク
- DeepSuite (Data Curve) — 訓練セットに含まれない大規模 OSS タスク
- Frontier Code (Cognition) — multi-PR タスク。pre-patch コードで落ちないテストを書くとペナルティ、judge model が code quality rule 準拠を判定

ただし講演自身が留保を付けている: **モデルが品質を judge できる範囲には限界がある**。モデルが良いコードを分かっているなら最初からそう書くはずだからである。judge 型 verifier の登場だけでは見直し条件を満たさない。

## Gotchas

- **これは vibe coding の話ではない**: 講演は「個人プロジェクトなら AI 任せで問題ない」と明示している。対象は複雑で長期運用されるコードベース。ただし境界は 10 年物のレガシーではなく、**3〜6 ヶ月**で現れると講演は言っている
- **「読む」を精神論にしない**: 全行読むことを可能にするのは事前設計であって根性ではない。読めない量の PR が出ているなら、PR が多すぎるのではなく手戻りの多い PR が多すぎる
- **この文書の主張は 2026-07 時点のモデル訓練構造に基づく**。`last_reviewed` から時間が経っていたら見直し条件を再評価する
