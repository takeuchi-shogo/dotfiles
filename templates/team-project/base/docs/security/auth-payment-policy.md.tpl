# Auth & Payment Change Policy — {{PROJECT_NAME}}

> 認証 (auth) と決済 (payment) は **高リスク領域**。通常の PR フローより厳しい統制を適用する。
> 対象パス: `{{AUTH_PATHS}}`, `{{PAYMENT_PATHS}}`

## Scope

以下に**任意の変更を加える** PR は本 policy の対象:

- ログイン / サインアップ / パスワードリセット / MFA フロー
- セッション管理・トークン発行・署名鍵
- Authorization (権限チェック、RBAC、RLS)
- 決済フロー (カード登録、課金、返金、サブスク管理)
- Webhook 受信 (Stripe / 認証プロバイダ)
- Secret / API key の取り扱いコード

## Required Approvals

- **最低 2 名の人間による承認** (Claude Code / AI エージェントは**カウントしない**)
- うち 1 名は `OWNERSHIP.md` の **Security Owner** or **Backend Owner**
- CODEOWNERS で自動アサインされるが、**手動追加レビュアーも歓迎**

> **GitHub Tier 注意**: Branch Protection の `Required approving reviews` は **GitHub Team plan 以上**で複数指定可能 (Free tier は 1 名のみ)。2-sign-off を機構化するには Team plan + "Require review from Code Owners" が必要。それ未満の tier では本 policy は**人間の規律** (PR reviewer 追加指名) で運用する。

## Required Artifacts in PR

以下を PR description に含める:

1. **変更理由** — 背景・関連 Issue
2. **Threat Model Delta** — 新たに発生する攻撃面 / 緩和策
3. **Test Evidence**
   - 単体テスト結果
   - 統合テスト (特に failure path: expired token / invalid signature / replay attack)
   - 手動検証のスクリーンショット or ログ
4. **Rollback Plan** — 問題発生時に 5 分以内で切り戻せる手順
5. **Feature Flag 状態** — 段階リリースするか、全員即適用か

## Prohibited Patterns

以下は **reject される**:

- Secret を diff に含める (環境変数・AWS Secrets Manager 等に外出し必須)
- `console.log` / `print` でトークンや個人情報を出力
- 既存の audit log 行を **update / delete** する変更 (append only)
- Webhook 受信で signature 検証をスキップ
- Session fixation / open redirect を招く URL 組み立て

## Automation (GitHub)

- `.github/CODEOWNERS` で auth/payment パスに owner を自動アサイン
- `.github/workflows/security-required.yml` でテスト網羅率と secret scan を enforce (推奨)
- Branch protection で **auth/payment パスを含む PR は 2 approvals + security review を必須** に設定

## Incident Response

auth/payment 由来の incident 発生時:

1. **Immediate**: 影響ユーザー範囲の特定 + 必要なら全セッション無効化
2. **Within 24h**: Incident Report 草稿 (`docs/incidents/`)
3. **Within 1 week**: Root cause 分析 + ADR 起票 (prevention)
4. **Communication**: 法務 / コンプライアンスへの通知判断 ({{LEGAL_CONTACT}})

## Review Cadence

- 四半期ごとに本 policy を review
- 新決済プロバイダ追加 / 新認証方式導入時は policy 更新

---

**Last Updated**: {{DATE}} / **Owner**: @{{SEC_OWNER_GH}}
