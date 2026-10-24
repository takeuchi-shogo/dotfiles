# 根拠になった実例と数値（参考・出典）

Lauren Tan (@poteto) の公開 PR と pstack を調べてまとめたもの。テンプレート文言の根拠。

- react/react の poteto の PR 458件: 変更行数中央値28行・2ファイル、100行以下が74%。2〜3本の stack（ghstack→Sapling）。
- タイトル: `[領域] 命令形の動詞で始める要約`（中央値42字）。動詞: Add / Fix / Update / Remove / Don't / Make / Allow / Revert。小さい変更は [ez]。2026年は Conventional Commits `type(scope): subject`。
- 本文（小さいPR）: 見出しなし約20語。「これまでは〜。〜でも〜が必要。理由は〜」の3文。例 https://github.com/react/react/pull/31384
- 本文（中〜大PR、pstack opening-a-pr.md 2026）: "one-minute briefing, not a lab notebook"。順に Why(1-3文) / What changed(1-3項目) / Scope(必須・やらないこと) / Tradeoffs(捨てた案がある時のみ) / Blast Radius(1-2文) / Verification(実際に動かしたコマンドと結果、性能は before→after)。40行以内、空見出しは削る。SHA一覧・ログ・表は貼らずリンク。
- 修正: 失敗する再現だけのPRを先に出し、修正は次のPR（例 https://github.com/react/react/pull/31383 → #31384）。pstack bug-fix.md: "Stage the commits so the failing repro lands before the fix in git history."
- Revert: `Revert "<元タイトル>"`、根拠リンク付き理由＋長期案＋"But for now, reverting"（例 https://github.com/react/react/pull/34747）
- コミット（pstack）: "Commit liberally. Rebase into small, ordered commits before opening PRs. Each commit is a future PR… Commit bodies don't restate the subject." 件名は短く命令形、末尾ピリオドなし、実在のシンボル名を含める。
- "Prefer five narrow PRs to one large PR." バージョン更新・リネーム・整形は別PR。
- Issue: 上流バグ報告は Current / Expected / Steps to reproduce（最小再現リポジトリ）/ Root cause。AIに書かせたら明記。TODOリストIssueはチェックボックス。
- 定型返信: 再現不可→再現リポジトリを依頼／修正済み→リリース版リンク＋「直っていなければreopenを」／貢献を誘う。
- レビュー: `nit:` に理由一言、代案や命名案を疑問形で、文言は suggestion ブロック、数値があれば本文に入れてもらう。
