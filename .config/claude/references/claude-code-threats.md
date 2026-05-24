---
status: reference
last_reviewed: 2026-04-23
---

# Claude Code エコシステム脅威ナレッジベース

security-reviewer エージェントおよび `/security-review` コマンドから参照される。
一般的な OWASP チェックを補完する Claude Code 固有の脅威カタログ。

---

## 1. CVE カタログ

### Critical

| CVE | コンポーネント | 影響 | 対策 |
|-----|---------------|------|------|
| CVE-2026-0755 | gemini-mcp-tool | LLM 生成引数が shell にそのまま渡され RCE (CVSS 9.8) | 使用停止、パッチ適用待ち |
| CVE-2025-35028 | HexStrike AI MCP | セミコロン注入による OS コマンド実行 (CVSS 9.1) | 使用停止 |
| CVE-2025-15061 | Framelink Figma MCP | fetchWithRetry のシェルメタ文字で RCE (CVSS 9.8) | 最新版に更新 |
| CVE-2025-49596 | MCP Inspector | RCE (CVSS 9.4) | 最新版に更新 |

### High

| CVE | コンポーネント | 影響 | 対策 |
|-----|---------------|------|------|
| CVE-2025-53109 | Filesystem MCP | prefix bypass + symlink でサンドボックス脱出 | 最新版に更新 |
| CVE-2025-53110 | Filesystem MCP | symlink 操作でサンドボックス脱出 | 最新版に更新 |
| CVE-2025-54135 | Cursor/mcp.json | プロンプトインジェクションで設定書き換え → RCE | 設定ファイルの権限制限 |
| CVE-2025-54136 | Team configuration | 承認後の改ざんで永続バックドア | 設定変更の監査 |
| CVE-2026-24052 | WebFetch MCP | ドメイン検証バイパスで SSRF | URL ホワイトリスト |
| CVE-2025-66032 | コマンド実行 | ブロックリスト欠陥で 8 種のバイパス | 許可リスト方式に移行 |
| CVE-2026-25725 | Claude Code sandbox | `.claude/settings.json` 欠落時に hook でサンドボックス脱出 | settings.json の存在確認 |
| CVE-2026-25253 | OpenClaw | 悪意ある WebSocket リンクで 1-click RCE | URL 検証 |
| CVE-2026-0757 | MCP Manager | execute-command のコマンドインジェクション | 使用停止 |

### Medium

| CVE | コンポーネント | 影響 | 対策 |
|-----|---------------|------|------|
| CVE-2026-3484 | nmap-mcp-server | child_process.exec のコマンドインジェクション | execFile に移行 |

---

## 2. MCP 攻撃パターン

### ラグプル攻撃
1. 正常な MCP サーバーを公開し信頼を獲得
2. ユーザーベース拡大後に悪意あるアップデートを配信
3. **対策**: バージョン固定 + ハッシュ検証 + 更新時の差分レビュー

### Tool Poisoning
- ツール説明のメタデータに隠し指示を埋め込み、LLM の挙動を操作
- **対策**: スキーマ差分モニタリング、ツール説明の定期監査

### Confused Deputy
- 信頼された名前を別サーバーに登録し、正規サーバーに偽装
- **対策**: 名前空間の検証、公式ソースとの照合

---

## 3. .claude/ フォルダ攻撃ベクター

外部リポジトリを clone した際、`.claude/` フォルダに悪意あるファイルが含まれる可能性がある。

| ベクター | メカニズム | リスク |
|----------|-----------|--------|
| 悪意ある agents | `allowed-tools: ["Bash"]` + データ流出プロンプト | HIGH |
| 汚染された commands | プロンプトテンプレートに隠し指示 | HIGH |
| 悪意ある hooks | PreToolUse/PostToolUse の bash スクリプト | HIGH |
| トロイの settings.json | 過度に許可的な `permissions.allow` | MEDIUM |
| 汚染された CLAUDE.md | セキュリティ設定を上書きする指示 | HIGH |

### 検査チェックリスト

外部リポジトリの `.claude/` を検査する際:
1. `agents/*.md` の `allowed-tools` に `Bash` が無制限で許可されていないか
2. `hooks/` 内のスクリプトが外部 URL にデータを送信していないか（`curl`, `wget`, `nc` 等）
3. `settings.json` の `permissions.allow` が過度に広くないか
4. `CLAUDE.md` に「セキュリティチェックを無効化」等の指示がないか
5. commands 内に `base64 -d` や `eval` 等の難読化パターンがないか

---

## 4. プロンプトインジェクション回避技法

| 技法 | 例 | 検出方法 |
|------|-----|---------|
| ゼロ幅文字 | U+200B, U+200C, U+200D | Unicode 正規表現 |
| RTL オーバーライド | U+202E で表示を反転 | 双方向文字スキャン |
| ANSI エスケープ | `\x1b[` シーケンス | エスケープフィルタ |
| Null バイト | `\x00` で文字列を切断 | Null 検出 |
| Base64 コメント | `# SGlkZGVuOi4u`（隠しコンテンツ） | エントロピーチェック |
| ネストコマンド | `$(evil_command)` | パターンブロック |
| ホモグリフ | キリル文字 `а` vs ラテン文字 `a` | Unicode 正規化 |

---

## 5. サプライチェーン脅威（悪意あるスキル）

### Snyk ToxicSkills 調査結果（2026年2月）

3,984件のスキル（ClawHub + skills.sh）を調査:

| 項目 | 数値 | カテゴリ |
|------|------|---------|
| セキュリティ欠陥あり | 36.82% (1,467件) | サプライチェーン |
| クリティカルリスク | 13.4% (534件) | マルウェア、インジェクション、秘密鍵露出 |
| ハードコード API キー | 10.9% | 認証情報窃取 |
| リモートプロンプト実行 | 2.9% | 動的ペイロード取得 |
| 悪意あるペイロード | 76件 | データ流出、バックドア |

### 検出すべきパターン

スキル導入時に以下を確認:
- `curl`, `wget`, `fetch` で外部 URL にデータを送信していないか
- `eval`, `exec`, `Function()` で動的コード実行していないか
- 環境変数（`process.env`, `os.environ`）を外部に送信していないか
- `~/.ssh/`, `~/.aws/`, `~/.config/` 等の機密ディレクトリにアクセスしていないか

---

## 6. MCP 導入時 5分監査チェックリスト

新しい MCP サーバーを導入する前に:

1. **出所確認**: GitHub で 100+ stars、アクティブなメンテナンス、Anthropic 公式か
2. **権限確認**: 最小権限か、ファイルシステムアクセスが制限されているか
3. **バージョン固定**: `package.json` でバージョンが固定されているか（`^` や `~` ではなく exact）
4. **コード監査**: 難読化がないか、`child_process.exec` の入力検証があるか
5. **既知脆弱性**: 上記 CVE カタログに該当するコンポーネントではないか

---

## 6.5 ローカル秘密ファイルの defense-in-depth

`permissions.deny` (`Read(.env*)` 等) は Claude Code プロセス内のみの防御。deny rule が silently fail する事例がコミュニティで報告されているため、OS ファイルシステムレイヤーで二層化する。

### 二層防御

1. **L1 (Claude Code)**: `permissions.deny` で `Read(.env*)` / `Read(**/*secret*)` を block (settings.json L90+ deny ブロックで pre-existing)
2. **L2 (OS filesystem)**: `chmod 600 .env` / `chmod 600 .env.*` で所有者のみ read 可に制限 (本セクションで追記)
   - L1 が誤動作しても OS が拒否
   - 副次効果: 他ユーザー・他プロセス (CI runner / shared cache 等、ただし同一 identity で動作する場合は無効) からの read も防ぐ
   - **注**: CI/CD pipeline で runner 自身が `.env` を動的生成する場合は chmod のみでは不十分。pipeline identity の権限制御 (secret manager / OIDC scope / least-privilege role) と併用すること

### 適用範囲

- プロジェクトルートに新規 `.env` / `.env.local` を作成する時点で `chmod 600` を必ず実行
- `~/.aws/credentials` / `~/.netrc` / `~/.ssh/id_*` は標準で 600 に設定済の前提
- 共有開発機 / CI runner 上では特に必須

### 検証

```bash
# プロジェクト内の秘密ファイル候補のパーミッション確認 (macOS BSD stat)
find . -maxdepth 2 -name ".env*" \
  \( -not -name ".env.example" -a -not -name ".env.sample" -a -not -name ".env.template" \) \
  -exec stat -f "%Sp %N" {} \;
# 期待出力: -rw-------

# Linux GNU stat 版
find . -maxdepth 2 -name ".env*" \
  \( -not -name ".env.example" -a -not -name ".env.sample" -a -not -name ".env.template" \) \
  -exec stat -c "%a %n" {} \;
# 期待出力: 600
```

---

## 6.6 Permission Hygiene（権限の棚卸し）

`permissions.allow` は session 毎に grant を追加していくと放置で増殖する (`Cowork trusted folders` パターンの settings.json 版)。grant 時点では正当でも、対象プロジェクト消滅・MCP 撤去・ツール置換などで「使われない権限」が蓄積する。

### 月次監査

`scripts/lifecycle/permission-audit.py` を月初に実行する (cron 不要、手動 trigger)。

```bash
python3 ~/dotfiles/scripts/lifecycle/permission-audit.py
```

出力:
- `permissions.allow` 件数 + tool 種別ヒストグラム (Bash/Read/Write/mcp__*/その他)
- `permissions.deny` 件数 (defense-in-depth が薄まっていないか)
- 該当しそうな pruning 候補 (path-specific grant で、対象 path が現存しない/参照履歴ゼロのもの)

### 採用基準

- 件数が 100 を超えたら必ず通読する
- mcp__* grant は対応 MCP server が `enabled: true` でなければ削除候補
- path-specific grant (`Read(~/path/...)`) は path が存在しなければ削除候補
- `Bash(...:*)` の wildcard 多用は scope creep の signal

### Build to Delete

本機構は「定期的に grant を勘定する」だけで、削除判定は人が行う。telemetry 整備 (実際の grant 使用頻度ログ) が `session_observer` 経由で揃った時点で auto-pruning に進化可能。現状は手動段階。


> Franklin et al. (Google DeepMind, 2026) — 自律型エージェントの情報環境を攻撃面とする脅威体系。

### 概要

| カテゴリ | ターゲット | 代表的攻撃 | 当セットアップへの関連性 |
|----------|-----------|-----------|----------------------|
| **Content Injection** | Perception | CSS隠蔽、aria-label偽装、Markdown masking | MCP応答・WebFetch経由で混入 → mcp-response-inspector.py で検出 |
| **Semantic Manipulation** | Reasoning | 権威的フレーミング、Critic Evasion（「教育目的」偽装） | レビューアーの判断を歪める → Critic Evasion 耐性注記で対策 |
| **Cognitive State** | Memory/Learning | メモリポイズニング（0.1%汚染で80%成功率）、ICL汚染 | メモリファイル改ざん → memory-integrity-check.py で検知 |
| **Behavioural Control** | Action | Data Exfiltration（80%成功率）、Sub-agent Spawning（58-90%成功率） | Depth-1 ルール + 外部コンテンツ隔離で緩和 |
| **Systemic** | Multi-Agent | Compositional Fragment Traps、Sybil Attacks | 単一ユーザー環境では低リスク。断片分散型は注意 |
| **Human-in-the-Loop** | Human Overseer | Approval Fatigue、Automation Bias | agency-safety-framework.md で認識・緩和策を記載 |

### Compositional Fragment Traps（A5: 特記）

複数の無害なフラグメントが異なるソース（MCP応答、メモリ、スキル定義等）に分散し、
エージェントのコンテキストウィンドウで結合された時に初めて攻撃ペイロードとして機能する。

- **検出困難**: 個々のフラグメントは無害に見えるため、単一ソースの検査では検出不可
- **緩和策**: mcp-response-inspector.py のパターン検出 + security-reviewer による cross-source 分析

---

## 更新履歴

- 2026-04-02: Agent Traps セクション追加（Franklin et al., Google DeepMind）
- 2026-03-11: 初版作成（claude-code-ultimate-guide の脅威DB を基に構築）
