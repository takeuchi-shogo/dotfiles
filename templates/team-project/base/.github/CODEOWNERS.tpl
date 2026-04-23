# CODEOWNERS — {{PROJECT_NAME}}
# Branch protection の "Require review from Code Owners" と併用。
# 高リスクパス (auth/payment) は 2 名以上。team 名 (@org/team) が人事変更に強い。
# ルール優先順: ファイル末尾に書かれた行が優先 (GitHub CODEOWNERS 仕様)。

*                               @{{DEFAULT_OWNER_GH}}

{{FE_PATHS}}                    @{{FE_OWNER_GH}} @{{FE_BACKUP_GH}}
{{BE_PATHS}}                    @{{BE_OWNER_GH}} @{{BE_BACKUP_GH}}
{{INFRA_PATHS}}                 @{{INFRA_OWNER_GH}} @{{INFRA_BACKUP_GH}}
{{DB_PATHS}}                    @{{DB_OWNER_GH}} @{{DB_BACKUP_GH}}

# High-Risk (docs/security/auth-payment-policy.md)
{{AUTH_PATHS}}                  @{{SEC_OWNER_GH}} @{{BE_OWNER_GH}}
{{PAYMENT_PATHS}}               @{{SEC_OWNER_GH}} @{{BE_OWNER_GH}}

docs/                           @{{DOC_OWNER_GH}}
docs/zones/OWNERSHIP.md         @{{DEFAULT_OWNER_GH}} @{{SEC_OWNER_GH}}
docs/security/                  @{{SEC_OWNER_GH}}
CLAUDE.md                       @{{DEFAULT_OWNER_GH}}
.github/CODEOWNERS              @{{DEFAULT_OWNER_GH}} @{{SEC_OWNER_GH}}
.github/workflows/              @{{INFRA_OWNER_GH}}
