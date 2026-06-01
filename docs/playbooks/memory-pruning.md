# Memory Pruning Playbook

MEMORY.md (Claude Code auto-memory index) が肥大化したときの**手動** pruning 手順。

> 出典: damidefi「Delete 90% of Your Obsidian Notes」absorb (2026-05-31) の validation-only follow-up。
> 自動 archive (`memory-archive.py`) は retired — 「ファイル位置=古さ」を仮定するため
> MEMORY.md のトピック別構造で逆効果 (前半のコア知識を archive する)。詳細: `references/retired-concepts.md`。

## いつ実行するか

`claudemd-size-check.py` (PostToolUse hook) が次を warn したとき:
- `MEMORY.md byte budget exceeded: >23000B`
- `MEMORY.md line budget exceeded: >180 lines`

(Claude Code ハード上限 200行/25KB の 90% で proactive に警告)

## 原則: thinking を残し information を archive

determinism boundary により、**検知は mechanism (hook)、pruning は judgment (人/Claude)**。
機械的に「古い順」では切れない。各セクションを次の test で分類する:

- **thinking (残す)**: family 横断教訓、設計判断、繰り返し効く知見、自分の reaction/thesis
- **information (archive)**: 過去 absorb の個別要約、収集物の索引。**本体 (`docs/research/*.md` 等) が source of truth として存在し、30秒で再取得できる**もの

borderline は archive 側に倒す (記事の lean-DELETE。noise を残すコストの方が高い)。

## 手順 (archive-before-delete)

```bash
MEMDIR="$HOME/.claude/projects/<project>/memory"

# 1. バックアップ (~/.claude/projects/ は git 管理外 — 復元は archive のみ)
cp "$MEMDIR/MEMORY.md" "$MEMDIR/MEMORY.md.bak-$(date +%F)"

# 2. セクション構造を確認
grep -n "^## " "$MEMDIR/MEMORY.md"

# 3. information セクションを特定 (例: 外部知見索引)。各エントリの本体リンクが
#    docs/research/*.md に存在することを確認 (= 情報損失なしの条件)

# 4. 該当セクションを archive に退避 (削除せず保持)
#    退避先: $MEMDIR/archive/YYYY-MM.md (memory-archive.py の旧慣習を踏襲)

# 5. MEMORY.md 本体は family 横断教訓のみに圧縮し、本体への 1 行ポインタを残す

# 6. 検証
wc -l "$MEMDIR/MEMORY.md"   # 180 行以下を確認
```

## やってはいけない

- `memory-archive.py` を実行する (retired、逆効果。実行前に必ず本 playbook を参照)
- 本体 (`docs/research/*.md`) が存在しないエントリを確認せず削除する (情報損失)
- バックアップなしで書き換える (memory ディレクトリは git 管理外)

## 実績

- 2026-05-31: MEMORY.md 223行/48K → 154行/16K。外部知見索引 70+ エントリを
  `archive/2026-05.md` に退避 + family 横断教訓 12 行に圧縮。
  レポート: `docs/research/2026-05-31-damidefi-delete-90-vault-absorb-analysis.md`
