# Applying the Team Template

Team project に template を適用する手順。シナリオ別に記載。

## シナリオ 1: 新規 project (一番簡単)

```bash
# 1. base をコピー
cp -R /path/to/dotfiles/templates/team-project/base/* /path/to/your-project/

# 2. (任意) variant を上書き
cp -R /path/to/dotfiles/templates/team-project/variants/<VARIANT>/* /path/to/your-project/

# 3. .tpl 拡張子を外す
cd /path/to/your-project
find . -name '*.tpl' -exec sh -c 'mv "$0" "${0%.tpl}"' {} \;

# 4. placeholder 置換 (例: sd を使う場合)
rg -l '\{\{' | xargs sd '\{\{PROJECT_NAME\}\}'  'MyApp'
rg -l '\{\{' | xargs sd '\{\{DEFAULT_OWNER_GH\}\}' 'alice'
# ... 残りの placeholder

# 5. 残る placeholder を確認
rg -o '\{\{[A-Z_]+\}\}' -h | sort -u

# 6. 初期 commit
git add docs/ CLAUDE.md .github/CODEOWNERS
git commit -m "docs: initialize Claude Code harness template"
```

## シナリオ 2: 既存 project に後付け (差分適用)

既に CLAUDE.md や docs/ が無い team project に template を導入する場合。
**Claude Code の `/init-project --team --apply-to <project-dir>` に委譲するのが楽**。

自動化を使わずに手動で行う場合:

```bash
cd /path/to/existing-project

# 1. 競合チェック
ls CLAUDE.md docs/facts.md docs/zones/OWNERSHIP.md .github/CODEOWNERS 2>/dev/null
# → 既存があれば、template の内容を merge する必要あり

# 2. 足りないファイルだけコピー (存在する場合は上書きしない)
for f in CLAUDE.md docs/facts.md docs/zones/OWNERSHIP.md docs/security/auth-payment-policy.md .github/CODEOWNERS; do
  src="/path/to/dotfiles/templates/team-project/base/${f}.tpl"
  dst="${f}"
  [ -f "$dst" ] && echo "SKIP (exists): $dst" && continue
  [ ! -f "$src" ] && src="${src%.tpl}"  # .tpl 無しの fallback (README, 0000-template.md)
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
done

# 3. placeholder 置換
# ...

# 4. 既存コードに合わせて Zone paths を調整
# (apps/web ? frontend/ ? src/client/ ? プロジェクトの構成に合わせる)

# 5. 初期 commit 前に diff を確認
git diff --stat
git diff CLAUDE.md
```

## シナリオ 3: 既存 CLAUDE.md をリファクタして本 template に合わせる

既に自作の CLAUDE.md があるが、team 向け要素が足りない場合:

1. **既存 CLAUDE.md を読む** — 残すべき project-specific な内容を確認
2. **base/CLAUDE.md.tpl の構成を参考に** — Zone 定義・Verification Gate・Scope Caps などを追加
3. **`/init-project --team --apply-to .` で gap 分析** を実行し、skill に不足分の提案をもらう
4. 差分を手動 merge

## Placeholder 命名規則

| プレフィックス | 意味 |
|---------------|------|
| `{{PROJECT_*}}` | プロジェクト名・ドメイン |
| `{{*_OWNER}}` | 人名 (表示用) |
| `{{*_OWNER_GH}}` | GitHub username (CODEOWNERS 用) |
| `{{*_PATHS}}` | glob pattern (例: `apps/web/**`) |
| `{{*_VERIFY_CMD}}` | 検証コマンド (例: `pnpm typecheck`) |
| `{{*_URL}}` | 外部 URL |
| `{{DATE}}`, `{{YYYY-MM-DD}}` | 日付 |
| `{{UPDATER}}`, `{{AUTHOR}}` | GitHub username |

## 不要ファイルの削除

以下は project によって不要:

- `docs/security/auth-payment-policy.md` — 認証・決済を扱わない project
- `docs/zones/OWNERSHIP.md` — 単独 owner project (ただし bus factor 対策に推奨)
- `.github/CODEOWNERS` の Infra / Database 行 — 該当 Zone がない場合

削除する場合は関連する参照 (CLAUDE.md などからのリンク) も削除する。

## よくある失敗

| 症状 | 原因 | 対応 |
|------|------|------|
| `.tpl` が残ったまま commit | rename step をスキップ | `find . -name '*.tpl'` で検出 |
| Placeholder が残ったまま commit | 置換スクリプトが一部しか走らなかった | `rg '\{\{[A-Z_]+\}\}'` で再確認 |
| CODEOWNERS が機能しない | GitHub Branch Protection 未設定 | Settings → Branches → Require CODEOWNERS approval を有効化 |
| ADR が書かれずに stack が勝手に変わる | ADR プロセスが team に浸透していない | PR template に `Related ADR:` 行を追加 |

## Claude Code との連携

team project で Claude Code を使う前提なら:

- **team 共通 `settings.json`**: `.claude/settings.json` に permissions / hooks を記載 (team でコミット)
- **個人 `settings.local.json`**: 個人設定 (gitignore)
- **Skills**: project 固有の skill は `.claude/skills/` に配置

個人 dotfiles harness の仕組みがどう team に翻訳されるかは `~/.claude/references/team-harness-patterns.md` を参照。
