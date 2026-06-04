# リファレンス中盤: Query・QueryAll・Search・Scheduler・Lightning Usage 等

> 出典: Salesforce『REST API 開発者ガイド』日本語版 (api_rest.pdf, 2026-03-31 生成, Spring '26 相当)
> PDF ページ 332–397。pypdf による自動抽出テキストのため、表組みのレイアウトが崩れている場合がある。

## 収録セクション

  - Query (PAGE 332)
  - Query More Results (PAGE 335)
  - QueryAll (PAGE 337)
  - QueryAll More Results (PAGE 338)
  - Query Performance Feedback (ベータ) (PAGE 340)
  - Quick Actions (PAGE 342)
  - Recent List Views (PAGE 344)
  - Recently Viewed Items (PAGE 346)
  - Record Count (PAGE 346)
  - sObject 関連項目 (PAGE 348)
  - ナレッジ言語設定の取得 (PAGE 350)
  - Search (PAGE 351)
  - Search Scope and Order (PAGE 352)
  - Search Result Layouts (PAGE 353)
  - Lightning Toggle Metrics (PAGE 353)
  - Lightning Usage by App Type (PAGE 354)
  - Lightning Usage by Browser (PAGE 355)
  - Lightning Usage by Page (PAGE 356)
  - Lightning Usage by FlexiPage (PAGE 358)
  - Lightning Exit by Page Metrics (PAGE 359)
  - Salesforce Scheduler リソース (PAGE 360)
  - オートコンプリートの結果とインスタント結果により推奨されたレコードの検索 (PAGE 373)
  - Search Suggested Article Title Matches (PAGE 379)
  - Search Suggested Queries (PAGE 382)
  - Salesforce アンケート翻訳リソース (PAGE 384)
  - Tabs (PAGE 393)
  - Themes (PAGE 395)

---

===== PAGE 332 =====
"revenueScheduleInstallmentsNumber": 10,
"revenueScheduleStartDate": "2018-09-15"
}
商談商品に対して数量によるスケジュールのみを確立します。
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/OpportunityLineItem/00kR0000001WJJAIA4/OpportunityLineItemSchedules
-H "Authorization: Bearer token"
JSON リクエストボディ
{
"type": “Quantity”,
"quantity": 10,
"quantityScheduleType": "Repeat",
"quantityScheduleInstallmentPeriod": “Daily”,
"quantityScheduleInstallmentsNumber": 150,
"quantityScheduleStartDate": "2020-09-15",
}
商品スケジュールの削除
商談商品の収益または数量スケジュールのすべての分割を削除します。すべてのスケジュールを削除すると、
削除トリガーも起動されます。このリソースは REST API バージョン 43.0 以降で使用できます。
構文
URI
/services/data/vXX.X/sobjects/OpportunityLineItem/OpportunityLineItemId/OpportunityLineItemSchedules
形式
JSON、XML
HTTP のメソッド
DELETE
認証
Authorization: Bearer token
リクエストボディ
None
要求パラメーター
None
Query
指定された SOQL クエリを実行します。
SOQL クエリが実行された場合、同期要求で一度に最大 2,000 個のレコードが返されます。ただし、パフォーマ
ンスを最適化するために、返されるバッチには、照会されたレコードのサイズと複雑さに基づいて、制限値ま
322
商品スケジュールの削除リファレンス

===== PAGE 333 =====
たはリクエストで設定された値よりも少ない数のレコードを含めることができます。結果の合計数が、この制
限または結果の要求数を超える場合、応答に含まれるのは、レコードの最初のバッチ、false 値の done、お
よびクエリロケーターになります。クエリロケーターは、次のレコードのバッチを取得するために「Query More
Results」 (ページ 325)リソースで使用できます。
応答には、QueryAll 要求で返されたレコードの総数 (totalSize)、これ以上結果がないことを示す Boolean 値
(done)、後続のレコードの URI (nextRecordsUrl)、クエリ結果レコードの配列 (records) が含まれます。
構文
URI
/services/data/vXX.X/query?q=query
形式
JSON、XML
HTTP メソッド
GET
認証
Authorization: Bearer token
パラメーター
説明パラメーター
SOQL クエリ。有効な URI を作成するには、クエリ文字列でスペースをプラス記号
+ または %20 に置き換えます。たとえば、SELECT+Name+FROM+MyObject のよ
q
うになります。SOQL クエリ文字列が無効な場合、MALFORMED_QUERY 応答が返され
ます。
例
レスポンスボディの例
{
"totalSize": 3222,
"done": false,
"nextRecordsUrl": "/services/data/v60.0/query/01gRO0000016PIAYA2-500",
"records": [
{
"attributes": {
"type": "Contact",
"url": "/services/data/v60.0/sobjects/Contact/003RO0000035WQgYAM"
},
"Id": "003RO0000035WQgYAM",
"Name": "John Smith"
},
...
]
}
323
Queryリファレンス

===== PAGE 334 =====
SOQL クエリ実行のリソース
• 例については、「SOQL クエリを実行する」を参照してください。
• バッチサイズの変更については、「Query Options ヘッダー」を参照してください。
• explain パラメーターを使用してクエリおよびレポートでフィードバックを取得するには、「クエリのパ
フォーマンスに関するフィードバックを取得する」を参照してください。
• SOQL 全般についての詳細は、『SOQL および SOSL リファレンス』を参照してください。
Data Cloud のクエリプロファイルパラメーター
Data Cloud のクエリおよび統合プロファイルパラメーターにより、Salesforce REST API クエリエンドポイントを活
用して組織内の統合プロファイル、データ取得元オブジェクト、またはデータモデルオブジェクトに対する
SOQL クエリを実行できます。この機能は API バージョン 51.0 以降でサポートされています。
Query REST コールの使用の一般的な情報については、「SOQL クエリを実行する」および「クエリ」を参照して
ください。
サポート対象 SOQL パラメーター
次の SOQL パラメーターは Data Cloud での使用がサポートされています。
• 単一オブジェクトでの SELECT ステートメント
• SELECT 句: count()
• SOQL WHERE 句: contains (次の文字列を含む) 演算子
• SOQL LIKE
• SOQL LIMIT 句
デフォルトの制限は 100 に設定されています。1 回のコールの最大制限は 2,000 レコードです。
• SOQL OFFSET 句
• SOQL ORDER BY 句
SOQL の制限
次のクエリは Data Cloud での使用がサポートされていません。
• SOQL サブクエリ
• SELECT 句: 集計関数
• SELECT 句: 日付関数
• SOQL HAVING 句
324
Data Cloud のクエリプロファイルパラメーターリファレンス

===== PAGE 335 =====
サンプルクエリ
クエリ使用事例
メールのクリックイベントを取得する SELECT  SubscriberKey__c,
EngagementChannel__c, EmailName__c, SubjectLine__c FROM
sfmc_email_engagement_click_{EID}__dll LIMIT  =100
データプレビュー:
データレークオブジェクトに
取り込まれたデータを調べま
す。
メールアドレスによって個人 ID を取得する
SELECT  PartyId__c FROM  ContactPointEmail__dlm WHERE
EmailAddress__c=’jjones@email.com’ LIMIT  =100
同意の参照:
メールアドレス、電話番号、
名および姓に基づいて、連絡
先データモデルから個人 ID を
取得します。
電話番号によって個人 ID を取得する SELECT  PartyId__c FROM
ContactPointPhone__dlm WHERE  TelephoneNumber__c=’555-123-4567’ LIMIT  =100
名前によって個人 ID を取得する SELECT  IndividualId__c FROM  Individual__dlm
WHERE  FirstName__c=’Jimmy’ AND LastName__c=’Smith’ LIMIT  =100
ステップ 1:
取得元レコード ID によって統合レコードを取得する
統合プロファイルの参照:
取得元レコード ID によって統
合個人と統合連絡先を取得し
ます。
SELECT  UnifiedRecordId__c FROM  IndividualIdentityLink__dlm WHERE
SourceRecordID__c='{sourceID}' LIMIT  =100
ステップ 2:
統合プロファイル ID によって統合個人を照会する
SELECT  FirstName__c, LastName__c FROM  UnifiedIndividual__dlm WHERE
Id__c='{UnifiedRecordId__c}' LIMIT  =100
ステップ 3:
統合プロファイル ID によって統合連絡先の詳細を照会する
統合連絡先メール SELECT  EmailAddress__c FROM  UnifiedContactPointEmail__dlm
WHERE  PartyId__c={UnifiedRecordId__c} LIMIT  =100
統合連絡先電話 SELECT  TelephoneNumber__c FROM  UnifiedContactPointPhone__dlm
WHERE  PartyId__c={UnifiedRecordId__c} LIMIT  =100
Query More Results
クエリロケーターを使用することにより、SOQL クエリから結果の次のバッチを返します。
SOQL クエリから返される結果数が、要求されたレコードの数または制限を超える場合、応答に含まれるのは、
結果のバッチ、false 値の done、およびクエリロケーターになります。レコードの次のバッチを取得するに
は、次の要求でクエリロケーターを使用します。まだ返されていないレコードがある場合は、応答に新しいク
エリロケーターが含まれ、done は false となります。結果の取得は、最初のクエリから done が true にな
るまで、つまり全結果が返されたことを示すまで、続けることができます。
325
Query More Resultsリファレンス

===== PAGE 336 =====
応答には、QueryAll 要求で返されたレコードの総数 (totalSize)、これ以上結果がないことを示す Boolean 値
(done)、後続のレコードの URI (nextRecordsUrl)、クエリ結果レコードの配列 (records) が含まれます。
構文
URI
/services/data/vXX.X/query/queryLocator
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
パラメーター
説明パラメーター
後続のクエリ結果を取得するために使用する文字列。まだ未取得の結果がある場
合、前のクエリ結果の nextRecordsUrl項目にクエリロケーターが含まれます。
queryLocator
例
レスポンスボディの例
{
"totalSize": 3222,
"done": false,
"nextRecordsUrl": "/services/data/v60.0/query/01gRO0000016PIAYA2-500",
"records": [
{
"attributes": {
"type": "Contact",
"url": "/services/data/v60.0/sobjects/Contact/003RO0000035WQgYAM"
},
"Id": "003RO0000035WQgYAM",
"Name": "John Smith"
},
...
]
}
SOQL クエリ実行のリソース
• クエリロケーターの使用方法については、「SOQL クエリを実行する」を参照してください。
• バッチサイズを変更する別のオプションについては、「Query Options ヘッダー」を参照してください。
• SOQL 全般についての詳細は、『SOQL および SOSL リファレンス』を参照してください。
326
Query More Resultsリファレンス

===== PAGE 337 =====
QueryAll
指定された SOQL クエリを実行します。Query リソースとは異なり、QueryAll は merge または delete によって削除
されるレコードを返します。また、QueryAll はアーカイブ済みの ToDo と行動のレコードの情報を返します。こ
のリソースは REST API バージョン 29.0 以降で使用できます。
QueryAll 要求が実行された場合、同期要求で一度に最大 2,000 個のレコードが返されます。ただし、パフォーマ
ンスを最適化するために、返されるバッチには、照会されたレコードのサイズと複雑さに基づいて、制限値ま
たはリクエストで設定された値よりも少ない数のレコードを含めることができます。結果の合計数が、この制
限または結果の要求数を超える場合、応答に含まれるのは、結果のバッチ、false 値の done、およびクエリ
ロケーターになります。クエリロケーターは、後続のレコードのバッチを取得するために「QueryAll More Results」
のリソースで使用できます。
nextRecordsUrl の URL に query が指定されている場合でも、最初の QueryAll 要求の残りの結果が提供され
ます。残りの結果には、最初のクエリに一致した削除されたレコードが含まれます。
応答には、QueryAll 要求で返されたレコードの総数 (totalSize)、これ以上結果がないことを示す Boolean 値
(done)、後続のレコードの URI (nextRecordsUrl)、クエリ結果レコードの配列 (records) が含まれます。
構文
URI
/services/data/vXX.X/queryAll?q=query
形式
JSON、XML
HTTP メソッド
GET
認証
Authorization: Bearer token
パラメーター
説明パラメーター
SOQL クエリ。有効な URI を作成するには、クエリ文字列ではスペース
をプラス記号 + に置き換えます。たとえば、
SELECT+Name+FROM+MyObject のようになります。
q
例
レスポンスボディの例
{
"totalSize": 3222,
"done": false,
"nextRecordsUrl": "/services/data/v60.0/query/01gRO0000016PIAYA2-500",
"records": [
327
QueryAllリファレンス

===== PAGE 338 =====
{
"attributes": {
"type": "Contact",
"url": "/services/data/v60.0/sobjects/Contact/003RO0000035WQgYAM"
},
"Id": "003RO0000035WQgYAM",
"Name": "John Smith"
},
...
]
}
SOQL クエリ実行のリソース
• 削除された項目を含むクエリを実行するには、「削除された項目を含む SOQL クエリを実行する」を参照し
てください。
• クエリ結果のバッチサイズを大きくするには、「SOQL クエリを実行する」で説明されているクエリ識別子
を使用するか、Query Options ヘッダーを使用します。
• SOQL 全般についての詳細は、『SOQL および SOSL リファレンス』を参照してください。
QueryAll More Results
QueryAll 要求でクエリロケーターを使用することにより、結果の次のバッチを返します。この API リソースは、
指定された QueryAll 要求を実行します。このリソースは REST API バージョン 29.0 以降で使用できます。
SOQL クエリから返される結果数が、要求されたレコードの数または制限を超える場合、応答に含まれるのは、
結果のバッチ、false 値の done、およびクエリロケーターになります。レコードの次のバッチを取得するに
は、QueryAll More Results の要求でクエリロケーターを使用します。まだ返されていないレコードがある場合は、
応答に新しいクエリロケーターが含まれ、done は false となります。結果の取得は、最初の QueryAll の要求
から done が true になるまで、つまり全結果が返されたことを示すまで、続けることができます。
メモ: QueryAll レスポンスボディの nextRecordsUrl 項目に指定された URI には、queryAll ではなく
query が含まれています。次の結果セットを取得するには、同じクエリロケーターで Query More Results ま
たは QueryAll More Results リソースを使用します。残りの結果には、最初のクエリに一致する削除されたレ
コードが含まれています。
たとえば、QueryAll 要求のレスポンスボディに "nextRecordsUrl":
"/services/data/v60.0/query/01g5e00001AH2dOAAT-4000" が含まれている場合、QueryAll の後続
の結果セットを次のいずれかの URI で取得することができます。
• /services/data/v60.0/query/01g5e00001AH2dOAAT-4000
• /services/data/v60.0/queryAll/01g5e00001AH2dOAAT-4000
応答には、QueryAll 要求で返されたレコードの総数 (totalSize)、これ以上結果がないことを示す Boolean 値
(done)、後続のレコードの URI (nextRecordsUrl)、クエリ結果レコードの配列 (records) が含まれます。
328
QueryAll More Resultsリファレンス

===== PAGE 339 =====
構文
URI
/services/data/vXX.X/queryAll/queryLocator
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
パラメーター
説明パラメーター
後続のクエリ結果を取得するために使用する文字列。まだ未取得の結
果がある場合、前の QueryAll の結果の nextRecordsUrl 項目にクエリ
ロケーターが含まれます。
queryLocator
例
レスポンスボディの例
{
"totalSize": 3222,
"done": false,
"nextRecordsUrl": "/services/data/v60.0/query/01gRO0000016PIAYA2-500",
"records": [
{
"attributes": {
"type": "Contact",
"url": "/services/data/v60.0/sobjects/Contact/003RO0000035WQgYAM"
},
"Id": "003RO0000035WQgYAM",
"Name": "John Smith"
},
...
]
}
SOQL クエリ実行のリソース
• 削除された項目を含む QueryAll 要求を送信するには、「削除された項目を含む SOQL クエリを実行する」を
参照してください。
• クエリ結果のバッチサイズを大きくするには、Query Options ヘッダーを使用します。
• SOQL 全般についての詳細は、『SOQL および SOSL リファレンス』を参照してください。
329
QueryAll More Resultsリファレンス

===== PAGE 340 =====
Query Performance Feedback (ベータ)
指定した SOQL クエリ、レポート、またはリストビューのパフォーマンスを実行することなく分析します。
要求で explain パラメーターを使用すると、Salesforce がクエリ、レポート、またはリストビューをどのよう
に処理し、どのように最適化するかを詳細に説明する応答を取得できます。
Query Performance Feedback リソースは、API バージョン 30.0 以降で使用できます。
メモ: この機能はベータサービスです。ベータサービスはお客様独自の裁量で試行するものとします。
ベータ機能の使用には、「Agreements and Terms」に記載されたベータサービス規約が適用されます。
構文
URI
/services/data/vXX.X/query?explain=query
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
パラメーター
説明パラメーター
分析する SOQL クエリ、レポート、リストビュー。クエリを分析するには、要求に
クエリ全体を指定します。レポートやリストビューを分析する場合は、レポート
またはリストビューの ID を指定します。
explain
SOQL クエリ文字列が無効な場合、MALFORMED_QUERY 応答が返されます。レポート
またはリストビューの ID が無効な場合、INVALID_ID 応答が返されます。
レスポンスボディ
レスポンスボディには、クエリ、レポート、またはリストビューの実行に使用できる 1 つ以上のプランが
含まれます。プランは、最も最適なものから順に並び替えられます。各プランには次の情報が含まれます。
説明データ型名前
インデックス項目に基づいてクエリから返されると予測される
レコード数 (存在する場合)。
numbercardinality
leadingOperationType が Index の場合、その値がクエリに使用さ
れるインデックス項目となります。それ以外の場合、値は null
です。
string[]fields
330
Query Performance Feedback (ベータ)リファレンス

===== PAGE 341 =====
説明データ型名前
クエリを最適化するために使用できる主な操作種別。次のいず
れかの値が有効です。
stringleadingOperationType
• Index — クエリオブジェクトに関するインデックスがクエリ
で使用されます。
• Other — Salesforce の内部的な最適化がクエリで使用されま
す。
• Sharing — ユーザーの共有ルールに基づいたインデックスが
クエリで使用されます。現在のユーザーに表示されるレコー
ドが制限される共有ルールの場合、そのルールでクエリを
最適化することができます。
• TableScan — クエリオブジェクトのすべてのレコードがクエ
リでスキャンされ、インデックスは使用されません。
1 つ以上のフィードバックメモの配列。各メモに含まれる内容
は、次のとおりです。
feedback note[]notes
• description  — 最適化の一部に関する詳細な説明。この
説明には、使用不可能な最適化についてと、その理由が含
まれます。
• fields  — 最適化に使用される 1 つ以上の項目の配列。
• tableEnumOrId — 最適化に使用される項目のテーブル名。
この応答項目は、API バージョン 33.0 以降で使用できます。
SOQL セレクティブクエリのしきい値と比較した、このクエリ
のコスト。1.0 を超える値は、クエリがセレクティブではない
numberrelativeCost
ことを示します。セレクティブクエリについての詳細は、『Apex
開発者ガイド』の「非常に大きい SOQL クエリの処理」を参照
してください。
組織内にあるクエリオブジェクトの全レコードの概数。numbersobjectCardinality
クエリオブジェクトの名前 (Merchandise__c など)。stringsobjectType
SOQL クエリ実行のリソース
• explain パラメーターの使用方法については、「クエリのパフォーマンスに関するフィードバックを取得
する」を参照してください。
• SOQL 全般についての詳細は、『SOQL および SOSL リファレンス』を参照してください。
331
Query Performance Feedback (ベータ)リファレンス

===== PAGE 342 =====
Quick Actions
グローバルクイックアクションやオブジェクト固有のクイックアクションにアクセスします。このリソースで
POST メソッドを使用することで、クイックアクションを使用してレコードを作成できます。このリソースは
REST API バージョン 28.0 以降で使用できます。
アクションを使用する場合は、「sObject Quick Actions」も参照してください。
このセクションの内容:
クイックアクションの取得
クイックアクションのリストを取得します。このリソースは REST API バージョン 28.0 以降で使用できます。
クイックアクションを使用したレコードの作成
クイックアクションによりレコードを作成します。このリソースは REST API バージョン 28.0 以降で使用でき
ます。
クイックアクションのヘッダーの返送
Quick Actions リソースに GET 要求を送信したときに返されるヘッダーのみを返します。リソースのコンテン
ツを取得する前に、ヘッダー値を確認できます。このリソースは REST API バージョン 28.0 以降で使用できま
す。
クイックアクションの取得
クイックアクションのリストを取得します。このリソースは REST API バージョン 28.0 以降で使用できます。
すべての必須項目をオブジェクトに追加してから、そのオブジェクトのクイックアクションを作成してくださ
い。クイックアクションの作成後に必須項目を追加すると、クイックアクションの Describe Result に項目が表示
されなくなります。その場合、クイックアクションの実行時に項目を使用できず、項目が欠落しているという
エラーが発生します。クイックアクションのレイアウトに必須項目を表示しない場合は、項目にデフォルト値
を設定します。
アクションを使用する場合は、「sObject Quick Actions」も参照してください。
構文
URI
/services/data/vXX.X/quickActions/
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
パラメーター
不要
332
Quick Actionsリファレンス

===== PAGE 343 =====
例
リクエストの例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/quickActions/ -H
"Authorization: Bearer token"
クイックアクションを使用したレコードの作成
クイックアクションによりレコードを作成します。このリソースは REST API バージョン 28.0 以降で使用できま
す。
すべての必須項目をオブジェクトに追加してから、そのオブジェクトのクイックアクションを作成してくださ
い。クイックアクションの作成後に必須項目を追加すると、クイックアクションの Describe Result に項目が表示
されなくなります。その場合、クイックアクションの実行時に項目を使用できず、項目が欠落しているという
エラーが発生します。クイックアクションのレイアウトに必須項目を表示しない場合は、項目にデフォルト値
を設定します。
アクションを使用する場合は、「sObject Quick Actions」も参照してください。
構文
URI
/services/data/vXX.X/quickActions/
形式
JSON、XML
HTTP のメソッド
POST
認証
Authorization: Bearer token
パラメーター
不要
例
リクエストの例
curl -X POST
https://MyDomainName.my.salesforce.com/services/data/v60.0/quickActions/CreateContact
-H "Authorization: Bearer token" -H "Content-Type: application/json" -d
@exampleRequestBody.json
リクエストボディの例
{
"record" : { "LastName" : "Smith" }
}
333
クイックアクションを使用したレコードの作成リファレンス

===== PAGE 344 =====
クイックアクションのヘッダーの返送
Quick Actions リソースに GET 要求を送信したときに返されるヘッダーのみを返します。リソースのコンテンツを
取得する前に、ヘッダー値を確認できます。このリソースは REST API バージョン 28.0 以降で使用できます。
すべての必須項目をオブジェクトに追加してから、そのオブジェクトのクイックアクションを作成してくださ
い。クイックアクションの作成後に必須項目を追加すると、クイックアクションの Describe Result に項目が表示
されなくなります。その場合、クイックアクションの実行時に項目を使用できず、項目が欠落しているという
エラーが発生します。クイックアクションのレイアウトに必須項目を表示しない場合は、項目にデフォルト値
を設定します。
アクションを使用する場合は、「sObject Quick Actions」も参照してください。
URI
/services/data/vXX.X/quickActions/
形式
JSON、XML
HTTP のメソッド
HEAD
認証
Authorization: Bearer token
パラメーター
不要
例
リクエストの例
curl -X HEAD --head
https://MyDomainName.my.salesforce.com/services/data/v60.0/quickActions/ -H
"Authorization: Bearer token"
Recent List Views
特定の sObject 種別に最近使用されたリストビューのリストを返します。このリソースは REST API バージョン
32.0 以降で使用できます。
構文
URI
/services/data/vXX.X/sobjects/sObject/listviews/recent
形式
JSON、XML
HTTP メソッド
GET
334
クイックアクションのヘッダーの返送リファレンス

===== PAGE 345 =====
認証
Authorization: Bearer token
パラメーター
なし
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/listviews/recent
-H "Authorization: Bearer token"
レスポンスボディの例
{
"done" : true,
"listviews" : [ {
"describeUrl" :
"/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcCNMA0/describe",
"developerName" : "MyAccounts",
"id" : "00BD0000005WcCNMA0",
"label" : "My Accounts",
"resultsUrl" :
"/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcCNMA0/results",
"soqlCompatible" : true,
"url" : "/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcCNMA0"
}, {
"describeUrl" :
"/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcBeMAK/describe",
"developerName" : "NewThisWeek",
"id" : "00BD0000005WcBeMAK",
"label" : "New This Week",
"resultsUrl" :
"/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcBeMAK/results",
"soqlCompatible" : true,
"url" : "/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcBeMAK"
}, {
"describeUrl" :
"/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcCFMA0/describe",
"developerName" : "AllAccounts",
"id" : "00BD0000005WcCFMA0",
"label" : "All Accounts",
"resultsUrl" :
"/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcCFMA0/results",
"soqlCompatible" : true,
"url" : "/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcCFMA0"
} ],
"nextRecordsUrl" : null,
"size" : 3,
"sobjectType" : "Account"
}
335
Recent List Viewsリファレンス

===== PAGE 346 =====
Recently Viewed Items
現在のユーザーが表示または参照した、最近参照された項目を取得します。Salesforce では、レコード参照に関
する情報がインターフェースに保存され、その情報を使用して、サイドバーや検索のオートコンプリートオプ
ションなどで、最近表示および参照したレコードのリストが生成されます。
このリソースは、最近使ったデータの情報にのみアクセスします。最近参照したデータのリストを変更するに
は、SOQL クエリで FOR VIEW 句または FOR REFERENCE 句を指定して、最近参照した情報を直接更新する必
要があります。
URI
/services/data/vXX.X/recent
形式
JSON、XML
HTTP メソッド
GET
認証
Authorization: Bearer token
パラメーター
説明パラメーター
返されるレコードの最大数を指定するパラメーター (省略可能)。この
パラメーターが指定されていない場合、返されるレコードのデフォル
limit
トの最大数は RecentlyViewed のエントリの最大数 (オブジェクトあたり
200 レコード) になります。
例
• 最近参照した項目のリストを取得する例については、「最近参照したレコードの表示」 (ページ 86)を参照
してください。
• レコードを最近参照したデータとして設定する例は、「最近参照したデータとしてレコードをマーク」
(ページ 87)を参照してください。
Record Count
組織内のオブジェクトレコード件数に関する情報をリストします。
このリソースは、REST API バージョン 40.0 以降で、「設定・定義を参照する」権限を持つ API ユーザーが利用で
きます。返されるレコード件数は概数で、次の種別のレコードは含まれません。
• ごみ箱に入っている削除されたレコード。
• アーカイブ済みのレコード。
336
Recently Viewed Itemsリファレンス

===== PAGE 347 =====
構文
URI
/services/data/vXX.X/limits/recordCount?sObjects=objectList
形式
JSON、XML
HTTP メソッド
GET
認証
Authorization: Bearer token
パラメーター
説明パラメーター
オブジェクト名のカンマ区切りリスト。リストされたオブジェクトが
組織内で見つからない場合は、無視されて、応答で返されません。
このパラメーターは省略可能です。このパラメーターが指定されてい
ない場合、このリソースは、組織内のすべてのオブジェクトのレコー
ド件数を返します。
sObjects
レスポンスボディ
Record Count レスポンスボディ
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/limits/recordCount?sObjects=Account,Contact
-H "Authorization: Bearer token"
レスポンスボディの例
{
"sObjects" : [ {
"count" : 3,
"name" : "Account"
}, {
"count" : 10,
"name" : "Contact"
} ]
}
Record Count レスポンスボディ
Record Count 要求の結果を記述します。
337
Record Count レスポンスボディリファレンス

===== PAGE 348 =====
Record Count Results
プロパティ
説明型名前
sObject レコード件数の結果のコレクション。コレクション
内のオブジェクトの順番は、要求内のオブジェクトの順
番とは必ずしも一致しません。
Record Count sObject
Result[]
sObjects
JSON の例
{
"sObjects" : [ {
"count" : 3,
"name" : "Account"
}, {
"count" : 10,
"name" : "Contact"
} ]
}
Record Count sObject Result
プロパティ
説明型名前
組織内のオブジェクトのレコード件数。これは概数で、
ソフト削除されたレコードやアーカイブ済みのレコード
は含まれません。
Integercount
オブジェクトの名前。Stringname
JSON の例
{
"count" : 10,
"name" : "Contact"
}
sObject 関連項目
現在のユーザーの最も関連性の高い項目を取得します。関連性の高い項目には、ユーザーのグローバル検索範
囲のオブジェクトや、最後に使用した (MRU) オブジェクトのレコードなどがあります。
関連項目には、ユーザーのグローバル検索範囲内の各オブジェクトの最大 50 件の最近参照または更新したレ
コードが含まれます。
338
sObject 関連項目リファレンス

===== PAGE 349 =====
メモ: ユーザーのグローバル検索範囲には、Salesforce Classic の検索結果ページでユーザーが固定したオブ
ジェクトなど、過去 30 日間にユーザーが最も多く操作したオブジェクトが含まれます。
その後リソースによって、レコードの最大数 (2,000) が返されるまで、最後に使用した (MRU) オブジェクトごと
にその他の最近のレコードが検索されます。
このリソースは、関連項目情報にのみアクセスします。関連項目リストの変更は、現在サポートされていませ
ん。
このリソースは API バージョン 35.0 以降で使用できます。
構文
URI
/services/data/vXX.X/sobjects/relevantItems
形式
JSON
HTTP メソッド
GET
認証
Authorization: Bearer token
パラメーター
説明パラメーター
省略可能。現在の関連項目リスト全体を以前のバージョンと比較しま
す (使用可能な場合)。以前の応答で返された lastUpdatedId 値を指
定します。
lastUpdatedId
省略可能。結果を特定のオブジェクトまたはオブジェクトセットに絞
り込むには、1 つ以上の sObject の名前を指定します。
sobjects
メモ:  sObject 名では大文字と小文字が区別されます。
省略可能。この特定のオブジェクトの現在の関連項目リストを以前の
バージョンと比較します (使用可能な場合)。以前の応答で返された
lastUpdatedId 値を指定します。
sobject.lastUpdatedId
メモ: sobjects パラメーターで指定された sObject では、このパ
ラメーターのみ指定できます。
応答ヘッダー
応答には、このリソースに固有のヘッダーが含まれます。
339
sObject 関連項目リファレンス

===== PAGE 350 =====
説明型名前
完全な結果セットの結果をこの応答リストの結果と比較
するために後続のコールで使用できる、一意のコード。
stringlastUpdatedId
現在のユーザーに対して応答が以前に要求されている場
合は、現在の応答が以前の応答または lastUpdatedId
で指定された応答と一致するかどうかを示します。
Boolean (true
または
false)
newResultSetSinceLastQuery
レスポンスボディ
応答には、返される各オブジェクトのレコードの配列が含まれます。各レコードの次の情報も含まれます。
説明型名前
オブジェクトの一意の名前 (Account など)。stringapiName
オブジェクト種別を示す、sObject の ID の最初の 3 文字。IDkey
オブジェクトの複数形の表示ラベル (Accounts など)。stringlabel
新しい結果セットの結果をこのオブジェクトの現在の結
果と比較するために後続のコールで使用できる、一意の
コード。
stringlastUpdatedId
sObject の一意の外部名。stringqualifiedApiName
一致するレコードの ID のカンマ区切りのリスト。IDrecordIds
例
「関連項目の表示」を参照してください。
ナレッジ言語設定の取得
既存のナレッジ言語設定 (デフォルトのナレッジ言語やサポートされるナレッジ言語情報のリストなど) を取得
します。このリソースは API バージョン 31.0 以降で使用できます。
Salesforce ナレッジが組織で有効になっている必要があります。ナレッジ言語設定 (デフォルトのナレッジ言語
やサポートされるナレッジ言語情報のリストなど) を取得します。
構文
URI
/services/data/vXX.X/knowledgeManagement/settings
形式
JSON、XML
340
ナレッジ言語設定の取得リファレンス

===== PAGE 351 =====
HTTP のメソッド
GET
認証
Authorization: Bearer token
リクエストボディ
不要
要求パラメーター
なし
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/knowledgeManagement/settings
-H "Authorization: Bearer token"
レスポンスボディの例
{
"defaultLanguage" : "en_US",
"knowledgeEnabled" : true,
"languages" : [ {
"active" : true,
"name" : "en_US"
}, {
"active" : true,
"name" : "it"
}, {
"active" : true,
"name" : "zh_CN"
}, {
"active" : true,
"name" : "fr"
} ]
}
Search
指定された SOSL 検索を実行します。検索文字列は URL 符号化されている必要があります。
SOSL についての詳細は、『SOQL および SOSL リファレンス』を参照してください。
構文
URI
/services/data/vXX.X/search/?q=SOSL_searchString
341
Searchリファレンス

===== PAGE 352 =====
形式
JSON、XML
HTTP メソッド
GET
認証
Authorization: Bearer token
パラメーター
説明パラメーター
適切に URL 符号化された SOSL ステートメント。q
例
「文字列を検索する」 (ページ 70)を参照してください。
Search Scope and Order
ログインユーザーのデフォルトのグローバル検索範囲内にあるオブジェクトの順序付きリストを返します。グ
ローバル検索は、操作するオブジェクトとそれらを操作する頻度を追跡し、それに基づいて検索結果を編成し
ます。最もよく使用されるオブジェクトは、リストの最上部に表示されます。
返されるリストには、ユーザーの検索結果ページの固定表示オブジェクトを含め、ユーザーのデフォルトの検
索範囲でのオブジェクト順が反映されます。このコールは、最適化されたグローバル検索範囲を使用してカス
タム検索結果ページを実装する場合に役立ちます。検索文字列は URL 符号化されている必要があります。
構文
URI
/services/data/vXX.X/search/scopeOrder
形式
JSON、XML
HTTP メソッド
GET
認証
Authorization: Bearer token
例
「デフォルトの検索範囲と検索順序の取得」を参照してください。
342
Search Scope and Orderリファレンス

===== PAGE 353 =====
Search Result Layouts
クエリ文字列に含まれるオブジェクトの検索結果レイアウトに関する情報を返します。このコールでは、検索
結果ページに列として表示される項目のリスト、最初のページに表示される行数、および検索結果ページで使
用されるラベルがオブジェクトごとに返されます。
このコールでは、1 回のクエリで 100 個までのオブジェクトの一括取得をサポートしています。
構文
URI
/services/data/vXX.X/search/layout/?q=commaDelimitedObjectList
形式
JSON、XML
HTTP メソッド
GET
認証
Authorization: Bearer token
応答形式
説明型プロパティ
ピリオドで区切られたオブジェク
ト名と項目名。たとえば、
Account.Name など。
Stringfield
日付のみまたは日時など、日付項
目のデータ型。日付関連のデータ
Stringformat
型のみ指定します。それ以外の場
合は、null。
ユーザーに表示される名前Stringlabel
API 参照名Stringname
例
「オブジェクトの検索結果レイアウトの取得」を参照してください。
Lightning Toggle Metrics
Salesforce Classic から Lightning Experience に切り替えたユーザーに関する詳細を返します。このリソースは REST API
バージョン 44.0 以降で使用できます。
次の API でこのオブジェクトを使用します。
343
Search Result Layoutsリファレンス

===== PAGE 354 =====
• Platform
• メタデータ API
• Tooling API
構文
URI
/services/data/vXX.X/sobjects/LightningToggleMetrics
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer tokens
要求パラメーター
説明パラメーター
ユーザー ID。UserId
返されたレコード数。RecordCount
切り替えが記録された日付。MetricsDate
ユーザーが Salesforce Classic または Lightning Experience に切り替えたかど
うか。
Action
例
SELECT sum(RecordCount) Total FROM LightningToggleMetrics WHERE MetricsDate = LAST_MONTH
AND Action = 'switchToAloha'
Lightning Usage by App Type
Lightning Experience ユーザーと Salesforce モバイルユーザーの合計数を返します。このリソースは REST API バージョ
ン 44.0 以降で使用できます。
次の API でこのオブジェクトを使用します。
• Platform
• メタデータ API
• Tooling API
344
Lightning Usage by App Typeリファレンス

===== PAGE 355 =====
構文
URI
/services/data/vXX.X/sobjects/LightningUsageByAppTypeMetrics
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
要求パラメーター
説明パラメーター
使用するアプリケーション。AppExperience
• Salesforce モバイル
• Lightning Experience
データが記録された日付。MetricsDate
ユーザー ID。UserID
例
SELECT MetricsDate,user.profile.name,COUNT_DISTINCT(user.id) Total FROM
LightningUsageByAppTypeMetrics WHERE MetricsDate = LAST_N_DAYS:30 AND AppExperience =
'Salesforce Mobile' GROUP BY MetricsDate,user.profile.name
Lightning Usage by Browser
ブラウザーインスタンスによってグループ化された Lightning Experience 利用状況の結果を返します。このリソー
スは REST API バージョン 44.0 以降で使用できます。
次の API でこのオブジェクトを使用します。
• Platform
• メタデータ API
• Tooling API
構文
URI
/services/data/vXX.X/sobjects/LightningUsageByBrowserMetrics
345
Lightning Usage by Browserリファレンス

===== PAGE 356 =====
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
リクエストボディ
SOQL クエリ。
要求パラメーター
説明パラメーター
使用するブラウザー。Browser
ページの読み込みが 3 ～ 5 秒だった回数。EptBin3To5
ページの読み込みが 5 ～ 8 秒だった回数。EptBin5To8
ページの読み込みが 8 ～ 10 秒だった回数。EptBin8To10
ページの読み込みが 10 秒以上だった回数。EptBinOver10
ページの読み込みが 3 秒未満だった回数。EptBinUnder3
総計値が記録された日付。MetricsDate
ページの名前。PageName
有効な EPT が記録されたページ/ブラウザーのレコード数。RecordCountEPT
ページ/ブラウザーの EPT 値の合計。SumEPT
ページ/ブラウザーの合計レコード。TotalCount
例
リクエストボディの例
SELECT CALENDAR_MONTH(MetricsDate) MetricsDate, Browser Browser, SUM(TotalCount) Total
FROM LightningUsageByBrowserMetrics WHERE MetricsDate = Last_N_Months:3 AND (NOT Browser
like 'OTHER%') GROUP BY CALENDAR_MONTH(MetricsDate),Browser
Lightning Usage by Page
Lightning Experience でユーザーが最も頻繁に表示した標準ページを示します。このリソースは REST API バージョ
ン 44.0 以降で使用できます。
次の API でこのオブジェクトを使用します。
346
Lightning Usage by Pageリファレンス

===== PAGE 357 =====
• Platform
• メタデータ API
• Tooling API
構文
URI
/services/data/vXX.X/sobjects/LightningUsageByPageMetrics
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
説明パラメーター
ページの読み込みが 3 ～ 5 秒だった回数。EptBin3To5
ページの読み込みが 5 ～ 8 秒だった回数。EptBin5To8
ページの読み込みが 8 ～ 10 秒だった回数。EptBin8To10
ページの読み込みが 10 秒以上だった回数。EptBinOver10
ページの読み込みが 3 秒未満だった回数。EptBinUnder3
ページの名前。PageName
総計値が記録された日付。MetricsDate
有効な EPT が記録されたページ/ユーザーのレコード数。RecordCountEPT
ページ/ユーザーの EPT 値の合計。SumEPT
ページ/ユーザーの合計レコード。TotalCount
ユーザー ID。UserId
例
SELECT TotalCount FROM LightningUsageByPageMetrics ORDER BY PageName ASC NULLS FIRST LIMIT
10
347
Lightning Usage by Pageリファレンス

===== PAGE 358 =====
Lightning Usage by FlexiPage
Lightning Experience で最も頻繁に表示されたカスタムページに関する詳細を返します。このリソースは REST API
バージョン 44.0 以降で使用できます。
次の API でこのオブジェクトを使用します。
• Platform
• メタデータ API
• Tooling API
構文
URI
/services/data/vXX.X/sobjects/LightningUsageByFlexiPageMetrics
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
要求パラメーター
説明パラメーター
FlexiPageファイルの名前空間およびファイル名、またはページ ID。FlexiPageNameOrId
FlexiPage 型。たとえば、レコードの詳細は RecordPage" 型を使用
して表示されます。
FlexiPageType
総計値が記録された日付。MetricsDate
有効な EPT が記録された FlexiPage 型のレコード数。RecordCountEPT
レコードの EPT 値の合計。SumEPT
型の合計レコード。TotalCount
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/LightningUsageByFlexiPageMetrics
-H "Authorization: Bearer token"
348
Lightning Usage by FlexiPageリファレンス

===== PAGE 359 =====
リクエストボディの例
SELECT FlexiPageNameOrId FlexiPageNameOrId, SUM(TotalCount) Total FROM
LightningUsageByFlexiPageMetrics WHERE MetricsDate = Last_N_DAYS:7 AND (NOT
FlexiPageNameOrId = 'unknown unknown') AND (NOT FlexiPageNameOrId = 'unknown | unknown')
GROUP BY FlexiPageNameOrId ORDER BY SUM(TotalCount) Desc Limit 10
Lightning Exit by Page Metrics
ユーザーが Lightning Experience から Salesforce Classic に切り替える標準ページに関する頻度の総計値を返します。
このリソースは REST API バージョン 44.0 以降で使用できます。
次の API でこのオブジェクトを使用します。
• Platform
• メタデータ API
• Tooling API
構文
URI
/services/data/vXX.X/sobjects/LightningExitByPageMetrics
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
要求パラメーター
説明パラメーター
データが記録された日付。MetricsDate
ユーザーが Lightning から Aloha に切り替える現在のページPageName
ユーザーおよびページあたりのレコード数。RecordCount
ユーザー ID。UserId
例
SELECT PageName PageName, SUM(RecordCount) Total FROM LightningExitByPageMetrics WHERE
MetricsDate = Last_N_DAYS:7 GROUP BY PageName ORDER BY SUM(RecordCount) Desc Limit 10
349
Lightning Exit by Page Metricsリファレンス

===== PAGE 360 =====
Salesforce Scheduler リソース
Salesforce Scheduler REST API を使用し、作業種別グループおよびサービステリトリーに基づいて、予定の時間枠ま
たは利用可能なサービスリソースを取得します。
このセクションの内容:
スケジュール設定
利用可能な Salesforce Scheduler REST リソースおよび対応する URI のリストを返します。このリソースは REST
API バージョン 45.0 以降で使用できます。
Get Appointment Slots
指定の作業種別グループまたは作業種別と、サービステリトリーに基づいて、リソースの利用可能な予定
の時間枠のリストを返します。
Get Appointment Candidates
作業種別グループまたは作業種別と、サービステリトリーに基づいて、サービスリソース (予定の候補) の
リストを返します。
リクエストのボディ
レスポンスのボディ
関連トピック:
Connect REST API 開発者ガイド: Lightning Scheduler リソース
スケジュール設定
利用可能な Salesforce Scheduler REST リソースおよび対応する URI のリストを返します。このリソースは REST API
バージョン 45.0 以降で使用できます。
構文
URI
/services/data/vXX.X/scheduling/
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
350
Salesforce Scheduler リソースリファレンス

===== PAGE 361 =====
例
レスポンスボディの例
{
"getAppointmentCandidates": "/services/data/v60.0/scheduling/getAppointmentCandidates",
"getAppointmentSlots" : "/services/data/v60.0/scheduling/getAppointmentSlots"
}
Get Appointment Slots
指定の作業種別グループまたは作業種別と、サービステリトリーに基づいて、リソースの利用可能な予定の時
間枠のリストを返します。
予定の時間枠は、Salesforce Scheduler のデータモデル設定に基づいて決定されます。以下に、データ設定時に検
討できる要件をいくつか示します。
• 要求を作成する前に、Salesforce Scheduler を設定します。設定には、サービスリソース、サービステリトリー
メンバー、作業種別グループ、作業種別、作業種別グループメンバー、およびサービステリトリー作業種
別の作成または設定が含まれます。詳細は、「Salesforce Scheduler のビジネス情報の管理」を参照してくだ
さい。
• サービステリトリー作業種別を使用して、リクエストボディ内の各テリトリーにマップされる作業種別を
設定します。作業種別グループメンバーを使用して、作業種別グループに同一の作業種別をマップします。
以下の要素は、時間枠が計算され、返される方法に影響します。
• 業務時間全体で異なるタイムゾーンが処理され、結果は常に UTC で返されます。
• リソースは、割り当てられたリソースオブジェクトの必須リソースとしてマークする必要があります。
• サービス予定に割り当てられたリソースの状況カテゴリが、[キャンセル済み]、[完了不可]、および [完
了] 以外の場合、リソースは利用不可と見なされます。
• すべての種別の [リソース不在] は、開始から終了まで利用不可と見なされます。
• 以下の作業種別レコードの項目 (設定されている場合) は、時間枠要件の調整に使用されます。詳細は、
「Salesforce Scheduler での作業種別の作成」を参照してください。
説明パラメーター
現在の時刻 + 時間枠開始より早い時間枠は返されません。時間枠開始
現在の時刻 + 時間枠終了より遅い時間枠は返されません。時間枠終了
予定が利用不可と見なされるまでの期間。予定前のブロックタイム
予定が利用不可と見なされた後の期間。予定後のブロックタイム
時間枠を決定する際は、取引先、作業種別、サービステリトリー、
およびサービステリトリーメンバーのすべての業務時間の重複が考
業務時間
慮されます。詳細は、「Salesforce Scheduler での業務時間の設定」を
参照してください。
351
Get Appointment Slotsリファレンス

===== PAGE 362 =====
• 開始日から 31 日の期間内の時間枠のみが返されます。
• Salesforce Scheduler では、項目値、スケジュール済み予定、不在、Scheduler の設定、スケジュールポリシーな
どの複数の要素を使用して、最も早い予定と最も遅い予定の時間枠を含む利用可能な時間枠が決定されま
す。「Salesforce Scheduler による対応可能な時間枠の決定方法」を参照してください。
メモ: アセットのスケジュールが有効化されている場合、requiredResourceIds にアセットベース
のサービスリソースを指定して、そのアセットリソースに対応可能な時間枠を取得できます。
構文
URI
/services/data/vXX.X/scheduling/getAppointmentSlots
使用可能なバージョン
45.0
形式
JSON、XML
HTTP のメソッド
POST
認証
Authorization: Bearer token
リクエストボディ
説明型必須パラメーター
関連取引先の ID。StringいいえaccountId
true の場合、時間枠での同時予定のスケジュールが許
可されます。false の場合、同時予定は許可されません。
デフォルトは false です。
API バージョン 47.0 以降で使用できます。
BooleanいいえallowConcurrentScheduling
ServiceResourceScheduleHandler  Apex インター
フェースにカスタム情報を渡すための ID。たとえば、
StringいいえcorrelationId
この相関関係 ID によって Apex インターフェース実装を
コールするアプリケーション、Web サイト、または外
部システムを識別できます。カスタム値を渡さない場
合、ランダムに生成された識別子が渡されます。
この項目は、API バージョン 53.0 以降で使用できます。
時間枠 (両端を含む) が終わる最も遅い時間。StringいいえendTime
エンゲージメントチャネル種別レコードの ID。時間枠
の対応可能状況は、選択したエンゲージメントチャネ
String []いいえengagementChannelTypeIds
ル種別に基づいて絞り込みます。この項目は、API バー
ジョン 56.0 以降で使用できます。
352
Get Appointment Slotsリファレンス

===== PAGE 363 =====
説明型必須パラメーター
メモ: この項目は、1 つのエンゲージメントチャ
ネル種別 ID のみをサポートします。
getAppointmentSlots  API でエンゲージメントチャ
ネル種別を使用できるのは、次の場合のみです。
• [エンゲージメントチャネルを使用して予定をスケ
ジュール] 設定が、Salesforce 組織の Salesforce Scheduler
の設定で有効になっている。
• シフトが、スケジュールポリシーで定義されてい
る。スケジュールポリシーでのシフトの設定の詳細
は、「スケジュールポリシーでのシフトルールの定
義」を参照してください。
メモ: エンゲージメントチャネル種別は、ス
ケジュールポリシーの営業時間ルールではサ
ポートされていません。
マルチリソーススケジュールのプライマリリソースの
ID。この項目は、API バージョン 48.0 以降で使用できま
す。
StringいいえprimaryResourceId
メモ: この項目は、マルチリソーススケジュール
が有効な場合のみ必須です。
時間枠内で利用可能でなければならないリソース ID の
リスト。
String[]はいrequiredResourceIds
AppointmentSchedulingPolicyオブジェクトの ID。リクエス
トボディでスケジュールポリシーが渡されない場合、
StringいいえschedulingPolicyId
デフォルトの設定が使用されます。時間枠の決定時に
使用される唯一のスケジュールポリシー設定は、取引
先訪問時間の適用です。
時間枠 (両端を含む) が始まる最も早い時間。指定され
ていない場合は、デフォルトの要求の現時刻に設定さ
れます。
StringいいえstartTime
要求されている作業が実施されるサービステリトリー
の ID のリスト。
String[]はいterritoryIds
実施される作業の種別。Work TypeworkTypeGroupId
が指定さ
workType
れていな
い場合は
必須で
す。
353
Get Appointment Slotsリファレンス

===== PAGE 364 =====
説明型必須パラメーター
実施されている作業種別を含む作業種別グループの
ID。
StringworkType
が指定さ
れていな
workTypeGroupId
い場合は
必須。
メモ: リクエストボディ内の必須項目を決める場合は、以下の点を考慮してください。
• リクエストボディに workTypeGroupId または workType のいずれかのパラメーターを指定しま
す。ただし両方は指定できません。
• workType パラメーターが指定されている場合、id または durationInMinutes のいずれかのパ
ラメーターを指定する必要があります。
• workType パラメーターの id が指定されている場合、他の workType 項目は省略可能です。
レスポンスボディ
要求の実行が成功すると、利用可能な時間枠のリストを含むレスポンスボディが返されます。
説明型必須パラメーター
各テリトリーに含まれる時間枠のリスト。Time Slots
(ページ
362)[]
はいtimeSlots
例
リクエストボディの例
workTypeGroupId を使用:
{
"startTime": "2019-01-23T00:00:00.000Z",
"endTime": "2019-02-28T00:00:00.000Z",
"workTypeGroupId": "0VSB0000000KyjBOAS",
"accountId": "001B000000qAUAWIA4",
"territoryIds": [
"0HhB0000000TO9WKAW"
],
"schedulingPolicyId": "0VrB0000000KyjB",
"requiredResourceIds": [
"0HnB0000000TO8gKAK"
],
"engagementChannelTypeIds": [
"0eFRM00000000Bv2AI"
]
}
354
Get Appointment Slotsリファレンス

===== PAGE 365 =====
workType を使用:
{
"startTime": "2019-01-23T00:00:00.000Z",
"endTime": "2019-02-28T00:00:00.000Z",
"workType": {
"id": "08qRM00000003fkYAA"
},
"requiredResourceIds": [
"0HnB0000000TO8gKAK"
],
"territoryIds": [
"0HhRM00000003OZ0AY"
],
"accountId": "001B000000qAUAWIA4",
"schedulingPolicyId": "0VrB0000000KyjB",
"engagementChannelTypeIds": [
"0eFRM00000000Bv2AI"
]
}
レスポンスボディの例
{
"timeSlots": [
{
"endTime": "2019-01-21T19:15:00.000+0000",
"startTime": "2019-01-21T16:15:00.000+0000",
"territoryId": "0HhB0000000TO9WKAW"
},
{
"endTime": "2019-01-21T19:30:00.000+0000",
"startTime": "2019-01-21T16:30:00.000+0000",
"territoryId": "0HhB0000000TO9WKAW"
},
{
"endTime": "2019-01-21T19:45:00.000+0000",
"startTime": "2019-01-21T16:45:00.000+0000",
"territoryId": "0HhB0000000TO9WKAW"
}
]
}
Get Appointment Candidates
作業種別グループまたは作業種別と、サービステリトリーに基づいて、サービスリソース (予定の候補) のリス
トを返します。
要求を作成する前に、Salesforce Scheduler を設定します。この設定には、サービスリソース、サービステリト
リーメンバー、作業種別グループ、作業種別、作業種別グループメンバー、およびサービステリトリー作業種
別の作成または設定が含まれます。詳細は、「Salesforce Scheduler の設定」を参照してください。
355
Get Appointment Candidatesリファレンス

===== PAGE 366 =====
利用可能な時間枠を決定するために、予定の時間枠が、項目値、スケジュール済み予定、不在、Scheduler の設
定、スケジュールポリシーなどの複数の要素に基づいて決定されます。詳細は、「Salesforce Scheduler による対
応可能な時間枠の決定」を参照してください。
リソースの開始時刻および終了時刻を返す際には、以下の要素が検討されます。
リソースの作業可能性
サービステリトリーメンバー、サービステリトリー、作業種別、取引先の営業時間の各項目を使用して判
断されます。
リソースの作業不可能性
リソースの不在、リソースが割り当てられた既存の予定に基づいて判断されます。リソースは、状況が [ク
ローズ済み]、[キャンセル]、または [完了] のいずれでもない予定の必須リソースとしてマークする必要が
あります。
スケジュールポリシー内の予定の開始時間の間隔
予定を開始できる時間は、スケジュールポリシー内の [Appointment start time interval (予定の開始時間の間隔)]
項目を使用して決定されます。この間隔には、5、10、15、20、30、または 60 を設定できます。デフォルト
では 15 に設定されます。
作業種別の期間
終了時刻は、開始時刻 + 作業種別の期間で計算されます。
メモ: アセットのスケジュールが有効化されている場合、応答にはアセットベースの候補も含まれます。
構文
URI
/services/data/vXX.X/scheduling/getAppointmentCandidates
使用可能なバージョン
45.0
形式
JSON、XML
HTTP のメソッド
POST
リクエストボディ
説明型必須パラメーター
関連取引先の ID。StringいいえaccountId
true の場合、時間枠での同時予定のスケジュールが許
可されます。false の場合、同時予定は許可されません。
デフォルトは false です。
この項目は、API バージョン 47.0 以降で使用できます。
BooleanいいえallowConcurrentScheduling
ServiceResourceScheduleHandler  Apex インター
フェースにカスタム情報を渡すための ID。たとえば、
StringいいえcorrelationId
356
Get Appointment Candidatesリファレンス

===== PAGE 367 =====
説明型必須パラメーター
この相関関係 ID によって Apex インターフェース実装を
コールするアプリケーション、Web サイト、または外
部システムを識別できます。カスタム値を渡さない場
合、ランダムに生成された識別子が渡されます。
この項目は、API バージョン 53.0 以降で使用できます。
時間枠 (両端を含む) が終わる最も遅い時間。StringいいえendTime
メモ: この API は、startTime から最大 31 日の
時間枠を返します。
エンゲージメントチャネル種別レコードの ID。サービ
スリソースの対応可能状況は、選択したエンゲージメ
String[]いいえengagementChannelTypeIds
ントチャネル種別に基づいて絞り込みます。この項目
は、API バージョン 56.0 以降で使用できます。
メモ: この項目は、1 つのエンゲージメントチャ
ネル種別 ID のみをサポートします。
getAppointmentCandidates API でエンゲージメント
チャネル種別を使用できるのは、次の場合のみです。
• [エンゲージメントチャネルを使用して予定をスケ
ジュール] 設定が、Salesforce 組織の Salesforce Scheduler
の設定で有効になっている。
• シフトが、スケジュールポリシーで定義されてい
る。スケジュールポリシーでのシフトの設定の詳細
は、「スケジュールポリシーでのシフトルールの定
義」を参照してください。
メモ: エンゲージメントチャネル種別は、ス
ケジュールポリシーの営業時間ルールではサ
ポートされていません。
サービスリソース ID のカンマ区切りリスト。API は、
リストと選択したサービステリトリーの両方の資格が
String[]いいえfilterByResources
あるサービスリソースのみを返します。リソースは、
リソース ID が渡された順序で並び替えられます。API
バージョン 51.0 以降で利用できます。
予定の配分が有効になっている場合に予定のスケジュー
ル中に表示するサービスリソースの最大数を指定しま
す。API バージョン 53.0 以降で利用できます。
IntegerいいえresourceLimitApptDistribution
メモ:  filterByResources 項目は、
resourceLimitApptDistribution 項目より優先されます。
357
Get Appointment Candidatesリファレンス

===== PAGE 368 =====
説明型必須パラメーター
時間枠 (両端を含む) が始まる最も早い時間。指定され
ていない場合は、デフォルトの要求の現時刻に設定さ
れます。過去の時間も使用できます。
StringいいえstartTime
AppointmentSchedulingPolicyオブジェクトの ID。リクエス
トボディでスケジュールポリシーが渡されない場合、
StringいいえschedulingPolicyId
デフォルトの設定が使用されます。この API を使用す
る場合、すべてのスケジュールポリシー設定が考慮さ
れます。
要求されている作業が実施されるサービステリトリー
ID のリスト。
String[]はいterritoryIds
実施される作業の種別。Work TypeworkTypeGroupId
が指定さ
workType
れていな
い場合は
必須。
実施されている作業種別を含む作業種別グループの
ID。
StringworkType
が指定さ
れていな
workTypeGroupId
い場合は
必須。
メモ: リクエストボディ内の必須項目を決める場合は、以下の点を考慮してください。
• リクエストボディに workTypeGroupId または workType のいずれかのパラメーターを指定しま
す。ただし両方は指定できません。
• workType パラメーターが指定されている場合、id または durationInMinutes のいずれかのパ
ラメーターを指定する必要があります。
• workType パラメーターの id が指定されている場合、他の workType 項目は省略可能です。
レスポンスボディ
要求の実行が成功すると、利用可能な予定のリソースのリストを含むレスポンスボディが返されます。
説明型必須パラメーター
利用可能な予定の候補のリスト。Candidates
(ページ
362)[]
はいcandidates
358
Get Appointment Candidatesリファレンス

===== PAGE 369 =====
例
リクエストボディの例
workTypeGroupId を使用:
{
"startTime": "2019-01-23T00:00:00.000Z",
"endTime": "2019-02-30T00:00:00.000Z",
"workTypeGroupId": "0VSB0000000KyjBOAS",
"accountId": "001B000000qAUAWIA4",
"territoryIds": [
"0HhB0000000TO9WKAW"
],
"schedulingPolicyId": "0VrB0000000KyjB",
"engagementChannelTypeIds": [
"0eFRM00000000Bv2AI"
]
}
workTypeId を使用:
{
"startTime": "2019-01-23T00:00:00.000Z",
"endTime": "2019-02-30T00:00:00.000Z",
"workType": {
"id": "08qRM00000003fkYAA"
},
"territoryIds": [
"0HhRM00000003OZ0AY"
],
"accountId": "001B000000qAUAWIA4",
"schedulingPolicyId": "0VrB0000000KyjB",
"engagementChannelTypeIds": [
"0eFRM00000000Bv2AI"
]
}
レスポンスボディの例
{
"candidates": [
{
"endTime": "2019-01-23T19:15:00.000+0000",
"resources": [
"0HnB0000000D2DsKAK"
],
"startTime": "2019-01-23T16:15:00.000+0000",
"territoryId": "0HhB0000000TO9WKAW",
"engagementChannelTypeIds": [
"0eFRM00000000Bv2AI"
]
},
{
"endTime": "2019-01-23T19:30:00.000+0000",
"resources": [
359
Get Appointment Candidatesリファレンス

===== PAGE 370 =====
"0HnB0000000D2DsKAK"
],
"startTime": "2019-01-23T16:30:00.000+0000",
"territoryId": "0HhB0000000TO9WKAW",
"engagementChannelTypeIds": [
"0eFRM00000000Bv2AI"
]
},
{
"endTime": "2019-01-23T19:45:00.000+0000",
"resources": [
"0HnB0000000D2DsKAK"
],
"startTime": "2019-01-23T16:45:00.000+0000",
"territoryId": "0HhB0000000TO9WKAW",
"engagementChannelTypeIds": [
"0eFRM00000000Bv2AI"
]
}
]
}
リクエストのボディ
POST、PATCH、または PUT 要求を実行するには、XML または JSON 形式のリクエストボディを作成します。この
章には、リクエストボディのリストが記載されています。
このセクションの内容:
作業種別
実行する作業の種別に関する詳細。
スキル要件 ID
作業種別の特定のタスクを完了するために必要なスキルのリスト。
作業種別
実行する作業の種別に関する詳細。
説明必須型名前
作業種別の ID。durationInMinutes
が指定されてい
Stringid
ない場合は必
須。
行動の長さ (分) が含まれます。id が指定されて
いない場合は必
須。
IntegerdurationInMinutes
360
リクエストのボディリファレンス

===== PAGE 371 =====
説明必須型名前
時間枠の始まり。いいえStringtimeframeStartInMinutes
時間枠の終わり。いいえStringtimeframeEndInMinutes
予定が利用不可と見なされるまでの期間。いいえStringblockTimeBeforeAppointmentInMinutes
予定が利用不可と見なされた後の期間。いいえStringblockTimeAfterAppointmentInMinutes
時間枠を決定する際は、取引先、作業種別、サー
ビステリトリー、およびサービステリトリーメ
いいえStringoperatingHoursId
ンバーのすべての営業時間の重複が考慮されま
す。
作業種別の特定のタスクを完了するために必要
なスキルのリスト。
いいえSkill Requirement[]skillRequirements
メモ: リクエストボディに Id または durationInMinutes のいずれかを指定します。ただし両方は
指定できません。
スキル要件 ID
作業種別の特定のタスクを完了するために必要なスキルのリスト。
説明必須型名前
必要となるスキル。はいStringskillId
必要となるスキルのレベル。スキルレベルの範
囲は、0 から 99.99 にすることができます。ビジ
いいえStringSkillLevel
ネスニーズに応じて、スキルレベルに、経験年
数、認定レベル、またはライセンスクラスを反
映させる場合があります。
レスポンスのボディ
Salesforce Scheduler リソースへの要求の実行が成功すると、JSON または XML いずれかの形式でレスポンスボディ
が返されます。たとえば予定の時間枠を取得する要求では、選択した作業種別グループおよびテリトリーで利
用できる時間枠のリストが返されます。
このセクションの内容:
時間枠
Get Appointments Slots 要求の結果を記述します。
候補
Get Appointments Candidates 要求の結果を記述します。
361
レスポンスのボディリファレンス

===== PAGE 372 =====
時間枠
Get Appointments Slots 要求の結果を記述します。
テリトリーごとに利用できる時間枠のリスト。
説明型名前
予定の時間枠の終了時刻。StringendTime
この時間枠に関連付けられているエンゲージメントチャ
ネル種別の ID。この項目は、API バージョン 56.0 以降で使
用できます。
String []engagementChanneltypeIds
タイムスロットで使用可能な予定の数。
タイムスロットで使用可能な予定の数 = タイムスロットで
定義されている予定の最大数 - タイムスロットでこれまで
にスケジュールされている予定の数
IntegerremainingAppointments
予定の時間枠の開始時刻。StringstartTime
この時間枠に関連付けられているサービステリトリー。StringterritoryId
候補
Get Appointments Candidates 要求の結果を記述します。
利用可能なサービスリソースのリスト。
説明型名前
予定の時間枠の終了時刻。StringendTime
このリソースの指定された時間枠に関連付けられている
エンゲージメントチャネル種別 ID。この項目は、API バー
ジョン 56.0 以降で使用できます。
String []engagementChanneltypeIds
利用可能なサービスリソース ID のリスト。String[]resources
重要: 現段階では、このリストで返されるリソース
は 1 つのみです。テリトリーに複数のリソースが含
まれている場合、JSON レスポンスボディのリソース
ごとに新しい子オブジェクトが 1 つ追加されます。
予定の時間枠の開始時刻。StringstartTime
このリソースに関連付けられているサービステリトリー。StringterritoryId
362
レスポンスのボディリファレンス

===== PAGE 373 =====
オートコンプリートの結果とインスタント結果により推奨された
レコードの検索
名前がユーザーの検索文字列と一致した推奨レコードのリストを返します。この推奨リソースは、ユーザーが
全文検索を実行する前に、関連する可能性のあるレコードに直接移動するためのオートコンプリートの結果と
インスタント結果を提供します。このリソースは REST API バージョン 32.0 以降で使用できます。
この推奨リソースは、レコード名項目が検索文字列と一致するテキストを含む場合にレコードを返します。検
索文字列内の最後の文字と、単語の先頭の一致も検出されます。1 語内に検索文字列が含まれるレコードは、
一致とは見なされません。
メモ: ユーザーの検索クエリに疑問符またはワイルドカードが含まれている場合、それらの記号は URI で
クエリ文字列から自動的に削除されます。
テキスト文字列 national u は national u* として扱われ、「National Utility」、「National Urban Company」、
「First National University」が返されます。
この推奨リソースは、関連する可能性があり、ユーザーがアクセス可能なレコードに関する、表示可能な状態
のデータを返します。関連性アルゴリズムは結果の順序を決定します。結果内の各推奨レコードには、次の要
素が含まれます。
説明要素
レコードのオブジェクト種別とレコードにアクセスするための URL。
要求された参照項目の値も含まれます。たとえば、fields=Id,Name
を要求した場合、結果には ID と名前が含まれます。
Attributes
レコードの名前項目。標準の名前項目がない場合、次のオブジェクトに
は標準のタイトル項目が使用されます。
Name  (または Title)
• Dashboard
• Idea
• IdeaTheme
• Note
• Question
標準の名前項目または役職項目がない場合、メインの識別項目が使用さ
れます。たとえば、ケースの場合はケース番号が使用されます。
レコードの一意の識別子。Id
この推奨リソースでは、次を除くすべての検索可能オブジェクトがサポートされます。
• ContentNote
• Event
• 外部オブジェクト
• FeedComment
363
オートコンプリートの結果とインスタント結果により推
奨されたレコードの検索
リファレンス

===== PAGE 374 =====
• FeedPost
• IdeaComment
• Pricebook2
• Reply
• TagDefinition
• Task
構文
URI
/services/data/vXX.X/search/suggestions?q=searchString&sobject=objectTypes
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
リクエストボディ
不要
要求パラメーター
説明パラメーター
省略可能。ルックアップクエリの作成に使用します。カンマ区切りの
リストを使用して複数の項目を指定します。応答で返される参照項目
を指定します。
fields
省略可能。API バージョン 48.0 以降で使用できます。追加の動的項目
を返すために使用されます。複数のオプションを指定するには、カン
dynamicFields
マ区切りのリストを使用します。たとえば、
dynamicFields=secondaryField の場合、検索レイアウトの次の
対象項目に基づいて、Id および Name  (または Title) 以外の項目が
結果の各推奨レコードに追加されます。
省略可能。返される質問が投稿されたグループの一意の識別子を指定
します。カンマ区切りのリストを使用して複数のグループを指定しま
groupId
す。このパラメーターは、パラメーターの type が question の場合に
のみ適用されます。userId と併せて使用しないでください。
省略可能。要求にサポート対象外のオブジェクトが含まれている場
合、このパラメーターは、実行するアクションを指定します。false
ignoreUnsupportedSObjects
に設定した場合は、エラーが返されます。true に設定した場合は、
オブジェクトが無視され、エラーは返されません。「サポート対象外
のオブジェクト」セクションを参照してください。デフォルトは、
false です。
364
オートコンプリートの結果とインスタント結果により推
奨されたレコードの検索
リファレンス

===== PAGE 375 =====
説明パラメーター
省略可能。返される推奨レコードの最大数を指定します。制限が指定
されていない場合、デフォルトで 5 レコードが返されます。指定され
limit
た制限を超える推奨レコードが存在すると、レスポンスボディの
hasMoreResults プロパティが true になります。
省略可能。質問が返される Experience Cloud サイトの一意の識別子を 1
つ以上指定します。カンマ区切りのリストを使用して複数のサイトを
networkId
指定します。このパラメーターは、パラメーターのtype が question
の場合、またはパラメーターの sobject が user の場合にのみ適用
されます。
必須。適切に URL 符号化された、ユーザーの検索クエリ文字列。ユー
ザーの検索クエリ文字列が最小長要件 (中国語、日本語、韓国語、タ
q
イ語の場合は 1 文字、その他の言語の場合は 3 文字) を満たしている場
合にのみ、推奨クエリが返されます。クエリ文字列が最大長である
255 文字 (または区切りの空白なしの連続した 200 文字) を超えると、エ
ラーが返されます。
必須。Account や offer__c など、検索の範囲となるオブジェクト。
sobject の値が feedItem の場合は、type パラメーターが必須とな
り、その値として question を設定する必要があります。
sobject
カンマ区切りのリストを使用して最大 10 個のオブジェクトを指定し
ます。たとえば、sobject=Account,Contact,Lead のように記述
します。この機能を利用するには、[CrossObjectTypeahead]権限を有効
にします。
オブジェクトごとに返す特定の項目を指定するには、次の構文を使用
します。複数の項目にはカンマ区切りのリストを使用します。sobject
は小文字です。
sobject=sobject.fields=fields
次に例を示します。
&sobject=Account,Contact,Lead&account.fields=Website,Phone
&contact.fields=Phone
省略可能。返される質問がタグ付けされた単一のトピックの一意の識
別子を指定します。このパラメーターは、パラメーターの type が
question の場合にのみ適用されます。
topicId
sobject の値が feedItem である場合は必須です。sobject のその
他すべての値に対してこのパラメーターを含めると、クエリには影響
type
しません。フィードの種別が質問であることを指定します。有効な値:
question。
365
オートコンプリートの結果とインスタント結果により推
奨されたレコードの検索
リファレンス

===== PAGE 376 =====
説明パラメーター
省略可能。返される質問を作成したユーザーの一意の識別子を指定し
ます。カンマ区切りのリストを使用して複数のユーザーを指定しま
userId
す。このパラメーターは、パラメーターの type が question の場合に
のみ適用されます。groupId と併せて使用しないでください。
省略可能。API バージョン 40.0 以降で使用できます。デフォルト値は、
false です。false の場合、要求で指定されたオブジェクトを使用
useSearchScope
してレコードが提案されます。true の場合、要求で指定されたオブ
ジェクトのほかに、ユーザーの検索範囲を使用してレコードが提案さ
れます。検索範囲は、ユーザーが最も頻繁に使用するオブジェクトの
リストです。
• 要求でオブジェクトが指定されない場合は、
useSearchScope=true が使用されます。
• useSearchScope=true でユーザーの検索範囲が空白の場合、デ
フォルトの検索範囲を使用してレコードが提案されます。
• 通常は、最初の 10 個のオブジェクトのみがレコードの提案に使用
されます。ただし、システム管理者は、結果が返されるときに常
に考慮されるオブジェクトを割り当てることができます。設定す
れば、最大 15 個のオブジェクトがレコードの提案に使用されます。
オブジェクトの割り当てについての詳細は、「Assign Search Results
Objects to Users (Beta) (検索結果オブジェクトのユーザーへの割り当て
(ベータ))」を参照してください。
• sobject パラメーターで指定されたオブジェクトは、ユーザーの
検索範囲内のオブジェクトよりも優先されます。
• ignoreUnsupportedSObjects パラメーターの値は検索範囲内の
オブジェクトには適用されません。
この例では、検索範囲のみを使用します。
.../search/suggestions?q=Acme&useSearchScope=true
この例では、検索範囲と Account オブジェクトを使用します。
.../search/suggestions?q=Acme&sobject=Account&useSearchScope=true
省略可能。SOQL の WHERE 句と同じ構文に従う検索条件。URL は式を
符号化します。
オブジェクトの句を使用するか、互換性のあるすべてのオブジェクト
の句をグローバルに使用します。オブジェクト固有の句の例:
where
account.where=name%20LIKE%20%27Smith%25%27。グローバルな
句の例: where=name%20LIKE%20%27Smith%25%27。パラメーターは
小文字である必要があります。オブジェクト固有の where 句は、グ
ローバルなwhere句よりも優先されます。このパラメーターは Question
オブジェクトには使用できません。
366
オートコンプリートの結果とインスタント結果により推
奨されたレコードの検索
リファレンス

===== PAGE 377 =====
説明パラメーター
複数のエンティティを指定する場合は、以下の例を参照してくださ
い。この機能はバージョン 38.0 以降で使用できます。
...search/suggestions?q=Smith
&sobject=Account,Contact,KnowledgeArticleVersion,CollaborationGroup,Topic,FeedItem
// Specifies a global where clause (to filter Account and
Contact)
&where=name%20LIKE%20%27Smith%25%27
// Overrides the global where clause for Knowledge Article
(filtering by PublishStatus and Language is required for
KnowledgeArticle)
&knowledgearticleversion.where=PublishStatus='online'+and+language='en_US'
// Overrides the global where clause for Topic
&topic.where=networkid=<1234567891>
// Overrides the global where clause for
CollaborationGroup
&collaborationgroup.where=networkid=<1234567891>
// FeedItem-Question doesn't support where clauses, but
we can filter
the type and networkId&type=question
&networkId==<1234567891>
例
レスポンスボディの例
{
"autoSuggestResults" : [ {
"attributes" : {
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001xx000003DH6WAAW"
},
"Id" : "001xx000003DH6WAAW",
"Name" : "National Utility Service"
}, {
{
"attributes" : {
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001xx000003DHJ4AAO"
},
"Id" : "001xx000003DHJ4AAO",
"Name" : "National Utility Service"
}, {
{
"attributes" : {
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001xx000003DHscAAG"
},
367
オートコンプリートの結果とインスタント結果により推
奨されたレコードの検索
リファレンス

===== PAGE 378 =====
"Id" : "001xx000003DHscAAG",
"Name" : "National Urban Technology Center"
} ],
"hasMoreResults" : false,
"meta" : {
"nameFields" : [ {
"entityApiName" : "Account",
"fieldApiName" : "Name"
} ],
"secondaryFields" : [ ]
}
}
複数オブジェクト要求のレスポンスボディの例
{
"autoSuggestResults" : [ {
"attributes" : {
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001xx000003DMEKAA4"
},
"Id" : "001xx000003DMEKAA4"
"Name" : "Joe Doe Printing"
}, {
{
"attributes" : {
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001xx000003DLjvAAG"
},
"Id" : "001xx000003DLjvAAGO"
"Name" : "Joe Doe Plumbing"
}, {
{
"attributes" : {
"type" : "Contact",
"url" : "/services/data/v60.0/sobjects/Contact/003xx000004U9Y9AAK"
},
"Id" : "003xx000004U9Y9AAK"
"Name" : "John Doe"
} ],
"hasMoreResults" : false,
"meta" : {
"nameFields" : [ {
"entityApiName" : "Account",
"fieldApiName" : "Name"
}, {
"entityApiName" : "Contact",
"fieldApiName" : "Name"
} ],
"secondaryFields" : [ ]
}
}
368
オートコンプリートの結果とインスタント結果により推
奨されたレコードの検索
リファレンス

===== PAGE 379 =====
XML レスポンスボディの例
<?xml version=”1.0” encoding=”UTF-8”?
<suggestions>
<autoSuggestResults type="Account"
url="/services/data/v60.0/sobjects/Account/001xx000003DH6WAAW">
<Id>001xx000003DH6WAAW</Id>
<Name>National Utility Service</Name>
</autoSuggestResults>
<autoSuggestResults type="Account"
url="/services/data/v60.0/sobjects/Account/001xx000003DHJ4AAO">
<Id>001xx000003DHJ4AAO</Id>
<Name>National Utility Service</Name>
</autoSuggestResults>
<autoSuggestResults type="Account"
url="/services/data/v60.0/sobjects/Account/001xx000003DHscAAG">
<Id>001xx000003DHscAAG</Id>
<Name>National Urban Technology Center</Name>
</autoSuggestResults>
<hasMoreResults>true</hasMoreResults>
<meta>
<nameFields>
<entityApiName>Account</entityApiName>
<fieldApiName>Name</fieldApiName>
</nameFields>
<nameFields>
<entityApiName>ContentDocument</entityApiName>
<fieldApiName>Title</fieldApiName>
</nameFields>
</meta>
</suggestions>
Search Suggested Article Title Matches
ユーザーの検索クエリ文字列に一致する Salesforce ナレッジ記事タイトルのリストを返します。ユーザーが検索
を実行する前に、関連する可能性のある記事に直接移動するためのショートカットを提供します。このリソー
スは REST API バージョン 30.0 以降で使用できます。
Salesforce ナレッジが組織で有効になっている必要があります。ユーザーの「記事の参照」権限が有効化されて
いる必要があります。ユーザーが参照する権限を持つデータカテゴリおよび記事タイプに基づいて、ユーザー
がアクセスできる記事のみが推奨記事に含まれます。
Suggest Article Title Matches リソースは、関係する可能性のある記事に関して表示準備のできたデータを返すよう
に設計されています。「a」、「for」、「the」などのストップワードを除いたクエリ文字列全体がタイトルに
含まれる記事も推奨されます。
たとえば、Backpacking for desert を検索すると、記事「Backpacking in the desert」が返されます。
メモ: この例では「Backpacking for desert survival」なども返されますが、タイトルにクエリ文字列のストップ
ワードが含まれる記事は、タイトルにストップワードが含まれない一致記事よりも前に表示されます。
クエリ文字列の末尾にあるストップワードは、検索語として扱われます。
369
Search Suggested Article Title Matchesリファレンス

===== PAGE 380 =====
ワイルドカードは、クエリ文字列の最後のトークンに自動的に付加されます。
メモ: ユーザーの検索クエリに疑問符またはワイルドカードが含まれている場合、それらの記号は URI で
他の特殊文字と同様にクエリ文字列から自動的に削除されます。
返される推奨クエリの数が要求で指定された制限を超えると、hasMoreResults という項目が応答の最後に
含まれます。返される推奨クエリが使用可能な推奨クエリのサブセットのみの場合は値が true になり、そう
でない場合は false になります。
構文
URI
/services/data/vXX.X/search/suggestTitleMatches?q=searchString
&language=articleLanguage&publishStatus=articlePublicationStatus
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
リクエストボディ
不要
要求パラメーター
説明パラメーター
省略可能。目的の記事タイプを示す 3 文字の ID プレフィックス。値ご
とにパラメーター名を繰り返すことで、1 回の REST コールでこのパラ
articleTypes
メーターに複数の値を指定できます。たとえば、
articleTypes=ka0&articleTypes=ka1 です。
省略可能。JSON の対応付けとして表現された、目的の記事のデータカ
テゴリグループの名前とデータカテゴリの名前。このパラメーターに
categories
は複数のデータカテゴリグループとデータカテゴリのペアを指定でき
ます。たとえば、
categories={"Regions":"Asia","Products":"Laptops"} のよ
うにします。URL 内の文字を符号化する必要がある場合があります。
この例の場合、categories=%7B%22Regions%22%3A%22Asia
%22%2C%22Products%22%3A%22Laptops%22%7D です。
省略可能。一致する記事を参照できるチャネル。有効な値は次のとお
りです。
channel
• AllChannels  – ユーザーがアクセス権を持つすべてのチャネルで
参照可能
• App  – 内部 Salesforce ナレッジアプリケーションで参照可能
370
Search Suggested Article Title Matchesリファレンス

===== PAGE 381 =====
説明パラメーター
• Pkb  – 公開知識ベースで参照可能
• Csp  – カスタマーポータルで参照可能
• Prm  – パートナーポータルで参照可能
channel が指定されていない場合、ユーザーの種別によってデフォ
ルト値が決まります。
• ゲストユーザーの Pkb
• カスタマーポータルユーザーの Csp
• パートナーポータルユーザーの Prm
• 他の種別のユーザーの App
channel が指定されている場合、特定の要件により、指定された値
が要求した実際の値にならないことがあります。
• ゲストユーザー、カスタマーポータルユーザー、パートナーポー
タルユーザーの場合、指定された値は各ユーザー種別のデフォル
ト値と一致する必要があります。値が一致しないか、AllChannels
が指定されていると、指定された値が App に置き換えられます。
• ゲストユーザー、カスタマーポータルユーザー、パートナーポー
タルユーザー以外のすべてのユーザーの場合は、次のようになり
ます。
– Pkb、Csp、Prm、または App が指定されていると、指定され
た値が使用されます。
– AllChannels が指定されていると、指定された値が App に置
き換えられます。
必須。ユーザーのクエリの言語。一致する記事が作成された言語を指
定します。
language
省略可能。返される記事の最大数を指定します。指定された制限を超
える推奨記事が存在すると、レスポンスボディの hasMoreResults
プロパティが true になります。
limit
必須。記事の公開状況。有効な値は次のとおりです。publishStatus
• Draft  – Salesforce ナレッジに公開されていない記事。
• Online  – Salesforce ナレッジに公開されている記事。
• Archived  – [アーカイブ済み記事] ビューで参照可能な公開されて
いない記事。
必須。適切に URL 符号化された、ユーザーの検索クエリ文字列。ユー
ザーの検索クエリ文字列が最小長要件 (中国語、日本語、韓国語の場
q
合は 1 文字、その他の言語の場合は 3 文字) を満たしている場合にの
371
Search Suggested Article Title Matchesリファレンス

===== PAGE 382 =====
説明パラメーター
み、推奨クエリが返されます。クエリ文字列が最大長である 250 文字
を超えると、エラーが返されます。
省略可能。返される記事のトピック。たとえば、
topics=outlook&topics=email です。
topics
省略可能。返される記事の検証状況。validationStatus
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/search/suggestTitleMatches?
q=orange+banana&language=en_US&publishStatus=Online -H "Authorization: Bearer token"
レスポンスボディの例
{
"autoSuggestResults" : [ {
"attributes" : {
"type" : "KnowledgeArticleVersion",
"url" : "/services/data/v60.0/sobjects/KnowledgeArticleVersion/ka0D00000004CcQ"
},
"Id" : "ka0D00000004CcQ",
"UrlName" : "orange-banana",
"Title" : "orange banana",
"KnowledgeArticleId" : "kA0D00000004Cfz"
} ],
"hasMoreResults" : false
}
Search Suggested Queries
他のユーザーが Salesforce ナレッジで実行した検索に一致するユーザーのクエリ文字列テキストに基づいて、提
案する検索のリストを返します。ユーザーが検索を実行する前に、検索の有効性を高める手段を提供します。
このリソースは REST API バージョン 30.0 以降で使用できます。
Salesforce ナレッジが組織で有効になっている必要があります。
クエリ文字列テキストと正確に一致する場合にのみ、クエリが推奨されます。クエリ内では、テキスト文字列
がプレフィックスである必要があります。テキスト文字列が単語に含まれる場合は、一致とみなされません。
たとえば、テキスト文字列が app の場合、apple bananaおよび banana applesという推奨クエリは返されますが、
pineapple は返されません。
返される推奨クエリの数が要求で指定された制限を超えると、hasMoreResults という項目が応答の最後に
含まれます。返される推奨クエリが使用可能な推奨クエリのサブセットのみの場合は値が true になり、そう
でない場合は false になります。
372
Search Suggested Queriesリファレンス

===== PAGE 383 =====
ユーザーの検索クエリに疑問符またはワイルドカードが含まれている場合、それらの記号は URI でクエリ文字
列から自動的に削除されます。
構文
URI
/services/data/vXX.X/search/suggestSearchQueries?q=searchString
&language=languageOfQuery
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
リクエストボディ
不要
要求パラメーター
説明パラメーター
省略可能。記事を参照できる Salesforce ナレッジチャネルを指定しま
す。有効な値は次のとおりです。
channel
• AllChannels  – ユーザーがアクセス権を持つすべてのチャネルで
参照可能
• App  – 内部 Salesforce ナレッジアプリケーションで参照可能
• Pkb  – 公開知識ベースで参照可能
• Csp  – カスタマーポータルで参照可能
• Prm  – パートナーポータルで参照可能
channel が指定されていない場合、ユーザーの種別によってデフォ
ルト値が決まります。
• ゲストユーザーの Pkb
• カスタマーポータルユーザーの Csp
• パートナーポータルユーザーの Prm
• 他の種別のユーザーの App
channel が指定されている場合、特定の要件により、指定された値
が要求した実際の値にならないことがあります。
• ゲストユーザー、カスタマーポータルユーザー、パートナーポー
タルユーザーの場合、指定された値は各ユーザー種別のデフォル
ト値と一致する必要があります。値が一致しないか、AllChannels
が指定されていると、指定された値が App に置き換えられます。
373
Search Suggested Queriesリファレンス

===== PAGE 384 =====
説明パラメーター
• ゲストユーザー、カスタマーポータルユーザー、パートナーポー
タルユーザー以外のすべてのユーザーの場合は、次のようになり
ます。
– Pkb、Csp、Prm、または App が指定されていると、指定され
た値が使用されます。
– AllChannels が指定されていると、指定された値が App に置
き換えられます。
必須。ユーザーのクエリの言語。language
省略可能。返される推奨検索の最大数を指定します。指定された制限
を超える推奨クエリが存在すると、レスポンスボディの
hasMoreResults プロパティが true になります。
limit
必須。適切に URL 符号化された、ユーザーの検索クエリ文字列。ユー
ザーの検索クエリ文字列が最小長要件 (中国語、日本語、韓国語の場
q
合は 1 文字、その他の言語の場合は 3 文字) を満たしている場合にの
み、推奨クエリが返されます。クエリ文字列が最大長である 250 文字
を超えると、エラーが返されます。
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/search/suggestSearchQueries?
q=app&language=en_US -H "Authorization: Bearer token"
レスポンスボディの例
{
"autoSuggestResults" : [ {
"0" : "apple",
"1" : "apple banana",
} ],
"hasMoreResults" : false
}
Salesforce アンケート翻訳リソース
REST API を使用して、アンケート項目を翻訳し、翻訳されたアンケート項目を表示、更新、または削除します。
アンケート項目の翻訳された値は、フロー項目に保存されます。
次のアンケート項目は、翻訳可能です。
• アンケート名
374
Salesforce アンケート翻訳リソースリファレンス

===== PAGE 385 =====
• 一時停止メッセージ
• 歓迎メッセージ
• 質問
• 回答の選択肢とランキング項目
• 感謝のメッセージ
このセクションの内容:
アンケート項目の翻訳を追加または変更する
アンケート項目が、翻訳可能な場合または特定の言語にすでに翻訳されている場合は、アンケート項目で、
翻訳された値を追加または変更できます。このリソースは REST API バージョン 48.0 以降で使用できます。
複数のアンケート項目の 1 つ以上の言語に翻訳された値を追加または更新する
1 つ以上のアンケート項目が、翻訳可能な場合、またはすでに翻訳されている場合は、アンケート項目で、
翻訳可能な言語を使用して、翻訳された値を追加または更新できます。このリソースは REST API バージョン
48.0 以降で使用できます。
アンケート項目の翻訳された値を削除する
アンケート項目が特定の言語にすでに翻訳されている場合は、アンケート項目で、翻訳された値を削除で
きます。このリソースは REST API バージョン 48.0 以降で使用できます。
複数のアンケート項目の 1 つ以上の言語に翻訳された値を削除する
アンケート項目が 1 つ以上の言語にすでに翻訳されている場合は、複数のアンケート項目の翻訳された値
を削除できます。このリソースは REST API バージョン 48.0 以降で使用できます。
アンケート項目の翻訳された値を取得する
アンケート項目が特定の言語にすでに翻訳されている場合は、このリソースを使用してアンケート項目の
翻訳された値を取得できます。このリソースは REST API バージョン 48.0 以降で使用できます。
複数のアンケート項目の 1 つ以上の言語に翻訳された値を取得する
アンケート項目が 1 つ以上の言語にすでに翻訳されている場合は、複数のアンケート項目の翻訳された値
を表示できます。このリソースは REST API バージョン 48.0 以降で使用できます。
アンケート項目の翻訳を追加または変更する
アンケート項目が、翻訳可能な場合または特定の言語にすでに翻訳されている場合は、アンケート項目で、翻
訳された値を追加または変更できます。このリソースは REST API バージョン 48.0 以降で使用できます。
メモ: この URI は、フロープロセス種別の Survey にのみ使用できます。
構文
URI
/services/data/vXX.X/localizedvalue/record/developerName/language
形式
JSON
375
アンケート項目の翻訳を追加または変更するリファレンス

===== PAGE 386 =====
HTTP のメソッド
POST
認証
Authorization: Bearer token
リクエストボディの JSON の例
{
"value": "China"
}
要求パラメーター
説明パラメーター
省略可能。フロー項目の API 参照名。developerName
フロー項目の省略可能な翻訳された言語。language
必須。フロー項目の翻訳された値。value
応答パラメーター
説明パラメーター
フロー項目を翻訳したユーザーの ID。createdBy
フロー項目が翻訳された日時。createdDate
フロー項目の API 参照名。developerName
フロー項目が翻訳された言語。language
フロー項目の翻訳された値。value
フロー項目が変更されているかどうかを示します。isOutofDate
例
{
"createdBy": "005xxx",
"createdDate": "2018-09-14T00:10:30Z",
"developerName": "Flow.Flow.MyFlow.1.Choice.Choice_1_Master.InputLabel",
"language": "zh_CN",
"value": "中國",
"isOutOfDate": true
}
376
アンケート項目の翻訳を追加または変更するリファレンス

===== PAGE 387 =====
複数のアンケート項目の 1 つ以上の言語に翻訳された値を追加または
更新する
1 つ以上のアンケート項目が、翻訳可能な場合、またはすでに翻訳されている場合は、アンケート項目で、翻
訳可能な言語を使用して、翻訳された値を追加または更新できます。このリソースは REST API バージョン 48.0
以降で使用できます。
メモ: この URI は、フロープロセス種別の Survey にのみ使用できます。
構文
URI
/services/data/vXX.X/localizedvalue/records/upsert
形式
JSON
HTTP のメソッド
POST
リクエストボディの JSON の例
[
{
"developerName": "Flow.Flow.MyFlow.1.Choice.Choice_1_Master.InputLabel",
"language": "en_US",
"value": "China"
},
{
"developerName": "Flow.Flow.MyFlow.1.Choice.Choice_1_Master.InputLabel",
"language": "zh_CN",
"value": "中國"
}
]
要求パラメーター
説明パラメーター
必須。フロー項目の API 参照名。developerName
必須。フロー項目の翻訳された言語。language
必須。フロー項目の新規または更新された値。value
応答パラメーター
説明パラメーター
フロー項目を翻訳したユーザーの ID。createdBy
フロー項目が翻訳された日時。createdDate
377
複数のアンケート項目の 1 つ以上の言語に翻訳された値
を追加または更新する
リファレンス

===== PAGE 388 =====
説明パラメーター
フロー項目の API 参照名。developerName
フロー項目が翻訳された言語。language
フロー項目の更新された値。value
フロー項目が変更されているかどうかを示します。isOutofDate
例
[
{
"createdBy": "005xxx",
"createdDate": "2018-09-14T00:10:30Z",
"developerName": "Flow.Flow.MyFlow.1.Choice.Choice_1_Master.InputLabel",
"language": "en_US",
"value": "China",
"isOutOfDate": false
},
{
"createdBy": "005xxx",
"createdDate": "2018-09-14T00:10:30Z",
"developerName": "Flow.Flow.MyFlow.1.Choice.Choice_1_Master.InputLabel",
"language": "zh_CN",
"value": "中國",
"isOutOfDate": false
}
]
アンケート項目の翻訳された値を削除する
アンケート項目が特定の言語にすでに翻訳されている場合は、アンケート項目で、翻訳された値を削除できま
す。このリソースは REST API バージョン 48.0 以降で使用できます。
メモ: この URI は、フロープロセス種別の Survey にのみ使用できます。
構文
URI
/services/data/vXX.X/localizedvalue/record/developerName/language
形式
JSON
HTTP のメソッド
DELETE
378
アンケート項目の翻訳された値を削除するリファレンス

===== PAGE 389 =====
要求パラメーター
説明パラメーター
フロー項目の API 参照名。例:
Flow.Flow.MyFlow.1.Choice.Choice_1_Master.InputLabel
developerName
翻訳された項目の言語。可能な値は次のとおりです。language
• da
• nl_NL
• fi
• fr
• de
複数のアンケート項目の 1 つ以上の言語に翻訳された値を削除する
アンケート項目が 1 つ以上の言語にすでに翻訳されている場合は、複数のアンケート項目の翻訳された値を削
除できます。このリソースは REST API バージョン 48.0 以降で使用できます。
メモ: この URI は、フロープロセス種別の Survey にのみ使用できます。
構文
URI
/services/data/vXX.X/localizedvalue/records/delete
形式
JSON
HTTP のメソッド
POST
リクエストボディの JSON の例
[
{
"developerName": "Flow.Flow.MyFlow.1.Choice.Choice_1_Master.InputLabel",
"language": "en_US"
},
{
"developerName": "Flow.Flow.MyFlow.1.Choice.Choice_1_Master.InputLabel",
"language": "zh_CN"
}
]
要求パラメーター
説明パラメーター
必須。フロー項目の API 参照名。developerName
379
複数のアンケート項目の 1 つ以上の言語に翻訳された値
を削除する
リファレンス

===== PAGE 390 =====
説明パラメーター
必須。フロー項目が翻訳された言語。language
アンケート項目の翻訳された値を取得する
アンケート項目が特定の言語にすでに翻訳されている場合は、このリソースを使用してアンケート項目の翻訳
された値を取得できます。このリソースは REST API バージョン 48.0 以降で使用できます。
メモ: この URI は、フロープロセス種別の Survey にのみ使用できます。
構文
URI
/services/data/vXX.X/localizedvalue/record/developerName/language
形式
JSON
HTTP のメソッド
GET
認証
Authorization: Bearer token
リクエストボディ
なし
要求のパラメーター
説明パスパラメーター
必須。フロー項目の API 参照名。例:
Flow.Flow.MyFlow.1.Choice.Choice_1_Master.InputLabel
developerName
必須。翻訳された項目の言語。可能な値は次のとおりです。language
• da
• nl_NL
• fi
• fr
• de
応答パラメーター
説明パラメーター
フロー項目を翻訳したユーザーの ID。createdBy
フロー項目が翻訳された日時。createdDate
380
アンケート項目の翻訳された値を取得するリファレンス

===== PAGE 391 =====
説明パラメーター
フロー項目の API 参照名。developerName
フロー項目が翻訳された言語。language
フロー項目の翻訳された値。value
フロー項目が変更されているかどうかを示します。isOutofDate
例
{
"createdBy": "005xxx",
"createdDate": "2018-09-14T00:10:30Z",
"developerName": "Flow.Flow.MyFlow.1.Choice.Choice_1_Master.InputLabel",
"language": "zh_CN",
"value": "中國",
"isOutOfDate": true
}
複数のアンケート項目の 1 つ以上の言語に翻訳された値を取得する
アンケート項目が 1 つ以上の言語にすでに翻訳されている場合は、複数のアンケート項目の翻訳された値を表
示できます。このリソースは REST API バージョン 48.0 以降で使用できます。
メモ: この URI は、フロープロセス種別の Survey にのみ使用できます。
構文
URI
/services/data/vXX.X/localizedvalue/records/get
形式
JSON
HTTP のメソッド
POST
リクエストボディの JSON の例
[
{
"developerName": "Flow.Flow.MyFlow.1.Choice.Choice_1_Master.InputLabel",
"language": "en_US"
},
{
"developerName": "Flow.Flow.MyFlow.1.Choice.Choice_1_Master.InputLabel",
"language": "zh_CN"
}
]
381
複数のアンケート項目の 1 つ以上の言語に翻訳された値
を取得する
リファレンス

===== PAGE 392 =====
要求パラメーター
説明パラメーター
必須。フロー項目の API 参照名。developerName
必須。フロー項目が翻訳された言語。language
応答パラメーター
説明パラメーター
フロー項目を翻訳したユーザーの ID。createdBy
フロー項目が翻訳された日時。createdDate
フロー項目の API 参照名。developerName
フロー項目が翻訳された言語。language
フロー項目の翻訳された値。value
フロー項目が変更されているかどうかを示します。isOutofDate
例
[
{
"createdBy": "005xxx",
"createdDate": "2018-09-14T00:10:30Z",
"developerName": "Flow.Flow.MyFlow.1.Choice.Choice_1_Master.InputLabel",
"language": "en_US",
"value": "China",
"isOutOfDate": true
},
{
"createdBy": "005xxx",
"createdDate": "2018-09-14T00:10:30Z",
"developerName": "Flow.Flow.MyFlow.1.Choice.Choice_1_Master.InputLabel",
"language": "zh_CN",
"value": "中國",
"isOutOfDate": true
}
]
382
複数のアンケート項目の 1 つ以上の言語に翻訳された値
を取得する
リファレンス

===== PAGE 393 =====
Tabs
ユーザーが [すべてのタブ] ([+]) タブカスタマイズ機能を使用してタブを非表示にしているかどうかに関係な
く、ログインユーザーが使用できるすべてのタブ (Lightning ページタブを含む) のリストを返します。このリ
ソースは REST API バージョン 31.0 以降で使用できます。
このセクションの内容:
タブの取得
ユーザーが [すべてのタブ] ([+]) タブカスタマイズ機能を使用してタブを非表示にしているかどうかに関係
なく、ログインユーザーが使用できるすべてのタブ (Lightning ページタブを含む) のリストを取得します。こ
のリソースは REST API バージョン 31.0 以降で使用できます。
タブを使用したヘッダーの返送
Tabs リソースに GET 要求をしたときに返されるヘッダーのみを返します。リソースのコンテンツを取得す
る前に、ヘッダー値を確認できます。このリソースは REST API バージョン 31.0 以降で使用できます。
タブの取得
ユーザーが [すべてのタブ] ([+]) タブカスタマイズ機能を使用してタブを非表示にしているかどうかに関係な
く、ログインユーザーが使用できるすべてのタブ (Lightning ページタブを含む) のリストを取得します。このリ
ソースは REST API バージョン 31.0 以降で使用できます。
構文
URI
/services/data/vXX.X/tabs/
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
リクエストボディ
なし
要求のパラメーター
なし
例
リクエストの例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/tabs -H "Authentication:
Bearer token"
383
Tabsリファレンス

===== PAGE 394 =====
レスポンスボディの例
これは、[取引先] タブを表す部分的なコードサンプルです。
[...,
"colors" : [ {
"color" : "6f7ccb",
"context" : "primary",
"theme" : "theme4"
}, {
"color" : "236FBD",
"context" : "primary",
"theme" : "theme3"
} ],
"custom" : false,
"iconUrl" : "https://MyDomainName.my.salesforce.com/img/icon/accounts32.png",
"icons" : [ {
"contentType" : "image/png",
"height" : 32,
"theme" : "theme3",
"url" : "https://MyDomainName.my.salesforce.com/img/icon/accounts32.png",
"width" : 32
}, {
"contentType" : "image/png",
"height" : 16,
"theme" : "theme3",
"url" : "https://MyDomainName.my.salesforce.com/img/icon/accounts16.png",
"width" : 16
}, {
"contentType" : "image/svg+xml",
"height" : 0,
"theme" : "theme4",
"url" : "https://MyDomainName.my.salesforce.com/img/icon/t4/standard/account.svg",
"width" : 0
}, {
"contentType" : "image/png",
"height" : 60,
"theme" : "theme4",
"url" : "https://MyDomainName.my.salesforce.com/img/icon/t4/standard/account_60.png",
"width" : 60
}, {
"contentType" : "image/png",
"height" : 120,
"theme" : "theme4",
"url" :
"https://MyDomainName.my.salesforce.com/img/icon/t4/standard/account_120.png",
"width" : 120
} ],
"label" : "Accounts",
"miniIconUrl" : "https://MyDomainName.my.salesforce.com/img/icon/accounts16.png",
"name" : "standard-Account",
"sobjectName" : "Account",
384
タブの取得リファレンス

===== PAGE 395 =====
"url" : "https://MyDomainName.my.salesforce.com/001/o",
...]
タブを使用したヘッダーの返送
Tabs リソースに GET 要求をしたときに返されるヘッダーのみを返します。リソースのコンテンツを取得する前
に、ヘッダー値を確認できます。このリソースは REST API バージョン 31.0 以降で使用できます。
構文
URI
/services/data/vXX.X/tabs/
形式
JSON、XML
HTTP のメソッド
HEAD
認証
Authorization: Bearer token
リクエストボディ
なし
要求のパラメーター
なし
例
すべてのタブに対する要求のヘッダーを返す
curl -X HEAD --head https://MyDomainName.my.salesforce.com/services/data/v60.0/tabs -H
"Authorization: Bearer token"
Themes
Salesforce アプリケーションのテーマで使用するアイコンと色のリストを取得します。テーマ情報は、Salesforce
UI のアイコンと色を使用する組織内のオブジェクトに提供されます。このリソースは REST API バージョン 29.0
以降で使用できます。
If-Modified-Since ヘッダーは、このリソースでは EEE, dd MMM yyyy HH:mm:ss z という日付形式で使
用できます。このヘッダーが使用される場合、指定の日付以降にオブジェクトメタデータが変更されていない
と、レスポンスボディなしで 304 Not Modified 状況コードが返されます。
構文
URI
/services/data/vXX.X/theme
385
タブを使用したヘッダーの返送リファレンス

===== PAGE 396 =====
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
リクエストボディ
なし
要求パラメーター
なし
応答データ
テーマ項目の配列。各テーマ項目には次の項目が含まれます。
説明型名前
テーマの色の配列。arraycolors
テーマアイコンの配列。arrayicons
テーマの色とアイコンが関連付けられるオブジェクトの名前。stringname
各テーマの色には次の項目が含まれます。
説明型名前
Web 色の RGB 形式で示される色 (00FF00 など)。stringcolor
オブジェクトでその色がメインの色 (primary) であるかどうかを決
定する色のコンテキスト。
stringcontext
関連付けられたテーマ。可能な値には、次のものがあります。stringtheme
• theme2  — Spring '10 より前に使用されていた「Salesforce Classic
2005 ユーザーインターフェースのテーマ」という名前のテー
マ
• theme3  — Spring '10 で導入された「Salesforce Classic 2010 ユー
ザーインターフェースのテーマ」という名前のテーマ
• theme4  — Winter '14 (Lightning Experience では Winter '16) に導入さ
れたモバイルタッチスクリーンバージョンの Salesforce テーマ
• custom  — カスタムアイコンに関連付けられたテーマ
各テーマアイコンには次の項目が含まれます。
386
Themesリファレンス

===== PAGE 397 =====
説明型名前
アイコンのコンテンツタイプは、「image/png」などです。stringcontentType
アイコンの高さ (ピクセル単位)。アイコンのコンテンツタイプが
SVG タイプである場合、高さと幅の値は使用されません。
numberheight
関連付けられたテーマ。可能な値には、次のものがあります。stringtheme
• theme2  — Spring '10 より前に使用されていた「Salesforce Classic
2005 ユーザーインターフェースのテーマ」という名前のテー
マ
• theme3  — Spring '10 で導入された「Salesforce Classic 2010 ユー
ザーインターフェースのテーマ」という名前のテーマ
• theme4  — Winter '14 (Lightning Experience では Winter '16) に導入さ
れたモバイルタッチスクリーンバージョンの Salesforce テーマ
• custom  — カスタムアイコンに関連付けられたテーマ
このアイコンの完全修飾 URL。stringurl
アイコンの幅 (ピクセル単位)。アイコンのコンテンツタイプが
SVG タイプである場合、高さと幅の値は使用されません。
numberwidth
例
{
"themeItems" : [
{
"name" : "Merchandise__c",
"icons" : [
{
"contentType" : "image/png",
"width" : 32,
"url" : "https://MyDomainName.my.salesforce.com/img/icon/computer32.png",
"height" : 32,
"theme" : "theme3"
},
{
"contentType" : "image/png",
"width" : 16,
"url" : "https://MyDomainName.my.salesforce.com/img/icon/computer16.png",
"height" : 16,
"theme" : "theme3"
} ],
"colors" : [
{
"context" : "primary",
"color" : "6666CC",
"theme" : "theme3"
},
387
Themesリファレンス
