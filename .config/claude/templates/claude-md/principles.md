<core_principles>

- **KISS / YAGNI / DRY / 最小インパクト**: シンプルに、必要な箇所だけ触る。3 回繰り返されるまで抽象化しない
- **search-first (既存探索)**: 既存の解決策・既存スクリプトを必ず確認してから書く。config → エントリポイント → モジュールの順で recall を上げる
- **CLI-first discovery (未知探索)**: 訓練外 CLI は `--help` で引数・サブコマンドを確認してから使う。発見順: CLI → Skills → MCP
- **壊れたら即STOP・ごまかし禁止**: 突き進まず再プラン。失敗報告は許される、検証スキップ・結果捏造は許されない。未検証の事実・ライブラリ挙動・外部応答は、推測で断定するより「未確認」と明示する方が正しい。再現性ある harness/tool 失敗は workaround で進めず `references/failure-escalation-protocol.md` に従い Issue + worktree に escalate する
- **暗黙フォールバック・モック・NO-OP 絶対禁止**: 実装層で「とりあえず動かす」「後で直す」のためのモック残置・NO-OP 実装・暗黙フォールバックを残さない。境界では Fail Fast、内部では Trust。詳細: `silent-failure-hunter` agent + `references/dual-audience-cli-guide.md`
- **自律的バグ解決 + 3点説明**: 生データ（ログ・スタックトレース・CI出力）を直接分析。修正時は原因・修正内容・効果を必ず明示
- **ドキュメント＝インフラ**: 仕様書は耐荷重構造物。「2 回説明したら書き下ろせ」。spec/reference に codify する
- **Build to Delete**: ハーネス (hook/script/agent) は過渡的技術。設計時に「何が改善されればこれは不要か？」を問い、削除コストを最小化する
- **Scaffolding > Model / 観測可能にする**: 協調プロトコル選択が品質差異の 44%、モデル選択は ~14%。診断に使えない信号は実質ゼロ
- **判断をゲート化する / 批評を成果物にする**: review/gate は suggestion ではなく pass/block 判定。criticism は pre-mortem/review/retrospective の 1st-class artifact
- **失敗 → capability gap → durable artifact**: "try harder" ではなく "what capability is missing, how to make it legible and enforceable"

</core_principles>
