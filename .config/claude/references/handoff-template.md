# Handoff テンプレート

エージェントが人間へのエスカレーションまたはセッション間の引き継ぎを行う際の構造化テンプレート。
受け手が元の会話にアクセスできなくても理解できる self-contained なサマリを作成する。

## テンプレート

### 1. コンテキスト
- **タスク**: [元のタスクの1行要約]
- **開始時点**: [タスク開始時の状態]
- **現在のブランチ**: [git branch]
- **関連ファイル**: [変更した/調査したファイルのリスト]

### 2. 進捗サマリ
- **完了した作業**: [完了済みのステップ、箇条書き]
- **部分的な成果物**: [途中まで作成したファイルやコード]

### 3. ブロッカー
- **何が止まっているか**: [具体的な問題の説明]
- **試行した解決策**: [試みた解決策とその結果、各1行]
- **エラー出力**: [関連するエラーメッセージやスタックトレース]

### 4. 推奨アクション
- **即座に必要なこと**: [次に取るべきアクション]
- **判断が必要な点**: [人間の意思決定が必要な事項]
- **代替案**: [検討すべき別のアプローチ]

### 5. 再開ガイド
- **前提条件**: [再開に必要な環境やツール]
- **再現手順**: [問題を再現する最短手順]
- **checkpoint**: [checkpoint ファイルのパス（あれば）]

## Usage Guidelines

### 使うべきタイミング（有効なトリガー）
1. **ユーザーが人間対応を明示的に要求した**場合
2. **ポリシーギャップ**: 既存のルールや権限では対応できない判断が必要な場合
3. **進行不能**: 環境・権限・外部依存等の制約でタスクを前に進められない場合

### 使うべきでないケース
- **感情ベースのエスカレーション**: ユーザーの感情トーンだけで判断しない（信頼性が低い）
- **自己申告の confidence**: 「自信がない」という主観的感覚だけでは escalate しない
- これらはノイズが多く、不要なエスカレーションを増やす原因になる

### Multi-concern リクエストの扱い
- 複数の懸念が含まれるリクエストは、個別の項目に分解する
- 独立した項目は並列で調査し、ブロッカーのある項目のみ handoff 対象にする

## Example

### 1. コンテキスト
- **タスク**: `auth-service` の integration test が staging 環境でのみ失敗する問題の調査
- **開始時点**: CI の test job が `TestOAuthCallback` で FAIL、ローカルでは再現しない
- **現在のブランチ**: `fix/oauth-callback-timeout`
- **関連ファイル**: `auth/oauth_test.go`, `auth/callback.go`, `docker-compose.staging.yml`

### 2. 進捗サマリ
- **完了した作業**:
  - ローカル環境での再現試行（成功せず）
  - `callback.go` の timeout 値を 5s → 15s に変更する修正を作成
  - staging の Docker network 設定の差分を特定
- **部分的な成果物**: `fix/oauth-callback-timeout` ブランチに timeout 修正をコミット済み

### 3. ブロッカー
- **何が止まっているか**: staging 環境の OAuth provider（外部 IdP）へのネットワーク到達性を検証できない
- **試行した解決策**:
  - `docker-compose.staging.yml` の network 設定確認 → ローカルと同一
  - timeout 延長 → CI で再実行したが同じ箇所で FAIL
- **エラー出力**: `oauth_test.go:142: context deadline exceeded: POST https://idp.staging.internal/token`

### 4. 推奨アクション
- **即座に必要なこと**: staging 環境から `idp.staging.internal` への疎通確認（`curl` / `dig`）
- **判断が必要な点**: IdP の staging endpoint が変更された可能性 — infra チームへの確認が必要
- **代替案**: mock server を使った integration test に切り替える（ただしカバレッジが変わる）

### 5. 再開ガイド
- **前提条件**: staging 環境への SSH アクセス、IdP 管理画面の権限
- **再現手順**: `git checkout fix/oauth-callback-timeout && make test-integration`
- **checkpoint**: `docs/plans/active/fix-oauth-timeout.md`
