# Reviewer Capability Scores

各レビューアーのドメイン別 capability score。
review SKILL.md Step 4 Section 7 (Capability-Weighted Synthesis) で使用。

## Score 定義

0-10 スケール。高いほどそのドメインの指摘を重視する。

## Capability Matrix

| Reviewer | security | architecture | style | correctness | performance | spec-compliance |
|----------|----------|-------------|-------|-------------|-------------|-----------------|
| code-reviewer | 6 | 7 | 8 | 8 | 6 | 5 |
| security-reviewer | 10 | 5 | 3 | 6 | 4 | 3 |
| cross-file-reviewer | 4 | 9 | 5 | 7 | 5 | 4 |
| codex-reviewer | 8 | 8 | 6 | 9 | 7 | 6 |
| product-reviewer | 3 | 4 | 4 | 5 | 3 | 10 |
| design-reviewer | 2 | 3 | 9 | 4 | 3 | 7 |
| golang-reviewer | 7 | 7 | 9 | 9 | 8 | 4 |

## ドメイン判定

指摘の failure_mode / カテゴリからドメインを判定:

| failure_mode / keyword | domain |
|----------------------|--------|
| injection, auth, XSS, CSRF, OWASP | security |
| coupling, cohesion, interface, dependency | architecture |
| naming, format, convention, readability | style |
| logic, bug, nil, race, off-by-one | correctness |
| N+1, allocation, complexity, latency | performance |
| spec, acceptance, requirement, scope | spec-compliance |

判定できない場合は correctness をデフォルトとする。

## 更新ポリシー

- `/skill-audit` のベンチマーク結果でスコアを調整
- 新レビューアー追加時はデフォルト 5 で開始し、10回のレビュー後に実績ベースで調整
