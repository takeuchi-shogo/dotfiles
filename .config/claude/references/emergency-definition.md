---
status: reference
last_reviewed: 2026-05-24
source_url: https://google.github.io/eng-practices/review/emergencies.html
source_repo: https://github.com/google/eng-practices/blob/master/review/emergencies.md
---

# Emergency Definition

Google eng-practices `emergencies.md` ([Web](https://google.github.io/eng-practices/review/emergencies.html) / [Repo](https://github.com/google/eng-practices/blob/master/review/emergencies.md)) 準拠の emergency 定義。
Large CL exception (`references/pr-splitting-patterns.md` §4 + `skills/github-pr/SKILL.md`) の発動条件。

## 1. Emergency 定義

以下のいずれかに該当する場合のみ emergency と認定する:

| 種別 | 例 |
|------|-----|
| **本番障害** | サービス全停止 / 重大なデータ損失 / セキュリティ侵害 / 認証完全停止 |
| **リリースブロッカー** | ロールバック不能なデプロイ直前の致命的バグ / ストア審査タイミング絡みの critical fix |
| **harness 破損** | CI / hooks / shell / build pipeline が完全停止しチームが作業不能 (dotfiles 文脈で valid) |

## 2. NOT Emergency

以下は emergency に**該当しない**。Large CL exception の発動禁止:

- **Friday closeout**: 「終業前に merge したい」「金曜中に終わらせたい」
- **Soft deadline**: 明示的な緊急性のない「早めに」「できれば今週中」
- **個人都合**: 作業効率上の都合 / 待ち時間を減らしたい
- **「全部つながっているから 1 CL でやりたい」**: splitting pattern で分割可能なら emergency ではない
- **レビュワー待ちの解消**: reviewer SLA の問題は別解決 (人を増やす / 並列化)

## 3. Large CL Exception との関係

emergency 認定時のみ Large CL (300 行超) を送ることが許容される。
emergency 後は **必ず follow-up CL で分割・整理する義務** を負う (作成自体は義務、期限は推奨)。

Large CL 送付時に CL description へ記載必須:

```
EMERGENCY: <種別 — 本番障害 / リリースブロッカー / harness 破損>
影響範囲: <ユーザー数 / システム範囲 / データ量>
follow-up: <分割計画 / 後日 cleanup CL の予定>
```

follow-up CL は emergency 解消後 **3 営業日以内** に作成することを推奨 (期限のみ推奨、作成自体は §3 冒頭の義務)。

## 4. AI Review Context での判断基準

300 行超の CL を受け取った AI reviewer (`agents/code-reviewer.md` Section E refactor-mixing-block + `agents/golang-reviewer.md` #16) は本 §4 を rubric として適用する (single source of truth、reviewer 側に同等ロジックを書かず本 §4 を参照する形に統一)。

1. CL description に `EMERGENCY:` 行があるか
2. 種別が §1 のいずれかに該当するか
3. 影響範囲と follow-up 計画が記載されているか

いずれか欠けた場合の reviewer 出力:
- `EMERGENCY:` 行なし → `[MUST]` Large CL の分割または emergency 認定の追記を要求
- 種別が §2 に該当 → `[MUST]` emergency 認定の取り下げ + splitting pattern 適用を要求
- follow-up 記載なし → `[MUST]` follow-up 計画の追記を要求

## 5. 参照

- `references/pr-splitting-patterns.md` — 300 行超の分割パターン (5 種)
- `skills/github-pr/SKILL.md` — Size & Splitting > Large CL Exception
- `agents/code-reviewer.md` — Section E: Refactor-Mixing Block、Section A: Cleanup-Later Boundary
