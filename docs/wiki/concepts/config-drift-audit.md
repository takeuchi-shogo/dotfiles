---
title: 設定ドリフト監査
topics: [harness, claude-code, agent]
sources:
  - 2026-06-07-karpathy-147k-claudemd-absorb-analysis.md
  - 2026-06-18-vercel-eve-agent-framework-absorb-analysis.md
updated: 2026-07-05
confidence: emerging
source_count: 2
last_validated: 2026-07-05
---

# 設定ドリフト監査

## 概要

設定・ドキュメント・harnessコードの間に生じる乖離（drift）を定期的に検出する監査手法。外部記事の内容が完全な焼き直し（delta=0）であっても、その原則群を物差し（adversarial lens）として既存harnessに当てることで、実際に死んでいるhookやstale factを発見できる。「採用0件=収穫なし」ではない、という点が中心的な発見である。

## 主要な知見

- 記事から新規に採用する手法がゼロであっても、記事の主張群をadversarial lensとして既存harnessに適用する監査（validation-only follow-up）は独立して価値を生む。2ヶ月以上死んでいたNO-OPフックや、symlink先の取り違えによる過小カウントなど、実機構の欠陥を複数発見できた [EXTRACTED, conf=90]
- 複数のlensでfindingを検出した後、skeptic的な立場のagentでadversarial verify（デフォルトfalseとして扱い、既にどこかでカバーされていないか確認する）を行うことで監査結果の信頼性を担保する。findingのうち一定数を「棄却」できること自体が監査の質を示す証跡になる [EXTRACTED, conf=85]
- 手書きのドキュメント（例: gate数を記載した索引ファイル）は手動同期に頼ると必ず腐る。人間・別のAI・既存docがそれぞれ異なる数値を報告した実例が、手書き管理の限界を裏付けた。解決は新しい手書きdocの追加ではなく、実際の設定ファイルから生成し差分を検証する仕組み（`--check`）への置き換えである [EXTRACTED, conf=90]
- settings.jsonに配線済みのhookが、存在しない環境変数を参照するなどの理由で一度も発火せず、数ヶ月単位で放置されるケースがある。配線されている＝機能しているとは限らない [EXTRACTED, conf=85]
- TypeScript/Node.js向けのproduction agent framework製品は、単一ユーザーのCLI harnessとはスコープが根本的に異なり、機能面の採用は構造的にゼロへ収束しやすい。一方でそのフレームワークが前提とする設計思想（設定は単一の真実源であるべき、など）は、自分のharnessに潜む腐敗を検出する物差しとして転用できる [EXTRACTED, conf=75]
- 外部フレームワークを取り込む価値は「機能を借りる」ことだけではなく、「その設計思想を使って自分のharnessの腐敗を検出する」ことにもある [INFERRED, conf=70]

## 実践的な適用

dotfilesでは`.bin/validate_configs.sh`にgate数のdrift check（settings.jsonの許可/拒否件数とカタログファイルのヘッダ記述を照合し、不一致でfailさせる）を追加した。ultracode validation auditでは6種類のlensを並列で走らせ、各findingをskeptic agentで再検証する運用が確立している。

## 関連概念

- [observability-signals.md](observability-signals.md) — 監査に使う実測データという観点で接続する
- [confirmation-bias.md](confirmation-bias.md) — 外部記事の検証と自harness監査を橋渡しする判断プロセス
- [harness-engineering.md](harness-engineering.md) — 監査対象となるharness設計そのものの原則

## ソース

- [Karpathy 24-rule CLAUDE.md ($147K記事) absorb分析](../../research/2026-06-07-karpathy-147k-claudemd-absorb-analysis.md) — Karpathy記事は全rehash、監査でNO-OPフック等15件のharness欠陥を発見修正
- [Vercel eve Agent Framework absorb分析](../../research/2026-06-18-vercel-eve-agent-framework-absorb-analysis.md) — Vercel eveは機能面で採用0だが設計思想からgate数drift検出を導入
