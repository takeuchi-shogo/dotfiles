---
source: https://qiita.com/yamamoto0/items/17817dc09a78078fa132
date: 2026-03-26
status: integrated
---

## Source Summary

**Title**: Claude Code Agent に入れるべき Skills 20 選 | skills.sh 活用ガイド
**Author**: yamamoto0 (Youichi Yamamoto)

**Main Claim**: AI エージェント単体ではプロダクションレベルに達しない。モデルのパラメータ数ではなく Skills (ルール定義) が品質を決定する。skills.sh で外部スキルをインストールすることで品質を大幅に向上できる。

**20 Skills**: find-skills, vercel-react-best-practices, frontend-design, web-design-guidelines, remotion-best-practices, brainstorming, agent-browser, browser-use, supabase-postgres-best-practices, azure-cost-optimization, cloudflare/skills, redis/agent-skills, vercel-composition-patterns, vercel-react-native-skills, sleek-design-mobile-apps, ui-skills, pdf, seo-audit, skill-creator, code-review-expert

## Gap Analysis

### Gap / Partial / N/A

| # | Skill | Verdict | Status |
|---|-------|---------|--------|
| 5 | remotion-best-practices | N/A | React video production, out of scope |
| 10 | azure-cost-optimization | N/A | Repo skill not found (renamed/removed). Skipped |
| 14 | vercel-react-native-skills | N/A | React Native unused |
| 15 | sleek-design-mobile-apps | N/A | Mobile app dev not primary |
| 17 | **pdf** | **Gap** | No PDF skill. Installed from anthropics/skills |
| 18 | seo-audit | N/A | SEO not primary |

### Already (all enhancement-unnecessary)

| # | Skill | Existing | Notes |
|---|-------|----------|-------|
| 1 | find-skills | superpowers:using-superpowers + 70+ skill routing | More comprehensive |
| 2 | vercel-react-best-practices | react-best-practices (same source) | Already installed |
| 3 | frontend-design | frontend-design (same source) | Already installed |
| 4 | web-design-guidelines | web-design-guidelines (same source) | Already installed |
| 6 | brainstorming | superpowers:brainstorming (same source) | Already installed |
| 7 | agent-browser | webapp-testing + ui-observer agent | Already installed |
| 13 | vercel-composition-patterns | vercel-composition-patterns (same source) | Already installed |
| 16 | ui-skills (ibelick) | ui-ux-pro-max (50+ styles, 161 palettes) | More comprehensive |
| 19 | skill-creator | skill-creator + eval/benchmark | More comprehensive |
| 20 | code-review-expert | review SKILL.md + 10+ reviewer agents | Far more sophisticated |

### Installed (user request, originally N/A)

| # | Skill | Source | Installed Skills |
|---|-------|--------|------------------|
| 8 | browser-use | browser-use/browser-use | browser-use, cloud, open-source, remote-browser (4) |
| 9 | supabase-postgres | supabase/agent-skills | supabase-postgres-best-practices (1) |
| 11 | cloudflare | cloudflare/skills | cloudflare, agents-sdk, building-ai-agent-on-cloudflare, building-mcp-server-on-cloudflare, durable-objects, sandbox-sdk, web-perf, workers-best-practices, wrangler (9) |
| 12 | redis | redis/agent-skills | redis-development (1) |

## Integration Decisions

- **pdf**: Installed. Gap filled.
- **browser-use, supabase, cloudflare, redis**: Installed per user request (originally N/A, installed for future readiness).
- **azure-cost-optimization**: Skipped. Skill not found in microsoft/github-copilot-for-azure repo.
- All Already items: No enhancement needed.

## Summary

Total installed: 16 new skills (1 pdf + 4 browser-use + 1 supabase + 9 cloudflare + 1 redis).
Article's core thesis (Skills > model params) aligns with our existing approach of 70+ custom skills.
