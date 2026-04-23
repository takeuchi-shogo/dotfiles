# Zone Ownership Matrix — {{PROJECT_NAME}}

> Zone = コードベースを責任で分割した領域。Owner は**最終責任者**であり、
> 日々のコーディングを独占する人ではない (他 Zone からも修正 PR は出す)。

## 目的

- **曖昧さの排除**: 「これ誰に聞けば？」を即答できる
- **Review の自動化**: `.github/CODEOWNERS` で PR reviewer を自動割り当て
- **Zone 跨ぎの警戒**: 1 PR で複数 Zone を触るときは事前共有

## Matrix

| Zone | Owner | Backup | 主要パス | 必須検証 |
|------|-------|--------|---------|---------|
| **Frontend** | @{{FE_OWNER_GH}} | @{{FE_BACKUP_GH}} | `{{FE_PATHS}}` | `{{FE_VERIFY_CMD}}` |
| **Backend** | @{{BE_OWNER_GH}} | @{{BE_BACKUP_GH}} | `{{BE_PATHS}}` | `{{BE_VERIFY_CMD}}` |
| **Infrastructure** | @{{INFRA_OWNER_GH}} | @{{INFRA_BACKUP_GH}} | `{{INFRA_PATHS}}` | `{{INFRA_VERIFY_CMD}}` |
| **Database** | @{{DB_OWNER_GH}} | @{{DB_BACKUP_GH}} | `{{DB_PATHS}}` | `{{DB_VERIFY_CMD}}` |
| **Security** | @{{SEC_OWNER_GH}} | @{{SEC_BACKUP_GH}} | `docs/security/`, `.github/workflows/security*.yml` | `{{SEC_VERIFY_CMD}}` |
| **Docs** | @{{DOC_OWNER_GH}} | — | `docs/`, `README.md` | — |

## Cross-Zone Change Protocol

1 PR で 2 つ以上の Zone を跨ぐ場合:

1. PR description に **Cross-Zone** タグと跨ぐ理由を明記
2. 関係する Zone owner に事前共有 (Slack / Issue 等)
3. CODEOWNERS により自動で複数 reviewer がアサインされることを確認
4. 各 Zone の検証コマンドを全て通す

**避けるべきパターン**:
- Frontend と Database schema を同時に変更 (migration タイミング問題)
- Infrastructure と Backend を同時に変更 (rollback が難しい)

## High-Risk Zones — 追加ルール

以下は **人間 2 名レビュー必須** (`docs/security/auth-payment-policy.md` 参照):
- 認証 (`{{AUTH_PATHS}}`)
- 決済 (`{{PAYMENT_PATHS}}`)
- 個人情報を扱う API endpoint

## On-Call / Escalation

| 状況 | 一次 | 二次 |
|------|-----|------|
| 本番障害 | {{PRIMARY_ONCALL}} | {{SECONDARY_ONCALL}} |
| Security incident | @{{SEC_OWNER_GH}} | {{SECURITY_ESCALATION}} |
| データ消失疑い | @{{DB_OWNER_GH}} | @{{BE_OWNER_GH}} |

## Update Rules

- 人事変更時は**同日中**に update (旧 owner に新 owner への引き継ぎ責任)
- Backup は必ず 1 名以上アサイン (bus factor 1 を避ける)
- 四半期に 1 回 owner が在籍確認 + パス整合性チェック

---

**Last Updated**: {{DATE}} / **By**: {{UPDATER}}
