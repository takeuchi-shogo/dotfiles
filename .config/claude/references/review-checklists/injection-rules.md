---
status: reference
last_reviewed: 2026-04-23
---

# Injection Rules Checklist

> AgentWatcher (arXiv:2604.01194) の 10 種ルール分類に基づくセキュリティレビュー用チェックリスト。
> `security-reviewer` エージェントが MCP レスポンスや外部入力を含むコードをレビューする際に参照する。
> 完全な分類定義: `references/injection-rule-taxonomy.md`

## 攻撃パターンチェック

- [ ] **R1 Instruction Hijacking**: 外部入力が元タスクの命令を上書きしていないか
- [ ] **R2 System Override**: system/developer 指示の偽装がないか
- [ ] **R3 Credential Theft**: 認証情報の要求・出力誘導がないか
- [ ] **R4 Resource Exfiltration**: ファイル/DB/環境変数の外部送信指示がないか
- [ ] **R5 Output Manipulation**: 出力フォーマット/内容の改竄指示がないか
- [ ] **R6 Attention Diversion**: タスクからの注意逸らし（"before you can..."パターン）がないか
- [ ] **R7 Task Expansion**: 指示範囲外の追加タスク挿入がないか
- [ ] **R8 Unrelated Requests**: タスクと無関係な操作の挿入がないか
- [ ] **R9 External Redirection**: 不審な外部 URL へのアクセス誘導がないか
- [ ] **R10 System Spoofing**: システムメッセージの偽装がないか

## 偽陽性チェック（ベナインルール）

- [ ] **B1**: ツール呼び出しはユーザーのタスク遂行に必要なものか
- [ ] **B2**: コンテキスト内の指示はタスク完了のための正当なものか
- [ ] **B3**: コンテンツはユーザーが明示的に指定したソースからのものか
- [ ] **B4**: 機密情報の存在だけで判定していないか（流出指示 R4 を伴うか）
