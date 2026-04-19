# Severity Matrix — 依存監査の優先度判定

dependency-auditor skill が Phase 4 Prioritize で参照する severity 判定基準。
CVSS v3.1 をベースに、deprecated/unmaintained/license シグナルを加味する。

## 基本スコア (CVSS v3.1)

| レベル | CVSS 範囲 | 意味 |
|--------|-----------|------|
| Critical | 9.0-10.0 | システム侵害、RCE、認証回避 |
| High | 7.0-8.9 | 権限昇格、深刻な情報漏洩 |
| Medium | 4.0-6.9 | XSS、CSRF、限定的な情報漏洩 |
| Low | 0.1-3.9 | DoS（制限付き）、軽微な情報漏洩 |

CVE ベースの vuln がない場合、以下の付加シグナルで判定する。

## 付加シグナル

### Deprecated / Unmaintained

| シグナル | 追加優先度 | 判定 |
|---------|-----------|------|
| `deprecated` フラグ付き (npm/PyPI) | +1 レベル | Medium → High |
| GitHub repo archived | +1 レベル | 同上 |
| 最終コミット > 2 年 | +0 or +1 | 代替がなければ +0、あれば +1 |
| 最終コミット > 5 年 | +1 レベル | 無条件で昇格 |

### License リスク

| License | 分類 | 対応 |
|---------|------|------|
| MIT / Apache-2.0 / BSD-*/ ISC | Low | 追加対応なし |
| MPL-2.0 / LGPL-* | Medium | 商用利用時は注意 (必ず確認) |
| GPL-2.0 / GPL-3.0 / AGPL-* | High | copyleft。商用非公開ソフトに組み込み不可の場合あり |
| Unknown / Unlicensed | High | 法的リスク。利用前に要確認 |
| Custom / Proprietary | Medium-High | 条項を精読 |

### Version Lag

| Lag | 優先度 |
|-----|--------|
| patch lag (x.y.Z) | Low |
| minor lag (x.Y.z) | Low-Medium |
| 1 major lag (X.y.z) | Medium |
| 2+ major lag | Medium-High |
| major lag で EOL | High |

### 依存の深さ

- **Direct dependency**: 表示された severity をそのまま使用
- **Transitive dependency**: severity を 1 段下げる (直接制御不能)。ただし Critical は維持
- **dev-dependency**: severity を 1 段下げる (本番影響なし)。ただし supply chain attack リスクは残る

## 組み合わせ判定の例

| ケース | CVSS | 追加シグナル | 最終判定 |
|--------|------|------------|----------|
| `lodash@4.17.15` (CVE-2020-8203) | 7.4 | direct, GitHub 活発 | **High** |
| `request@2.88.2` | — | deprecated, direct, EOL | **High** (deprecated +1) |
| `moment@2.29.4` | — | 最終コミット 3 年前, 代替あり (dayjs) | **Medium** |
| `log4j@2.14.0` (Log4Shell) | 10.0 | direct, transitive 両方 | **Critical** |
| 内部 private package with custom license | — | Unknown license | **High** (license +1) |
| `eslint-plugin-foo@1.0` (dev, patch lag) | — | dev-dep, patch lag | **Low** |

## 修正アクション優先度

```
Critical  → 即時 patch / workaround。24h 以内
High      → 次回 sprint。1 週間以内
Medium    → 月次 dependency update cycle
Low       → backlog (四半期単位)
```

## 判定フロー

```
1. CVE スキャン結果を取得 → CVSS から初期レベル決定
2. Deprecated / Unmaintained シグナルで調整 (+1)
3. License リスクで調整 (+1 まで)
4. 依存の深さで調整 (transitive/dev は -1)
5. 最終レベルに応じて修正アクションを提案
```

## Anti-Patterns

- **CVSS だけで判定する**: deprecated は CVE がなくても長期リスクが大きい
- **dev-dep を無視する**: supply chain attack (例: eslint-scope incident) は dev 経由で成立
- **license を無視する**: 組織のポリシーに抵触すると後から差し戻しが発生
- **transitive を全無視する**: 直接 update 不可でも override/resolutions で対応可能なケースがある
