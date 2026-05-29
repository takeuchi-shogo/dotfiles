# mattpocock-skills (local wrapper marketplace)

upstream `github.com/mattpocock/skills` には `.claude-plugin/marketplace.json` が無いため、
native `claude plugin marketplace add mattpocock/skills` が使えない。この薄い wrapper が
marketplace を提供し、プラグイン本体は `source: {github, mattpocock/skills}` で取得する。

## 既知の制約: machine-specific 絶対パス (review [MUST] 由来)

`settings.json` の `extraKnownMarketplaces.mattpocock-skills.source.path` は **絶対パス**で記録される。
Claude Code は `~` / `${HOME}` を add 時に絶対パスへ正規化するため、portable な形で保存できない
(directory source の構造的制約。portable なのは github source のみ)。

→ **別マシン / 別ユーザー名で dotfiles を clone した場合、この 1 件だけ再 bootstrap が必要**:

```bash
claude plugin marketplace add ~/dotfiles/.config/claude/marketplaces/mattpocock-skills
claude plugin install mattpocock-skills@mattpocock-skills --scope user
```

(他 4 件の marketplace は github source なので再 bootstrap 不要。これだけが例外)

## 撤退トリガ (Build to Delete)

upstream が `.claude-plugin/marketplace.json` を追加したら、この wrapper は不要になる:
1. `extraKnownMarketplaces.mattpocock-skills.source` を `{source: github, repo: mattpocock/skills}` に変更
2. この wrapper ディレクトリを削除
3. `claude plugin marketplace update mattpocock-skills`

upstream 状況: https://github.com/mattpocock/skills (定期確認)
