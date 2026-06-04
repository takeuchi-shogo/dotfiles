# リファレンス前半: Versions・制限・Describe・sObject 系・レイアウト・アクション・リストビュー等

> 出典: Salesforce『REST API 開発者ガイド』日本語版 (api_rest.pdf, 2026-03-31 生成, Spring '26 相当)
> PDF ページ 140–331。pypdf による自動抽出テキストのため、表組みのレイアウトが崩れている場合がある。

## 収録セクション

- リファレンス (PAGE 140)
  - Versions (PAGE 151)
  - Resources by Version (PAGE 151)
  - 制限 (PAGE 152)
  - Describe Global (PAGE 158)
  - sObject Basic Information (PAGE 159)
  - sObject Describe (PAGE 161)
  - sObject Get Deleted (PAGE 162)
  - sObject Get Updated (PAGE 164)
  - sObject Named Layouts (PAGE 165)
  - sObject Rows (PAGE 166)
  - sObject Rows by External ID (PAGE 171)
  - sObject Blob Get (PAGE 177)
  - sObject ApprovalLayouts (PAGE 177)
  - sObject Single Approval Process (PAGE 179)
  - sObject CompactLayouts (PAGE 181)
  - sObject Layouts (PAGE 187)
  - 複数のレコードタイプを持つオブジェクトの sObject Layouts (PAGE 189)
  - sObject Global Publisher Layouts (PAGE 192)
  - sObject PlatformAction (PAGE 194)
  - sObject Quick Actions (PAGE 195)
  - 特定の sObject Quick Actions (PAGE 197)
  - sObject Quick Action の詳細 (PAGE 199)
  - sObject Quick Action のデフォルト値 (PAGE 201)
  - sObject Quick Action の ID 別デフォルト値 (PAGE 202)
  - sObject Rich Text Image Get (PAGE 204)
  - sObject Relationships (PAGE 206)
  - sObjects Suggested Articles (PAGE 210)
  - sObjects Suggested Articles by ID (PAGE 212)
  - sObject User Password (PAGE 214)
  - sObject セルフサービスユーザーのパスワード (PAGE 217)
  - Platform Event Schema by Event Name (PAGE 221)
  - スキーマ ID によるプラットフォームイベントスキーマ (PAGE 226)
  - appMenu の種別の取得 (PAGE 232)
  - AppMenu Items (PAGE 233)
  - AppMenu Mobile Items (PAGE 234)
  - Compact Layouts (PAGE 238)
  - Consent (PAGE 241)
  - Consent Write (PAGE 259)
  - 記述用の組み込みサービス設定 (PAGE 262)
  - Invocable Actions (PAGE 265)
  - Invocable Actions Custom (PAGE 267)
  - Invocable Actions Standard (PAGE 270)
  - List View Basic Information (PAGE 273)
  - List View Describe (PAGE 274)
  - List View Results (PAGE 277)
  - オブジェクトのリストビュー (PAGE 287)
  - REST API を使用してナレッジをサポートする (PAGE 289)
  - パラメーター化された検索 (PAGE 303)
  - Portability (PAGE 315)
  - Process Approvals (PAGE 318)
  - Process Rules (PAGE 321)
  - sObject のプロセスルール (PAGE 324)
  - sObject のプロセスルールのリスト (PAGE 326)
  - Product Schedules (PAGE 329)

---

===== PAGE 140 =====
第 4 章 リファレンス
次の表に、API でサポートされている REST リソースをリストし、それぞれのリソースについて簡単に説明しま
す。
それぞれの場合で、リソースの URI は、ベース URI (https://MyDomainName.my.salesforce.com) に続きま
す。
たとえば、バージョン 60.0 の Account オブジェクトに関する基本情報を取得する場合、
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account を使用しま
す。
sObject リソースでアクセスする標準オブジェクトとカスタムオブジェクトについての詳細は、『Salesforce プ
ラットフォームのオブジェクトリファレンス』を参照してください。
これらのリソースの一部は、対応するパッケージがインストールされているか、対応する機能が有効になって
いる場合にのみ使用できます。
メモ: 要求 URI の一部分には、ID のように大文字と小文字が区別される部分があります。他のオブジェク
ト名や項目名などの URI の部分は大文字と小文字が区別されません。要求が正常に処理されない場合は、
URI をこのガイドのリファレンス情報や例と比較して、大文字と小文字が正しく入力されているかどうか
を確認してください。
URI および説明リソース名
/services/dataVersions
バージョン、表示ラベル、および各バージョンのルートへのリンクなど、現在使
用可能な各 Salesforce バージョンの概要情報をリストします。
/services/data/vXX.XResources by Version
リソース名および URI を含む、指定された API バージョンで使用可能なリソースを
リストします。
/services/data/vXX.X/actions/standardInvocable Actions
/services/data/vXX.X/actions/custom
アクションを使用してアプリケーションに機能を追加します。Chatter への投稿や
メールの送信などの標準アクションから選択するか、会社のニーズに基づいてア
クションを作成します。
/services/data/vXX.X/analyticsAnalytics
(Reports および Dashboards
REST API にアクセス)
Reports および Dashboards REST API リソースにアクセスします。『Salesforce Reports and
Dashboards REST API Developer Guide (Salesforce Reports および Dashboards REST API 開発者
ガイド)』を参照してください。
130

===== PAGE 141 =====
URI および説明リソース名
/services/data/vXX.X/appMenu/Get AppMenu Types
Salesforce アプリケーションのドロップダウンメニューのアプリケーションメニュー
種別にアクセスします。
/services/data/vXX.X/appMenu/AppSwitcherAppMenu Items
アプリケーションメニュー項目には、Salesforce アプリケーションのドロップダウ
ンメニューからアクセスします。
/services/data/vXX.X/appMenu/Salesforce1/AppMenu Mobile Items
アプリケーションメニュー項目に、Android および iOS の Salesforce モバイルアプリ
ケーションおよびモバイル Web のナビゲーションメニューからアクセスします。
/services/data/vXX.X/asset-managementAsset Management
Makes により、ライフサイクル管理される納入商品のデータを営業担当や取引先
担当が Lightning Experience で表示できるようにします。『Connect REST API 開発者ガ
イド』の「顧客の納入商品ライフサイクル管理」を参照してください。
/services/data/vXX.X/async-queriesAsync Queries
非同期で処理する SOQL クエリを送信します。次を参照してください。
• 『Connect REST API 開発者ガイド』の「非同期クエリ」。
• 『Salesforce セキュリティガイド』の「リアルタイムイベント監視での非同期
SOQL の使用」。
• 詳細は、『Big Objects Implementation Guide (Big Object 実装ガイド)』の「Async SOQL
Use Case (非同期 SOQL の使用事例)」。
/services/data/vXX.X/chatterChatter
(Connect REST API) Connect REST API で機能にアクセスします。『Connect REST API 開発者ガイド』を参照
してください。
/services/data/vXX.X/commerceCommerce
(注文実行 REST API) 注文実行 REST API で機能にアクセスします。『Place Order REST API Developer Guide (注
文実行 REST API 開発者ガイド)』を参照してください。
/services/data/vXX.X/compactLayouts?q=objectListCompact Layouts
複数のオブジェクトの Compact Layouts のリストを返します。
/services/data/vXX.X/compositeComposite
一連の REST API 要求を 1 回の POST 要求で実行するか、他の複合リソースのリスト
を GET 要求で取得します。
131
リファレンス

===== PAGE 142 =====
URI および説明リソース名
/services/data/vXX.X/composite/batchComposite Batch
1 回の要求で最大 25 個のサブ要求を実行します。
/services/data/vXX.X/composite/graphUsing Composite Graphs
拡張された方法で Composite 要求を実行できます。
/services/data/vXX.X/composite/treesObject Tree
指定されたタイプのルートレコードを持つ 1 つ以上の sObject ツリーを作成しま
す。sObject ツリーは、同じルートレコードを持つネストされた親-子レコードの
コレクションです。
/services/data/vXX.X/composite/sobjectssObject Collections
1 つの要求で複数のレコードに対してアクションを実行します。
/services/data/vXX.X/connectConnect REST API
Connect REST API で機能にアクセスします。『Connect REST API 開発者ガイド』を参照
してください。
/services/data/vXX.X/connect/financialservicesFinancial Services
Financial Services オブジェクトにアクセスします。『Financial Services Cloud 開発者ガ
イド』を参照してください。
/services/data/vXX.X/connect/health/care-servicesHealth Cloud
Health Cloud オブジェクトにアクセスします。『Health Cloud Developer Guide (Health
Cloud 開発者ガイド)』を参照してください。
/services/data/vXX.X/connect/manufacturingManufacturing
Manufacturing Cloud オブジェクトにアクセスします。『Manufacturing Cloud Developer
Guide (Manufacturing Cloud 開発者ガイド)』を参照してください。
/services/data/vXX.X/connect/object-detectionConsumer Goods
/services/data/vXX.X/connect/visit/recommendations
Consumer Goods ビジネス API にアクセスします。『Consumer Goods Cloud 開発者ガイ
ド』を参照してください。
/services/data/vXX.X/consentConsent
ユーザーの同意設定を追跡します。
/services/data/vXX.X/contact-tracingContact Tracing
132
リファレンス

===== PAGE 143 =====
URI および説明リソース名
健全性コンタクトを追跡します。『Emergency Response Management for Public Health
Developer Guide (公衆衛生向け緊急時対応管理システム開発者ガイド)』を参照して
ください。
/services/data/vXX.X/dedupeDedupe
重複リソース、ジョブ定義、およびジョブをリストします。『Connect REST API 開
発者ガイド』を参照してください。
/services/data/vXX.X/dominoDomino
組織内でのみ使用します。
/services/data/vXX.X/eclairEclair
(geodata) geodata の定義にアクセスします。『Analytics REST API 開発者ガイド』の「Charts Geodata
リソース」を参照してください。
/services/data/vXX.X/emailConnectEmail Connect
組織内でのみ使用します。
/services/data/vXX.X/event/eventSchema/schemaIdPlatform Event Schema by
Schema ID
スキーマ名のプラットフォームイベントの定義を JSON 形式で取得します。この
リソースは REST API バージョン 40.0 以降で使用できます。
/services/data/vXX.X/foldersFolders
Analytics Folders API を使用して、レポートフォルダーとダッシュボードフォルダー
を操作します。『Reports and Dashboards REST API Developer Guide (Reports および Dashboards
REST API 開発者ガイド)』の「Folders (フォルダー)」を参照してください。
/services/data/vXX.X/jobsJobs
(Bulk API 2.0) Bulk API 2.0 でジョブにアクセスします。『Bulk API 2.0 および Bulk API 開発者ガイド』
を参照してください。
/services/data/vXX.X/jsonxformjsonxform
(Analytics REST API) Tableau テンプレートのルールの結果をテストします。『Analytics テンプレート開
発者ガイド』の「Rules Testing with jsonxform/transformation endpoint
(jsonxform/transformation エンドポイントでテストするルール)」を参照してくださ
い。
/services/data/vXX.X/knowledgeManagementKnowledge Management
Salesforce ナレッジ機能にアクセスします。『ナレッジ開発者ガイド』を参照して
ください。
133
リファレンス

===== PAGE 144 =====
URI および説明リソース名
/services/data/vXX.X/licensingLicensing
組織内でのみ使用します。
/services/data/vXX.X/limitsLimits
組織内の制限に関する情報をリストします。このリソースでは、各制限の最大割
り当てと使用量に基づく残りの割り当てが返されます。
/services/data/vXX.X/limits/recordCountRecord Count
組織内のオブジェクトレコード件数に関する情報をリストします。
/services/data/vXX.X/localizedvalueSalesforce Surveys Translation
Resources
REST API を使用して、アンケート項目を翻訳し、翻訳されたアンケート項目を表
示、更新、または削除します。アンケート項目の翻訳された値は、フロー項目に
保存されます。
/services/data/vXX.X/metadataMetadata
Metadata API で機能にアクセスします。『メタデータ API 開発者ガイド』を参照し
てください。
/services/data/vXX.X/parameterizedSearch/?q=searchStringParameterized Search
SOSL 句の代わりにパラメーターを使用して簡単な REST 検索を実行します。GET メ
ソッドで URI にパラメーターを指定します。または POST メソッドを使用してリク
エストボディに複雑な検索を作成します。
/services/data/vXX.X/paymentsPayments
組織内でのみ使用します。
/services/data/vXX.X/process/approvalsProcess Approvals
すべての承認プロセスにアクセスします。特定のレコードが承認プロセスをサ
ポートしていて、承認プロセスがすでに定義されている場合、そのレコードを送
信するためにも使用できます。現在のユーザーが割り当てられた承認者である場
合、レコードを承認および却下できます。
/services/data/vXX.X/process/rulesProcess Rules
すべての有効なワークフロールールのリストにアクセスします。レコードまたは
項目を取得するには、GET メソッドを使用します。HTTP ヘッダーの情報を取得す
るには、HEAD メソッドを使用します。すべての有効なワークフロールールをト
リガーするには、POST メソッドを使用します。
/services/data/vXX.X/query/?q=soqlQuery
(SOQL)
134
リファレンス

===== PAGE 145 =====
URI および説明リソース名
指定された SOQL クエリを実行します。
/services/data/vXX.X/queryAll/?q=soqlQueryAll
(SOQL) 指定された SOQL クエリを実行します。結果には削除されたレコード、マージさ
れたレコード、およびアーカイブ済みレコードが含まれる場合があります。
/services/data/vXX.X/quickActionsQuick Actions
グローバルクイックアクションとその種別のリスト、および Chatter フィードに表
示されるカスタム項目とオブジェクトを返します。
/services/data/vXX.X/recentRecently Viewed Items
現在のユーザーが表示または参照した、最近参照された項目を取得します。
/services/data/vXX.X/scheduling/Salesforce Scheduler Resources
Scheduler REST API にアクセスし、作業種別グループおよびサービステリトリーに基
づいて、予定の時間枠または利用可能なサービスリソースを取得します。
/services/data/vXX.X/search/?q=soslSearch
(SOSL) 指定された SOSL 検索を実行します。検索文字列は URL 符号化されている必要があ
ります。
/services/data/vXX.X/search/scopeOrderSearch Scope and Order
ログインユーザーのデフォルトのグローバル検索範囲内にあるオブジェクトの順
序付きリストを返します。グローバル検索は、操作するオブジェクトとそれらを
操作する頻度を追跡し、それに基づいて検索結果を編成します。最もよく使用さ
れるオブジェクトは、リストの最上部に表示されます。
/services/data/vXX.X/search/suggestSearchQueries?q=searchString
&language=languageOfQuery
Search Suggested Queries
他のユーザーが Salesforce ナレッジで実行した検索に一致するユーザーのクエリ文
字列テキストに基づいて、提案する検索のリストを返します。ユーザーが検索を
実行する前に、検索の有効性を高める手段を提供します。このリソースは REST
API バージョン 30.0 以降で使用できます。
/services/data/vXX.X/search/suggestTitleMatches?q=searchString
&language=articleLanguage&publishStatus=articlePublicationStatus
Search Suggested Article Title
Matches
ユーザーの検索クエリ文字列に一致する Salesforce ナレッジ記事タイトルのリスト
を返します。ユーザーが検索を実行する前に、関連する可能性のある記事に直接
移動するためのショートカットを提供します。
/services/data/vXX.X/searchlayout/?q=commaDelimitedObjectListSearch Result Layouts
135
リファレンス

===== PAGE 146 =====
URI および説明リソース名
クエリ文字列に含まれるオブジェクトの検索結果レイアウトに関する情報を返し
ます。このコールでは、検索結果ページに列として表示される項目のリスト、最
初のページに表示される行数、および検索結果ページで使用される表示ラベルが
オブジェクトごとに返されます。
/services/data/vXX.X/serviceTemplatesService Templates
組織内でのみ使用します。
/services/data/vXX.X/smartdatadiscoverySmart Data Discovery
(インサイト API) インサイト API を使用して、インサイトを Web サイト、アプリケーション、また
はダッシュボードに埋め込みます。『プログラムによる説明的インサイトと診断
的インサイトの取得』を参照してください。
/services/data/vXX.X/sobjectsDescribe Global
/services/data/vXX.X/sobjects/eventName/eventSchemaPlatform Event Schema by Event
Name
イベント名のプラットフォームイベントの定義を JSON 形式で取得します。
/services/data/vXX.X/sobjects/LightningExitByPageMetricsLightning Exit by Page Metrics
ユーザーが Lightning Experience から Salesforce Classic に切り替える標準ページに関す
る頻度の総計値を返します。
/services/data/vXX.X/sobjects/LightningToggleMetricsLightning Toggle Metrics
Salesforce Classic から Lightning Experience に切り替えたユーザーに関する詳細を返し
ます。
/services/data/vXX.X/sobjects/LightningUsageByAppTypeMetricsLightning Usage by App Type
Lightning Experience ユーザーと Salesforce モバイルユーザーの合計数を返します。こ
のリソースは REST API バージョン 44.0 以降で使用できます。
/services/data/vXX.X/sobjects/LightningUsageByBrowserMetricsLightning Usage by Browser
ブラウザーインスタンスによってグループ化された Lightning Experience 利用状況の
結果を返します。
/services/data/vXX.X/sobjects/LightningUsageByFlexiPageMetricsLightning Usage by FlexiPage
Lightning Experience で最も頻繁に表示されたカスタムページに関する詳細を返しま
す。
/services/data/vXX.X/sobjects/LightningUsageByPageMetricsLightning Usage by Page
Lightning Experience でユーザーが最も頻繁に表示した標準ページを示します。
136
リファレンス

===== PAGE 147 =====
URI および説明リソース名
/services/data/vXX.X/sobjects/PlatformActionsObject PlatformAction
ユーザー、コンテキスト、デバイス形式、レコード ID に応じて、UI に表示するア
クションを照会します。たとえば、標準およびカスタムボタン、クイックアク
ション、生産性アクションなどを照会できます。
/services/data/vXX.X/sobjects/relevantItemssObject Relevant Items
現在のユーザーに最も関連性の高い項目を取得します。関連性の高い項目には、
ユーザーのグローバル検索範囲のオブジェクトや、最後に使用した (MRU) オブジェ
クトのレコードなどがあります。
/services/data/vXX.X/sobjects/sObjectsObject Basic Information
指定されたオブジェクトの基本メタデータを取得するか、指定されたオブジェク
トの新規レコードを作成します。
/services/data/vXX.X/sobjects/sObject/deleted/
?start=startDateAndTime&end=endDateAndTime
sObject Get Deleted
指定されたオブジェクトについて、特定の期間内に削除された個々のレコードの
リストを取得します。
/services/data/vXX.X/sobjects/sObject/describesObject Describe
指定されたオブジェクトのすべてのレベルで、個別のメタデータを完全に説明し
ます。たとえば、これは、Account オブジェクトの項目、URL、および子リレーショ
ンを取得するために使用できます。
/services/data/vXX.X/sobjects/sObject/describe/approvalLayoutssObject ApprovalLayouts
指定されたオブジェクトの承認レイアウトのリストを取得します。このリソース
は REST API バージョン 30.0 以降で使用できます。
/services/data/vXX.X/sobjects/sObject/describe/compactLayoutssObject CompactLayouts
特定のオブジェクトのコンパクトレイアウトのリストを取得します。このリソー
スは REST API バージョン 29.0 以降で使用できます。
/services/data/vXX.X/sobjects/sObject/describe/layouts
/services/data/vXX.X/sobjects/Global/describe/layouts
sObject Layouts
ページレイアウトとその説明のリストを取得します。特定のオブジェクトのすべ
てのレイアウト、または特定のオブジェクトの指定されたレコードタイプに関連
するレイアウトの情報を要求できます。
/services/data/vXX.X/sobjects/sObject/describe/namedLayouts/layoutNamesObject Named Layouts
137
リファレンス

===== PAGE 148 =====
URI および説明リソース名
特定のオブジェクトの代替名前付きレイアウトに関する情報を取得します。この
リソースは REST API バージョン 31.0 以降で使用できます。
/services/data/vXX.X/sobjects/sObject/fieldName/fieldValuesObject Rows by External ID
指定された外部 ID 項目の値に基づいて、レコードを作成するか、既存のレコード
を更新 (レコードを Upsert) します。
/services/data/vXX.X/sobjects/sObject/listviewsList Views for an Object
/services/data/vXX.X/sobjects/sObject/listviews/listViewId
指定された sObject のリストビューのリストを返します。各リストビューの ID と
その他の基本情報も含まれます。ID で特定のリストビューの基本情報を取得する
こともできます。
/services/data/vXX.X/sobjects/sObject/listviews/listViewID/resultsList View Results
リストビューに対する SOQL クエリを実行し、結果のデータと表示情報を返しま
す。
/services/data/vXX.X/sobjects/sObject/listviews/queryLocator/describeList View Describe
ID、列、SOQL クエリなど、リストビューに関する詳細な情報を返します。
/services/data/vXX.X/sobjects/sObject/listviews/recentRecent List Views
特定のオブジェクトに最近使用されたリストビューのリストを返します。
/services/data/vXX.X/sobjects/sObject/quickActions/sObject Quick Actions
オブジェクトのアクションとアクションの詳細にアクセスします。
/services/data/vXX.X/sobjects/sObject/updated/
?start=startDateAndTime&end=endDateAndTime
sObject Get Updated
/services/data/vXX.X/sobjects/sObject/idsObject Rows
指定されたオブジェクトとレコード ID に基づいてレコードにアクセスします。
HTTP メソッドに従ってレコードを取得、更新、または削除します。レコードまた
は特定の項目値を取得するには GET メソッド、レコードを削除するには DELETE メ
ソッド、レコードを更新するには PATCH メソッドを使用します。
/services/data/vXX.X/sobjects/sObject/id/blobFieldsObject Blob Get
個別のレコードから指定された blob 項目を取得して、バイナリデータとして返し
ます。
/services/data/vXX.X/sobjects/sObject/id/relationshipNamesObject Relationships
138
リファレンス

===== PAGE 149 =====
URI および説明リソース名
使い慣れた URL を介してオブジェクトリレーションをトラバースし、レコードに
アクセスします。トラバースされたリレーション項目に関連付けられたレコード
を取得、更新、または削除できます。複数の関連レコードがある場合、関連付け
られたレコードの完全なセットを取得できます。
/services/data/vXX.X/sobjects/sObject/id/
richTextImageFields/fieldName/contentReferenceId
sObject Rich Text Image Get
特定のレコードの特定のリッチテキストエリア項目から、指定された画像データ
を取得します。
/services/data/vXX.X/sobjects/Event/id/fromThisEventOnwardsDelete Lightning Experience
Event Series
一連の IsRecurrence2 行動から 1 つ以上を削除します。
/services/data/vXX.X/sobjects/StreamingChannel/channelId/pushStreaming Channel Push
(ストリーミング API) 登録者情報を取得し、ストリーミングチャネルの通知を転送します。『ストリー
ミング API 開発者ガイド』を参照してください。
/services/data/vXX.X/sobjects/User/userId/passwordsObject User Password
指定されたユーザー ID に基づいてユーザーパスワードにアクセスします。HTTP
メソッドに基づき、ユーザーパスワードの有効期限の状況を設定、リセット、ま
たは取得します。パスワードの有効期限の状況を取得するには GET メソッド、パ
スワードを設定するには POST メソッド、パスワードのリセットを開始するには
DELETE メソッドを使用します。
/services/data/vXX.X/sobjects/SelfServiceUser/
selfServiceUserId/password
sObject Self-Service User
Password
指定されたユーザー ID に基づいてセルフサービスユーザーパスワードにアクセス
します。HTTP メソッドに基づき、セルフサービスユーザーパスワードの有効期限
の状況を設定、リセット、または取得します。パスワードの有効期限の状況を取
得するには GET メソッド、パスワードを設定するには POST メソッド、パスワード
のリセットを開始するには DELETE メソッドを使用します。
/services/data/vXX.X/support/dataCategoryGroupsData Category Groups
現在のユーザーが参照可能なデータカテゴリグループを取得します。
/services/data/vXX.X/support/dataCategoryGroups/group/
dataCategories/category
Data Category Detail
指定されたカテゴリのデータカテゴリの詳細と子カテゴリを取得します。
/services/data/vXX.X/support/embeddedservice/configuration/
serviceName
Embedded Service
Configuration Describe
139
リファレンス

===== PAGE 150 =====
URI および説明リソース名
フィールドサービスの 1 つ以上のサービスレポートテンプレートに対応する情報
を返します。
/services/data/vXX.X/support/fieldservice/Flow
?developerNames=flowName
Field Service Flow
Field Service フローに対応する情報を返します。『Field Service 開発者ガイド』の「Field
Service フロー」を参照してください。
/services/data/vXX.X/support/fieldservice/ServiceReportTemplateField Service Report Template
フィールドサービスの 1 つ以上のサービスレポートテンプレートに対応する情報
を返します。『Field Service 開発者ガイド』の「サービスレポートテンプレート」
を参照してください。
/services/data/vXX.X/support/knowledgeArticles/articleIdArticles Details
/services/data/vXX.X/support/knowledgeArticles/articleUrlName
ユーザーがアクセスできるすべての記事項目を取得します。
/services/data/vXX.X/tabsTabs
ユーザーが [すべてのタブ] ([+]) タブカスタマイズ機能を使用してタブを非表示に
しているかどうかに関係なく、ログインユーザーが使用できるすべてのタブ
(Lightning ページタブを含む) のリストを返します。
/services/data/vXX.X/themeThemes
Salesforce アプリケーションのテーマで使用するアイコンと色のリストを取得しま
す。
/services/data/vXX.X/toolingTooling API
Tooling API で機能にアクセスします。『Tooling API 開発者ガイド』を参照してくだ
さい。
/services/data/vXX.X/ui-apiUI API
UI API で機能にアクセスします。『ユーザーインターフェース API 開発者ガイド』
を参照してください。
/services/data/vXX.X/waveWave
(Analytics REST API) Analytics REST API で機能にアクセスします。『Analytics REST API 開発者ガイド』を参
照してください。
140
リファレンス

===== PAGE 151 =====
Versions
バージョン、表示ラベル、および各バージョンのルートへのリンクなど、現在使用可能な各 Salesforce バージョ
ンの概要情報をリストします。
構文
URI
/services/data/
形式
JSON、XML
HTTP メソッド
GET
認証
なし
パラメーター
なし
例
「使用可能な REST API バージョンをリストする」 (ページ 34)を参照してください。
Resources by Version
リソース名および URI を含む、指定された API バージョンで使用可能なリソースをリストします。
構文
URI
/services/data/vXX.X/
形式
JSON、XML
HTTP メソッド
GET
認証
Authorization: Bearer token
パラメーター
なし
141
Versionsリファレンス

===== PAGE 152 =====
例
「使用可能な REST リソースをリストする」 (ページ 39)を参照してください。
制限
組織内の制限に関する情報をリストします。このリソースでは、各制限の最大割り当てと使用量に基づく残り
の割り当てが返されます。
このリソースは、REST API バージョン 29.0 以降で、「設定・定義を参照する」権限を持つ API ユーザーが利用で
きます。
構文
URI
/services/data/vXX.X/limits/
形式
JSON、XML
HTTP メソッド
GET
認証
Authorization: Bearer token
レスポンスボディ
説明制限の表示ラベル
分析
REST API を介して毎日アップロードできる外部データの最大
量 (バイト)。
AnalyticsExternalDataSizeMB
レポート非同期実行の結果への同時 REST API 要求数ConcurrentAsyncGetReportInstances
REST API を使用した同時 Einstein Discovery データインサイトス
トーリー作成
ConcurrentEinsteinDataInsightsStoryCreation
REST API を使用した同時 Einstein Discovery ストーリー作成ConcurrentEinsteinDiscoveryStoryCreation
REST API を使用したレポート同時同期実行数ConcurrentSyncReportRuns
1 時間あたりの REST API を使用したレポート非同期実行数HourlyAsyncReportRuns
1 時間あたりの REST API を使用したレポート同期実行数HourlySyncReportRuns
1 時間あたりの REST API を使用したダッシュボード更新数HourlyDashboardRefreshes
1 時間あたりのダッシュボードの結果への REST API 要求数HourlyDashboardResults
1 時間あたりの REST API を使用したダッシュボード状況要求数HourlyDashboardStatuses
142
制限リファレンス

===== PAGE 153 =====
説明制限の表示ラベル
1 日あたりの REST API を使用した Analytics データフロージョブ
実行数
DailyAnalyticsDataflowJobExecutions
1 日あたりのアップロードされた Analytics ファイルの累積サ
イズ (MB)
DailyAnalyticsUploadedFilesSizeMB
1 日あたりの REST API を使用して作成された Einstein Discovery
データインサイトストーリー数
DailyEinsteinDataInsightsStoryCreation
1 日あたりの Einstein Discovery REST API 要求 (予測) の累積数DailyEinsteinDiscoveryPredictAPICalls
1 日あたりの作成された Einstein Discovery 変更データキャプチャ
アドオン (予測) の累積数
DailyEinsteinDiscoveryPredictionsByCDC
1 日あたりの Einstein Discovery 最適化ジョブ実行の累積数DailyEinsteinDiscoveryOptimizationJobRuns
1 日あたりの REST API を使用して作成された Einstein Discovery ス
トーリーの累積数
DailyEinsteinDiscoveryStoryCreation
1 月あたりの REST API を使用して作成された Einstein Discovery ス
トーリーの累積数
MonthlyEinsteinDiscoveryStoryCreation
メール
Apex または API を介して外部メールアドレスに送信される 1
日あたりの一括メール数
MassEmail
外部メールアドレスに送信される 1 日あたりの単一メール数SingleEmail
メモ:  Spring '19 よりも前に作成された組織では、この日
次制限は、Apex と Salesforce API (REST API を除く) を介して
送信されたメールに対してのみ適用されます。Spring '19
以降に作成された組織では、この日次制限はメールア
ラート、単純なメールアクション、フロー内の [メール
を送信] アクション、および REST API にも適用されます。
組織がこの制限に達したため新しく計数されたメール
のいずれかを送信できない場合、通知のメールがユー
ザーに送信され、エントリがデバッグログに追加され
ます。
Lightning Platform REST および Bulk API
許容されるカスタム権限セットの最大数。この制限は、API
バージョン 41.0 以降で使用できます。
CreateCustom
Daily API コールDailyApiRequests
1 日あたりの非同期 Apex メソッド (Apex 一括処理、future メ
ソッド、キュー可能 Apex、スケジュール済み Apex を含む) の
実行数
DailyAsyncApexExecutions
143
制限リファレンス

===== PAGE 154 =====
説明制限の表示ラベル
1 日あたりの非同期 Apex テストの実行数。この制限は、API
バージョン 56.0 以降で使用できます。
DailyAsyncApexTests
Daily Bulk API および Bulk API 2.0 のバッチDailyBulkApiBatches (API バージョン 49.0
以降) または DailyBulkApiRequests  (API
バージョン 48.0 以降) Bulk API では、取り込み操作とクエリ操作の両方でバッチが使
用されます。Bulk API 2.0 では、取り込み操作でのみバッチが
使用されます。
Bulk API 2.0 のクエリの日次ストレージ (MB で測定)。この制限
は、API バージョン 47.0 以降で使用できます。
DailyBulkV2QueryFileStorageMB
Bulk API 2.0 の 1 日あたりのクエリジョブ数。この制限は、API
バージョン 47.0 以降で使用できます。
DailyBulkV2QueryJobs
許容される権限セットの最大数。「権限セット: 最大数 (イン
ストールされた管理 AppExchange パッケージの一部として作
PermissionSets
成および追加される権限セット)」機能の割り当てに対応し
ます。この制限は、API バージョン 41.0 以降で使用できます。
プラットフォームイベント
次の値はプラットフォームイベントにのみ適用されます。変更データキャプチャイベントには適用され
ません。
1 時間あたりの公開される大規模プラットフォームイベント
通知
HourlyPublishedPlatformEvents
1 時間あたりの公開される標準量のプラットフォームイベン
ト通知
(標準量イベントは、定義できなくなりました。新規のプラッ
トフォームイベントは、デフォルトで大規模となります。)
HourlyPublishedStandardVolumePlatform
Events
CometD クライアントに配信する 1 日あたりの標準量プラット
フォームイベント通知
(標準量イベントは、定義できなくなりました。新規のプラッ
トフォームイベントは、デフォルトで大規模となります。)
DailyStandardVolumePlatformEvents
プラットフォームイベントと変更データキャプチャ
次の値は、プラットフォームイベントと変更データキャプチャイベントに適用されます。
アドオンライセンスのない組織: 1 日の利用状況とデフォルト
の割り当て
DailyDeliveredPlatformEvents
過去 24 時間に CometD および Pub/Sub API クライアント、
empApi  Lightning コンポーネント、イベントリレーに配信さ
れた大規模プラットフォームイベントおよび変更イベントの
144
制限リファレンス

===== PAGE 155 =====
説明制限の表示ラベル
数を取得するには、DailyDeliveredPlatformEvents を
使用します。この値は、Apex トリガー、フロー、プロセスな
どの他の登録者には適用されません。この値は、大規模プ
ラットフォームイベントまたは変更データキャプチャアドオ
ンを購入したことがない組織に適用されます。
使用量の追跡頻度: DailyDeliveredPlatformEvents はイ
ベントの配信後、数分以内に更新されます。
アドオンライセンスのある組織: 毎月のイベント配信使用量MonthlyPlatformEvents  (API バージョン
47.0 以前)
組織で大規模プラットフォームイベントまたは変更データ
キャプチャのアドオンを購入している場合は、
MonthlyPlatformEvents を使用します。使用量ベースのエンタイ
トルメントを取得するには、この表の
MonthlyPlatformEventsUsageEntitlement のエントリを確認してくだ
さい。
CometD および Pub/Sub API クライアント、empApi  Lightning コ
ンポーネント、イベントリレーへの大規模プラットフォーム
イベントと変更イベントの両方の毎月の配信の利用状況を取
得するには、MonthlyPlatformEvents を使用します。こ
の値は、Apex トリガー、フロー、プロセスなどの他の登録者
には適用されません。
使用量の追跡頻度: MonthlyPlatformEvents はイベントの
配信後、数分以内に更新されます。
アドオンライセンスのある組織: 月次使用量ベースのエンタ
イトルメント
MonthlyPlatformEventsUsageEntitlement
(API バージョン 48.0 以降)
組織で大規模プラットフォームイベントまたは変更データ
キャプチャのアドオンを購入している場合は、
MonthlyPlatformEventsUsageEntitlement を使用しま
す。この値は、CometD および Pub/Sub API クライアント、
empApi  Lightning コンポーネント、イベントリレーへのイベ
ント配信の月次エンタイトルメントと使用量で、クライアン
トごとに増分されます。この値は、Apex トリガー、フロー、
プロセスなどの他の登録者には適用されません。この値に
は、大規模プラットフォームイベントと変更イベントの両方
の使用量が含まれます。
使用量の追跡頻度:
MonthlyPlatformEventsUsageEntitlement は 1 日に 1 回
更新されます。
145
制限リファレンス

===== PAGE 156 =====
説明制限の表示ラベル
エンタイトルメントは、契約開始日以降、毎月リセットされ
ます。エンタイトルメントの使用量は本番組織でのみ計算さ
れます。Sandbox またはトライアル組織では使用できません。
詳細は、「使用量ベースのエンタイトルメント項目」を参照
してください。
アドオンライセンスにより、エンタイトルメントの最大値を
一定量超過できます。その結果、最大値を超過した場合、返
される残りの値が負の数値になることがあります。
API バージョン 48.0 以降では
MonthlyPlatformEventsUsageEntitlementを使用して、
契約の初日に基づく正確なイベント配信使用量を取得してく
ださい。API バージョン 47.0 以前の場合、
MonthlyPlatformEvents では契約開始日ではなく、月の
初日に基づく使用量が返されます。
プライベートコネクト
送信のプライベート接続を介して 1 時間あたりに転送できる
データの最大量 (バイト)。
PrivateConnectOutboundCalloutHourlyLimitMB
Salesforce Connect
1 時間あたりの新しい長期的な外部レコード ID の対応付けHourlyLongTermIdMapping
1 時間あたりの OData コールアウトHourlyODataCallout
1 時間あたりの新しい短期的な外部レコード ID の対応付けHourlyShortTermIdMapping
Salesforce 開発者エクスペリエンス
エディション種別に基づいて任意の時点に有することができ
るスクラッチ組織の最大数。割り当てが使用可能になるの
ActiveScratchOrgs
は、スクラッチ組織を削除した場合、またはスクラッチ組織
が期限切れになった場合です。
ローリング (スライディング) 24 時間ウィンドウでスクラッチ
組織の作成を正常に開始できる最大回数。割り当ては、過去
DailyScratchOrgs
24 時間に作成されたスクラッチ組織の数に基づいて決定され
ます。
1 日に作成可能なパッケージバージョンの数。ロック解除済
みの第二世代管理パッケージに適用されます。
Package2VersionCreates
1 日に作成可能な検証をスキップするパッケージバージョン
の数。ロック解除済みの第二世代管理パッケージに適用され
ます。
Package2VersionCreatesWithoutValidation
Salesforce Functions
146
制限リファレンス

===== PAGE 157 =====
説明制限の表示ラベル
Functions を使用した組織の毎日の API コール数。値が表示さ
れるのは、Salesforce Functions が有効である場合のみです。詳
DailyFunctionsApiCallLimit  (API バー
ジョン 53.0 以降)
細は、「Functions Limits (Functions の制限)」を参照してくださ
い。
ストレージ
データストレージ (MB)
API ユーザーは「ユーザーの管理」権限を持っている必要が
あります。
DataStorageMB
ファイルストレージ (MB)
API ユーザーは「ユーザーの管理」権限を持っている必要が
あります。
FileStorageMB
ストリーミング API — デュラブル (API バージョン 37.0 以降)
過去 24 時間にすべての CometD クライアントに配信された汎
用イベント通知数
DailyDurableGenericStreamingApiEvents
過去 24 時間にすべての CometD クライアントに配信された
PushTopic イベント通知数
DailyDurableStreamingApiEvents
すべてのチャネルおよびすべてのイベント種別での、同時
CometD クライアント (登録者) の数
DurableStreamingApiConcurrentClients
ストリーミング API (API バージョン 36.0 以前)
過去 24 時間にすべての CometD クライアントに配信された汎
用イベント通知数
DailyGenericStreamingApiEvents
過去 24 時間にすべての CometD クライアントに配信された
PushTopic イベント通知数
DailyStreamingApiEvents
すべてのチャネルおよびすべてのイベント種別での、同時
CometD クライアント (登録者) の数
StreamingApiConcurrentClients
ワークフロー
1 日あたりのワークフローメール数DailyWorkflowEmails
1 時間あたりのワークフロータイムトリガー数HourlyTimeBasedWorkflow
例
「組織の制限をリストする」を参照してください。
147
制限リファレンス

===== PAGE 158 =====
Describe Global
使用可能なオブジェクトと関連するメタデータをリスト表示します。
さらに、組織の文字コードとクエリで許可される最大バッチサイズを返します。文字コードについての詳細
は、「国際化と文字コード」を参照してください。
このリソースでは、If-Modified-Sinceヘッダーまたは If-Unmodified-Sinceヘッダーを使用できます。
If-Modified-Since ヘッダーが使用される場合、指定の日付以降に使用可能なオブジェクトのメタデータが
変更されていないと、レスポンスボディなしで 304 Not Modified 状況コードが返されます。
メモ: If-Modified-Since ヘッダーと If-Unmodified-Since ヘッダーでチェックするのは、オブジェ
クト固有のメタデータの変更のみではありません。権限、プロファイル、項目表示ラベルに対する変更
など、組織全体の行動もチェックします。
構文
URI
/services/data/vXX.X/sobjects/
形式
JSON、XML
HTTP メソッド
GET
認証
Authorization: Bearer token
パラメーター
説明パラメーター
日時を指定する省略可能なヘッダー。この要求では、その日時以降に
変更されたレコードが返されます。
If-Modified-Since
形式は EEE, dd MMM yyyy HH:mm:ss z です。例:
If-Modified-Since: Mon, 30 Nov 2020 08:34:54 MST。
日時を指定する省略可能なヘッダー。この要求では、その日時以降に
変更されなかったレコードが返されます。
If-Unmodified-Since
形式は EEE, dd MMM yyyy HH:mm:ss z です。例:
If-Unmodified-Since: Mon, 30 Nov 2020 08:34:54 MST。
148
Describe Globalリファレンス

===== PAGE 159 =====
例
「オブジェクトのリストを取得する」 (ページ 42)を参照してください。
関連トピック:
条件付き要求ヘッダー
sObject Basic Information
指定されたオブジェクトの基本メタデータを取得するか、指定されたオブジェクトの新規レコードを作成しま
す。
たとえば、このリソースは、GET メソッドを使用した Account オブジェクトのメタデータの取得や、POST メソッ
ドを使用した新規 Account オブジェクトの作成に使用できます。
このセクションの内容:
sObject Basic Information を使用したオブジェクトメタデータの取得
指定されたオブジェクトのオブジェクトプロパティ、最近使ったデータ、オブジェクトに関連する他のリ
ソースの URI などの基本メタデータを取得します。
sObject Basic Information を使用したレコードの作成
リクエストボディの項目値に基づいて、指定されたオブジェクトの新しいレコードを作成します。
sObject Basic Information を使用したオブジェクトメタデータの取得
指定されたオブジェクトのオブジェクトプロパティ、最近使ったデータ、オブジェクトに関連する他のリソー
スの URI などの基本メタデータを取得します。
オブジェクトのすべてのメタデータを取得するには、sObject Describe リソースを使用します。
構文
URI
/services/data/vXX.X/sobjects/sObject/
形式
JSON、XML
HTTP メソッド
GET
認証
Authorization: Bearer token
149
sObject Basic Informationリファレンス

===== PAGE 160 =====
パラメーター
説明パラメーター
オブジェクトの名前。たとえば、Account などです。sObject
必須のパスパラメーター。
例
オブジェクトのメタデータを取得する例は、「オブジェクトのメタデータの取得」 (ページ 44)を参照してく
ださい。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
sObject Basic Information を使用したレコードの作成
リクエストボディの項目値に基づいて、指定されたオブジェクトの新しいレコードを作成します。
リクエストボディ内の必須項目には、値を指定する必要があります。他の項目の値の指定は、省略可能です。
構文
URI
/services/data/vXX.X/sobjects/sObject/
形式
JSON、XML
HTTP メソッド
POST
認証
Authorization: Bearer token
パラメーター
説明パラメーター
要求と応答の形式を指定する省略可能なヘッダー。次から選択できま
す。
Content-Type
• Content-Type: application/json
• Content-Type: application/xml
オブジェクトの名前。たとえば、Account などです。sObject
必須のパスパラメーター。
150
sObject Basic Information を使用したレコードの作成リファレンス

===== PAGE 161 =====
例
• POST を使用した新規レコードを作成する例は、「レコードを作成する」 (ページ 48)を参照してください。
• レコードの blob データを指定して新規レコードを作成する例は、「Blob データを挿入または更新する」
(ページ 79)を参照してください。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
sObject Describe
指定されたオブジェクトのすべてのレベルで、個別のメタデータを完全に説明します。たとえば、これは、
Account オブジェクトの項目、URL、および子リレーションを取得するために使用できます。
取得されるメタデータについての詳細は、『SOAP API 開発者ガイド』の「DescribesObjectResult」を参照してくだ
さい。
このリソースでは、If-Modified-Sinceヘッダーまたは If-Unmodified-Sinceヘッダーを使用できます。
If-Modified-Since ヘッダーが使用される場合、指定の日付以降に使用可能なオブジェクトのメタデータが
変更されていないと、レスポンスボディなしで 304 Not Modified 状況コードが返されます。
構文
URI
/services/data/vXX.X/sobjects/sObject/describe/
形式
JSON、XML
HTTP メソッド
GET
認証
Authorization: Bearer token
パラメーター
説明パラメーター
オブジェクトの名前。たとえば、Account などです。sObject
必須のパスパラメーター。
日時を指定する省略可能なヘッダー。この要求では、その日時以降に
変更されたレコードが返されます。
If-Modified-Since
形式は EEE, dd MMM yyyy HH:mm:ss z です。例:
If-Modified-Since: Mon, 30 Nov 2020 08:34:54 MST。
151
sObject Describeリファレンス

===== PAGE 162 =====
説明パラメーター
日時を指定する省略可能なヘッダー。この要求では、その日時以降に
変更されなかったレコードが返されます。
If-Unmodified-Since
形式は EEE, dd MMM yyyy HH:mm:ss z です。例:
If-Unmodified-Since: Mon, 30 Nov 2020 08:34:54 MST。
例
「オブジェクトの項目と他のメタデータを取得する」を参照してください。If-Modified-Since  HTTP ヘッ
ダーの使用例は、「オブジェクトのメタデータの変更の取得」を参照してください。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
条件付き要求ヘッダー
sObject Get Deleted
指定されたオブジェクトについて、特定の期間内に削除された個々のレコードのリストを取得します。このリ
ソースは REST API バージョン 29.0 以降で使用できます。
このリソースは、データ複製アプリケーションで一般的に使用されます。次の考慮事項に注意してください。
• 削除されたレコードは、このリソースからアクセス可能な削除ログに出力されます。2 時間ごとに実行され
るバックグラウンドプロセスは、削除ログのレコード数が制限を超えた場合、削除ログに書き込まれてか
ら 2 時間以上経過したレコードを消去します。最も古いレコードから順に、削除ログが制限を下回るまで
消去を行います。大量の削除ログによる Salesforce のパフォーマンス上の問題を防ぐためにこの処理を行い
ます。
• 削除されたレコードに関する情報は、現在のセッションのユーザーにそれらのレコードへのアクセス権が
ある場合にのみ返されます。
• コールが実行された日から 15 日以内の結果が返されます (管理者がごみ箱の中身を消去した場合、期間が
短くなる場合があります)。
データ複製およびデータ複製の制限についての詳細は、『SOAP API 開発者ガイド』の「データ複製」を参照し
てください。
構文
URI
/services/data/vXX.X/sobjects/sObject/deleted/?start=startDateAndTime&end=endDateAndTime
形式
JSON、XML
152
sObject Get Deletedリファレンス

===== PAGE 163 =====
HTTP メソッド
GET
認証
Authorization: Bearer token
パラメーター
説明パラメーター
データを取得する期間の開始日時 (ローカル時間ではなく協定世界時
(UTC))。API は、指定された dateTime 値に含まれる秒の部分を切り捨て
start
ます (たとえば、12:30:15 は 12:30:00 UTC となります)。日時は、「Date お
よび DateTime の有効な書式」の説明に従って書式設定する必要があり
ます。start の日付/時間値は、end の値より過去の日時でなければ
なりません。このパラメーターは URL 符号化されている必要がありま
す。
データを取得する期間の終了日時 (ローカル時間ではなく協定世界時
(UTC))。API は、指定された dateTime 値に含まれる秒の部分を切り捨て
end
ます (たとえば、12:35:15 は 12:35:00 UTC となります)。日時は、「Date お
よび DateTime の有効な書式」の説明に従って書式設定する必要があり
ます。このパラメーターは URL 符号化されている必要があります。
レスポンスボディ
説明型プロパティ
要求で指定された開始日と終了日を満たす削除されたレコード
の配列。各エントリには、レコード ID と協定世界時 (UTC) タイ
arraydeletedRecords
ムゾーンを使用した ISO 8601 形式でそのレコードが削除された
日時が含まれています。
最後に物理的に削除されたオブジェクトの ISO 8601 形式のタイ
ムスタンプ (ローカル時間ではなく協定世界時 (UTC) タイムゾー
ン)。
StringearliestDateAvailable
要求の対象となる最終日の ISO 8601 形式のタイムスタンプ (ロー
カル時間ではなく協定世界時 (UTC) タイムゾーン)。
StringlatestDateCovered
例
削除された項目のリストを取得する例は、「特定の時間枠に削除されたレコードのリストの取得」を参照して
ください。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
153
sObject Get Deletedリファレンス

===== PAGE 164 =====
sObject Get Updated
指定されたオブジェクトに対して指定された期間内に更新された (追加または変更された) 個別のレコードのリ
ストを取得します。このリソースは REST API バージョン 29.0 以降で使用できます。
このリソースは、データ複製アプリケーションで一般的に使用されます。次の考慮事項に注意してください。
• コールが実行された日から 30 日以内の結果が返されます。
• クライアントアプリケーションは、適切な権限が付与されている場合、任意のオブジェクトを複製できま
す。たとえば、組織のすべてのデータを複製するには、クライアントアプリケーションは指定されたオブ
ジェクトの「すべてのデータの参照」アクセス権限を持ってログインしなければなりません。同様に、オ
ブジェクトはそのユーザーの共有ルールに含まれていなければなりません。
• このリソースから返される ID は、600,000 件までに制限されています。600,000 件以上の ID が返された場合、
EXCEEDED_ID_LIMIT が返されます。開始日と終了日の期間を短くすることでこのエラーを回避できます。
データ複製およびデータ複製の制限についての詳細は、『SOAP API 開発者ガイド』の「データ複製」を参照し
てください。
構文
URI
/services/data/vXX.X/sobjects/sObject/updated/?start=startDateAndTime&end=endDateAndTime
形式
JSON、XML
HTTP メソッド
GET
認証
Authorization: Bearer token
パラメーター
説明パラメーター
データを取得する期間の開始日時 (ローカル時間ではなく協定世界時
(UTC))。API は、指定された dateTime 値に含まれる秒の部分を切り捨て
start
ます (たとえば、12:30:15 は 12:30:00 UTC となります)。日時は、「Date お
よび DateTime の有効な書式」の説明に従って書式設定する必要があり
ます。start の日付/時間値は、end の値より過去の日時でなければ
なりません。このパラメーターは URL 符号化されている必要がありま
す。
データを取得する期間の終了日時 (ローカル時間ではなく協定世界時
(UTC))。API は、指定された dateTime 値に含まれる秒の部分を切り捨て
end
ます (たとえば、12:35:15 は 12:35:00 UTC となります)。日時は、「Date お
よび DateTime の有効な書式」の説明に従って書式設定する必要があり
ます。このパラメーターは URL 符号化されている必要があります。
154
sObject Get Updatedリファレンス

===== PAGE 165 =====
応答形式
説明型プロパティ
要求で指定された開始日と終了日を満たす更新されたレコード
の配列。各エントリにはレコード ID が含まれます。
arrayids
要求の対象となる最終日の ISO 8601 形式のタイムスタンプ (ロー
カル時間ではなく協定世界時 (UTC) タイムゾーン)。
StringlatestDateCovered
例
更新された項目のリストを取得する例は、「特定の時間枠に更新されたレコードのリストの取得」を参照して
ください。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
sObject Named Layouts
特定のオブジェクトの代替名前付きレイアウトに関する情報を取得します。このリソースは REST API バージョ
ン 31.0 以降で使用できます。
このリソースを使用して、特定のオブジェクトの名前付きレイアウトに関する情報を取得します。有効な名前
付きレイアウト名をリソース URI の一部として指定する必要があります。
特定のオブジェクトの名前付きレイアウトのリストを取得するには、sObject Describe リソースを使用し、レス
ポンスボディで「namedLayoutInfos」項目を見つけます。
構文
URI
/services/data/vXX.X/sobjects/sObject/describe/namedLayouts/layoutName
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
リクエストボディ
なし
155
sObject Named Layoutsリファレンス

===== PAGE 166 =====
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/User/describe/namedLayouts/UserAlt
-H "Authorization: Bearer token"
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
sObject Rows
指定されたオブジェクトとレコード ID に基づいてレコードにアクセスします。HTTP メソッドに従ってレコー
ドを取得、更新、または削除します。レコードまたは特定の項目値を取得するには GET メソッド、レコードを
削除するには DELETE メソッド、レコードを更新するには PATCH メソッドを使用します。
新規レコードを作成するには、sObject Basic Information または sObject Rows by External ID リソースを使用します。
このセクションの内容:
sObject Rows を使用したレコードの取得
指定されたオブジェクトとレコード ID に基づいてレコードを取得します。レコードの項目と項目値が、レ
スポンスボディで返されます。このリソースは API バージョン 32.0 以降で外部オブジェクトに使用できま
す。
sObject Rows を使用したレコードの更新
指定されたオブジェクトとレコード ID に基づいてレコードを更新します。リクエストボディで提供された
項目値が、レコード内の既存の値と置き換えられます。このリソースは API バージョン 32.0 以降で外部オブ
ジェクトに使用できます。
sObject Rows を使用したレコードの削除
指定されたオブジェクトとレコード ID に基づいてレコードを削除します。このリソースは API バージョン
32.0 以降で外部オブジェクトに使用できます。
sObject Rows を使用したレコードの取得
指定されたオブジェクトとレコード ID に基づいてレコードを取得します。レコードの項目と項目値が、レス
ポンスボディで返されます。このリソースは API バージョン 32.0 以降で外部オブジェクトに使用できます。
データが大量ではない外部データソースに関連付けられた外部オブジェクトは、id に 18 文字の Salesforce ID を
使用します。それ以外の外部オブジェクトは、id に外部オブジェクトの外部 ID 標準項目を使用します。
レスポンスボディの項目についての詳細は、『SOAP API 開発者ガイド』の「DescribeSObjectResult」を参照してく
ださい。
156
sObject Rowsリファレンス

===== PAGE 167 =====
オブジェクトが Account オブジェクトの場合、応答には ETag ヘッダーも含まれます。(例: ETag:
"ddpAdaTHz+GcV35e7NLJ9iKD3XXVqAzXT1Sl2ykkP7g=--gzip") この ETag は If-Match ヘッダーと
If-None-Match ヘッダーで使用できます。詳細は、「条件付き要求ヘッダー」を参照してください。
構文
URI
/services/data/vXX.X/sobjects/sObject/id/
形式
JSON、XML
HTTP メソッド
GET
認証
Authorization: Bearer token
パラメーター
説明パラメーター
オブジェクトの名前。たとえば、Account などです。sObject
オブジェクトの識別子。たとえば、001R0000005hDFYIA2 のように
なります。
id
レスポンスボディで返される項目と値を指定する項目のカンマ区切り
のリスト。たとえ
fields
ば、?fields=name,description,numberofemployees,industry
のようになります。
1 つ以上の ETag のカンマ区切りリストを指定する省略可能なヘッダー。
これは、Account オブジェクトで使用される場合にのみ影響します。
If-Match
要求は、Account の ETag がリストに含まれている ETag と一致する場合
にのみ処理されます。
例: If-Match:
"94C83JSreaVMGpL+lUzv8Dr3inI0kCvuKATVJcTuApA=--gzip",
"ddpAdaTHz+GcV35e7NLJ9iKD3XXVqAzXT1Sl2ykkP7g=--gzip"。
1 つ以上の ETag のカンマ区切りリストを指定する省略可能なヘッダー。
これは、Account オブジェクトで使用される場合にのみ影響します。
If-None-Match
要求は、Account の ETag がリストに含まれている ETag と一致しない場
合にのみ処理されます。
例: If-None-Match:
"94C83JSreaVMGpL+lUzv8Dr3inI0kCvuKATVJcTuApA=--gzip",
"ddpAdaTHz+GcV35e7NLJ9iKD3XXVqAzXT1Sl2ykkP7g=--gzip"。
157
sObject Rows を使用したレコードの取得リファレンス

===== PAGE 168 =====
説明パラメーター
日時を指定する省略可能なヘッダー。この要求では、その日時以降に
変更されたレコードが返されます。
If-Modified-Since
形式は EEE, dd MMM yyyy HH:mm:ss z です。
例: If-Modified-Since: Mon, 30 Nov 2020 08:34:54 MST。
日時を指定する省略可能なヘッダー。この要求では、その日時以降に
変更されなかったレコードが返されます。
If-Unmodified-Since
形式は EEE, dd MMM yyyy HH:mm:ss z です。
例: If-Unmodified-Since: Mon, 30 Nov 2020 08:34:54 MST。
例
レコードを取得する例については、「標準オブジェクトレコードから項目値を取得する」を参照してくださ
い。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
sObject Rows を使用したレコードの更新
指定されたオブジェクトとレコード ID に基づいてレコードを更新します。リクエストボディで提供された項
目値が、レコード内の既存の値と置き換えられます。このリソースは API バージョン 32.0 以降で外部オブジェ
クトに使用できます。
データが大量ではない外部データソースに関連付けられた外部オブジェクトは、id に 18 文字の Salesforce ID を
使用します。それ以外の外部オブジェクトは、id に外部オブジェクトの外部 ID 標準項目を使用します。
レスポンスボディの項目についての詳細は、『SOAP API 開発者ガイド』の「DescribeSObjectResult」を参照してく
ださい。
オブジェクトが Account オブジェクトの場合、応答には ETag ヘッダーも含まれます。(例: ETag:
"ddpAdaTHz+GcV35e7NLJ9iKD3XXVqAzXT1Sl2ykkP7g=--gzip") この ETag は If-Match ヘッダーと
If-None-Match ヘッダーで使用できます。詳細は、「条件付き要求ヘッダー」を参照してください。
構文
URI
/services/data/vXX.X/sobjects/sObject/id/
形式
JSON、XML
158
sObject Rows を使用したレコードの更新リファレンス

===== PAGE 169 =====
HTTP メソッド
PATCH
認証
Authorization: Bearer token
パラメーター
説明パラメーター
要求と応答の形式を指定する省略可能なヘッダー。有効なヘッダー値
は次のとおりです。
Content-Type
• Content-Type: application/json
• Content-Type: application/xml
オブジェクトの名前。例、Account、CustomObject__c。sObject
オブジェクトの識別子。たとえば、001R0000005hDFYIA2 のように
なります。
id
1 つ以上の ETag のカンマ区切りリストを指定する省略可能なヘッダー。
これは、Account オブジェクトで使用される場合にのみ影響します。
If-Match
要求は、Account の ETag がリストに含まれている ETag と一致する場合
にのみ処理されます。
例: If-Match:
"94C83JSreaVMGpL+lUzv8Dr3inI0kCvuKATVJcTuApA=--gzip",
"ddpAdaTHz+GcV35e7NLJ9iKD3XXVqAzXT1Sl2ykkP7g=--gzip"。
1 つ以上の ETag のカンマ区切りリストを指定する省略可能なヘッダー。
これは、Account オブジェクトで使用される場合にのみ影響します。
If-None-Match
要求は、Account の ETag がリストに含まれている ETag と一致しない場
合にのみ処理されます。
例: If-None-Match:
"94C83JSreaVMGpL+lUzv8Dr3inI0kCvuKATVJcTuApA=--gzip",
"ddpAdaTHz+GcV35e7NLJ9iKD3XXVqAzXT1Sl2ykkP7g=--gzip"。
日時を指定する省略可能なヘッダー。この要求では、その日時以降に
変更されたレコードが返されます。
If-Modified-Since
形式は EEE, dd MMM yyyy HH:mm:ss z です。
例: If-Modified-Since: Mon, 30 Nov 2020 08:34:54 MST。
日時を指定する省略可能なヘッダー。この要求では、その日時以降に
変更されなかったレコードが返されます。
If-Unmodified-Since
形式は EEE, dd MMM yyyy HH:mm:ss z です。
159
sObject Rows を使用したレコードの更新リファレンス

===== PAGE 170 =====
説明パラメーター
例: If-Unmodified-Since: Mon, 30 Nov 2020 08:34:54 MST。
例
PATCH を使用してレコードを更新する例は、「レコードを更新する」を参照してください。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
条件付き要求ヘッダー
sObject Rows を使用したレコードの削除
指定されたオブジェクトとレコード ID に基づいてレコードを削除します。このリソースは API バージョン 32.0
以降で外部オブジェクトに使用できます。
データが大量ではない外部データソースに関連付けられた外部オブジェクトは、id に 18 文字の Salesforce ID を
使用します。それ以外の外部オブジェクトは、id に外部オブジェクトの外部 ID 標準項目を使用します。
オブジェクトが Account オブジェクトの場合、応答には ETag ヘッダーも含まれます。(例: ETag:
"ddpAdaTHz+GcV35e7NLJ9iKD3XXVqAzXT1Sl2ykkP7g=--gzip") この ETag は If-Match ヘッダーと
If-None-Match ヘッダーで使用できます。詳細は、「条件付き要求ヘッダー」を参照してください。
構文
URI
/services/data/vXX.X/sobjects/sObject/id/
形式
JSON、XML
HTTP メソッド
DELETE
認証
Authorization: Bearer token
パラメーター
説明パラメーター
オブジェクトの名前。たとえば、Account などです。sObject
レコードの識別子。例: 001R0000005hDFYIA2。id
1 つ以上の ETag のカンマ区切りリストを指定する省略可能なヘッダー。
これは、Account オブジェクトで使用される場合にのみ影響します。
If-Match
160
sObject Rows を使用したレコードの削除リファレンス

===== PAGE 171 =====
説明パラメーター
要求は、Account の ETag がリストに含まれている ETag と一致する場合
にのみ処理されます。
例: If-Match:
"94C83JSreaVMGpL+lUzv8Dr3inI0kCvuKATVJcTuApA=--gzip",
"ddpAdaTHz+GcV35e7NLJ9iKD3XXVqAzXT1Sl2ykkP7g=--gzip"。
1 つ以上の ETag のカンマ区切りリストを指定する省略可能なヘッダー。
これは、Account オブジェクトで使用される場合にのみ影響します。
If-None-Match
要求は、Account の ETag がリストに含まれている ETag と一致しない場
合にのみ処理されます。
例: If-None-Match:
"94C83JSreaVMGpL+lUzv8Dr3inI0kCvuKATVJcTuApA=--gzip",
"ddpAdaTHz+GcV35e7NLJ9iKD3XXVqAzXT1Sl2ykkP7g=--gzip"。
日時を指定する省略可能なヘッダー。この要求では、その日時以降に
変更されたレコードが返されます。
If-Modified-Since
形式は EEE, dd MMM yyyy HH:mm:ss z です。
例: If-Modified-Since: Mon, 30 Nov 2020 08:34:54 MST。
日時を指定する省略可能なヘッダー。この要求では、その日時以降に
変更されなかったレコードが返されます。
If-Unmodified-Since
形式は EEE, dd MMM yyyy HH:mm:ss z です。
例: If-Unmodified-Since: Mon, 30 Nov 2020 08:34:54 MST。
例
DELETE を使用してレコードを削除する例は、「レコードを削除する」を参照してください。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
sObject Rows by External ID
指定された外部 ID 項目の値に基づいて、レコードの作成、取得、更新/挿入、削除を実行します。このリソー
スで PATCH メソッドを使用することで、Salesforce に更新/挿入要求を送信できます。
このセクションの内容:
sObject Rows by External ID を使用したレコードの取得
指定された外部 ID 項目の値に基づいて、レコードを取得します。
161
sObject Rows by External IDリファレンス

===== PAGE 172 =====
sObject Rows by External ID を使用したレコードの作成
リクエストボディに含まれる項目値に基づいて、新しいレコードを作成します。このリソースでは、外部
ID 項目を使用する必要はありません。
sObject Rows by External ID を使用したレコードの更新/挿入
指定された外部 ID 項目の値に基づいて、レコードを更新/挿入します。外部 ID の値がすでに存在するかど
うかに応じて、要求時に新しいレコードが作成されるか、または既存のレコードが更新されます。
sObject Rows by External ID 使用したレコードの削除
指定された外部 ID 項目の値に基づいて、レコードを削除します。
sObject Rows by External ID 使用したヘッダーの返送
sObject Rows by External ID リソースに GET 要求を送信したときに返されるヘッダーのみを返します。これによ
り、コンテンツ自体を取得する前に、GET 要求で返されたヘッダー値を確認できます。
sObject Rows by External ID を使用したレコードの取得
指定された外部 ID 項目の値に基づいて、レコードを取得します。
メモ: セキュリティ上の理由で、一部のトップレベルドメイン (TLD) は特定のファイル形式拡張子と競合
する場合があります。実装を調整して、そのようなケースを回避してください。
たとえば、example@email.inc のようなメールアドレスを外部 ID として使用すると、「404 not found」
エラーが返されます。
競合する TLD は、いくつかの回避策によって対処できます。
• 別の外部 ID 項目を使用します。
• メール項目と同じ新しい外部 ID 項目を作成し、このケースに対応するために「.」を「_」に置き換え
ます。
• 「.inc」で終わるメールに対してクエリを実行し、レコード ID を取得してそれを upsert (更新/挿入) 要求
に使用します。
• upsert 要求に REST API の代わりに SOAP API を使用します。
• カスタム Apex REST API を作成して、メールをパスパラメーターでなくクエリパラメーターとして受け
入れます。Apex を使用して、upsert 要求を実行します。
構文
URI
/services/data/vXX.X/sobjects/sObject/fieldName/fieldValue
形式
JSON、XML
HTTP メソッド
GET
認証
Authorization: Bearer token
162
sObject Rows by External ID を使用したレコードの取得リファレンス

===== PAGE 173 =====
パラメーター
なし
例
外部 ID に基づいてレコードを取得する例は、「外部 ID を使用したレコードの取得」 (ページ 51)を参照してく
ださい。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
sObject Rows by External ID を使用したレコードの作成
リクエストボディに含まれる項目値に基づいて、新しいレコードを作成します。このリソースでは、外部 ID
項目を使用する必要はありません。
特殊なケースとして、API バージョン 37.0 以降では、/services/data/vXX.X/sobjects/sObjectName/Id
に対する POST 要求を使用してレコードを作成できます。Id の値が null であるため、要求から除かれ、リク
エストボディに従ってレコードが作成されます。このリソースを使用したレコードの作成では、新規レコード
ごとに各 POST 要求で同じ URI を使用できるため便利です。この場合、レコードを作成するために外部 ID を指
定する必要はありません。
メモ: リクエストボディに ID または外部 ID 項目を指定してはいけません。指定すると、エラーが発生し
ます。
構文
URI
/services/data/vXX.X/sobjects/sObject/Id
形式
JSON、XML
HTTP メソッド
POST
認証
Authorization: Bearer token
パラメーター
なし
163
sObject Rows by External ID を使用したレコードの作成リファレンス

===== PAGE 174 =====
例
リクエストの例
curl -X POST
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/Id -H
"Authorization: Bearer token" -H "Content-Type: application/json" -d "@newaccount.json"
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
sObject Rows by External ID を使用したレコードの更新/挿入
指定された外部 ID 項目の値に基づいて、レコードを更新/挿入します。外部 ID の値がすでに存在するかどうか
に応じて、要求時に新しいレコードが作成されるか、または既存のレコードが更新されます。
• 外部 ID が既存レコードと一致しない場合は、リクエストボディに従って新規レコードが作成されます。
• 外部 ID が 1 つの既存レコードと一致する場合は、リクエストボディに従って既存レコードが更新されます。
• 外部 ID が複数の既存レコードと一致する場合は、300 エラーが返され、レコードは作成も更新もされませ
ん。
External ID 属性と Unique 属性の両方が選択された (インデックスが一意) カスタム項目を持つオブジェク
トのレコードを更新/挿入する場合、特別な権限は必要ありません。Unique 属性は重複作成を防止します。
[外部 ID] 属性が選択され、Unique 属性が選択されていない (インデックスが一意ではない) オブジェクトの
レコードを更新/挿入する場合、クライアントアプリケーションがこのコールを実行するには「すべてのデー
タの参照」権限が必要です。
メモ: セキュリティ上の理由で、一部のトップレベルドメイン (TLD) は特定のファイル形式拡張子と競合
する場合があります。実装を調整して、そのようなケースを回避してください。
たとえば、example@email.inc のようなメールアドレスを外部 ID として使用すると、「404 not found」
エラーが返されます。
競合する TLD は、いくつかの回避策によって対処できます。
• 別の外部 ID 項目を使用します。
• メール項目と同じ新しい外部 ID 項目を作成し、このケースに対応するために「.」を「_」に置き換え
ます。
• 「.inc」で終わるメールに対してクエリを実行し、レコード ID を取得してそれを upsert (更新/挿入) 要求
に使用します。
• upsert 要求に REST API の代わりに SOAP API を使用します。
• カスタム Apex REST API を作成して、メールをパスパラメーターでなくクエリパラメーターとして受け
入れます。Apex を使用して、upsert 要求を実行します。
構文
URI
/services/data/vXX.X/sobjects/sObject/fieldName/fieldValue
164
sObject Rows by External ID を使用したレコードの更新/
挿入
リファレンス

===== PAGE 175 =====
形式
JSON、XML
HTTP メソッド
PATCH
認証
Authorization: Bearer token
パラメーター
なし
例
外部 ID に基づいてレコードを作成および更新する例は、「外部 ID を使用してレコードを挿入/更新 (Upsert) す
る」 (ページ 52)を参照してください。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
sObject Rows by External ID 使用したレコードの削除
指定された外部 ID 項目の値に基づいて、レコードを削除します。
メモ: セキュリティ上の理由で、一部のトップレベルドメイン (TLD) は特定のファイル形式拡張子と競合
する場合があります。実装を調整して、そのようなケースを回避してください。
たとえば、example@email.inc のようなメールアドレスを外部 ID として使用すると、「404 not found」
エラーが返されます。
競合する TLD は、いくつかの回避策によって対処できます。
• 別の外部 ID 項目を使用します。
• メール項目と同じ新しい外部 ID 項目を作成し、このケースに対応するために「.」を「_」に置き換え
ます。
• 「.inc」で終わるメールに対してクエリを実行し、レコード ID を取得してそれを upsert (更新/挿入) 要求
に使用します。
• upsert 要求に REST API の代わりに SOAP API を使用します。
• カスタム Apex REST API を作成して、メールをパスパラメーターでなくクエリパラメーターとして受け
入れます。Apex を使用して、upsert 要求を実行します。
構文
URI
/services/data/vXX.X/sobjects/sObject/fieldName/fieldValue
形式
JSON、XML
165
sObject Rows by External ID 使用したレコードの削除リファレンス

===== PAGE 176 =====
HTTP メソッド
DELETE
認証
Authorization: Bearer token
パラメーター
なし
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
sObject Rows by External ID 使用したヘッダーの返送
sObject Rows by External ID リソースに GET 要求を送信したときに返されるヘッダーのみを返します。これにより、
コンテンツ自体を取得する前に、GET 要求で返されたヘッダー値を確認できます。
メモ: セキュリティ上の理由で、一部のトップレベルドメイン (TLD) は特定のファイル形式拡張子と競合
する場合があります。実装を調整して、そのようなケースを回避してください。
たとえば、example@email.inc のようなメールアドレスを外部 ID として使用すると、「404 not found」
エラーが返されます。
競合する TLD は、いくつかの回避策によって対処できます。
• 別の外部 ID 項目を使用します。
• メール項目と同じ新しい外部 ID 項目を作成し、このケースに対応するために「.」を「_」に置き換え
ます。
• 「.inc」で終わるメールに対してクエリを実行し、レコード ID を取得してそれを upsert (更新/挿入) 要求
に使用します。
• upsert 要求に REST API の代わりに SOAP API を使用します。
• カスタム Apex REST API を作成して、メールをパスパラメーターでなくクエリパラメーターとして受け
入れます。Apex を使用して、upsert 要求を実行します。
構文
URI
/services/data/vXX.X/sobjects/sObject/fieldName/fieldValue
形式
JSON、XML
HTTP メソッド
HEAD
認証
Authorization: Bearer token
166
sObject Rows by External ID 使用したヘッダーの返送リファレンス

===== PAGE 177 =====
パラメーター
なし
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
sObject Blob Get
個別のレコードから指定された blob 項目を取得して、バイナリデータとして返します。blob 項目があるのは、
Attachment、ContentNote、ContentVersion、Document、Folder、Note などの特定の標準オブジェクトのみです。
メモ:  sObject Blob Get リソースは、JSON または XML 形式のデータではなくバイナリデータを返すため、複
合 API 要求と互換性がありません。Blob データを取得するには、代わりに、個別の sObject Blob Get 要求を実
行します。
構文
URI
/services/data/vXX.X/sobjects/sObject/id/blobField
形式
バイナリデータ
HTTP メソッド
GET
認証
Authorization: Bearer token
パラメーター
不要
例
Document から blob データを取得する例は、「blob データの取得」 (ページ 85)を参照してください。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
sObject ApprovalLayouts
指定されたオブジェクトの承認レイアウトのリストを取得します。このリソースは REST API バージョン 30.0 以
降で使用できます。
167
sObject Blob Getリファレンス

===== PAGE 178 =====
このセクションの内容:
承認レイアウトの取得
指定されたオブジェクトの承認レイアウトのリストを取得します。このリソースは REST API バージョン 30.0
以降で使用できます。
承認レイアウトのヘッダーの返送
sObject ApprovalLayouts リソースに GET 要求をしたときに返されるヘッダーのみを返します。リソースのコン
テンツを取得する前に、ヘッダー値を確認できます。このリソースは REST API バージョン 30.0 以降で使用で
きます。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
承認レイアウトの取得
指定されたオブジェクトの承認レイアウトのリストを取得します。このリソースは REST API バージョン 30.0 以
降で使用できます。
構文
URI
/services/data/vXX.X/sobjects/sObject/describe/approvalLayouts/
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
要求のパラメーター
不要
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/describe/approvalLayouts/
-H "Authorization: Bearer token"
レスポンスボディの例
{
"approvalLayouts" : [ {
"id" : "04aD00000008Py9IAE",
"label" : "MyApprovalProcessName",
"layoutItems" : [...],
168
承認レイアウトの取得リファレンス

===== PAGE 179 =====
"name" : "MyApprovalProcessName"
}, {
"id" : "04aD00000008Q0KIAU",
"label" : "Process1",
"layoutItems" : [...],
"name" : "Process1"
} ]
}
オブジェクトの承認レイアウトを定義していない場合は、応答が {"approvalLayouts" : [ ]} になり
ます。
承認レイアウトのヘッダーの返送
sObject ApprovalLayouts リソースに GET 要求をしたときに返されるヘッダーのみを返します。リソースのコンテン
ツを取得する前に、ヘッダー値を確認できます。このリソースは REST API バージョン 30.0 以降で使用できます。
構文
URI
指定されたオブジェクトの承認レイアウトの説明に対する要求のヘッダーを取得するに
は、/services/data/vXX.X/sobjects/sObject/describe/approvalLayouts/ を使用します。
形式
JSON、XML
HTTP のメソッド
HEAD
認証
Authorization: Bearer token
要求のパラメーター
不要
例
リクエストの例
curl -X HEAD --head
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/describe/approvalLayouts/
-H "Authorization: Bearer token"
sObject Single Approval Process
特定のオブジェクトの指定された承認プロセスに対する承認レイアウトを取得します。このリソースは REST
API バージョン 30.0 以降で使用できます。
169
承認レイアウトのヘッダーの返送リファレンス

===== PAGE 180 =====
指定されたオブジェクトの単一承認プロセスでのレイアウトの取得
特定のオブジェクトの指定された承認プロセスに対する承認レイアウトを取得します。このリソースは REST
API バージョン 30.0 以降で使用できます。
構文
URI
/services/data/vXX.X/sobjects/sObject/describe/approvalLayouts/approvalProcessName
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
要求パラメーター
不要
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/describe/approvalLayouts/ExampleApprovalProcessName
-H "Authorization: Bearer token"
レスポンスボディの例
{
"approvalLayouts" : [ {
"id" : "04aD00000008Py9IAE",
"label" : "ExampleApprovalProcessName",
"layoutItems" : [...],
"name" : "ExampleApprovalProcessName"
} ]
}
指定されたオブジェクトの単一承認プロセスでのヘッダーの取得
sObject ApprovalLayouts リソースに GET 要求をしたときに返されるヘッダーのみを返します。リソースのコンテン
ツを取得する前に、ヘッダー値を確認できます。要求を 1 つの特定の承認レイアウトに制限するには、特定の
承認プロセス名を指定します。このリソースは REST API バージョン 30.0 以降で使用できます。
構文
URI
/services/data/vXX.X/sobjects/sObject/describe/approvalLayouts/approvalProcessName
170
指定されたオブジェクトの単一承認プロセスでのレイア
ウトの取得
リファレンス

===== PAGE 181 =====
形式
JSON、XML
HTTP のメソッド
HEAD
認証
Authorization: Bearer token
要求パラメーター
不要
例
リクエストの例
curl -X HEAD --head
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/describe/approvalLayouts/ExampleApprovalProcessName
-H "Authorization: Bearer token"
sObject CompactLayouts
特定のオブジェクトのコンパクトレイアウトのリストを取得します。このリソースは REST API バージョン 29.0
以降で使用できます。
このセクションの内容:
sObject CompactLayouts を使用したコンパクトレイアウトの取得
特定のオブジェクトのコンパクトレイアウトのリストを取得します。このリソースは REST API バージョン
29.0 以降で使用できます。
sObject CompactLayouts を使用したヘッダーの返送
sObject CompactLayouts リソースに GET 要求をしたときに返されるヘッダーのみを返します。リソースのコン
テンツを取得する前に、前もってヘッダー値を確認できます。このリソースは REST API バージョン 29.0 以降
で使用できます。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
sObject CompactLayouts を使用したコンパクトレイアウトの取得
特定のオブジェクトのコンパクトレイアウトのリストを取得します。このリソースは REST API バージョン 29.0
以降で使用できます。
171
sObject CompactLayoutsリファレンス

===== PAGE 182 =====
構文
URI
/services/data/vXX.X/sobjects/sObject/describe/compactLayouts/
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
要求のパラメーター
不要
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/describe/compactLayouts
-H "Authorization: Bearer token"
レスポンスボディの例
このサンプルの JSON 応答は、Account オブジェクトに対して作成されたコンパクトレイアウト用です。この
例では、Account に対してカスタムコンパクトレイアウトが 1 つのみ作成されます。カスタムコンパクトレ
イアウトは、オブジェクトの主コンパクトレイアウトとして割り当てられ、[取引先名] と [電話] の 2 つ
の項目が含まれます。
{
"compactLayouts" : [ {
"actions" : [ {
"custom" : false,
"icons" : null,
"label" : "Call",
"name" : "CallHighlightAction"
}, {
"custom" : false,
"icons" : null,
"label" : "Send Email",
"name" : "EmailHighlightAction"
}, {
"custom" : false,
"icons" : null,
"label" : "Map",
"name" : "MapHighlightAction"
}, {
"custom" : false,
"icons" : null,
"label" : "Read News",
"name" : "NewsHighlightAction"
172
sObject CompactLayouts を使用したコンパクトレイアウ
トの取得
リファレンス

===== PAGE 183 =====
}, {
"custom" : false,
"icons" : null,
"label" : "View Website",
"name" : "WebsiteHighlightAction"
} ],
"fieldItems" : [ {
"editable" : false,
"label" : "Account Name",
"layoutComponents" : [ {
"components" : [ ],
"details" : {
"autoNumber" : false,
"byteLength" : 765,
"calculated" : false,
"calculatedFormula" : null,
"cascadeDelete" : false,
"caseSensitive" : false,
"controllerName" : null,
"createable" : true,
"custom" : false,
"defaultValue" : null,
"defaultValueFormula" : null,
"defaultedOnCreate" : false,
"dependentPicklist" : false,
"deprecatedAndHidden" : false,
"digits" : 0,
"displayLocationInDecimal" : false,
"externalId" : false,
"extraTypeInfo" : null,
"filterable" : true,
"groupable" : true,
"htmlFormatted" : false,
"idLookup" : false,
"inlineHelpText" : null,
"label" : "Account Name",
"length" : 255,
"mask" : null,
"maskType" : null,
"name" : "Name",
"nameField" : true,
"namePointing" : false,
"nillable" : false,
"permissionable" : false,
"picklistValues" : [ ],
"precision" : 0,
"queryByDistance" : false,
"referenceTo" : [ ],
"relationshipName" : null,
"relationshipOrder" : null,
"restrictedDelete" : false,
"restrictedPicklist" : false,
"scale" : 0,
"soapType" : "xsd:string",
173
sObject CompactLayouts を使用したコンパクトレイアウ
トの取得
リファレンス

===== PAGE 184 =====
"sortable" : true,
"type" : "string",
"unique" : false,
"updateable" : true,
"writeRequiresMasterRead" : false
},
"displayLines" : 1,
"tabOrder" : 2,
"type" : "Field",
"value" : "Name"
} ],
"placeholder" : false,
"required" : false
}, {
"editable" : false,
"label" : "Phone",
"layoutComponents" : [ {
"components" : [ ],
"details" : {
"autoNumber" : false,
"byteLength" : 120,
"calculated" : false,
"calculatedFormula" : null,
"cascadeDelete" : false,
"caseSensitive" : false,
"controllerName" : null,
"createable" : true,
"custom" : false,
"defaultValue" : null,
"defaultValueFormula" : null,
"defaultedOnCreate" : false,
"dependentPicklist" : false,
"deprecatedAndHidden" : false,
"digits" : 0,
"displayLocationInDecimal" : false,
"externalId" : false,
"extraTypeInfo" : null,
"filterable" : true,
"groupable" : true,
"htmlFormatted" : false,
"idLookup" : false,
"inlineHelpText" : null,
"label" : "Account Phone",
"length" : 40,
"mask" : null,
"maskType" : null,
"name" : "Phone",
"nameField" : false,
"namePointing" : false,
"nillable" : true,
"permissionable" : true,
"picklistValues" : [ ],
"precision" : 0,
"queryByDistance" : false,
174
sObject CompactLayouts を使用したコンパクトレイアウ
トの取得
リファレンス

===== PAGE 185 =====
"referenceTo" : [ ],
"relationshipName" : null,
"relationshipOrder" : null,
"restrictedDelete" : false,
"restrictedPicklist" : false,
"scale" : 0,
"soapType" : "xsd:string",
"sortable" : true,
"type" : "phone",
"unique" : false,
"updateable" : true,
"writeRequiresMasterRead" : false
},
"displayLines" : 1,
"tabOrder" : 3,
"type" : "Field",
"value" : "Phone"
} ],
"placeholder" : false,
"required" : false
} ],
"id" : "0AHD000000000AbOAI",
"imageItems" : [ {
"editable" : false,
"label" : "Photo URL",
"layoutComponents" : [ {
"components" : [ ],
"details" : {
"autoNumber" : false,
"byteLength" : 765,
"calculated" : false,
"calculatedFormula" : null,
"cascadeDelete" : false,
"caseSensitive" : false,
"controllerName" : null,
"createable" : false,
"custom" : false,
"defaultValue" : null,
"defaultValueFormula" : null,
"defaultedOnCreate" : false,
"dependentPicklist" : false,
"deprecatedAndHidden" : false,
"digits" : 0,
"displayLocationInDecimal" : false,
"externalId" : false,
"extraTypeInfo" : "imageurl",
"filterable" : true,
"groupable" : true,
"htmlFormatted" : false,
"idLookup" : false,
"inlineHelpText" : null,
"label" : "Photo URL",
"length" : 255,
"mask" : null,
175
sObject CompactLayouts を使用したコンパクトレイアウ
トの取得
リファレンス

===== PAGE 186 =====
"maskType" : null,
"name" : "PhotoUrl",
"nameField" : false,
"namePointing" : false,
"nillable" : true,
"permissionable" : false,
"picklistValues" : [ ],
"precision" : 0,
"queryByDistance" : false,
"referenceTo" : [ ],
"relationshipName" : null,
"relationshipOrder" : null,
"restrictedDelete" : false,
"restrictedPicklist" : false,
"scale" : 0,
"soapType" :
"xsd:string",
"sortable" : true,
"type" : "url",
"unique" : false,
"updateable" : false,
"writeRequiresMasterRead" : false
},
"displayLines" : 1,
"tabOrder" : 1,
"type" : "Field",
"value" : "PhotoUrl"
} ],
"placeholder" : false,
"required" : false
} ],
"label" : "Custom Account Compact Layout",
"name" : "Custom_Account_Compact_Layout"
} ],
"defaultCompactLayoutId" : "0AHD000000000AbOAI",
"recordTypeCompactLayoutMappings" : [ {
"available" : true,
"compactLayoutId" : "0AHD000000000AbOAI",
"compactLayoutName" : "Custom_Account_Compact_Layout",
"recordTypeId" : "012000000000000AAA",
"recordTypeName" : "Master",
"urls" : {
"compactLayout" :
"/services/data/v60.0/sobjects/Account/describe/compactLayouts/012000000000000AAA"
}
} ],
"urls" : {
"primary" : "/services/data/v60.0/sobjects/Account/describe/compactLayouts/primary"
}
}
オブジェクトのコンパクトレイアウトを定義していない場合は、compactLayoutId が Null として返さ
れます。
176
sObject CompactLayouts を使用したコンパクトレイアウ
トの取得
リファレンス

===== PAGE 187 =====
sObject CompactLayouts を使用したヘッダーの返送
sObject CompactLayouts リソースに GET 要求をしたときに返されるヘッダーのみを返します。リソースのコンテ
ンツを取得する前に、前もってヘッダー値を確認できます。このリソースは REST API バージョン 29.0 以降で使
用できます。
構文
URI
特定のオブジェクトのコンパクトレイアウトの説明について
は、/services/data/vXX.X/sobjects/sObject/describe/compactLayouts/ を使用します。
形式
JSON、XML
HTTP のメソッド
HEAD
認証
Authorization: Bearer token
要求のパラメーター
不要
例
リクエストの例
curl -X HEAD --head
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/describe/compactLayouts
-H "Authorization: Bearer token"
sObject Layouts
ページレイアウトとその説明のリストを取得します。特定のオブジェクトのすべてのレイアウト、または特定
のオブジェクトの指定されたレコードタイプに関連するレイアウトの情報を要求できます。
このセクションの内容:
指定されたオブジェクトのレイアウトと説明の取得
単一オブジェクトのレイアウトとその説明のリストを取得します。
指定されたオブジェクトのレイアウトヘッダーの返送
sObject Layouts リソースに GET 要求をしたときに返されるヘッダーのみを返します。リソースのコンテンツ
を取得する前に、前もってヘッダー値を確認できます。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
177
sObject CompactLayouts を使用したヘッダーの返送リファレンス

===== PAGE 188 =====
指定されたオブジェクトのレイアウトと説明の取得
単一オブジェクトのレイアウトとその説明のリストを取得します。
構文
URI
/services/data/vXX.X/sobjects/sObject/describe/layouts/
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
パラメーター
不要
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Battle_Station__c/describe/layouts/
-H "Authorization: Bearer token"
レスポンスボディの例
{
"layouts" : [ {
"buttonLayoutSection" : {
"detailButtons" : [
...
]
},
"detailLayoutSections" : [
...
],
"editLayoutSections" : [
...
],
"feedView" : null,
"highlightsPanelLayoutSection" : null,
"id" : "00ho000000BKMebAAH",
"multirowEditLayoutSections" : [ ],
"offlineLinks" : [ ],
"quickActionList" : {
"quickActionListItems" : [
...
]
},
178
指定されたオブジェクトのレイアウトと説明の取得リファレンス

===== PAGE 189 =====
"relatedContent" : null,
"relatedLists" : [
...
],
"saveOptions" : [ ]
} ],
"recordTypeMappings" : [
...
],
"recordTypeSelectorRequired" : [ false ]
}
指定されたオブジェクトのレイアウトヘッダーの返送
sObject Layouts リソースに GET 要求をしたときに返されるヘッダーのみを返します。リソースのコンテンツを取
得する前に、前もってヘッダー値を確認できます。
構文
URI
/services/data/vXX.X/sobjects/sObject/describe/layouts/
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
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Battle_Station__c/describe/layouts/
-H "Authorization: Bearer token"
複数のレコードタイプを持つオブジェクトの sObject Layouts
複数のレコードタイプが定義されているオブジェクトのページレイアウトのリストとその説明を取得します。
179
指定されたオブジェクトのレイアウトヘッダーの返送リファレンス

===== PAGE 190 =====
複数のレコードタイプを持つオブジェクトのレイアウトと説明の取
得
レイアウトとその説明のリストを取得します。
複数のレコードタイプが定義されているオブジェクトのレイアウトの説明については、recordTypeId を
/services/data/vXX.X/sobjects/sObject/describe/layouts/ の結果から取得できます。
複数のレコードタイプが定義されているオブジェクトの GET 要求は、応答の layouts セクションで null を返し
ます。
構文
URI
/services/data/vXX.X/sobjects/sObject/describe/layouts/recordTypeId
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
パラメーター
不要
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Chocolate__c/describe/layouts/0125c000000oIN9AAM
-H "Authorization: Bearer token"
レスポンスボディの例
{
"buttonLayoutSection" : {
"detailButtons" : [
...
]
},
"detailLayoutSections" : [
...
],
"editLayoutSections" : [
...
],
"feedView" : null,
"highlightsPanelLayoutSection" : null,
"id" : "00ho000000CUJWIAA5",
180
複数のレコードタイプを持つオブジェクトのレイアウト
と説明の取得
リファレンス

===== PAGE 191 =====
"multirowEditLayoutSections" : [ ],
"offlineLinks" : [ ],
"quickActionList" : {
"quickActionListItems" : [
...
]
},
"relatedContent" : null,
"relatedLists" : [
...
],
"saveOptions" : [ ]
}
複数のレコードタイプを持つオブジェクトのレイアウトヘッダーの
返送
sObject Layouts リソースに GET 要求をしたときに返されるヘッダーのみを返します。リソースのコンテンツを取
得する前に、前もってヘッダー値を確認できます。
構文
URI
/services/data/vXX.X/sobjects/sObject/describe/layouts/recordTypeId
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
curl -X HEAD
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Chocolate__c/describe/layouts/0125c000000oIN9AAM
-H "Authorization: Bearer token"
181
複数のレコードタイプを持つオブジェクトのレイアウト
ヘッダーの返送
リファレンス

===== PAGE 192 =====
sObject Global Publisher Layouts
グローバルパブリッシャーレイアウトのリストを取得します。グローバルパブリッシャーレイアウトは、グ
ローバルページ (Home ページなど) のアクションをカスタマイズします。Lightning Experience では、これらのレ
イアウトが [グローバルアクション] メニューに表示されます。
このセクションの内容:
グローバルパブリッシャーレイアウトと説明の取得
グローバルパブリッシャーレイアウトとその説明のリストを取得します。グローバルパブリッシャーレイ
アウトは、グローバルページ (Home ページなど) のアクションをカスタマイズします。Lightning Experience で
は、これらのレイアウトが [グローバルアクション] メニューに表示されます。
すべてのグローバルパブリッシャーレイアウトのヘッダーの返送
sObject Layouts リソースに GET 要求をしたときに返されるヘッダーのみを返します。リソースのコンテンツ
を取得する前に、前もってヘッダー値を確認できます。
グローバルパブリッシャーレイアウトと説明の取得
グローバルパブリッシャーレイアウトとその説明のリストを取得します。グローバルパブリッシャーレイアウ
トは、グローバルページ (Home ページなど) のアクションをカスタマイズします。Lightning Experience では、こ
れらのレイアウトが [グローバルアクション] メニューに表示されます。
構文
URI
/services/data/vXX.X/sobjects/Global/describe/layouts/
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
パラメーター
不要
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Global/describe/layouts/
-H "Authorization: Bearer token"
182
sObject Global Publisher Layoutsリファレンス

===== PAGE 193 =====
レスポンスボディの例
{
"layouts": [
{
"buttonLayoutSection": null,
"detailLayoutSections": [],
"editLayoutSections": [],
"feedView": null,
"highlightsPanelLayoutSection": null,
"id": "00hRO000000Mo6jYAC",
"multirowEditLayoutSections": [],
"offlineLinks": [],
"quickActionList": {
"quickActionListItems": [
{
"accessLevelRequired": null,
"colors": [
{
"color": "65CAE4",
"context": "primary",
"theme": "theme4"
}
],
"iconUrl": null,
"icons": [
{
"contentType": "image/svg+xml",
"height": 0,
"theme": "theme4",
"url":
"https://rockyroads.test1.my.pc-rnd.salesforce.com/img/icon/t4v35/action/share_post.svg",
"width": 0
},
...
],
"label": "Post",
"miniIconUrl": "",
"quickActionName": "FeedItem.TextPost",
"targetSobjectType": null,
"type": "Post",
"urls": {}
},
...
]
},
"relatedContent": null,
"relatedLists": [],
"saveOptions": []
}
],
"recordTypeMappings": [],
"recordTypeSelectorRequired": [
183
グローバルパブリッシャーレイアウトと説明の取得リファレンス

===== PAGE 194 =====
false
]
}
すべてのグローバルパブリッシャーレイアウトのヘッダーの返送
sObject Layouts リソースに GET 要求をしたときに返されるヘッダーのみを返します。リソースのコンテンツを取
得する前に、前もってヘッダー値を確認できます。
構文
URI
/services/data/vXX.X/sobjects/Global/describe/layouts/
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
curl -X HEAD
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Global/describe/layouts/
-H "Authorization: Bearer token"
sObject PlatformAction
PlatformAction の説明を返します。PlatformAction は、参照のみの仮想オブジェクトです。ユーザー、コンテキス
ト、デバイス形式、レコード ID に応じて、UI に表示するアクションを照会できるようにします。たとえば、
標準およびカスタムボタン、クイックアクション、生産性アクションなどを照会できます。このリソースは
API バージョン 33.0 以降で使用できます。
このリソースで可能な操作はクエリのみです。
構文
URI
/services/data/vXX.X/sobjects/PlatformAction
184
すべてのグローバルパブリッシャーレイアウトのヘッ
ダーの返送
リファレンス

===== PAGE 195 =====
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
リクエストボディ
None
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
sObject Quick Actions
オブジェクトのアクションとアクションの詳細にアクセスします。このリソースは REST API バージョン 28.0 以
降で使用できます。
アクションを使用する場合は、「Quick Actions」も参照してください。
このセクションの内容:
sObject Quick Actions の取得
グローバルアクションだけでなく特定のオブジェクトのアクションをします。このリソースは REST API バー
ジョン 28.0 以降で使用できます。
sObject Quick Actions を使用したヘッダーの返送
sObject Quick Actions リソースに GET 要求を送信したときに返されるヘッダーのみを返します。リソースのコ
ンテンツを取得する前に、ヘッダー値を確認できます。このリソースは REST API バージョン 28.0 以降で使用
できます。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
sObject Quick Actions の取得
グローバルアクションだけでなく特定のオブジェクトのアクションをします。このリソースは REST API バージョ
ン 28.0 以降で使用できます。
リソースからは、要求したアクションに加え、すべてのアクション (グローバルおよび標準) が返されます。
アクションを使用する場合は、「Quick Actions」も参照してください。
185
sObject Quick Actionsリファレンス

===== PAGE 196 =====
構文
URI
/services/data/vXX.X/sobjects/sObject/quickActions/
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
パラメーター
不要
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/quickActions/
-H "Authorization: Bearer token"
sObject Quick Actions を使用したヘッダーの返送
sObject Quick Actions リソースに GET 要求を送信したときに返されるヘッダーのみを返します。リソースのコンテ
ンツを取得する前に、ヘッダー値を確認できます。このリソースは REST API バージョン 28.0 以降で使用できま
す。
リソースからは、要求したアクションに加え、すべてのアクション (グローバルおよび標準) が返されます。
アクションを使用する場合は、「Quick Actions」も参照してください。
構文
URI
/services/data/vXX.X/sobjects/sObject/quickActions/
形式
JSON、XML
HTTP のメソッド
HEAD
認証
Authorization: Bearer token
パラメーター
不要
186
sObject Quick Actions を使用したヘッダーの返送リファレンス

===== PAGE 197 =====
例
リクエストの例
curl -X HEAD --head
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/quickActions/
-H "Authorization: Bearer token"
特定の sObject Quick Actions
オブジェクトに対する特定のアクションにアクセスします。このリソースで POST メソッドを使用することで、
オブジェクトのクイックアクションを使用してレコードを作成できます。
アクションを使用する場合は、「Quick Actions」も参照してください。
このセクションの内容:
特定の sObject Quick Actions の取得
オブジェクトに対する特定のアクションと、そのアクションの詳細を取得します。このリソースは REST API
バージョン 28.0 以降で使用できます。
特定の sObject Quick Actions を使用したレコードの作成
リクエストボディに含まれる項目値に基づいて、特定のクイックアクションによりレコードを作成します。
このリソースは REST API バージョン 28.0 以降で使用できます。
特定の sObject Quick Actions を使用したヘッダーの返送
sObject Quick Actions リソースに GET 要求を送信したときに返されるヘッダーのみを返します。リソースのコ
ンテンツを取得する前に、ヘッダー値を確認できます。このリソースは REST API バージョン 28.0 以降で使用
できます。
特定の sObject Quick Actions の取得
オブジェクトに対する特定のアクションと、そのアクションの詳細を取得します。このリソースは REST API バー
ジョン 28.0 以降で使用できます。
アクションを使用する場合は、「Quick Actions」も参照してください。
構文
URI
/services/data/vXX.X/sobjects/sObject/quickActions/actionName
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
187
特定の sObject Quick Actionsリファレンス

===== PAGE 198 =====
パラメーター
不要
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/quickActions/CreateContact
-H "Authorization: Bearer token"
特定の sObject Quick Actions を使用したレコードの作成
リクエストボディに含まれる項目値に基づいて、特定のクイックアクションによりレコードを作成します。こ
のリソースは REST API バージョン 28.0 以降で使用できます。
アクションを使用する場合は、「Quick Actions」も参照してください。
構文
URI
/services/data/vXX.X/sobjects/sObject/quickActions/actionName
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
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/quickActions/CreateContact
-H 'Authorization: Bearer token -H "Content-Type: application/json" -d @newcontact.json'
リクエストボディの例
{
"contextId" : "001D000000JRSGf",
"record" : { "LastName" : "Smith" }
}
188
特定の sObject Quick Actions を使用したレコードの作成リファレンス

===== PAGE 199 =====
特定の sObject Quick Actions を使用したヘッダーの返送
sObject Quick Actions リソースに GET 要求を送信したときに返されるヘッダーのみを返します。リソースのコンテ
ンツを取得する前に、ヘッダー値を確認できます。このリソースは REST API バージョン 28.0 以降で使用できま
す。
アクションを使用する場合は、「Quick Actions」も参照してください。
構文
URI
/services/data/vXX.X/sobjects/sObject/quickActions/actionName
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
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/quickActions/CreateContact
-H "Authorization: Bearer token"
sObject Quick Action の詳細
オブジェクトに対する特定のアクションの説明の詳細にアクセスします。
アクションを使用する場合は、「Quick Actions」も参照してください。
このセクションの内容:
sObject Quick Action の詳細の取得
特定のアクションの説明の詳細を返します。このリソースは REST API バージョン 28.0 以降で使用できます。
sObject Quick Actions の詳細を使用したヘッダーの返送
sObject Quick Actions リソースに GET 要求を送信したときに返されるヘッダーのみを返します。リソースのコ
ンテンツを取得する前に、ヘッダー値を確認できます。このリソースは REST API バージョン 28.0 以降で使用
できます。
189
特定の sObject Quick Actions を使用したヘッダーの返送リファレンス

===== PAGE 200 =====
sObject Quick Action の詳細の取得
特定のアクションの説明の詳細を返します。このリソースは REST API バージョン 28.0 以降で使用できます。
アクションを使用する場合は、「Quick Actions」も参照してください。
構文
URI
/services/data/vXX.X/sobjects/sObject/quickActions/actionName/describe/
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
パラメーター
不要
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/quickActions/CreateContact/describe/
-H "Authorization: Bearer token"
sObject Quick Actions の詳細を使用したヘッダーの返送
sObject Quick Actions リソースに GET 要求を送信したときに返されるヘッダーのみを返します。リソースのコンテ
ンツを取得する前に、ヘッダー値を確認できます。このリソースは REST API バージョン 28.0 以降で使用できま
す。
アクションを使用する場合は、「Quick Actions」も参照してください。
構文
URI
/services/data/vXX.X/sobjects/sObject/quickActions/actionName/describe/
形式
JSON、XML
HTTP のメソッド
HEAD
認証
Authorization: Bearer token
190
sObject Quick Action の詳細の取得リファレンス

===== PAGE 201 =====
パラメーター
不要
例
リクエストの例
curl -X HEAD --head
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/quickActions/CreateContact/describe/
-H "Authorization: Bearer token"
sObject Quick Action のデフォルト値
オブジェクトへの特定のアクションに対する、デフォルト値 (項目のデフォルト値を含む) を取得します。
アクションを使用する場合は、「Quick Actions」も参照してください。
このセクションの内容:
sObject Quick Action のデフォルト値の取得
特定のアクションのデフォルト値 (項目の値も含む) を返します。このリソースは REST API バージョン 28.0 以
降で使用できます。
sObject Quick Action のデフォルト値を使用したヘッダーの返送
sObject Quick Actions リソースに GET 要求を送信したときに返されるヘッダーのみを返します。リソースのコ
ンテンツを取得する前に、ヘッダー値を確認できます。このリソースは REST API バージョン 28.0 以降で使用
できます。
sObject Quick Action のデフォルト値の取得
特定のアクションのデフォルト値 (項目の値も含む) を返します。このリソースは REST API バージョン 28.0 以降
で使用できます。
アクションを使用する場合は、「Quick Actions」も参照してください。
構文
URI
/services/data/vXX.X/sobjects/sObject/quickActions/actionName/defaultValues/
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
191
sObject Quick Action のデフォルト値リファレンス

===== PAGE 202 =====
パラメーター
不要
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/quickActions/CreateContact/defaultValues/
-H "Authorization: Bearer token"
sObject Quick Action のデフォルト値を使用したヘッダーの返送
sObject Quick Actions リソースに GET 要求を送信したときに返されるヘッダーのみを返します。リソースのコンテ
ンツを取得する前に、ヘッダー値を確認できます。このリソースは REST API バージョン 28.0 以降で使用できま
す。
アクションを使用する場合は、「Quick Actions」も参照してください。
構文
URI
/services/data/vXX.X/sobjects/sObject/quickActions/actionName/defaultValues/
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
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/quickActions/CreateContact/defaultValues/
-H "Authorization: Bearer token"
sObject Quick Action の ID 別デフォルト値
オブジェクトに対する特定のアクションのデフォルト値を評価します。応答には項目のデフォルト値も含まれ
ます。
192
sObject Quick Action のデフォルト値を使用したヘッダー
の返送
リファレンス

===== PAGE 203 =====
アクションを使用する場合は、「Quick Actions」も参照してください。
このセクションの内容:
sObject Quick Action の ID 別デフォルト値の取得
context_id オブジェクト固有のアクションのデフォルト値を返します。このリソースは REST API バージョ
ン 29.0 以降で使用できます。
sObject Quick Action の ID 別デフォルト値を使用したヘッダーの返送
sObject Quick Actions リソースに GET 要求を送信したときに返されるヘッダーのみを返します。リソースのコ
ンテンツを取得する前に、ヘッダー値を確認できます。このリソースは REST API バージョン 29.0 以降で使用
できます。
sObject Quick Action の ID 別デフォルト値の取得
context_id オブジェクト固有のアクションのデフォルト値を返します。このリソースは REST API バージョン
29.0 以降で使用できます。
API バージョン 28.0 で、アクションのデフォルト値を評価するに
は、/services/data/vXX.X/sobjects/sObject/quickActions/action_name/defaultValues/parent_id
を使用します。
アクションを使用する場合は、「Quick Actions」も参照してください。
構文
URI
/services/data/vXX.X/sobjects/sObject/quickActions/actionName/defaultValues/contextId
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
パラメーター
不要
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/quickActions/CreateContact/defaultValues/001D000000JRWBd
-H "Authorization: Bearer token"
193
sObject Quick Action の ID 別デフォルト値の取得リファレンス

===== PAGE 204 =====
sObject Quick Action の ID 別デフォルト値を使用したヘッダーの返送
sObject Quick Actions リソースに GET 要求を送信したときに返されるヘッダーのみを返します。リソースのコンテ
ンツを取得する前に、ヘッダー値を確認できます。このリソースは REST API バージョン 29.0 以降で使用できま
す。
API バージョン 28.0 で、アクションのデフォルト値を評価するに
は、/services/data/vXX.X/sobjects/sObject/quickActions/action_name/defaultValues/parent_id
を使用します。
アクションを使用する場合は、「Quick Actions」も参照してください。
構文
URI
/services/data/vXX.X/sobjects/sObject/quickActions/actionName/defaultValues/contextId
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
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/quickActions/CreateContact/defaultValues/001D000000JRWBd
-H "Authorization: Bearer token"
sObject Rich Text Image Get
特定のレコードの特定のリッチテキストエリア項目から、指定された画像データを取得します。画像を取得す
るには、レコードの画像がリッチテキストエリア項目にアップロードされている必要があります。
構文
URI
/services/data/vXX.X/sobjects/sObject/id/richTextImageFields/fieldName/contentReferenceId
形式
バイナリデータ
194
sObject Quick Action の ID 別デフォルト値を使用したヘッ
ダーの返送
リファレンス

===== PAGE 205 =====
HTTP メソッド
GET
認証
Authorization: Bearer token
パラメーター
説明パラメーター
レコードの標準オブジェクトの名前を示します。sObjectName
オブジェクトの ID。id
リッチテキストエリア項目の名前。fieldName
リッチテキストエリア項目内の画像を一意に識別する参照 ID。
オブジェクトの情報を取得することで、参照を取得できます。次の記
述はリッチテキストエリア項目のコンテンツを示しています。次に例
を示します。
{
"attributes" : {
contentReferenceId
"type" : "Lead",
"url" :
"/services/data/v60.0/sobjects/Lead/00QRM000003ZfDb2AK"
},
"Id" : "00QRM000003ZfDb2AK",
...
"ContactPhoto__c" :
"Sarah Loehr and her two dogs.
<img alt=\"Sarah Loehr.\"
src=\"https://MyDomainName.file.force.com/servlet/rtaImage?
eid=00QRM000003ZfDb&amp;
feoid=00NRM000001E73j&amp;
refid=0EMRM00000002Ip\"></img>"
}
画像の refid パラメーター (この例では 0EMRM00000002Ip) が
contentReferenceId になります。
例
リッチテキストエリア項目から blob データを取得する例は、「リッチテキストエリア項目から画像を取得」
(ページ 78)を参照してください。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
195
sObject Rich Text Image Getリファレンス

===== PAGE 206 =====
sObject Relationships
使い慣れた URL を介してオブジェクトリレーションをトラバースし、レコードにアクセスします。トラバース
されたリレーション項目に関連付けられたレコードを取得、更新、または削除できます。複数の関連レコード
がある場合、関連付けられたレコードの完全なセットを取得できます。このリソースは REST API バージョン 36.0
以降で使用できます。
このセクションの内容:
sObject Relationships を使用したレコードの取得
指定されたオブジェクト、レコード ID、リレーション項目に基づいてレコードを取得します。レコードの
項目と項目値が、レスポンスボディで返されます。複数の関連レコードがある場合、関連付けられたレコー
ドの完全なセットを取得できます。
sObject Relationships を使用したレコードの更新
指定されたオブジェクト、レコード ID、リレーション項目名に基づいて親レコードを更新します。リクエ
ストボディで提供された項目値が、レコード内の既存の値と置き換えられます。レコードを更新するとき
にトラバースできるのは、子から親へのリレーションだけです。
sObject Relationships を使用したレコードの削除
指定されたオブジェクト、レコード ID、リレーション項目名に基づいて親レコードを削除します。レコー
ドを削除するときにトラバースできるのは、子から親へのリレーションだけです。
sObject Relationships を使用したレコードの取得
指定されたオブジェクト、レコード ID、リレーション項目に基づいてレコードを取得します。レコードの項目
と項目値が、レスポンスボディで返されます。複数の関連レコードがある場合、関連付けられたレコードの完
全なセットを取得できます。
リレーション項目に関連付けられたレコードがない場合、404 エラー応答が返されます。リレーション項目が
正常に複数のレコードに解決され、リレーションセットが存在しない場合、200 応答が返されます。項目レベ
ルセキュリティによってコンシューマーに表示されないか存在しない項目でfields パラメーターが使用され
ている場合、400 エラー応答が返されます。その他のエラーメッセージについては、「状況コードとエラー応
答」を参照してください。
構文
URI
/services/data/vXX.X/sobjects/sObject/id/relationshipFieldName
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
196
sObject Relationshipsリファレンス

===== PAGE 207 =====
パラメーター
説明パラメーター
オブジェクトの名前。たとえば、Account などです。sObject
レコードの識別子。たとえば、001R0000005hDFYIA2 のようになり
ます。
id
リレーションを含む項目の名前。たとえば、Opportunities などで
す。
relationshipFieldFame
GET では省略可能です。レスポンスボディで返される関連するリレー
ションレコードの項目のカンマ区切りのリスト。次に例を示します。
/services/data/v60.0/sobjects/sObject/id/relationship
field?fields=field1,field2
fields
例
sObject Relationships を使用してリレーション項目にアクセスする例については、「フレンドリー URL を使用した
リレーションのトラバース」を参照してください。
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Merchandise__c/a01D000000INjVe/Distributor__r
-H “Authorization: Bearer token”
レスポンスボディの例
レスポンスボディはリレーション項目に関連付けられたレコードのコンテンツです。カスタムオブジェク
ト Merchandise__c のリレーション項目に関連付けられた Distributor__c レコードを返す、簡単なリレーション
トラバースの要求と JSON レスポンスボディの例を次に示します。
{
"attributes" :
{
"type" : "Distributor__c",
"url" : "/services/data/v60.0/sobjects/Distributor__c/a03D0000003DUhcIAG"
},
"Id" : "a03D0000003DUhcIAG",
"OwnerId" : "005D0000001KyEIIA0",
"IsDeleted" : false,
"Name" : "Distributor1",
"CreatedDate" : "2011-12-16T17:43:01.000+0000",
"CreatedById" : "005D0000001KyEIIA0",
"LastModifiedDate" : "2011-12-16T17:43:01.000+0000",
"LastModifiedById" : "005D0000001KyEIIA0",
"SystemModstamp" : "2011-12-16T17:43:01.000+0000",
197
sObject Relationships を使用したレコードの取得リファレンス

===== PAGE 208 =====
"Location__c" : "San Francisco"
}
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
sObject Relationships を使用したレコードの更新
指定されたオブジェクト、レコード ID、リレーション項目名に基づいて親レコードを更新します。リクエスト
ボディで提供された項目値が、レコード内の既存の値と置き換えられます。レコードを更新するときにトラ
バースできるのは、子から親へのリレーションだけです。
項目レベルセキュリティによってコンシューマーに表示されないか存在しない項目でfields パラメーターが
使用されている場合、400 エラー応答が返されます。その他のエラーメッセージについては、「状況コードと
エラー応答」を参照してください。
構文
URI
/services/data/vXX.X/sobjects/sObject/id/relationshipFieldName
形式
JSON、XML
HTTP のメソッド
PATCH
認証
Authorization: Bearer token
パラメーター
説明パラメーター
オブジェクトの名前。たとえば、Contact などです。sObject
レコードの識別子。たとえば、003R0000005hDFYIA2  (Contact の ID)
などです。
id
リレーションを含む項目の名前。たとえば、Account などです。
Account は、リレーション名は子 Contact オブジェクトの名前です。
relationshipFieldName
例
PATCH を使用してレコードを更新する例については、
198
sObject Relationships を使用したレコードの更新リファレンス

===== PAGE 209 =====
「レコードを更新する」を参照してください。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
sObject Relationships を使用したレコードの削除
指定されたオブジェクト、レコード ID、リレーション項目名に基づいて親レコードを削除します。レコードを
削除するときにトラバースできるのは、子から親へのリレーションだけです。
項目レベルセキュリティによってコンシューマーに表示されないか存在しない項目でfields パラメーターが
使用されている場合、400 エラー応答が返されます。その他のエラーメッセージについては、「状況コードと
エラー応答」を参照してください。
構文
URI
/services/data/vXX.X/sobjects/sObject/id/relationshipFieldName
形式
JSON、XML
HTTP のメソッド
DELETE
認証
Authorization: Bearer token
パラメーター
説明パラメーター
オブジェクトの名前。たとえば、Contact などです。sObject
レコードの識別子。たとえば、003R0000005hDFYIA2  (Contact の ID)
などです。
id
リレーションを含む項目の名前。たとえば、Account などです。
Account は、リレーション名は子 Contact オブジェクトの名前です。
relationshipFieldName
親レコードを削除すると、親レコードと主従関係があるすべての子レコードが削除されます。
199
sObject Relationships を使用したレコードの削除リファレンス

===== PAGE 210 =====
例
sObject Relationships を使用してリレーションレコードを削除する例については、「フレンドリー URL を使用した
リレーションのトラバース」を参照してください。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
sObjects Suggested Articles
ケース、作業指示、作業指示品目の推奨記事の結果を返します。この推奨は、レコードが保存されて ID が割
り当てられる前に入力されたタイトル、説明、またはその他の情報内の一般的なキーワードに基づいて行われ
ます。このリソースは REST API バージョン 30.0 以降で使用できます。
Salesforce ナレッジが組織で有効になっている必要があります。ユーザーの「記事の参照」権限が有効化されて
いる必要があります。ユーザーが参照する権限を持つデータカテゴリおよび記事タイプに基づいて、ユーザー
がアクセスできる記事のみが推奨記事に含まれます。
記事は、関連アルゴリズムに基づいて推奨されます。suggestedArticles リソースは、ケース、作業指示、
または作業指示品目に関係する記事の ID を取得するように設計されています。この ID は、表示用の記事デー
タを取得するために使用することよりも、他のサービスと併用することが意図されています。
構文
URI
/services/data/vXX.X/sobjects/sObject/suggestedArticles
?language=articleLanguage&subject=subject&description=description。
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
200
sObjects Suggested Articlesリファレンス

===== PAGE 211 =====
説明パラメーター
省略可能。目的の記事のデータカテゴリグループの名前とデータカテ
ゴリ API 名 (カテゴリタイトルではない)。この構文は
categories
categories={"Group":"Category"} です。URL 内の文字を符号化
する必要がある場合があります。次に例を示します。
categories=%7B%22Regions%22%3A%22Asia%22%2C%22
Products%22%3A%22Laptops%22%7D
同じデータカテゴリグループを複数回指定することはできません。た
だし、複数のデータカテゴリグループとデータカテゴリのペアを指定
できます。例:
categories={"Regions":"Asia","Products":"Laptops"}.
説明のテキスト。既存の ID がない新規レコードに対してのみ有効で、
subject が null の場合は必須です。記事の推奨は、件名、説明、また
はその両方に含まれる一般的なキーワードに基づいて行われます。
description
必須。記事が作成されている言語。language
省略可能。返される推奨記事の最大数を指定します。limit
省略可能。記事の公開状況。有効な値は次のとおりです。publishStatus
• Draft  – 非公開
• Online  – Salesforce ナレッジに公開
• Archived
件名のテキスト。既存の ID がない新規レコードに対してのみ有効で、
description が null の場合は必須です。記事の推奨は、件名、説明、
subject
またはその両方に含まれる一般的なキーワードに基づいて行われま
す。
省略可能。返される記事のトピック。たとえば、
topics=outlook&topics=email です。
topics
省略可能。返される記事の検証状況。validationStatus
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Case/suggestedArticles?
language=en_US&subject=orange+banana&articleTypes=ka0&articleTypes=ka1
-H "Authorization: Bearer token"
201
sObjects Suggested Articlesリファレンス

===== PAGE 212 =====
レスポンスボディの例
[ {
"attributes" : {
"type" : "KnowledgeArticleVersion",
"url" : "/services/data/v60.0/sobjects/KnowledgeArticleVersion/ka0D00000004CcQ"
"Id" : "ka0D00000004CcQ"
}, {
"attributes" : {
"type" : "KnowledgeArticleVersion",
"url" : "/services/data/v60.0/sobjects/KnowledgeArticleVersion/ka0D00000004CXo"
},
"Id" : "ka0D00000004CXo"
} ]
sObjects Suggested Articles by ID
記事 ID を入力すると、入力した ID と類似する情報を提供するレコードを検索できます。このリソースは REST
API バージョン 30.0 以降で使用できます。
Salesforce ナレッジが組織で有効になっている必要があります。ユーザーの「記事の参照」権限が有効化されて
いる必要があります。ユーザーが参照する権限を持つデータカテゴリおよび記事タイプに基づいて、ユーザー
がアクセスできる記事のみが推奨記事に含まれます。
記事は、関連アルゴリズムに基づいて推奨されます。suggestedArticles リソースは、ケース、作業指示、
または作業指示品目に関係する記事の ID を取得するように設計されています。この ID は、表示用の記事デー
タを取得するために使用することよりも、他のサービスと併用することが意図されています。
構文
URI
/services/data/vXX.X/sobjects/sObject/ID/suggestedArticles?language=articleLanguage
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
202
sObjects Suggested Articles by IDリファレンス

===== PAGE 213 =====
説明パラメーター
メーターに複数の値を指定できます。たとえば、
articleTypes=ka0&articleTypes=ka1 です。
省略可能。目的の記事のデータカテゴリグループの名前とデータカテ
ゴリ API 名 (カテゴリタイトルではない)。この構文は
categories
categories={"Group":"Category"} です。URL 内の文字を符号化
する必要がある場合があります。次に例を示します。
categories=%7B%22Regions%22%3A%22Asia%22%2C%22
Products%22%3A%22Laptops%22%7D
同じデータカテゴリグループを複数回指定することはできません。た
だし、複数のデータカテゴリグループとデータカテゴリのペアを指定
できます。例:
categories={"Regions":"Asia","Products":"Laptops"}.
説明のテキスト。既存の ID がない新規レコードに対してのみ有効で、
subject が null の場合は必須です。記事の推奨は、件名、説明、また
はその両方に含まれる一般的なキーワードに基づいて行われます。
description
必須。記事が作成されている言語。language
省略可能。返される推奨記事の最大数を指定します。limit
省略可能。記事の公開状況。有効な値は次のとおりです。publishStatus
• Draft  – 非公開
• Online  – Salesforce ナレッジに公開
• Archived
件名のテキスト。既存の ID がない新規レコードに対してのみ有効で、
description が null の場合は必須です。記事の推奨は、件名、説明、
subject
またはその両方に含まれる一般的なキーワードに基づいて行われま
す。
省略可能。返される記事のトピック。たとえば、
topics=outlook&topics=email です。
topics
省略可能。返される記事の検証状況。validationStatus
例
レスポンスボディの例
[ {
"attributes" : {
"type" : "KnowledgeArticleVersion",
"url" : "/services/data/v60.0/sobjects/KnowledgeArticleVersion/ka0D00000004CcQ"
203
sObjects Suggested Articles by IDリファレンス

===== PAGE 214 =====
"Id" : "ka0D00000004CcQ"
}, {
"attributes" : {
"type" : "KnowledgeArticleVersion",
"url" : "/services/data/v60.0/sobjects/KnowledgeArticleVersion/ka0D00000004CXo"
},
"Id" : "ka0D00000004CXo"
} ]
sObject User Password
指定されたユーザー ID に基づいてユーザーパスワードにアクセスします。HTTP メソッドに基づき、ユーザー
パスワードの有効期限の状況を設定、リセット、または取得します。パスワードの有効期限の状況を取得する
には GET メソッド、パスワードを設定するには POST メソッド、パスワードのリセットを開始するには DELETE
メソッドを使用します。
このセクションの内容:
ユーザーパスワードの有効期限の状況の取得
指定されたユーザー ID に基づいてユーザーパスワードの有効期限の状況を取得します。レスポンスボディ
で True または False の値が返されます。このリソースは REST API バージョン 24.0 以降で使用できます。
ユーザーのパスワードの設定
指定されたユーザー ID に基づいてユーザーのパスワードを設定します。リクエストボディで提供されたパ
スワードが、ユーザーの既存のパスワードと置き換えられます。このリソースは REST API バージョン 24.0 以
降で使用できます。
ユーザーのパスワードのリセット
指定されたユーザー ID に基づいて、ユーザーのパスワードのリセットを開始します。ユーザーの現在のパ
スワードが無効となり、ユーザーに、パスワードのリセットのリンクが記載されたメールが送信されます。
再度ログインするには、パスワードの再設定を終了する必要があります。このリソースは REST API バージョ
ン 24.0 以降で使用できます。
sObject User Password を使用したヘッダーの返送
sObject User Password リソースに GET 要求を送信したときに返されるヘッダーのみを返します。この操作によ
り、コンテンツ自体を取得する前に、GET 要求で返されたヘッダー値を確認できます。このリソースは REST
API バージョン 24.0 以降で使用できます。
ユーザーパスワードの有効期限の状況の取得
指定されたユーザー ID に基づいてユーザーパスワードの有効期限の状況を取得します。レスポンスボディで
True または False の値が返されます。このリソースは REST API バージョン 24.0 以降で使用できます。
セッションにユーザー情報にアクセスする権限がない場合、INSUFFICIENT_ACCESS エラーが返されます。
204
sObject User Passwordリファレンス

===== PAGE 215 =====
構文
URI
/services/data/vXX.X/sobjects/User/userId/password
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
パラメーター
不要
例
パスワード情報の取得、パスワードの設定、パスワードのリセットの例は、「ユーザーパスワードを管理す
る」 (ページ 88)を参照してください。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
ユーザーのパスワードの設定
指定されたユーザー ID に基づいてユーザーのパスワードを設定します。リクエストボディで提供されたパス
ワードが、ユーザーの既存のパスワードと置き換えられます。このリソースは REST API バージョン 24.0 以降で
使用できます。
1 つの要求で設定可能なパスワードは 1 つのみです。新しいパスワードは、組織のパスワードポリシーに準拠
する必要があり、そうでない場合は INVALID_NEW_PASSWORD エラーが返されます。
セッションにユーザー情報にアクセスする権限がない場合、INSUFFICIENT_ACCESS エラーが返されます。
構文
URI
/services/data/vXX.X/sobjects/User/userId/password
形式
JSON、XML
HTTP のメソッド
POST
認証
Authorization: Bearer token
パラメーター
不要
205
ユーザーのパスワードの設定リファレンス

===== PAGE 216 =====
例
パスワード情報の取得、パスワードの設定、パスワードのリセットの例は、「ユーザーパスワードを管理す
る」 (ページ 88)を参照してください。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
ユーザーのパスワードのリセット
指定されたユーザー ID に基づいて、ユーザーのパスワードのリセットを開始します。ユーザーの現在のパス
ワードが無効となり、ユーザーに、パスワードのリセットのリンクが記載されたメールが送信されます。再度
ログインするには、パスワードの再設定を終了する必要があります。このリソースは REST API バージョン 24.0
以降で使用できます。
ユーザーの一時的なパスワードが自動生成され、レスポンスボディ内に返されます。ユーザーがメールのリン
クにアクセスできない場合、仮のパスワードでログインすることでパスワードのリセットを完了できます。
セッションにユーザー情報にアクセスする権限がない場合、INSUFFICIENT_ACCESS エラーが返されます。
構文
URI
/services/data/vXX.X/sobjects/User/userId/password
形式
JSON、XML
HTTP のメソッド
DELETE
認証
Authorization: Bearer token
パラメーター
不要
例
パスワード情報の取得、パスワードの設定、パスワードのリセットの例は、「ユーザーパスワードを管理す
る」 (ページ 88)を参照してください。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
206
ユーザーのパスワードのリセットリファレンス

===== PAGE 217 =====
sObject User Password を使用したヘッダーの返送
sObject User Password リソースに GET 要求を送信したときに返されるヘッダーのみを返します。この操作により、
コンテンツ自体を取得する前に、GET 要求で返されたヘッダー値を確認できます。このリソースは REST API バー
ジョン 24.0 以降で使用できます。
セッションにユーザー情報にアクセスする権限がない場合、INSUFFICIENT_ACCESS エラーが返されます。
構文
URI
/services/data/vXX.X/sobjects/User/userId/password
形式
JSON、XML
HTTP のメソッド
HEAD
認証
Authorization: Bearer token
パラメーター
不要
例
パスワード情報の取得、パスワードの設定、パスワードのリセットの例は、「ユーザーパスワードを管理す
る」 (ページ 88)を参照してください。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
sObject セルフサービスユーザーのパスワード
指定されたユーザー ID に基づいてセルフサービスユーザーパスワードにアクセスします。HTTP メソッドに基
づき、セルフサービスユーザーパスワードの有効期限の状況を設定、リセット、または取得します。パスワー
ドの有効期限の状況を取得するには GET メソッド、パスワードを設定するには POST メソッド、パスワードの
リセットを開始するには DELETE メソッドを使用します。
このセクションの内容:
セルフサービスユーザーパスワードの有効期限の状況の取得
指定されたユーザー ID に基づいてセルフサービスユーザーパスワードの有効期限の状況を取得します。レ
スポンスボディで True または False の値が返されます。このリソースは REST API バージョン 24.0 以降で使用
できます。
207
sObject User Password を使用したヘッダーの返送リファレンス

===== PAGE 218 =====
セルフサービスユーザーパスワードの設定
指定されたユーザー ID に基づいてセルフサービスユーザーのパスワードを設定します。リクエストボディ
で提供されたパスワードが、ユーザーの既存のパスワードと置き換えられます。このリソースは REST API
バージョン 24.0 以降で使用できます。
セルフサービスユーザーのパスワードのリセット
指定されたユーザー ID に基づいて、セルフサービスユーザーのパスワードのリセットを開始します。ユー
ザーの現在のパスワードが無効となり、ユーザーに、パスワードのリセットのリンクが記載されたメール
が送信されます。再度ログインするには、パスワードの再設定を終了する必要があります。このリソース
は REST API バージョン 24.0 以降で使用できます。
sObject Self-Service User Password を使用したヘッダーの返送
sObject Self-Service User Password リソースに GET 要求を送信したときに返されるヘッダーのみを返します。この
操作により、コンテンツ自体を取得する前に、GET 要求で返されたヘッダー値を確認できます。このリソー
スは REST API バージョン 24.0 以降で使用できます。
セルフサービスユーザーパスワードの有効期限の状況の取得
指定されたユーザー ID に基づいてセルフサービスユーザーパスワードの有効期限の状況を取得します。レス
ポンスボディで True または False の値が返されます。このリソースは REST API バージョン 24.0 以降で使用できま
す。
セッションにユーザー情報にアクセスする権限がない場合、INSUFFICIENT_ACCESS エラーが返されます。
構文
URI
/services/data/vXX.X/sobjects/SelfServiceUser/selfServiceUserId/password
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
パラメーター
不要
例
パスワード情報の取得、パスワードの設定、パスワードのリセットの例は、「ユーザーパスワードを管理す
る」 (ページ 88)を参照してください。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
208
セルフサービスユーザーパスワードの有効期限の状況の
取得
リファレンス

===== PAGE 219 =====
セルフサービスユーザーパスワードの設定
指定されたユーザー ID に基づいてセルフサービスユーザーのパスワードを設定します。リクエストボディで
提供されたパスワードが、ユーザーの既存のパスワードと置き換えられます。このリソースは REST API バージョ
ン 24.0 以降で使用できます。
1 つの要求で設定可能なパスワードは 1 つのみです。新しいパスワードは、組織のパスワードポリシーに準拠
する必要があり、そうでない場合は INVALID_NEW_PASSWORD エラーが返されます。
セッションにユーザー情報にアクセスする権限がない場合、INSUFFICIENT_ACCESS エラーが返されます。
構文
URI
/services/data/vXX.X/sobjects/SelfServiceUser/selfServiceUserId/password
形式
JSON、XML
HTTP のメソッド
POST
認証
Authorization: Bearer token
パラメーター
不要
例
パスワード情報の取得、パスワードの設定、パスワードのリセットの例は、「ユーザーパスワードを管理す
る」 (ページ 88)を参照してください。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
セルフサービスユーザーのパスワードのリセット
指定されたユーザー ID に基づいて、セルフサービスユーザーのパスワードのリセットを開始します。ユーザー
の現在のパスワードが無効となり、ユーザーに、パスワードのリセットのリンクが記載されたメールが送信さ
れます。再度ログインするには、パスワードの再設定を終了する必要があります。このリソースは REST API バー
ジョン 24.0 以降で使用できます。
ユーザーの一時的なパスワードが自動生成され、レスポンスボディ内に返されます。ユーザーがメールのリン
クにアクセスできない場合、仮のパスワードでログインすることでパスワードのリセットを完了できます。
セッションにユーザー情報にアクセスする権限がない場合、INSUFFICIENT_ACCESS エラーが返されます。
209
セルフサービスユーザーパスワードの設定リファレンス

===== PAGE 220 =====
構文
URI
/services/data/vXX.X/sobjects/SelfServiceUser/selfServiceUserId/password
形式
JSON、XML
HTTP のメソッド
DELETE
認証
Authorization: Bearer token
パラメーター
不要
例
パスワード情報の取得、パスワードの設定、パスワードのリセットの例は、「ユーザーパスワードを管理す
る」 (ページ 88)を参照してください。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
sObject Self-Service User Password を使用したヘッダーの返送
sObject Self-Service User Password リソースに GET 要求を送信したときに返されるヘッダーのみを返します。この操
作により、コンテンツ自体を取得する前に、GET 要求で返されたヘッダー値を確認できます。このリソースは
REST API バージョン 24.0 以降で使用できます。
セッションにユーザー情報にアクセスする権限がない場合、INSUFFICIENT_ACCESS エラーが返されます。
構文
URI
/services/data/vXX.X/sobjects/SelfServiceUser/selfServiceUserId/password
形式
JSON、XML
HTTP のメソッド
HEAD
認証
Authorization: Bearer token
パラメーター
不要
210
sObject Self-Service User Password を使用したヘッダーの
返送
リファレンス

===== PAGE 221 =====
例
パスワード情報の取得、パスワードの設定、パスワードのリセットの例は、「ユーザーパスワードを管理す
る」 (ページ 88)を参照してください。
関連トピック:
Salesforce プラットフォームのオブジェクトリファレンス
Platform Event Schema by Event Name
イベント名のプラットフォームイベントの定義を JSON 形式で取得します。このリソースは REST API バージョン
40.0 以降で使用できます。
説明400 Bad Request
要求の形式が正しくありません — URI の payloadFormat パラメーターで無効な値が渡さ
れました。
API バージョン
43.0 以降
要求の形式が正しくありません — URI で payloadFormat パラメーターが渡されました
が、この API バージョンではこのパラメーターはサポートされていません。
API バージョン
42.0 以前
構文
URI
/services/data/vXX.X/sobjects/eventName/eventSchema
形式
JSON
HTTP のメソッド
GET
認証
Authorization: Bearer token
パラメーター
説明パラメーター
(省略可能なクエリパラメーター。API バージョン 43.0 以降で使用可能)。返され
るイベントスキーマの形式。このパラメーターは、次のいずれかの値を取りま
す。
payloadFormat
• EXPANDED  — イベントスキーマの JSON 表現。これは、API バージョン 43.0 以
降で payloadFormat を指定しない場合のデフォルトの形式です。拡張され
たイベントスキーマは、オープンソースの Apache Avro 形式ですが、レコード
複合型に厳密には準拠していません。スキーマ項目の詳細は、「Apache Avro
形式」を参照してください。
211
Platform Event Schema by Event Nameリファレンス

===== PAGE 222 =====
説明パラメーター
• COMPACT  — レコード複合型のオープンソース Apache Avro 仕様に準拠する、
イベントスキーマの JSON 表現。スキーマ項目の詳細は、「Apache Avro 形式」
を参照してください。登録者は、コンパクトスキーマ形式を使用して、バイ
ナリ形式で受信したコンパクトイベントを並列化します。
API バージョン 43.0 以降の例
この URI は、プラットフォームイベント名が Low_Ink__e のスキーマを取得します。API バージョン 43.0 以降
では、応答形式がイベントスキーマの JSON 表現となっています。
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Low_Ink__e/eventSchema
-H "Authorization: Bearer token"
または
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Low_Ink__e/eventSchema?payloadFormat=EXPANDED
-H "Authorization: Bearer token"
API バージョン 60.0 では、拡張された形式について返される応答は次のようになります。
{
"name": "Low_Ink__e",
"namespace": "com.sforce.eventbus",
"type": "expanded-record",
"fields": [
{
"name": "data",
"type": {
"type": "record",
"name": "Data",
"namespace": "",
"fields": [
{
"name": "schema",
"type": "string"
},
{
"name": "payload",
"type": {
"type": "record",
"name": "Payload",
"doc": "",
"fields": [
{
"name": "CreatedDate",
"type": "string",
"doc": "CreatedDate:DateTime"
},
212
Platform Event Schema by Event Nameリファレンス

===== PAGE 223 =====
{
"name": "CreatedById",
"type": "string",
"doc": "CreatedBy:EntityId"
},
{
"name": "Printer_Model__c",
"type": [
"null",
"string"
],
"doc": "Data:Text:00NRM000001krnv",
"default": null
},
{
"name": "Serial_Number__c",
"type": [
"null",
"string"
],
"doc": "Data:Text:00NRM000001kro0",
"default": null
},
{
"name": "Ink_Percentage__c",
"type": [
"null",
"double"
],
"doc": "Data:Double:00NRM000001kro5",
"default": null
}
]
}
},
{
"name": "event",
"type": {
"type": "record",
"name": "Event",
"fields": [
{
"name": "replayId",
"type": "long"
}
]
}
}
]
}
},
{
"name": "channel",
"type": "string"
213
Platform Event Schema by Event Nameリファレンス

===== PAGE 224 =====
}
]
}
コンパクト (Apache Avro) 形式を取得するには、次の URI を使用します。
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Low_Ink__e/eventSchema?payloadFormat=COMPACT
-H "Authorization: Bearer token"
API バージョン 60.0 では、コンパクト形式について返される応答は次のようになります。
{
"name": "Low_Ink__e",
"namespace": "com.sforce.eventbus",
"type": "record",
"fields": [
{
"name": "CreatedDate",
"type": "long",
"doc": "CreatedDate:DateTime"
},
{
"name": "CreatedById",
"type": "string",
"doc": "CreatedBy:EntityId"
},
{
"name": "Printer_Model__c",
"type": [
"null",
"string"
],
"doc": "Data:Text:00NRM000001krnv",
"default": null
},
{
"name": "Serial_Number__c",
"type": [
"null",
"string"
],
"doc": "Data:Text:00NRM000001kro0",
"default": null
},
{
"name": "Ink_Percentage__c",
"type": [
"null",
"double"
],
"doc": "Data:Double:00NRM000001kro5",
"default": null
}
],
214
Platform Event Schema by Event Nameリファレンス

===== PAGE 225 =====
"uuid": "5E5OtZj5_Gm6Vax9XMXH9A"
}
メモ: コンパクトスキーマには replayId または channel 項目は含まれません。これは、これらの項目
が受信したコンパクトイベントの並列化に不要であるためです。
API バージョン 42.0 以前の例
API バージョン 42.0 以前では、応答形式はレコード複合型のオープンソース Apache Avro 仕様に準拠しています。
メモ: この形式は、?payloadFormat=COMPACT パラメーターを追加した場合に API バージョン 43.0 以降
の API が返す形式です。
curl
https://MyDomainName.my.salesforce.com/services/data/v42.0/sobjects/Low_Ink__e/eventSchema
-H "Authorization: Bearer token"
API バージョン 42.0 では、返される応答は次のようになります。
{
"name": "Low_Ink__e",
"namespace": "com.sforce.eventbus",
"type": "record",
"fields": [
{
"name": "CreatedDate",
"type": "long",
"doc": "CreatedDate:DateTime"
},
{
"name": "CreatedById",
"type": "string",
"doc": "CreatedBy:EntityId"
},
{
"name": "Printer_Model__c",
"type": [
"null",
"string"
],
"doc": "Data:Text:00NRM000001krnv",
"default": null
},
{
"name": "Serial_Number__c",
"type": [
"null",
"string"
],
"doc": "Data:Text:00NRM000001kro0",
"default": null
},
{
215
Platform Event Schema by Event Nameリファレンス

===== PAGE 226 =====
"name": "Ink_Percentage__c",
"type": [
"null",
"double"
],
"doc": "Data:Double:00NRM000001kro5",
"default": null
}
],
"uuid": "5E5OtZj5_Gm6Vax9XMXH9A"
}
メモ: プラットフォームイベントの定義を変更すると、このプラットフォームイベントのスキーマ ID も変
更されます。
Apache Avro 形式
返される応答の項目は、レコード複合型のオープンソース Apache Avro 仕様に準拠しています (Apache Avro 仕様
の「Avro レコード」を参照してください)。次の点に注意してください。
• name はプラットフォームイベントの名前です。
• namespace は com.sforce.eventbus に対応します。
• type は Avro 複合型です。
• fields はプラットフォームイベントの項目が含まれる JSON 配列です。各項目は、次のようになっていま
す。
– type は、その項目が null であるか、指定された型の値があるかを示します。項目が存在しない場合、
値は default です。
– doc は、項目のデータ型の説明と、カスタム項目の項目 ID を含んでいます。この項目は、組織内で使用
することを目的としています。たとえば、Salesforce では、このデータ型情報を使用して、DateTime 項目
が long から DateTime に変換されます。この項目の値は、将来変更される可能性があるため、依存しない
ことをお勧めします。
応答には uuid 項目も含まれ、この項目にはこのスキーマの ID が含まれています。この ID は、base-64 URL バリ
アントとして符号化された、正規化された Avro スキーマの MD5 フィンガープリントです。この ID を
/vXX.X/event/eventSchema/  URI に追加してスキーマを取得することができます。
スキーマ ID によるプラットフォームイベントスキーマ
スキーマ名のプラットフォームイベントの定義を JSON 形式で取得します。このリソースは REST API バージョン
40.0 以降で使用できます。
説明400 Bad Request
要求の形式が正しくありません — URI の payloadFormat パラメーターで無効な値が渡さ
れました。
API バージョン
43.0 以降
216
スキーマ ID によるプラットフォームイベントスキーマリファレンス

===== PAGE 227 =====
説明400 Bad Request
要求の形式が正しくありません — URI で payloadFormat パラメーターが渡されました
が、この API バージョンではこのパラメーターはサポートされていません。
API バージョン
42.0 以前
構文
URI
/services/data/vXX.X/event/eventSchema/schemaId
形式
JSON
HTTP のメソッド
GET
認証
Authorization: Bearer token
パラメーター
説明パラメーター
(省略可能なクエリパラメーター。API バージョン 43.0 以降で使用可能)。返され
るイベントスキーマの形式。このパラメーターは、次のいずれかの値を取りま
す。
payloadFormat
• EXPANDED  — イベントスキーマの JSON 表現。これは、API バージョン 43.0 以
降で payloadFormat を指定しない場合のデフォルトの形式です。拡張され
たイベントスキーマは、オープンソースの Apache Avro 形式ですが、レコード
複合型に厳密には準拠していません。スキーマ項目の詳細は、「Apache Avro
形式」を参照してください。
• COMPACT  — レコード複合型のオープンソース Apache Avro 仕様に準拠する、
イベントスキーマの JSON 表現。スキーマ項目の詳細は、「Apache Avro 形式」
を参照してください。登録者は、コンパクトスキーマ形式を使用して、バイ
ナリ形式で受信したコンパクトイベントを並列化します。
API バージョン 43.0 以降の例
この URI は、スキーマ ID が 5E5OtZj5_Gm6Vax9XMXH9A のプラットフォームイベントのスキーマを取得しま
す。このスキーマ ID が例の ID です。これをイベントの有効なスキーマ ID に置き換えます。
/services/data/v60.0/event/eventSchema/5E5OtZj5_Gm6Vax9XMXH9A
または
/services/data/v60.0/event/eventSchema/5E5OtZj5_Gm6Vax9XMXH9A?payloadFormat=EXPANDED
217
スキーマ ID によるプラットフォームイベントスキーマリファレンス

===== PAGE 228 =====
API バージョン 43.0 以降では、デフォルトで応答形式がイベントスキーマの JSON 表現となっています。API バー
ジョン 60.0 では、返される応答は次のようになります。
{
"name": "Low_Ink__e",
"namespace": "com.sforce.eventbus",
"type": "expanded-record",
"fields": [
{
"name": "data",
"type": {
"type": "record",
"name": "Data",
"namespace": "",
"fields": [
{
"name": "schema",
"type": "string"
},
{
"name": "payload",
"type": {
"type": "record",
"name": "Payload",
"doc": "",
"fields": [
{
"name": "CreatedDate",
"type": "string",
"doc": "CreatedDate:DateTime"
},
{
"name": "CreatedById",
"type": "string",
"doc": "CreatedBy:EntityId"
},
{
"name": "Printer_Model__c",
"type": [
"null",
"string"
],
"doc": "Data:Text:00NRM000001krnv",
"default": null
},
{
"name": "Serial_Number__c",
"type": [
"null",
"string"
],
"doc": "Data:Text:00NRM000001kro0",
"default": null
},
218
スキーマ ID によるプラットフォームイベントスキーマリファレンス

===== PAGE 229 =====
{
"name": "Ink_Percentage__c",
"type": [
"null",
"double"
],
"doc": "Data:Double:00NRM000001kro5",
"default": null
}
]
}
},
{
"name": "event",
"type": {
"type": "record",
"name": "Event",
"fields": [
{
"name": "replayId",
"type": "long"
}
]
}
}
]
}
},
{
"name": "channel",
"type": "string"
}
]
}
コンパクト (Apache Avro) 形式を取得するには、次の URI を使用します。
/services/data/v60.0/event/eventSchema/5E5OtZj5_Gm6Vax9XMXH9A?payloadFormat=COMPACT
API バージョン 60.0 では、コンパクト形式について返される応答は次のようになります。
{
"name": "Low_Ink__e",
"namespace": "com.sforce.eventbus",
"type": "record",
"fields": [
{
"name": "CreatedDate",
"type": "long",
"doc": "CreatedDate:DateTime"
},
{
"name": "CreatedById",
"type": "string",
"doc": "CreatedBy:EntityId"
219
スキーマ ID によるプラットフォームイベントスキーマリファレンス

===== PAGE 230 =====
},
{
"name": "Printer_Model__c",
"type": [
"null",
"string"
],
"doc": "Data:Text:00NRM000001krnv",
"default": null
},
{
"name": "Serial_Number__c",
"type": [
"null",
"string"
],
"doc": "Data:Text:00NRM000001kro0",
"default": null
},
{
"name": "Ink_Percentage__c",
"type": [
"null",
"double"
],
"doc": "Data:Double:00NRM000001kro5",
"default": null
}
],
"uuid": "5E5OtZj5_Gm6Vax9XMXH9A"
}
メモ: コンパクトスキーマには replayId または channel 項目は含まれません。これは、これらの項目
が受信したコンパクトイベントの並列化に不要であるためです。
API バージョン 42.0 以前の例
API バージョン 42.0 以前では、応答形式はレコード複合型のオープンソース Apache Avro 仕様に準拠しています。
メモ: この形式は、?payloadFormat=COMPACT パラメーターを追加した場合に API バージョン 43.0 以降
の API が返す形式です。
この URI は、スキーマ ID が 5E5OtZj5_Gm6Vax9XMXH9A のプラットフォームイベントのスキーマを取得しま
す。このスキーマ ID が例の ID です。これをイベントの有効なスキーマ ID に置き換えます。
/services/data/v42.0/event/eventSchema/5E5OtZj5_Gm6Vax9XMXH9A
API バージョン 42.0 では、返される応答は次のようになります。
{
"name": "Low_Ink__e",
"namespace": "com.sforce.eventbus",
"type": "record",
"fields": [
220
スキーマ ID によるプラットフォームイベントスキーマリファレンス

===== PAGE 231 =====
{
"name": "CreatedDate",
"type": "long",
"doc": "CreatedDate:DateTime"
},
{
"name": "CreatedById",
"type": "string",
"doc": "CreatedBy:EntityId"
},
{
"name": "Printer_Model__c",
"type": [
"null",
"string"
],
"doc": "Data:Text:00NRM000001krnv",
"default": null
},
{
"name": "Serial_Number__c",
"type": [
"null",
"string"
],
"doc": "Data:Text:00NRM000001kro0",
"default": null
},
{
"name": "Ink_Percentage__c",
"type": [
"null",
"double"
],
"doc": "Data:Double:00NRM000001kro5",
"default": null
}
],
"uuid": "5E5OtZj5_Gm6Vax9XMXH9A"
}
メモ: プラットフォームイベントの定義を変更すると、このプラットフォームイベントのスキーマ ID も変
更されます。
スキーマ ID がない場合は、プラットフォームイベント名を入力するとスキーマを取得できま
す。/services/data/vXX.X/sobjects/eventName/eventSchema に対して GET 要求を行います。「イベ
ント名によるプラットフォームイベントスキーマ」を参照してください。
Apache Avro 形式
返される応答の項目は、レコード複合型のオープンソース Apache Avro 仕様に準拠しています (Apache Avro 仕様
の「Avro レコード」を参照してください)。次の点に注意してください。
221
スキーマ ID によるプラットフォームイベントスキーマリファレンス

===== PAGE 232 =====
• name はプラットフォームイベントの名前です。
• namespace は com.sforce.eventbus に対応します。
• type は Avro 複合型です。
• fields はプラットフォームイベントの項目が含まれる JSON 配列です。各項目は、次のようになっていま
す。
– type は、その項目が null であるか、指定された型の値があるかを示します。項目が存在しない場合、
値は default です。
– doc は、項目のデータ型の説明と、カスタム項目の項目 ID を含んでいます。この項目は、組織内で使用
することを目的としています。たとえば、Salesforce では、このデータ型情報を使用して、DateTime 項目
が long から DateTime に変換されます。この項目の値は、将来変更される可能性があるため、依存しない
ことをお勧めします。
応答には uuid 項目も含まれ、この項目にはこのスキーマの ID が含まれています。この ID は、base-64 URL バリ
アントとして符号化された、正規化された Avro スキーマの MD5 フィンガープリントです。この ID を
/vXX.X/event/eventSchema/  URI に追加してスキーマを取得することができます。
appMenu の種別の取得
Salesforce アプリケーションのドロップダウンメニューに表示されるアプリケーションメニュー種別のリストを
取得します。このリソースは REST API バージョン 29.0 以降で使用できます。
構文
URI
/services/data/vXX.X/appMenu/
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
リクエストボディ
なし
要求のパラメーター
不要
例
リクエストの例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/appMenu/ -H
"Authorization: Bearer token"
222
appMenu の種別の取得リファレンス

===== PAGE 233 =====
AppMenu Items
アプリケーションメニュー項目には、Salesforce アプリケーションのドロップダウンメニューからアクセスしま
す。アプリケーションメニュー項目のリストを取得するには、GET メソッドを使用します。アプリケーション
メニューへの要求で返されるヘッダーを取得するには、HEAD メソッドを使用します。
このセクションの内容:
AppMenu Items の取得
Salesforce Lightning ドロップダウンメニューに表示されるアプリケーションメニュー項目のリストを取得しま
す。このリソースは REST API バージョン 29.0 以降で使用できます。
アプリケーションメニュー項目の要求のヘッダーの返送
Salesforce アプリケーションドロップダウンメニュー項目の GET 要求をしたときに返されるヘッダーのみを返
します。リソースのコンテンツを取得する前に、この URI を使用してヘッダー値を確認できます。このリ
ソースは REST API バージョン 29.0 以降で使用できます。
AppMenu Items の取得
Salesforce Lightning ドロップダウンメニューに表示されるアプリケーションメニュー項目のリストを取得します。
このリソースは REST API バージョン 29.0 以降で使用できます。
構文
URI
/services/data/vXX.X/appMenu/AppSwitcher/
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
リクエストボディ
なし
要求パラメーター
不要
例
リクエストの例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/appMenu/AppSwitcher -H
"Authorization: Bearer token"
223
AppMenu Itemsリファレンス

===== PAGE 234 =====
アプリケーションメニュー項目の要求のヘッダーの返送
Salesforce アプリケーションドロップダウンメニュー項目の GET 要求をしたときに返されるヘッダーのみを返し
ます。リソースのコンテンツを取得する前に、この URI を使用してヘッダー値を確認できます。このリソース
は REST API バージョン 29.0 以降で使用できます。
構文
URI
/services/data/vXX.X/appMenu/AppSwitcher/ を使用します。
形式
JSON、XML
HTTP のメソッド
HEAD
認証
Authorization: Bearer token
リクエストボディ
なし
要求のパラメーター
不要
例
リクエストの例
curl -X HEAD --head
https://MyDomainName.my.salesforce.com/services/data/v60.0/appMenu/AppSwitcher -H
"Authorization: Bearer token"
AppMenu Mobile Items
アプリケーションメニュー項目に、Android および iOS の Salesforce モバイルアプリケーションおよびモバイル
Web のナビゲーションメニューからアクセスします。
このセクションの内容:
AppMenu Mobile Items の取得
Android および iOS の Salesforce モバイルアプリケーションおよびモバイル Web ナビゲーションメニューのア
プリケーションメニュー項目のリストを取得します。このリソースは REST API バージョン 29.0 以降で使用で
きます。
AppMenu Mobile Item の要求のヘッダーの返送
Android および iOS の Salesforce モバイルアプリケーションとモバイル Web のナビゲーションメニューについ
ての GET 要求で返されるヘッダーのみを返します。リソースのコンテンツを取得する前に、この URI を使用
してヘッダー値を確認できます。このリソースは REST API バージョン 29.0 以降で使用できます。
224
アプリケーションメニュー項目の要求のヘッダーの返送リファレンス

===== PAGE 235 =====
AppMenu Mobile Items の取得
Android および iOS の Salesforce モバイルアプリケーションおよびモバイル Web ナビゲーションメニューのアプリ
ケーションメニュー項目のリストを取得します。このリソースは REST API バージョン 29.0 以降で使用できます。
構文
URI
/services/data/vXX.X/appMenu/Salesforce1/
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
リクエストボディ
なし
要求パラメーター
不要
例
リクエストの例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/appMenu/Salesforce1/
-H "Authorization: Bearer token"
レスポンスボディの例
{
"appMenuItems" : [ {
"type" : "Standard.Search",
"content" : null,
"icons" : null,
"colors" : null,
"label" : "Smart Search Items",
"url" : "/search"
}, {
"type" : "Standard.MyDay",
"content" : null,
"icons" : null,
"colors" : null,
"label" : "Today",
"url" : "/myDay"
}, {
"type" : "Standard.Tasks",
"content" : null,
"icons" : null,
"colors" : null,
225
AppMenu Mobile Items の取得リファレンス

===== PAGE 236 =====
"label" : "Tasks",
"url" : "/tasks"
}, {
"type" : "Standard.Dashboards",
"content" : null,
"icons" : null,
"colors" : null,
"label" : "Dashboards",
"url" : "/dashboards"
}, {
"type" : "Tab.flexiPage",
"content" : "MySampleFlexiPage",
"icons" : [ {
"contentType" : "image/png",
"width" : 32,
"height" : 32,
"theme" : "theme3",
"url" : "http://myorg.com/img/icon/custom51_100/bell32.png"
}, {
"contentType" : "image/png",
"width" : 16,
"height" : 16,
"theme" : "theme3",
"url" : "http://myorg.com/img/icon/custom51_100/bell16.png"
}, {
"contentType" : "image/svg+xml",
"width" : 0,
"height" : 0,
"theme" : "theme4",
"url" : "http://myorg.com/img/icon/t4/custom/custom53.svg"
}, {
"contentType" : "image/png",
"width" : 60,
"height" : 60,
"theme" : "theme4",
"url" : "http://myorg.com/img/icon/t4/custom/custom53_60.png"
}, {
"contentType" : "image/png",
"width" : 120,
"height" : 120,
"theme" : "theme4",
"url" : "http://myorg.com/img/icon/t4/custom/custom53_120.png"
} ],
"colors" : [ {
"context" : "primary",
"color" : "FC4F59",
"theme" : "theme4"
}, {
"context" : "primary",
"color" : "FC4F59",
"theme" : "theme3"
} ],
"label" : "My App Home Page",
"url" : "/servlet/servlet.Integration?lid=01rxx0000000Vsd&ic=1"
226
AppMenu Mobile Items の取得リファレンス

===== PAGE 237 =====
}, {
"type" : "Tab.apexPage",
"content" : "/apex/myapexpage",
"icons" : [ {
"contentType" : "image/png",
"width" : 32,
"height" : 32,
"theme" : "theme3",
"url" : "http://myorg.com/img/icon/cash32.png"
}, {
"contentType" : "image/png",
"width" : 16,
"height" : 16,
"theme" : "theme3",
"url" : "http://myorg.com/img/icon/cash16.png"
}, {
"contentType" : "image/svg+xml",
"width" : 0,
"height" : 0,
"theme" : "theme4",
"url" : "http://myorg.com/img/icon/t4/custom/custom41.svg"
}, {
"contentType" : "image/png",
"width" : 60,
"height" : 60,
"theme" : "theme4",
"url" : "http://myorg.com/img/icon/t4/custom/custom41_60.png"
}, {
"contentType" : "image/png",
"width" : 120,
"height" : 120,
"theme" : "theme4",
"url" : "http://myorg.com/img/icon/t4/custom/custom41_120.png"
} ],
"colors" : [ {
"context" : "primary",
"color" : "3D8D8D",
"theme" : "theme4"
}, {
"context" : "primary",
"color" : "3D8D8D",
"theme" : "theme3"
} ],
"label" : "label",
"url" : "/servlet/servlet.Integration?lid=01rxx0000000Vyb&ic=1"
} ]
}
AppMenu Mobile Item の要求のヘッダーの返送
Android および iOS の Salesforce モバイルアプリケーションとモバイル Web のナビゲーションメニューについての
GET 要求で返されるヘッダーのみを返します。リソースのコンテンツを取得する前に、この URI を使用してヘッ
ダー値を確認できます。このリソースは REST API バージョン 29.0 以降で使用できます。
227
AppMenu Mobile Item の要求のヘッダーの返送リファレンス

===== PAGE 238 =====
構文
URI
/services/data/vXX.X/appMenu/Salesforce1/
形式
JSON、XML
HTTP のメソッド
HEAD
認証
Authorization: Bearer token
リクエストボディ
なし
要求パラメーター
不要
例
リクエストの例
curl -X HEAD --head
https://MyDomainName.my.salesforce.com/services/data/v60.0/appMenu/Salesforce1 -H
"Authorization: Bearer token"
Compact Layouts
複数のオブジェクトの Compact Layouts のリストを返します。このリソースは REST API バージョン 31.0 以降で使
用できます。
このリソースは、オブジェクトのセットの主 Compact Layouts を返します。オブジェクトのセットは、クエリパ
ラメーターを使用して指定します。一度に最大 100 個のオブジェクトを照会できます。
メモ: 一括クエリでは、PersonAccount はサポートされていません。PersonAccount の主 Compact Layouts を取得
する場合
は、/services/data/v60.0/sobjects/Account/describe/compactLayouts/primaryPersonAccount
から直接取得します。
構文
URI
/services/data/vXX.X/compactLayouts?q=objectList
形式
JSON、XML
HTTP のメソッド
GET
228
Compact Layoutsリファレンス

===== PAGE 239 =====
認証
Authorization: Bearer token
要求パラメーター
説明パラメーター
オブジェクトのカンマ区切りリスト。このリソースの応答で、このリ
スト内の各オブジェクトの主 Compact Layouts が返されます。
q
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/compactLayouts?q=Account,Contact,CustomObj__c
-H "Authorization: Bearer token"
レスポンスボディの例
{
"Account" : {
"actions" : [ {
"behavior" : null,
"content" : null,
"contentSource" : null,
"custom" : false,
"encoding" : null,
"height" : null,
"icons" : null,
"label" : "Call",
"menubar" : false,
"name" : "CallHighlightAction",
"overridden" : false,
"resizeable" : false,
"scrollbars" : false,
"showsLocation" : false,
"showsStatus" : false,
"toolbar" : false,
"url" : null,
"width" : null,
"windowPosition" : null
},
...
"id" : "0AHD000000000AbOAI",
"label" : "Custom Account Compact Layout",
"name" : "Custom_Account_Compact_Layout"
},
"Contact" : {
"actions" : [ {
"behavior" : null,
"content" : null,
"contentSource" : null,
229
Compact Layoutsリファレンス

===== PAGE 240 =====
"custom" : false,
"encoding" : null,
"height" : null,
"icons" : null,
"label" : "Call",
"menubar" : false,
"name" : "CallHighlightAction",
"overridden" : false,
"resizeable" : false,
"scrollbars" : false,
"showsLocation" : false,
"showsStatus" : false,
"toolbar" : false,
"url" : null,
"width" : null,
"windowPosition" : null
},
...
"id" : null,
"label" : "System Default",
"name" : "SYSTEM"
}
"CustomObj__c" : {
"actions" : [ {
"behavior" : null,
"content" : null,
"contentSource" : null,
"custom" : false,
"encoding" : null,
"height" : null,
"icons" : null,
"label" : "Call",
"menubar" : false,
"name" : "CallHighlightAction",
"overridden" : false,
"resizeable" : false,
"scrollbars" : false,
"showsLocation" : false,
"showsStatus" : false,
"toolbar" : false,
"url" : null,
"width" : null,
"windowPosition" : null
},
...
"id" : null,
"imageItems" : null,
"label" : "System Default",
"name" : "SYSTEM"
}
}
230
Compact Layoutsリファレンス

===== PAGE 241 =====
Consent
ユーザーは、さまざまな場所 (一貫性がない可能性がある) に同意設定を保存することがあります。API バージョ
ン 44.0 以降を使用している場合は、複数のレコードから顧客の同意設定を見つけることができます。同意設定
の追跡は、あなたとユーザーが最も制限の厳しい要求を順守するのに役立ちます。この Consent API は、API バー
ジョン 50.0 以降において、特定の Data Cloud パラメーターと組み合わせて使用できます。
同意設定のコンパイル
レコードに参照関係がある場合、特定の同意管理オブジェクト間で、メールや追跡などの単一アクションに
よって同意の詳細を取得します。このリソースは REST API バージョン 45.0 以降で使用できます。
Consent API をコールするには、「すべてのデータの参照」または「プライバシーデータへのユーザーのアクセ
スを許可」ユーザー権限を持っている必要があります。権限を必須にすることで、システム管理者は明示的権
限を付与できます。これは、この API が、ユーザーが通常アクセスするレコードだけでなく、レコード間のリ
ンクや同意フラグの値など、組織全体の同意データにアクセスするためです。
Consent API は、レコードに参照関係がある場合、連絡先オブジェクト、連絡先種別に関する同意オブジェク
ト、データ使用目的オブジェクト、個人オブジェクト、リードオブジェクト、個人取引先オブジェクト、ユー
ザーオブジェクト間で、同意の詳細をメールや追跡などの単一アクションにより取得します。
action として email を選択すると、同じメールアドレスを含むレコードの同意のみが集計されます。URI で指定
されたレコード ID が異なるメールアドレスを含むレコードに関連付けられている場合、その関連レコードの
同意設定は API レスポンスに含まれません。Consent API は、メールアドレス項目がプラットフォームの暗号化
によって保護されているレコードを見つけることはできません。
メモ:  API で複数のレコードの同意設定が比較されるとき、変換されたリードの設定は含まれません。
レスポンスのスキーマAPI レスポンス参照する項目アクション
{ContactPointTypeConsent
で指定する場合
は、時間範囲内:
email Contact.HasOptedOutOfEmail
"<ID/Email>" :
{
ContactPointTypeConsent.ContactPointType
ContactPointTypeConsent.EffectiveFrom
参照される項目値
がすべて 0 の場
"result" : "<Success/errormessage>",
"proceed" : { "emailResult" : "<Success/errormessage>",
email : “<true/false>” }
ContactPointTypeConsent.EffectiveTo
ContactPointTypeConsent.PrivacyConsentStatus合、TRUE を返しま
す。DataUsePurpose.Name
}
参照される項目値
のいずれかが 1 の
Lead.HasOptedOutOfEmail
}PersonAccount.HasOptedOutOfEmail
場合、または関連
する連絡先オブ
ジェクト、連絡先
種別に関する同意
オブジェクト、
リードオブジェク
ト、個人取引先オ
231
Consentリファレンス

===== PAGE 242 =====
ブジェクトが存在
しない場合、FALSE
を返します。
{参照される項目値
がすべて 0 の場
fax Contact.HasOptedOutOfFax
"<ID/Email>" :DataUsePurpose.Name
合、TRUE を返しま
す。
{
"result" : "<Success/errormessage>",
Lead.HasOptedOutOfFax
PersonAccount.HasOptedOutOfFax
参照される項目値
のいずれかが 1 の "proceed" : { "faxResult" : "<Success/errormessage>", fax
: "<true/false>" }
場合、または関連
}する取引先責任
}者、リード、また
は個人取引先オブ
ジェクトが存在し
ない場合、FALSE を
返します。
{参照される項目値
が 0 の場合、TRUE
を返します。
geotrack DataUsePurpose.Name
"<ID/Email>" :
{
Individual.HasOptedOutGeoTracking
参照される項目値
が 1 の場合、また
"result" : "<Success/errormessage>",
"proceed" : { "geotrackResult" : "<Success/errormessage>",
"geotrack" : "<true/false>" }は関連する個人オ
ブジェクトが存在
}しない場合、FALSE
を返します。 }
{ContactPointTypeConsent
で指定する場合
は、時間範囲内:
mail ContactPointTypeConsent.ContactPointType
"<ID/Email>" :
{
ContactPointTypeConsent.EffectiveFrom
ContactPointTypeConsent.EffectiveTo
参照される項目値
がすべて 0 の場
"result" : "<Success/errormessage>",
"proceed" : { "mailingResult" : "<Success/errormessage>",
"mail" : "<true/false>" }
ContactPointTypeConsent.PrivacyConsentStatus
DataUsePurpose.Name 合、TRUE を返しま
す。
}
参照される項目値
のいずれかが 1 の }
場合、または関連
する連絡先オブ
ジェクト、連絡先
種別に関する同意
オブジェクト、
リードオブジェク
232
同意設定のコンパイルリファレンス

===== PAGE 243 =====
ト、個人取引先オ
ブジェクトが存在
しない場合、FALSE
を返します。
{ContactPointTypeConsent
で指定する場合
は、時間範囲内:
phone Contact.DoNotCall
"<ID/Email>" :
{
ContactPointTypeConsent.ContactPointType
ContactPointTypeConsent.EffectiveFrom
参照される項目値
がすべて 0 の場
"result" : "<Success/errormessage>",
"proceed" : { "phoneResult" : "<Success/errormessage>",
"phone" : "<true/false>" }
ContactPointTypeConsent.EffectiveTo
ContactPointTypeConsent.PrivacyConsentStatus合、TRUE を返しま
す。DataUsePurpose.Name
}
参照される項目値
のいずれかが 1 の
Lead.DoNotCall
}PersonAccount.DoNotCall
場合、または関連
する連絡先オブ
ジェクト、連絡先
種別に関する同意
オブジェクト、
リードオブジェク
ト、個人取引先オ
ブジェクトが存在
しない場合、FALSE
を返します。
{参照される項目値
が 1 の場合、TRUE
を返します。
portability DataUsePurpose.Name
"<ID/Email>" :
{
Individual.SendIndividualData
参照される項目値
が 0 の場合、また
"result" : "<Success/errormessage>",
"proceed" : { "portabilityResult" :
"<Success/errormessage>", "portability" : "<true/false>"
}
は関連する個人オ
ブジェクトが存在
しない場合、FALSE
を返します。 }
}
{参照される項目値
が 0 の場合、TRUE
を返します。
process DataUsePurpose.Name
"<ID/Email>" :
{
Individual.HasOptedOutProcessing
参照される項目値
が 1 の場合、また
"result" : "<Success/errormessage>",
"proceed" : { "processResult" : "<Success/errormessage>",
"process" : "<true/false>" }は関連する個人オ
ブジェクトが存在
233
同意設定のコンパイルリファレンス

===== PAGE 244 =====
}しない場合、FALSE
を返します。 }
{参照される項目値
が 0 の場合、TRUE
を返します。
profile DataUsePurpose.Name
"<ID/Email>" :
{
Individual.HasOptedOutProfiling
参照される項目値
が 1 の場合、また
"result" : "<Success/errormessage>",
"proceed" : { "profileResult" : "<Success/errormessage>",
"profile" : "<true/false>" }は関連する個人オ
ブジェクトが存在
}しない場合、FALSE
を返します。 }
{参照される項目値
が 1 の場合、TRUE
を返します。
shouldforget DataUsePurpose.Name
"<ID/Email>" :
{
Individual.ShouldForget
参照される項目値
が 0 の場合、また
"result" : "<Success/errormessage>",
"proceed" : { "shouldForgetResult" :
"<Success/errormessage>", "shouldforget" :
"<true/false>" }
は関連する個人オ
ブジェクトが存在
しない場合、FALSE
を返します。 }
}
{ContactPointTypeConsent
で指定する場合
は、時間範囲内:
social ContactPointTypeConsent.ContactPointType
"<ID/Email>" :
{
ContactPointTypeConsent.EffectiveFrom
ContactPointTypeConsent.EffectiveTo
参照される項目値
がすべて 0 の場
"result" : "<Success/errormessage>",
"proceed" : { "socialResult" : "<Success/errormessage>",
"social" : "<true/false>" }
ContactPointTypeConsent.PrivacyConsentStatus
DataUsePurpose.Name 合、TRUE を返しま
す。
}
参照される項目値
のいずれかが 1 の }
場合、または関連
する連絡先オブ
ジェクト、連絡先
種別に関する同意
オブジェクト、
リードオブジェク
ト、個人取引先オ
ブジェクトが存在
しない場合、FALSE
を返します。
234
同意設定のコンパイルリファレンス

===== PAGE 245 =====
{参照される項目値
が 0 の場合、TRUE
を返します。
solicit DataUsePurpose.Name
"<ID/Email>" :
{
Individual.HasOptedOutSolicit
参照される項目値
が 1 の場合、また
"result" : "<Success/errormessage>",
"proceed" : { "solicitResult" : "<Success/errormessage>",
"solicit" : "<true/false>" }は関連する個人オ
ブジェクトが存在
}しない場合、FALSE
を返します。 }
{参照される項目値
が 1 の場合、TRUE
を返します。
storepiielsewhereDataUsePurpose.Name
"<ID/Email>" :
{
Individual.CanStorePiiElsewhere
参照される項目値
が 0 の場合、また
"result" : "<Success/errormessage>",
"proceed" : { "storePIIElsewhereResult" :
"<Success/errormessage>", "storepiielsewhere" :
"<true/false>" }
は関連する個人オ
ブジェクトが存在
しない場合、FALSE
を返します。 }
}
{参照される項目値
が 0 の場合、TRUE
を返します。
track DataUsePurpose.Name
"<ID/Email>" :
{
Individual.HasOptedOutTracking
参照される項目値
が 1 の場合、また
"result" : "<Success/errormessage>",
"proceed" : { "trackResult" : "<Success/errormessage>",
"track" : "<true/false>" }は関連する個人オ
ブジェクトが存在
}しない場合、FALSE
を返します。 }
{ContactPointTypeConsent
で指定する場合
は、時間範囲内:
web ContactPointTypeConsent.ContactPointType
"<ID/Email>" :
{
ContactPointTypeConsent.EffectiveFrom
ContactPointTypeConsent.EffectiveTo
参照される項目値
がすべて 0 の場
"result" : "<Success/errormessage>",
"proceed" : { "webResult" : "<Success/errormessage>",
"web" : "<true/false>" }
ContactPointTypeConsent.PrivacyConsentStatus
DataUsePurpose.Name 合、TRUE を返しま
す。
}
参照される項目値
のいずれかが 1 の }
場合、または関連
する連絡先オブ
235
同意設定のコンパイルリファレンス

===== PAGE 246 =====
ジェクト、連絡先
種別に関する同意
オブジェクト、
リードオブジェク
ト、個人取引先オ
ブジェクトが存在
しない場合、FALSE
を返します。
構文
URI
/services/data/vXX.X/consent/action/action?ids=listOfIds
形式
JSON
HTTP のメソッド
GET
認証
Authorization: Bearer token
リクエストボディ
None
要求パラメーター
説明パラメーター
必須。提案されたアクション。
このパラメーターが使用されている場合、actionは使用できません。
action
省略可能: true または false。aggregatedConsent は
aggregatedConsent=true と同じです。true の場合、各 ID の結果で
aggregatedConsent
はなく、進むか否かを示す結果が 1 つ返されます。リスト内のいずれ
かの ID で false が返されると、集計された結果は false になります。
省略可能。同意が確定された際のタイムスタンプ。値は UTC タイム
ゾーンに変換され、「Date および DateTime の有効な書式」の説明に
datetime
従って書式設定する必要があります。指定されていない場合、デフォ
ルトの現在の日付と時刻に設定されます。
必須。ID のカンマ区切りのリスト。ID には、レコード ID か、レコード
に記載されたメールアドレスを使用できます。
ids
省略可能。連絡先チャネルについて明示的な同意が得られたかどうか
を API 応答に指定するには、policy=requireExplicitConsent を
policy
236
同意設定のコンパイルリファレンス

===== PAGE 247 =====
説明パラメーター
使用します。同意が指定されていない場合、API は、infoNotFound 応答
を返します。
このパラメーターは API バージョン 49.0 以降で使用できます。
省略可能。顧客に連絡する理由。purpose
省略可能: true または false。verbose は verbose=true と同じです。
verbose レスポンスは、verbose 以外のレスポンスより時間がかかりま
す。verbose レスポンスの例を参照してください。
verbose
例
URI 構造の要求
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/consent/action/track?ids=003xx000004TxyY,00Qxx00000syyO,003zz000004zzZ
-H "Authorization: Bearer token"
ID としてのメールアドレス、指定された目的と期間、および verbose レスポンスの要求
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/consent/action/email?ids=j0t5t5b2@tkbxp5ia.com,4quxlswo@23wj7pwh.com&datetime=2018-12-12T00:00:00Z
-H "Authorization: Bearer token"
レスポンスボディ
{
"j0t5t5b2@tkbxp5ia.com" : {
"result" : "Success",
"proceed" : {
"email" : "true"
"emailResult" : "Success"
},
"explanation" : [ {
"objectConsulted" : "ContactTypePointConsent",
"status" : "opt_in",
"purpose" : "billing",
"recordId" : "003xx000004TxyY",
"value" : "true"
},{
"objectConsulted" : "Contact",
"field" : "HasOptedOutOfTracking",
"recordId" : "1",
"value" : "true"
}]
},
"4quxlswo@23wj7pwh.com" : {
"result" : "Success",
"proceed" : {
"email" : "false"
237
同意設定のコンパイルリファレンス

===== PAGE 248 =====
"emailResult" : "Success"
},
"explanation" : [ {
"objectConsulted" : "Contact",
"field" : "HasOptedOutOfEmail",
"recordId" : "00Qxx00000skwO",
"value" : "true"
} ]
}
}
複数の種別の同意設定のコンパイル
レコードに参照関係がある場合、特定の同意管理オブジェクト間で、メールと追跡などの複数のアクションに
よって同意の詳細を取得します。API バージョン 45.0 以降で利用できます。
Consent API をコールするには、「すべてのデータの参照」または「プライバシーデータへのユーザーのアクセ
スを許可」ユーザー権限を持っている必要があります。権限を必須にすることで、システム管理者は明示的権
限を付与できます。これは、この API が、ユーザーが通常アクセスするレコードだけでなく、レコード間のリ
ンクや同意フラグの値など、組織全体の同意データにアクセスするためです。
Consent API は、レコードに参照関係がある場合、取引先オブジェクト、連絡先種別に関する同意オブジェク
ト、データ使用目的オブジェクト、個人オブジェクト、リードオブジェクト、個人取引先オブジェクト、およ
びユーザーオブジェクト間で同意の詳細を取得します。
次の表に、API レスポンスの決定方法を示します。参照される項目に競合する同意の設定があると、レスポン
スは権限が最小限の設定を返します。たとえば、Contact.HasOptedOutOfEmail が false であるが、
Lead.HasOptedOutOfEmail が true の場合、ユーザーへのメール送信を継続できないことを示すレスポンスが返さ
れます。
action として email を選択すると、同じメールアドレスを含むレコードの同意のみが集計されます。URI で指定
されたレコード ID が異なるメールアドレスを含むレコードに関連付けられている場合、その関連レコードの
同意設定は API レスポンスに含まれません。
メモ:  API で複数のレコードの同意設定が比較されるとき、変換されたリードの設定は含まれません。
レスポンスのスキーマAPI レスポンス参照する項目アクション
{ContactPointTypeConsent
で指定する場合
は、時間範囲内:
email Contact.HasOptedOutOfEmail
"<ID/Email>" :
{
ContactPointTypeConsent.ContactPointType
ContactPointTypeConsent.EffectiveFrom
参照される項目値
がすべて 0 の場
"result" : "<Success/errormessage>",
"proceed" : { "emailResult" : "<Success/errormessage>",
email : “<true/false>” }
ContactPointTypeConsent.EffectiveTo
ContactPointTypeConsent.PrivacyConsentStatus合、TRUE を返しま
す。DataUsePurpose.Name
}
参照される項目値
のいずれかが 1 の
Lead.HasOptedOutOfEmail
}PersonAccount.HasOptedOutOfEmail
場合、または関連
238
複数の種別の同意設定のコンパイルリファレンス

===== PAGE 249 =====
する連絡先オブ
ジェクト、連絡先
種別に関する同意
オブジェクト、
リードオブジェク
ト、個人取引先オ
ブジェクトが存在
しない場合、FALSE
を返します。
{参照される項目値
がすべて 0 の場
fax Contact.HasOptedOutOfFax
"<ID/Email>" :DataUsePurpose.Name
合、TRUE を返しま
す。
{
"result" : "<Success/errormessage>",
Lead.HasOptedOutOfFax
PersonAccount.HasOptedOutOfFax
参照される項目値
のいずれかが 1 の "proceed" : { "faxResult" : "<Success/errormessage>", fax
: "<true/false>" }
場合、または関連
}する取引先責任
}者、リード、また
は個人取引先オブ
ジェクトが存在し
ない場合、FALSE を
返します。
{参照される項目値
が 0 の場合、TRUE
を返します。
geotrack DataUsePurpose.Name
"<ID/Email>" :
{
Individual.HasOptedOutGeoTracking
参照される項目値
が 1 の場合、また
"result" : "<Success/errormessage>",
"proceed" : { "geotrackResult" : "<Success/errormessage>",
"geotrack" : "<true/false>" }は関連する個人オ
ブジェクトが存在
}しない場合、FALSE
を返します。 }
{ContactPointTypeConsent
で指定する場合
は、時間範囲内:
mail ContactPointTypeConsent.ContactPointType
"<ID/Email>" :
{
ContactPointTypeConsent.EffectiveFrom
ContactPointTypeConsent.EffectiveTo
参照される項目値
がすべて 0 の場
"result" : "<Success/errormessage>",
"proceed" : { "mailingResult" : "<Success/errormessage>",
"mail" : "<true/false>" }
ContactPointTypeConsent.PrivacyConsentStatus
DataUsePurpose.Name 合、TRUE を返しま
す。
}
参照される項目値
のいずれかが 1 の }
239
複数の種別の同意設定のコンパイルリファレンス

===== PAGE 250 =====
場合、または関連
する連絡先オブ
ジェクト、連絡先
種別に関する同意
オブジェクト、
リードオブジェク
ト、個人取引先オ
ブジェクトが存在
しない場合、FALSE
を返します。
{ContactPointTypeConsent
で指定する場合
は、時間範囲内:
phone Contact.DoNotCall
"<ID/Email>" :
{
ContactPointTypeConsent.ContactPointType
ContactPointTypeConsent.EffectiveFrom
参照される項目値
がすべて 0 の場
"result" : "<Success/errormessage>",
"proceed" : { "phoneResult" : "<Success/errormessage>",
"phone" : "<true/false>" }
ContactPointTypeConsent.EffectiveTo
ContactPointTypeConsent.PrivacyConsentStatus合、TRUE を返しま
す。DataUsePurpose.Name
}
参照される項目値
のいずれかが 1 の
Lead.DoNotCall
}PersonAccount.DoNotCall
場合、または関連
する連絡先オブ
ジェクト、連絡先
種別に関する同意
オブジェクト、
リードオブジェク
ト、個人取引先オ
ブジェクトが存在
しない場合、FALSE
を返します。
{参照される項目値
が 1 の場合、TRUE
を返します。
portability DataUsePurpose.Name
"<ID/Email>" :
{
Individual.SendIndividualData
参照される項目値
が 0 の場合、また
"result" : "<Success/errormessage>",
"proceed" : { "portabilityResult" :
"<Success/errormessage>", "portability" : "<true/false>"
}
は関連する個人オ
ブジェクトが存在
しない場合、FALSE
を返します。 }
}
240
複数の種別の同意設定のコンパイルリファレンス

===== PAGE 251 =====
{参照される項目値
が 0 の場合、TRUE
を返します。
process DataUsePurpose.Name
"<ID/Email>" :
{
Individual.HasOptedOutProcessing
参照される項目値
が 1 の場合、また
"result" : "<Success/errormessage>",
"proceed" : { "processResult" : "<Success/errormessage>",
"process" : "<true/false>" }は関連する個人オ
ブジェクトが存在
}しない場合、FALSE
を返します。 }
{参照される項目値
が 0 の場合、TRUE
を返します。
profile DataUsePurpose.Name
"<ID/Email>" :
{
Individual.HasOptedOutProfiling
参照される項目値
が 1 の場合、また
"result" : "<Success/errormessage>",
"proceed" : { "profileResult" : "<Success/errormessage>",
"profile" : "<true/false>" }は関連する個人オ
ブジェクトが存在
}しない場合、FALSE
を返します。 }
{参照される項目値
が 1 の場合、TRUE
を返します。
shouldforget DataUsePurpose.Name
"<ID/Email>" :
{
Individual.ShouldForget
参照される項目値
が 0 の場合、また
"result" : "<Success/errormessage>",
"proceed" : { "shouldForgetResult" :
"<Success/errormessage>", "shouldforget" :
"<true/false>" }
は関連する個人オ
ブジェクトが存在
しない場合、FALSE
を返します。 }
}
{ContactPointTypeConsent
で指定する場合
は、時間範囲内:
social ContactPointTypeConsent.ContactPointType
"<ID/Email>" :
{
ContactPointTypeConsent.EffectiveFrom
ContactPointTypeConsent.EffectiveTo
参照される項目値
がすべて 0 の場
"result" : "<Success/errormessage>",
"proceed" : { "socialResult" : "<Success/errormessage>",
"social" : "<true/false>" }
ContactPointTypeConsent.PrivacyConsentStatus
DataUsePurpose.Name 合、TRUE を返しま
す。
}
参照される項目値
のいずれかが 1 の }
場合、または関連
する連絡先オブ
241
複数の種別の同意設定のコンパイルリファレンス

===== PAGE 252 =====
ジェクト、連絡先
種別に関する同意
オブジェクト、
リードオブジェク
ト、個人取引先オ
ブジェクトが存在
しない場合、FALSE
を返します。
{参照される項目値
が 0 の場合、TRUE
を返します。
solicit DataUsePurpose.Name
"<ID/Email>" :
{
Individual.HasOptedOutSolicit
参照される項目値
が 1 の場合、また
"result" : "<Success/errormessage>",
"proceed" : { "solicitResult" : "<Success/errormessage>",
"solicit" : "<true/false>" }は関連する個人オ
ブジェクトが存在
}しない場合、FALSE
を返します。 }
{参照される項目値
が 1 の場合、TRUE
を返します。
storepiielsewhereDataUsePurpose.Name
"<ID/Email>" :
{
Individual.CanStorePiiElsewhere
参照される項目値
が 0 の場合、また
"result" : "<Success/errormessage>",
"proceed" : { "storePIIElsewhereResult" :
"<Success/errormessage>", "storepiielsewhere" :
"<true/false>" }
は関連する個人オ
ブジェクトが存在
しない場合、FALSE
を返します。 }
}
{参照される項目値
が 0 の場合、TRUE
を返します。
track DataUsePurpose.Name
"<ID/Email>" :
{
Individual.HasOptedOutTracking
参照される項目値
が 1 の場合、また
"result" : "<Success/errormessage>",
"proceed" : { "trackResult" : "<Success/errormessage>",
"track" : "<true/false>" }は関連する個人オ
ブジェクトが存在
}しない場合、FALSE
を返します。 }
{ContactPointTypeConsent
で指定する場合
は、時間範囲内:
web ContactPointTypeConsent.ContactPointType
"<ID/Email>" :
{
ContactPointTypeConsent.EffectiveFrom
ContactPointTypeConsent.EffectiveTo
242
複数の種別の同意設定のコンパイルリファレンス

===== PAGE 253 =====
参照される項目値
がすべて 0 の場
"result" : "<Success/errormessage>",
"proceed" : { "webResult" : "<Success/errormessage>",
"web" : "<true/false>" }
ContactPointTypeConsent.PrivacyConsentStatus
DataUsePurpose.Name
合、TRUE を返しま
す。 }
参照される項目値
のいずれかが 1 の
}
場合、または関連
する連絡先オブ
ジェクト、連絡先
種別に関する同意
オブジェクト、
リードオブジェク
ト、個人取引先オ
ブジェクトが存在
しない場合、FALSE
を返します。
構文
URI
/services/data/vXX.X/consent/multiaction?actions=listOfActions&ids=listOfIds
形式
JSON
HTTP のメソッド
GET
認証
Authorization: Bearer token
リクエストボディ
None
要求パラメーター
説明パラメーター
必須。提案されたアクションのカンマ区切りリスト。
このパラメーターが使用されている場合、actionは使用できません。
actions
省略可能: true または false。aggregatedConsent は
aggregatedConsent=true と同じです。true の場合、各 ID の結果で
aggregatedConsent
はなく、進むか否かを示す結果が 1 つ返されます。リスト内のいずれ
かの ID で false が返されると、集計された結果は false になります。
省略可能。同意が確定された際のタイムスタンプ。値は UTC タイム
ゾーンに変換され、「Date および DateTime の有効な書式」の説明に
datetime
243
複数の種別の同意設定のコンパイルリファレンス

===== PAGE 254 =====
説明パラメーター
従って書式設定する必要があります。指定されていない場合、デフォ
ルトの現在の日付と時刻に設定されます。
必須。ID のカンマ区切りのリスト。ID には、レコード ID か、レコード
に記載されたメールアドレスを使用できます。
ids
省略可能。連絡先チャネルについて明示的な同意が得られたかどうか
を API 応答に指定するには、policy=requireExplicitConsent を
policy
使用します。同意が指定されていない場合、API は、infoNotFound 応答
を返します。
このパラメーターは API バージョン 49.0 以降で使用できます。
省略可能。顧客に連絡する理由。purpose
省略可能: true または false。verbose は verbose=true と同じです。
verbose レスポンスは、verbose 以外のレスポンスより時間がかかりま
す。verbose レスポンスの例を参照してください。
verbose
例
複数アクションの URI 構造の要求
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/consent/multiaction?actions=track,geotrack,email&ids=003xx000008TiyY,00Qxx00000skwO,dek65@tf7h.com
-H "Authorization: Bearer token"
ID としてのメールアドレス、指定された目的と期間、および verbose レスポンスの要求
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/consent/action/email?ids=j0t5t5b2@tkbxp5ia.com,4quxlswo@23wj7pwh.com&datetime=2018-12-12T00:00:00Z&purpose=billing&verbose=true
-H "Authorization: Bearer token"
レスポンスボディ
{
"j0t5t5b2@tkbxp5ia.com" : {
"result" : "Success",
"proceed" : {
"email" : "false"
"emailResult" : "Success"
"track" : "false"
"trackResult" : "Success"
"solicit" : "false"
"solicitResult" : "Success"
},
"explanation" : [ {
"objectConsulted" : "ContactTypePointConsent",
"status" : "opt_in",
"purpose" : "billing",
"recordId" : "003xx000004TxyY",
244
複数の種別の同意設定のコンパイルリファレンス

===== PAGE 255 =====
"value" : "true"
},{
"objectConsulted" : "Individual",
"field" : "HasOptedOutOfTracking",
"recordId" : "0PKx000006JkyZ",
"value" : "true"
}]
},
"4quxlswo@23wj7pwh.com" : {
"result" : "Success",
"proceed" : {
"email" : "false"
"emailResult" : "Success"
"track" : "false"
"trackResult" : "Success"
"solicit" : "true"
"solicitResult" : "Success"
},
"explanation" : [ {
"objectConsulted" : "Contact",
"field" : "HasOptedOutOfEmail",
"recordId" : "00Qxx00000skwO",
"value" : "true"
},{
"objectConsulted" : "Individual",
"field" : "HasOptedOutOfSolicit",
"recordId" : "0PKx000003JcpK",
"value" : "false"
}]
}
}
Data Cloud での同意 API の使用
同意 API では Data Cloud がサポートされています。同意 API を使用することで、Data Cloud で読み取りと書き込み
を行うことができます。Data Cloud 内での消費者の権利の指針については、Salesforce の担当者にお問い合わせく
ださい。
必須権限
同意 API 用の Data Cloud パラメーターを使用するには、ModifyAllData または ConsentApiUpdate ユーザー権限を持っ
ている必要があります。権限を必須にすることで、Salesforce 管理者は明示的に権限を付与できます。これらの
パラメーターによって、通常は管理者以外のユーザーがアクセスできないレコード間のリンクや同意フラグの
値などの組織全体の同意データが書き込まれます。
245
Data Cloud での同意 API の使用リファレンス

===== PAGE 256 =====
同意 API でサポートされる Data Cloud でのアクション
説明アクション
このアクションは、Data Cloud 処理で、クエリやセグメント化などのデータの処
理を制限するために使用します。
Processing
このアクションは、Data Cloud プロファイルデータをエクスポートできるように
するために使用します。
Portability
このアクションは、自分の PII (個人識別情報) データと関連レコードの削除を意
味する忘れられる権利を示します。
Shouldforget
Data Cloud の読み取りパラメーター
同意 API を使用することで、Data Cloud プロファイルに関する情報を収集できます。Data Cloud の mode および
ids パラメーターの使用方法は次のとおりです。
構文
HTTP のメソッド
GET
適用開始バージョン:
48.0
URI
メモ: 同意 API は、アクションに基づき 3 種類の URI を使用してアクセスできます。サポートされてい
るアクションは processing、portability、および shouldforget です。
/services/data/vXX.X/consent/action/processing?ids=<list_of_ids>&mode=<cdp>
/services/data/vXX.X/consent/action/portability?ids=<list_of_ids>&mode=<cdp>
/services/data/vXX.X/consent/action/shouldforget?ids=<list_of_ids>&mode=<cdp>
要求のパラメーター
説明パラメーター
必須。ID のカンマ区切りのリスト。指定された ID は、Individual.Individual
ID に対応付けられた項目に存在する必要があります。
ids
省略可能。デフォルト値は normal です。Data Cloud プロファイルを取得
する場合の有効な値は cdp です。
mode
読み取り例
URI
/services/data/v60.0/consent/action/portability?ids=00932I3SU92&mode=cdp
246
Data Cloud での同意 API の使用リファレンス

===== PAGE 257 =====
応答
{ "j00932I3SU92" : { "result" : "Success", "proceed" : { "portability" : "true"
"portabilityResult" : "Success" } } }
書き込みパラメーター
同意 API を使用することで、Data Cloud プロファイルに情報を書き込むこともできます。ids、mode、および status
パラメーターの使用方法は、次のとおりです。
メモ: 同意 API では、3 種類の URI を使用して同意情報を更新できます。それらの URI は、Data Cloud プロ
ファイルに対して実行されるアクションに応じて選択します。サポートされているアクションは
processing、portability、および shouldforget です。
構文
HTTP のメソッド
PATCH
適用開始バージョン
50.0
アクション処理時の URI
/services/data/vXX.X/consent/action/processing?ids=list_of_ids&mode=cdp&status=optin
or optout
アクション処理時の要求パラメーター
説明パラメーター
必須。ID のカンマ区切りのリスト。指定された ID は、Individual.Individual
ID に対応付けられた項目に存在する必要があります。
ids
省略可能。デフォルト値は normal です。Data Cloud プロファイルの更新
に使用できる有効な値は cdp です。
mode
必須。同意の状況。有効な値は、optin または optout です。ただ
し、アクション処理時は、状況に optout を使用してください。
status
アクションが shouldforget の場合の URI
/services/data/vXX.X/consent/action/shouldforget?ids=list_of_ids&mode=cdp&status=optin
or optout
アクションが shouldforget の場合の要求パラメーター
説明パラメーター
必須。ID のカンマ区切りのリスト。指定された ID は、Individual.Individual
ID に対応付けられた項目に存在する必要があります。
ids
247
Data Cloud での同意 API の使用リファレンス

===== PAGE 258 =====
説明パラメーター
省略可能。デフォルト値は normal です。Data Cloud プロファイルの更新
に使用できる有効な値は cdp です。
mode
必須。同意の状況。有効な値は、optin または optout です。ただ
し、アクションが shouldforget の場合は、状況に optin を使用してく
ださい。
status
アクションが portability の場合の URI
/services/data/vXX.X/consent/action/portability?ids=list_of_ids&mode=cdp&status=optin
or optout
アクションが portability の場合の要求パラメーター
説明パラメーター
必須。ID のカンマ区切りのリスト。指定された ID は、Individual.Individual
ID に対応付けられた項目に存在する必要があります。
ids
省略可能。デフォルト値は normal です。Data Cloud プロファイルの更新
に使用できる有効な値は cdp です。
mode
必須。同意の状況。有効な値は、optin または optout です。ただ
し、アクションが portability の場合は、状況に optin を使用してくだ
さい。
status
mode が cdp、action が portability の場合にのみ必須です。このパラメー
ターは、PATCH リクエストボディの一部として渡す必要があります。
aws_s3_bucket_id
このパラメーターは可搬性に関する要求の S3 バケットの場所を Data
Cloud に渡すために使用します。
mode が cdp、action が portability の場合にのみ必須です。このパラメー
ターは、PATCH リクエストボディの一部として渡す必要があります。
aws_access_key_id
このパラメーターは可搬性に関する要求の S3 バケットのアクセスキー
を Data Cloud に渡すために使用します。
mode が cdp、action が portability の場合にのみ必須です。このパラメー
ターは、PATCH リクエストボディの一部として渡す必要があります。
aws_secret_access_key
このパラメーターは可搬性に関する要求の S3 バケットの秘密のアク
セスキーを Data Cloud に渡すために使用します。
mode が cdp、action が portability の場合にのみ必須です。このパラメー
ターは、PATCH リクエストボディの一部として渡す必要があります。
aws_s3_folder
このパラメーターは可搬性に関する要求の S3 バケットのフォルダー
を Data Cloud に渡すために使用します。
mode が cdp、action が portability の場合にのみ必須です。このパラメー
ターは、PATCH リクエストボディの一部として渡す必要があります。
aws_region
248
Data Cloud での同意 API の使用リファレンス

===== PAGE 259 =====
説明パラメーター
このパラメーターは可搬性に関する要求の S3 バケットの aws リージョ
ンを Data Cloud に渡すために使用します。
書き込みの例
アクションが processing の場合
/services/data/v60.0/consent/action/processing?ids=100000695&mode=cdp&status=optout
body: {}
アクションが portability の場合
/services/data/v60.0/consent/action/portability?ids=100000695&mode=cdp&status=optin
body:{
"aws_s3_bucket_id" : "cdpgdprtest",
"aws_access_key_id": "ABCD1234WEXAMPLE",
"aws_secret_access_key": "WXYZ1234EXAMPLE",
"aws_s3_folder": "yyun/Person",
"aws_region": "us-west-1"
}
アクションが shouldforget の場合
/services/data/v60.0/consent/action/shouldforget?ids=100000695 &mode=cdp&status=optin
body: {}
Consent Write
ユーザーはさまざまな場所に同意設定を保存することがあります。Consent Write API では、1 つの API コールを介
して複数のレコードで同意の更新および書き込みができるため、レコード全体で同意を同期したり、新しい同
意データモデルを入力したりするのに役立ちます。このリソースは REST API バージョン 48.0 以降で使用できま
す。
Consent API は、レコードに参照関係があるか、メールアドレスを共有している場合、取引先オブジェクト、連
絡先種別承諾オブジェクト、データ使用目的オブジェクト、個人オブジェクト、リードオブジェクト、個人取
引先オブジェクト、ユーザーオブジェクトに同意の値を書き込みます。この API は Data Cloud 個人レコードに書
き込むこともできます。Consent API は、メールアドレス項目がプラットフォームの暗号化によって保護されて
いるレコードを見つけることはできません。
メモ:  Spring '21 リリースでは、この API にはメールアドレスが 1 つのみ取り込まれます。メールアドレス
が一致したレコードは、API コールで設定されたパラメーターに基づいて更新されます。
リストされたメールアドレスを使用するすべてのレコードが更新されます。createIndividual パラメーターが選択
されていて、個人レコードが存在しない場合は、API によって個人レコードが作成されます。正当な場合、連
絡先種別承諾および連絡先メールレコードも作成されます。
リクエストボディを使用するのは Data Cloud のみです。リクエストボディで何も渡さない場合は、空のオブジェ
クト {} を渡します。
249
Consent Writeリファレンス

===== PAGE 260 =====
構文
URI
/services/data/vXX.X/consent/action/action?ids=listOfIds
形式
JSON
HTTP のメソッド
PATCH
認証
Authorization: Bearer token
要求のパラメーター
説明パラメーター
省略可能。可搬性の書き込み位置などの情報を Data Cloud に渡すため
に使用します。mode=cdp の場合のみ使用します。このパラメーター
は、PATCH リクエストボディの一部として渡す必要があります。
blobParam
省略可能。同意が捕捉される日時。デフォルトは API コールが実行さ
れる日時です。
captureDate
省略可能。同意の捕捉方法を表します (Web、電話、メール)。サポー
トされている値は、次のとおりです。
captureContactPointType
• email
• phone
• web  (デフォルト)
省略可能。同意の捕捉元。デフォルトの捕捉元は Consent API です。最
大文字数は 255 文字です。
captureSource
省略可能。新しい同意レコードの名前を設定するために使用します。
デフォルトは、Individual Name-Datetime (<名前>
2019-03-31T15:47:57) です。 最大文字数は 255 文字です。
consentName
省略可能。ブール型。true に設定し、API コールに個人オブジェクト
のない複数のレコードに一致するメールアドレスが含まれている場
createIndividual
合、個人オブジェクトが作成されます。API コールでメールに一致す
るメールアドレスが使用されている同意レコードは、新しい個人オブ
ジェクトにリンクされます。複数のレコードが見つかった場合、個人
オブジェクトにリンクされていないレコードは、他のレコードで見つ
かった個人オブジェクトにリンクされます。一致するレコードで複数
の個人オブジェクトが見つかった場合、コールは拒否されます。
省略可能。ダブルオプトインが完了した日時。書式は「Date および
DateTime の有効な書式」に記載されています。
doubleOptIn
250
Consent Writeリファレンス

===== PAGE 261 =====
説明パラメーター
省略可能。同意が有効である期間の開始日。書式は「Date および
DateTime の有効な書式」に記載されています。デフォルトは API コー
ルが実行される日付です。
effectiveFrom
省略可能。同意が有効である期間の終了日。書式は「Date および
DateTime の有効な書式」に記載されています。
effectiveTo
必須。同意を同期するために使用されるメールアドレス。ID には、レ
コード ID か、レコードに記載されたメールアドレスを使用できます。
mode=cdp の場合、ID 値は [個人 ID] 属性に等しい文字列です。
ids
省略可能。個人レコードの個人の名前。新しい個人レコードに名前が
入力されていない場合、渡されたメールアドレスのローカル部分が使
用されます。最大文字数は 80 文字です。
individualName
省略可能。デフォルト値はnormalです。許可されるモードはnormal
または cdp です。mode=cdp の場合、要求は Data Cloud プラットフォー
mode
ムに渡され、同意が取得されるか、または書き込まれます。mode=cdp
パラメーターは、action、blobParam、および ids パラメーターの
みをサポートします。
省略可能。同意したデータ使用目的。以前作成した既存のデータ使用
目的を使用する必要があります。同じ名前の目的が複数ある場合、そ
の 1 つのみが選択されます。
purposeName
必須。同意の状況 (OptIn、OptOut、Seen、NotSeen)。個人オブジェ
クトにアクションがある場合 (追跡や処理など)、有効な値は OptIn と
OptOut のみです。
status
アクション
有効な値は、次のとおりです。
• email
• fax
• geotrack
• mailing
• phone
• portability
• process
• profile
• shouldForget
• social
• solicit
• storePiiElsewhere
251
Consent Writeリファレンス

===== PAGE 262 =====
• track
• web
セキュリティ
Consent Write API をコールするには、ModifyAllData または ConsentApiUpdate ユーザー権限を持っている必要があり
ます。これは、この API が、ユーザーが通常アクセスするレコードだけでなく、レコード間のリンクや同意フ
ラグの値など、組織全体の同意データを書き込むためです。ConsentApiUpdate ユーザー権限によって、Consent
Write API コール時の完全な更新権限がユーザーに付与されます。
例
リクエストの例
curl -X PATCH
https://MyDomainName.my.salesforce.com/services/data/v60.0/consent/action/<action>?ids=<email-OR-recordID>&status=<optout/optin/seen/notseen>&createIndividual=<true/false>
-H "Content-Type: application/json" -d "@exampleRequestBody.json"
リクエストボディの例
{}
レスポンスボディの例
{
"<email-OR-recordID>" : {
"result" : "Success",
"edited" : [{
"objectType" : "<Contact, Lead, User, etc.>",
"field" : "<HasOptedOutofFax, DoNotCall,etc>",
"valueOfField" : "<true/false>",
"id" : "<recordID>"
}],
}
}
記述用の組み込みサービス設定
組み込みサービスリリース設定の値、または要求によって返されたヘッダーを取得します。
このセクションの内容:
組み込みサービス設定の取得
ブランドの色、フォント、サイト URL を含む組み込みサービスリリース設定の値を取得します。このリソー
スは REST API バージョン 45.0 以降で使用できます。
252
記述用の組み込みサービス設定リファレンス

===== PAGE 263 =====
組み込みサービス設定のヘッダーの返送
Embedded Service Configuration Describe リソースへの GET 要求のヘッダーのみを返します。リソースのコンテン
ツを取得する前に、前もってヘッダー値を確認できます。照会する EmbeddedServiceConfigDeveloperName を所
有するアカウントにログインしている必要があります。このリソースは REST API バージョン 45.0 以降で使用
できます。
組み込みサービス設定の取得
ブランドの色、フォント、サイト URL を含む組み込みサービスリリース設定の値を取得します。このリソース
は REST API バージョン 45.0 以降で使用できます。
照会する EmbeddedServiceConfigDeveloperName を所有するアカウントにログインしている必要があります。
構文
URI
/services/data/vXX.X/support/embeddedservice/configuration/embeddedServiceConfigDeveloperName
形式
JSON
HTTP のメソッド
GET
認証
Authorization: Bearer token
要求パラメーター
なし
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/support/embeddedservice/configuration/TestOne
-H "Authorization: Bearer token"
レスポンスボディの例
{
"embeddedServiceConfig" : {
"areGuestUsersAllowed" : false,
"authMethod" : "CustomLogin",
"embeddedServiceBranding" : {
"contrastInvertedColor" : "#ffffff",
"contrastPrimaryColor" : "#333333",
"font" : "Salesforce Sans",
"height" : 498,
"navBarColor" : "#222222",
"primaryColor" : "#222222",
"secondaryColor" : "#005290",
253
組み込みサービス設定の取得リファレンス

===== PAGE 264 =====
"width" : 320
},
"embeddedServiceLiveAgent" : {
"avatarImg" : "",
"embeddedServiceQuickActions" : [ {
"order" : 1,
"quickActionDefinition" : "Snapins_Case_OfflineCaseQuickAction_08hRM00000000cC",
"quickActionType" : "OfflineCase"
}, {
"order" : 1,
"quickActionDefinition" : "Snapins_Contact_PrechatQuickAction_08hRM00000000RC",
"quickActionType" : "Prechat"
}, {
"order" : 2,
"quickActionDefinition" : "Snapins_Case_PrechatQuickAction_08hRM00000000RC",
"quickActionType" : "Prechat"
} ],
"enabled" : true,
"fontSize" : "Medium",
"headerBackgroundImg" : "https://google.com/img/headerBgImgUrl.png",
"isOfflineCaseEnabled" : true,
"isQueuePositionEnabled" : true,
"liveChatButton" : "573RM0000004GGf",
"liveChatDeployment" : "572RM0000004CDV",
"offlineCaseBackgroundImg" : "https://google.com/img/offlineBgImgUrl.png",
"prechatBackgroundImg" : "https://google.com/img/prechatBgImgUrl.png",
"prechatEnabled" : true,
"scenario" : "Service",
"smallCompanyLogoImg" : "https://google.com/img/logoImgUrl.png",
"waitingStateBackgroundImg" : "https://google.com/img/bgImgUrl.png"
},
"shouldHideAuthDialog" : false,
"siteUrl" : "https://snapins-15f082fb956-15fbc261d27.stmfa.stm.force.com/napili2"
}
}
組み込みサービス設定のヘッダーの返送
Embedded Service Configuration Describe リソースへの GET 要求のヘッダーのみを返します。リソースのコンテンツ
を取得する前に、前もってヘッダー値を確認できます。照会する EmbeddedServiceConfigDeveloperName を所有す
るアカウントにログインしている必要があります。このリソースは REST API バージョン 45.0 以降で使用できま
す。
構文
URI
/services/data/vXX.X/support/embeddedservice/configuration/embeddedServiceConfigDeveloperName
254
組み込みサービス設定のヘッダーの返送リファレンス

===== PAGE 265 =====
形式
JSON
HTTP のメソッド
HEAD
認証
Authorization: Bearer token
要求パラメーター
なし
Invocable Actions
標準呼び出し可能アクションおよびカスタム呼び出し可能アクションを表します。アクションを使用してアプ
リケーションに機能を追加します。Chatter への投稿やメールの送信などの標準アクションから選択するか、会
社のニーズに基づいてアクションを作成します。
このセクションの内容:
呼び出し可能アクションの取得
呼び出し可能な標準アクションおよびカスタムアクションの URI を Salesforce から取得します。このリソー
スは REST API バージョン 32.0 以降で使用できます。
呼び出し可能アクションの HTTP ヘッダーの返送
呼び出し可能アクションリソースに GET 要求を送信したときに返されるヘッダーのみを返します。これに
より、コンテンツを取得する前に、GET 要求で返されたヘッダー値を確認できます。このリソースは REST
API バージョン 32.0 以降で使用できます。
関連トピック:
Apex 開発者ガイド: InvocableMethod アノテーション
呼び出し可能アクションの取得
呼び出し可能な標準アクションおよびカスタムアクションの URI を Salesforce から取得します。このリソースは
REST API バージョン 32.0 以降で使用できます。
例
URI
/services/data/vXX.X/actions
形式
JSON、XML
255
Invocable Actionsリファレンス

===== PAGE 266 =====
HTTP のメソッド
GET
認証
Authorization: Bearer token
要求パラメーター
不要
例
リクエストの例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/actions -H "Authorization:
Bearer token"
レスポンスボディの例
{
"standard" : "/services/data/v60.0/actions/standard",
"custom" : "/services/data/v60.0/actions/custom"
}
呼び出し可能アクションの HTTP ヘッダーの返送
呼び出し可能アクションリソースに GET 要求を送信したときに返されるヘッダーのみを返します。これによ
り、コンテンツを取得する前に、GET 要求で返されたヘッダー値を確認できます。このリソースは REST API バー
ジョン 32.0 以降で使用できます。
URI
/services/data/vXX.X/actions
形式
JSON、XML
HTTP のメソッド
HEAD
認証
Authorization: Bearer token
256
呼び出し可能アクションの HTTP ヘッダーの返送リファレンス

===== PAGE 267 =====
要求パラメーター
不要
例
リクエストの例
curl -X HEAD --head https://MyDomainName.my.salesforce.com/services/data/v60.0/actions -H
"Authorization: Bearer token"
レスポンスボディの例
HTTP/1.1 200 OK
Date: Mon, 21 Nov 2022 22:56:26 GMT
Invocable Actions Custom
静的に呼び出し可能なカスタム呼び出し可能アクションのリストを返します。また、アクション種別ごとに基
本情報を取得することもできます。
このセクションの内容:
カスタム呼び出し可能アクションの取得
すべてのカスタム呼び出し可能アクションのリストを取得します。いくつかのアクションでは、特別なア
クセス権が必要です。このリソースは REST API バージョン 32.0 以降で使用できます。
カスタム呼び出し可能アクションの HTTP ヘッダーの返送
カスタム呼び出し可能アクションリソースに GET 要求を送信したときに返されるヘッダーのみを返します。
これにより、コンテンツを取得する前に、GET 要求で返されたヘッダー値を確認できます。このリソースは
REST API バージョン 32.0 以降で使用できます。
関連トピック:
Apex 開発者ガイド: InvocableMethod アノテーション
カスタム呼び出し可能アクションの取得
すべてのカスタム呼び出し可能アクションのリストを取得します。いくつかのアクションでは、特別なアクセ
ス権が必要です。このリソースは REST API バージョン 32.0 以降で使用できます。
emailAlert アクションを使用したメールの送信は、ワークフローの日次メール制限に反映されます。詳細
は、Salesforce ヘルプの「メールアラートの 1 日の割り当て」を参照してください。
POST メソッドを使用して Apex アクションを呼び出し、要求で入力を提供する場合、入力でサポートされてい
るのは次のプリミティブ型のみです。
• Blob
• Boolean
257
Invocable Actions Customリファレンス

===== PAGE 268 =====
• Date
• Datetime
• Decimal
• Double
• ID
• Integer
• Long
• String
• Time
Apex アクションの説明と呼び出しでは、Apex クラスのプロファイルアクセスが考慮されます。アクセス権を
持たない場合は、エラーになります。
Apex アクションをフローに追加した後で、Apex クラスから Invocable Method アノテーションを削除すると、フ
ローでランタイムエラーが発生します。
フローユーザーが自動起動フローを呼び出すと、有効なフローバージョンが実行されます。有効なバージョン
がない場合は、最新バージョンが実行されます。フロー管理者がフローを呼び出すと、常に最新のバージョン
が実行されます。
フローで次のいずれかの要素を使用すると、その要素を参照する、パッケージ化可能なコンポーネントは自動
的にパッケージに含まれません。
• Apex アクション
• メールアラート
• Chatter に投稿コアアクション
• クイックアクションコアアクション
• メールを送信コアアクション
• 承認申請コアアクション
たとえば、メールアラートを送信する場合は、そのメールアラートで使用されるメールテンプレートを手動で
追加します。パッケージを正常にリリースするには、参照されるこれらのコンポーネントをパッケージに手動
で追加します。
アクションについての詳細は、『Actions Developer Guide (アクション開発者ガイド)』を参照してください。
構文
URI
/services/data/vXX.X/actions/custom
形式
JSON、XML
258
カスタム呼び出し可能アクションの取得リファレンス

===== PAGE 269 =====
HTTP のメソッド
\ GET
認証
Authorization: Bearer token
要求パラメーター
不要
例
リクエストの例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/actions/custom -H
"Authorization: Bearer token"
レスポンスボディの例
{
"quickAction" : "/services/data/v60.0/actions/custom/quickAction",
"apex" : "/services/data/v60.0/actions/custom/apex",
"emailAlert" : "/services/data/v60.0/actions/custom/emailAlert",
"flow" : "/services/data/v60.0/actions/custom/flow",
"sendNotification" : "/services/data/v60.0/actions/custom/sendNotification"
}
カスタム呼び出し可能アクションの HTTP ヘッダーの返送
カスタム呼び出し可能アクションリソースに GET 要求を送信したときに返されるヘッダーのみを返します。こ
れにより、コンテンツを取得する前に、GET 要求で返されたヘッダー値を確認できます。このリソースは REST
API バージョン 32.0 以降で使用できます。
URI
/services/data/vXX.X/actions/custom
形式
JSON、XML
HTTP のメソッド
HEAD
259
カスタム呼び出し可能アクションの HTTP ヘッダーの返
送
リファレンス

===== PAGE 270 =====
認証
Authorization: Bearer token
要求パラメーター
不要
例
リクエストの例
curl -X HEAD --head
https://MyDomainName.my.salesforce.com/services/data/v60.0/actions/custom -H "Authorization:
Bearer token"
レスポンスボディの例
HTTP/1.1 200 OK
Date: Mon, 21 Nov 2022 22:56:26 GMT
Invocable Actions Standard
静的に呼び出し可能な標準呼び出し可能アクションのリストを返します。また、アクション種別ごとに基本情
報を取得することもできます。
このセクションの内容:
標準呼び出し可能アクションの取得
Salesforce が提供する標準の呼び出し可能アクションのリストを取得します。いくつかのアクションでは、
特別なアクセス権が必要です。このリソースは REST API バージョン 32.0 以降で使用できます。
標準呼び出し可能アクションの HTTP ヘッダーの返送
標準呼び出し可能アクションリソースに GET 要求を送信したときに返されるヘッダーのみを返します。こ
れにより、コンテンツを取得する前に、GET 要求で返されたヘッダー値を確認できます。このリソースは
REST API バージョン 32.0 以降で使用できます。
関連トピック:
Apex 開発者ガイド: InvocableMethod アノテーション
標準呼び出し可能アクションの取得
Salesforce が提供する標準の呼び出し可能アクションのリストを取得します。いくつかのアクションでは、特別
なアクセス権が必要です。このリソースは REST API バージョン 32.0 以降で使用できます。
Salesforce Omnichannel Inventory および Salesforce Order Management では、対応する Connect REST API エンドポイントま
たは Apex ConnectApi メソッドをコールすることもできます。詳細は、『Connect REST API 開発者ガイド』の「Salesforce
260
Invocable Actions Standardリファレンス

===== PAGE 271 =====
Omnichannel Inventory リソース」と「Salesforce Order Management リソース」、および『Apex リファレンスガイド』
の「ConnectApi 名前空間」を参照してください。
Chatter への投稿アクションでは、本文の投稿で特殊な形式を使用する次の機能がサポートされています。たと
えば、「Hi @[005000000000001], check out #[some_topic]」という文字列は「Hi @Joe, check
out #some_topic」として適切に保存されます。ここで、「@Joe」と「#some_topic」は、それぞれユーザー
およびトピックへのリンクです。
• @[<id>] を使用する @メンション
• #[<topicString>] を使用するトピックリンク
アクションについての詳細は、『Actions Developer Guide (アクション開発者ガイド) 』を参照してください。
構文
URI
/services/data/vXX.X/actions/standard
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
要求パラメーター
不要
例
リクエストの例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/actions/standard -H
"Authorization: Bearer token"
レスポンスボディの例
{
"actions" : [ {
"label" : "Post to Chatter",
"name" : "chatterPost",
"type" : "CHATTERPOST",
261
標準呼び出し可能アクションの取得リファレンス

===== PAGE 272 =====
"url" : "/services/data/v60.0/actions/standard/chatterPost"
}, {
"label" : "Enable Folder Support for a Content Workspace (Library)",
"name" : "contentWorkspaceEnableFolders",
"type" : "CONTENTWORKSPACE_ENABLE_FOLDERS",
"url" : "/services/data/v60.0/actions/standard/contentWorkspaceEnableFolders"
}, {
"label" : "Send Email",
"name" : "emailSimple",
"type" : "EMAILSIMPLE",
"url" : "/services/data/v60.0/actions/standard/emailSimple"
}, {
"label" : "Submit for Approval",
"name" : "submit",
"type" : "SUBMITAPPROVAL",
"url" : "/services/data/v60.0/actions/standard/submit"
}, {
"label" : "Deactivate Session-Based Permission Set",
"name" : "deactivateSessionPermSet",
"type" : "DEACTIVATE_SESSION_PERM_SET",
"url" : "/services/data/v60.0/actions/standard/deactivateSessionPermSet"
}, {
"label" : "Activate Session-Based Permission Set",
"name" : "activateSessionPermSet",
"type" : "ACTIVATE_SESSION_PERM_SET",
"url" : "/services/data/v60.0/actions/standard/activateSessionPermSet"
}, {
"label" : "Choose Price Book",
"name" : "choosePricebook",
"type" : "CHOOSE_PRICEBOOK",
"url" : "/services/data/v60.0/actions/standard/choosePricebook"
}, {
"label" : "Routing Address Verification",
"name" : "routingAddressVerification",
"type" : "ROUTING_ADDRESS_VERIFICATION",
"url" : "/services/data/v60.0/actions/standard/routingAddressVerification"
}, {
"label" : "Create Customer Contact Request",
"name" : "contactRequestAction",
"type" : "CONTACT_REQUEST_ACTION",
"url" : "/services/data/v60.0/actions/standard/contactRequestAction"
}, {
"label" : "Publish Managed Content Release",
"name" : "managedContentReleasePublish",
"type" : "MANAGED_CONTENT_RELEASE_PUBLISH",
"url" : "/services/data/v60.0/actions/standard/managedContentReleasePublish"
} ]
}
262
標準呼び出し可能アクションの取得リファレンス

===== PAGE 273 =====
標準呼び出し可能アクションの HTTP ヘッダーの返送
標準呼び出し可能アクションリソースに GET 要求を送信したときに返されるヘッダーのみを返します。これに
より、コンテンツを取得する前に、GET 要求で返されたヘッダー値を確認できます。このリソースは REST API
バージョン 32.0 以降で使用できます。
構文
URI
/services/data/vXX.X/actions/standard
形式
JSON、XML
HTTP のメソッド
HEAD
認証
Authorization: Bearer token
要求パラメーター
不要
例
リクエストの例
curl -X HEAD --head
https://MyDomainName.my.salesforce.com/services/data/v60.0/actions/standard -H
"Authorization: Bearer token"
レスポンスボディの例
HTTP/1.1 200 OK
Date: Mon, 21 Nov 2022 22:56:26 GMT
List View Basic Information
ラベル、API 参照名、ID など、特定のリストビューの基本情報を返します。このリソースは REST API バージョン
32.0 以降で使用できます。
263
標準呼び出し可能アクションの HTTP ヘッダーの返送リファレンス

===== PAGE 274 =====
URI
/services/data/vXX.X/sobjects/sObject/listviews/listViewID
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
パラメーター
なし
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcBeMAK
-H "Authorization: Bearer token"
レスポンスボディの例
{
"describeUrl" :
"/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcBeMAK/describe",
"developerName" : "NewThisWeek",
"id" : "00BD0000005WcBeMAK",
"label" : "New This Week",
"resultsUrl" :
"/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcBeMAK/results",
"soqlCompatible" : true,
"url" : "/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcBeMAK"
}
List View Describe
ID、列、SOQL クエリなど、リストビューに関する詳細な情報を返します。
このリソースは REST API バージョン 32.0 以降で使用できます。
URI
/services/data/vXX.X/sobjects/sObject/listviews/queryLocator/describe
形式
JSON、XML
HTTP メソッド
GET
認証
Authorization: Bearer token
264
List View Describeリファレンス

===== PAGE 275 =====
パラメーター
なし
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcBeMAK/describe
-H "Authorization: Bearer token"
レスポンスボディの例
{
"columns" : [ {
"ascendingLabel" : "Z-A",
"descendingLabel" : "A-Z",
"fieldNameOrPath" : "Name",
"hidden" : false,
"label" : "Account Name",
"selectListItem" : "Name",
"sortDirection" : "ascending",
"sortIndex" : 0,
"sortable" : true,
"type" : "string"
}, {
"ascendingLabel" : "Z-A",
"descendingLabel" : "A-Z",
"fieldNameOrPath" : "Site",
"hidden" : false,
"label" : "Account Site",
"selectListItem" : "Site",
"sortDirection" : null,
"sortIndex" : null,
"sortable" : true,
"type" : "string"
}, {
"ascendingLabel" : "Z-A",
"descendingLabel" : "A-Z",
"fieldNameOrPath" : "BillingState",
"hidden" : false,
"label" : "Billing State/Province",
"selectListItem" : "BillingState",
"sortDirection" : null,
"sortIndex" : null,
"sortable" : true,
"type" : "string"
}, {
"ascendingLabel" : "9-0",
"descendingLabel" : "0-9",
"fieldNameOrPath" : "Phone",
"hidden" : false,
"label" : "Phone",
265
List View Describeリファレンス

===== PAGE 276 =====
"selectListItem" : "Phone",
"sortDirection" : null,
"sortIndex" : null,
"sortable" : true,
"type" : "phone"
}, {
"ascendingLabel" : "Low to High",
"descendingLabel" : "High to Low",
"fieldNameOrPath" : "Type",
"hidden" : false,
"label" : "Type",
"selectListItem" : "toLabel(Type)",
"sortDirection" : null,
"sortIndex" : null,
"sortable" : true,
"type" : "picklist"
}, {
"ascendingLabel" : "Z-A",
"descendingLabel" : "A-Z",
"fieldNameOrPath" : "Owner.Alias",
"hidden" : false,
"label" : "Account Owner Alias",
"selectListItem" : "Owner.Alias",
"sortDirection" : null,
"sortIndex" : null,
"sortable" : true,
"type" : "string"
}, {
"ascendingLabel" : null,
"descendingLabel" : null,
"fieldNameOrPath" : "Id",
"hidden" : true,
"label" : "Account ID",
"selectListItem" : "Id",
"sortDirection" : null,
"sortIndex" : null,
"sortable" : false,
"type" : "id"
}, {
"ascendingLabel" : null,
"descendingLabel" : null,
"fieldNameOrPath" : "CreatedDate",
"hidden" : true,
"label" : "Created Date",
"selectListItem" : "CreatedDate",
"sortDirection" : null,
"sortIndex" : null,
"sortable" : false,
"type" : "datetime"
}, {
"ascendingLabel" : null,
"descendingLabel" : null,
"fieldNameOrPath" : "LastModifiedDate",
"hidden" : true,
266
List View Describeリファレンス

===== PAGE 277 =====
"label" : "Last Modified Date",
"selectListItem" : "LastModifiedDate",
"sortDirection" : null,
"sortIndex" : null,
"sortable" : false,
"type" : "datetime"
}, {
"ascendingLabel" : null,
"descendingLabel" : null,
"fieldNameOrPath" : "SystemModstamp",
"hidden" : true,
"label" : "System Modstamp",
"selectListItem" : "SystemModstamp",
"sortDirection" : null,
"sortIndex" : null,
"sortable" : false,
"type" : "datetime"
} ],
"id" : "00BD0000005WcBe",
"orderBy" : [ {
"fieldNameOrPath" : "Name",
"nullsPosition" : "first",
"sortDirection" : "ascending"
}, {
"fieldNameOrPath" : "Id",
"nullsPosition" : "first",
"sortDirection" : "ascending"
} ],
"query" : "SELECT name, site, billingstate, phone, tolabel(type), owner.alias, id,
createddate, lastmodifieddate, systemmodstamp FROM Account WHERE CreatedDate = THIS_WEEK
ORDER BY Name ASC NULLS FIRST, Id ASC NULLS FIRST",
"scope" : null,
"sobjectType" : "Account",
"whereCondition" : {
"field" : "CreatedDate",
"operator" : "equals",
"values" : [ "THIS_WEEK" ]
}
}
List View Results
リストビューに対する SOQL クエリを実行し、結果のデータと表示情報を返します。このリソースは REST API
バージョン 32.0 以降で使用できます。
構文
URI
/services/data/vXX.X/sobjects/sObject/listviews/listViewID/results
形式
JSON、XML
267
List View Resultsリファレンス

===== PAGE 278 =====
HTTP メソッド
GET
認証
Authorization: Bearer token
パラメーター
説明パラメーター
返すレコードの最大数 (1 ～ 2000)。デフォルト値は、
25 です。
limit
返す最初のレコード。このパラメーターを使用し
て、結果をページ設定します。デフォルト値は、1
です。
offset
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcCNMA0/results
-H "Authorization: Bearer token"
レスポンスボディの例
{
"columns" : [ {
"ascendingLabel" : "Z-A",
"descendingLabel" : "A-Z",
"fieldNameOrPath" : "Name",
"hidden" : false,
"label" : "Account Name",
"selectListItem" : "Name",
"sortDirection" : "ascending",
"sortIndex" : 0,
"sortable" : true,
"type" : "string"
}, {
"ascendingLabel" : "Z-A",
"descendingLabel" : "A-Z",
"fieldNameOrPath" : "Site",
"hidden" : false,
"label" : "Account Site",
"selectListItem" : "Site",
"sortDirection" : null,
"sortIndex" : null,
"sortable" : true,
"type" : "string"
}, {
"ascendingLabel" : "Z-A",
"descendingLabel" : "A-Z",
268
List View Resultsリファレンス

===== PAGE 279 =====
"fieldNameOrPath" : "BillingState",
"hidden" : false,
"label" : "Billing State/Province",
"selectListItem" : "BillingState",
"sortDirection" : null,
"sortIndex" : null,
"sortable" : true,
"type" : "string"
}, {
"ascendingLabel" : "9-0",
"descendingLabel" : "0-9",
"fieldNameOrPath" : "Phone",
"hidden" : false,
"label" : "Phone",
"selectListItem" : "Phone",
"sortDirection" : null,
"sortIndex" : null,
"sortable" : true,
"type" : "phone"
}, {
"ascendingLabel" : "Low to High",
"descendingLabel" : "High to Low",
"fieldNameOrPath" : "Type",
"hidden" : false,
"label" : "Type",
"selectListItem" : "toLabel(Type)",
"sortDirection" : null,
"sortIndex" : null,
"sortable" : true,
"type" : "picklist"
}, {
"ascendingLabel" : "Z-A",
"descendingLabel" : "A-Z",
"fieldNameOrPath" : "Owner.Alias",
"hidden" : false,
"label" : "Account Owner Alias",
"selectListItem" : "Owner.Alias",
"sortDirection" : null,
"sortIndex" : null,
"sortable" : true,
"type" : "string"
}, {
"ascendingLabel" : null,
"descendingLabel" : null,
"fieldNameOrPath" : "Id",
"hidden" : true,
"label" : "Account ID",
"selectListItem" : "Id",
"sortDirection" : null,
"sortIndex" : null,
"sortable" : false,
"type" : "id"
}, {
"ascendingLabel" : null,
269
List View Resultsリファレンス

===== PAGE 280 =====
"descendingLabel" : null,
"fieldNameOrPath" : "CreatedDate",
"hidden" : true,
"label" : "Created Date",
"selectListItem" : "CreatedDate",
"sortDirection" : null,
"sortIndex" : null,
"sortable" : false,
"type" : "datetime"
}, {
"ascendingLabel" : null,
"descendingLabel" : null,
"fieldNameOrPath" : "LastModifiedDate",
"hidden" : true,
"label" : "Last Modified Date",
"selectListItem" : "LastModifiedDate",
"sortDirection" : null,
"sortIndex" : null,
"sortable" : false,
"type" : "datetime"
}, {
"ascendingLabel" : null,
"descendingLabel" : null,
"fieldNameOrPath" : "SystemModstamp",
"hidden" : true,
"label" : "System Modstamp",
"selectListItem" : "SystemModstamp",
"sortDirection" : null,
"sortIndex" : null,
"sortable" : false,
"type" : "datetime"
} ],
"developerName" : "MyAccounts",
"done" : true,
"id" : "00BD0000005WcCN",
"label" : "My Accounts",
"records" : [ {
"columns" : [ {
"fieldNameOrPath" : "Name",
"value" : "Burlington Textiles Corp of America"
}, {
"fieldNameOrPath" : "Site",
"value" : null
}, {
"fieldNameOrPath" : "BillingState",
"value" : "NC"
}, {
"fieldNameOrPath" : "Phone",
"value" : "(336) 222-7000"
}, {
"fieldNameOrPath" : "Type",
"value" : "Customer - Direct"
}, {
"fieldNameOrPath" : "Owner.Alias",
270
List View Resultsリファレンス

===== PAGE 281 =====
"value" : "TUser"
}, {
"fieldNameOrPath" : "Id",
"value" : "001D000000JliSTIAZ"
}, {
"fieldNameOrPath" : "CreatedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "LastModifiedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "SystemModstamp",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
} ]
}, {
"columns" : [ {
"fieldNameOrPath" : "Name",
"value" : "Dickenson plc"
}, {
"fieldNameOrPath" : "Site",
"value" : null
}, {
"fieldNameOrPath" : "BillingState",
"value" : "KS"
}, {
"fieldNameOrPath" : "Phone",
"value" : "(785) 241-6200"
}, {
"fieldNameOrPath" : "Type",
"value" : "Customer - Channel"
}, {
"fieldNameOrPath" : "Owner.Alias",
"value" : "TUser"
}, {
"fieldNameOrPath" : "Id",
"value" : "001D000000JliSVIAZ"
}, {
"fieldNameOrPath" : "CreatedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "LastModifiedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "SystemModstamp",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
} ]
}, {
"columns" : [ {
"fieldNameOrPath" : "Name",
"value" : "Edge Communications"
}, {
"fieldNameOrPath" : "Site",
"value" : null
}, {
271
List View Resultsリファレンス

===== PAGE 282 =====
"fieldNameOrPath" : "BillingState",
"value" : "TX"
}, {
"fieldNameOrPath" : "Phone",
"value" : "(512) 757-6000"
}, {
"fieldNameOrPath" : "Type",
"value" : "Customer - Direct"
}, {
"fieldNameOrPath" : "Owner.Alias",
"value" : "TUser"
}, {
"fieldNameOrPath" : "Id",
"value" : "001D000000JliSSIAZ"
}, {
"fieldNameOrPath" : "CreatedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "LastModifiedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "SystemModstamp",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
} ]
}, {
"columns" : [ {
"fieldNameOrPath" : "Name",
"value" : "Express Logistics and Transport"
}, {
"fieldNameOrPath" : "Site",
"value" : null
}, {
"fieldNameOrPath" : "BillingState",
"value" : "OR"
}, {
"fieldNameOrPath" : "Phone",
"value" : "(503) 421-7800"
}, {
"fieldNameOrPath" : "Type",
"value" : "Customer - Channel"
}, {
"fieldNameOrPath" : "Owner.Alias",
"value" : "TUser"
}, {
"fieldNameOrPath" : "Id",
"value" : "001D000000JliSXIAZ"
}, {
"fieldNameOrPath" : "CreatedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "LastModifiedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "SystemModstamp",
272
List View Resultsリファレンス

===== PAGE 283 =====
"value" : "Fri Aug 01 21:15:46 GMT 2014"
} ]
}, {
"columns" : [ {
"fieldNameOrPath" : "Name",
"value" : "GenePoint"
}, {
"fieldNameOrPath" : "Site",
"value" : null
}, {
"fieldNameOrPath" : "BillingState",
"value" : "CA"
}, {
"fieldNameOrPath" : "Phone",
"value" : "(650) 867-3450"
}, {
"fieldNameOrPath" : "Type",
"value" : "Customer - Channel"
}, {
"fieldNameOrPath" : "Owner.Alias",
"value" : "TUser"
}, {
"fieldNameOrPath" : "Id",
"value" : "001D000000JliSPIAZ"
}, {
"fieldNameOrPath" : "CreatedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "LastModifiedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "SystemModstamp",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
} ]
}, {
"columns" : [ {
"fieldNameOrPath" : "Name",
"value" : "Grand Hotels and Resorts Ltd"
}, {
"fieldNameOrPath" : "Site",
"value" : null
}, {
"fieldNameOrPath" : "BillingState",
"value" : "IL"
}, {
"fieldNameOrPath" : "Phone",
"value" : "(312) 596-1000"
}, {
"fieldNameOrPath" : "Type",
"value" : "Customer - Direct"
}, {
"fieldNameOrPath" : "Owner.Alias",
"value" : "TUser"
}, {
273
List View Resultsリファレンス

===== PAGE 284 =====
"fieldNameOrPath" : "Id",
"value" : "001D000000JliSWIAZ"
}, {
"fieldNameOrPath" : "CreatedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "LastModifiedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "SystemModstamp",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
} ]
}, {
"columns" : [ {
"fieldNameOrPath" : "Name",
"value" : "Pyramid Construction Inc."
}, {
"fieldNameOrPath" : "Site",
"value" : null
}, {
"fieldNameOrPath" : "BillingState",
"value" : null
}, {
"fieldNameOrPath" : "Phone",
"value" : "(014) 427-4427"
}, {
"fieldNameOrPath" : "Type",
"value" : "Customer - Channel"
}, {
"fieldNameOrPath" : "Owner.Alias",
"value" : "TUser"
}, {
"fieldNameOrPath" : "Id",
"value" : "001D000000JliSUIAZ"
}, {
"fieldNameOrPath" : "CreatedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "LastModifiedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "SystemModstamp",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
} ]
}, {
"columns" : [ {
"fieldNameOrPath" : "Name",
"value" : "sForce"
}, {
"fieldNameOrPath" : "Site",
"value" : null
}, {
"fieldNameOrPath" : "BillingState",
"value" : "CA"
274
List View Resultsリファレンス

===== PAGE 285 =====
}, {
"fieldNameOrPath" : "Phone",
"value" : "(415) 901-7000"
}, {
"fieldNameOrPath" : "Type",
"value" : null
}, {
"fieldNameOrPath" : "Owner.Alias",
"value" : "TUser"
}, {
"fieldNameOrPath" : "Id",
"value" : "001D000000JliSaIAJ"
}, {
"fieldNameOrPath" : "CreatedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "LastModifiedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "SystemModstamp",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
} ]
}, {
"columns" : [ {
"fieldNameOrPath" : "Name",
"value" : "United Oil and Gas Corp."
}, {
"fieldNameOrPath" : "Site",
"value" : null
}, {
"fieldNameOrPath" : "BillingState",
"value" : "NY"
}, {
"fieldNameOrPath" : "Phone",
"value" : "(212) 842-5500"
}, {
"fieldNameOrPath" : "Type",
"value" : "Customer - Direct"
}, {
"fieldNameOrPath" : "Owner.Alias",
"value" : "TUser"
}, {
"fieldNameOrPath" : "Id",
"value" : "001D000000JliSZIAZ"
}, {
"fieldNameOrPath" : "CreatedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "LastModifiedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "SystemModstamp",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
} ]
275
List View Resultsリファレンス

===== PAGE 286 =====
}, {
"columns" : [ {
"fieldNameOrPath" : "Name",
"value" : "United Oil and Gas, Singapore"
}, {
"fieldNameOrPath" : "Site",
"value" : null
}, {
"fieldNameOrPath" : "BillingState",
"value" : "Singapore"
}, {
"fieldNameOrPath" : "Phone",
"value" : "(650) 450-8810"
}, {
"fieldNameOrPath" : "Type",
"value" : "Customer - Direct"
}, {
"fieldNameOrPath" : "Owner.Alias",
"value" : "TUser"
}, {
"fieldNameOrPath" : "Id",
"value" : "001D000000JliSRIAZ"
}, {
"fieldNameOrPath" : "CreatedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "LastModifiedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "SystemModstamp",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
} ]
}, {
"columns" : [ {
"fieldNameOrPath" : "Name",
"value" : "United Oil and Gas, UK"
}, {
"fieldNameOrPath" : "Site",
"value" : null
}, {
"fieldNameOrPath" : "BillingState",
"value" : "UK"
}, {
"fieldNameOrPath" : "Phone",
"value" : "+44 191 4956203"
}, {
"fieldNameOrPath" : "Type",
"value" : "Customer - Direct"
}, {
"fieldNameOrPath" : "Owner.Alias",
"value" : "TUser"
}, {
"fieldNameOrPath" : "Id",
"value" : "001D000000JliSQIAZ"
276
List View Resultsリファレンス

===== PAGE 287 =====
}, {
"fieldNameOrPath" : "CreatedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "LastModifiedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "SystemModstamp",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
} ]
}, {
"columns" : [ {
"fieldNameOrPath" : "Name",
"value" : "University of Arizona"
}, {
"fieldNameOrPath" : "Site",
"value" : null
}, {
"fieldNameOrPath" : "BillingState",
"value" : "AZ"
}, {
"fieldNameOrPath" : "Phone",
"value" : "(520) 773-9050"
}, {
"fieldNameOrPath" : "Type",
"value" : "Customer - Direct"
}, {
"fieldNameOrPath" : "Owner.Alias",
"value" : "TUser"
}, {
"fieldNameOrPath" : "Id",
"value" : "001D000000JliSYIAZ"
}, {
"fieldNameOrPath" : "CreatedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "LastModifiedDate",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
}, {
"fieldNameOrPath" : "SystemModstamp",
"value" : "Fri Aug 01 21:15:46 GMT 2014"
} ]
} ],
"size" : 12
}
オブジェクトのリストビュー
指定された sObject のリストビューのリストを返します。各リストビューの ID とその他の基本情報も含まれま
す。このリソースは REST API バージョン 32.0 以降で使用できます。
URI
/services/data/vXX.X/sobjects/sObject/listviews
277
オブジェクトのリストビューリファレンス

===== PAGE 288 =====
形式
JSON、XML
HTTP メソッド
GET
認証
Authorization: Bearer token
パラメーター
なし
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/listviews
-H "Authorization: Bearer token"
レスポンスボディの例
{
"done" : true,
"listviews" : [ {
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
"/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcBpMAK/describe",
"developerName" : "NewLastWeek",
"id" : "00BD0000005WcBpMAK",
"label" : "New Last Week",
"resultsUrl" :
"/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcBpMAK/results",
"soqlCompatible" : true,
"url" : "/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcBpMAK"
}, {
"describeUrl" :
"/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcC6MAK/describe",
"developerName" : "PlatinumandGoldSLACustomers",
"id" : "00BD0000005WcC6MAK",
"label" : "Platinum and Gold SLA Customers",
"resultsUrl" :
"/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcC6MAK/results",
"soqlCompatible" : true,
"url" : "/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcC6MAK"
278
オブジェクトのリストビューリファレンス

===== PAGE 289 =====
}, {
"describeUrl" :
"/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcCEMA0/describe",
"developerName" : "RecentlyViewedAccounts",
"id" : "00BD0000005WcCEMA0",
"label" : "Recently Viewed Accounts",
"resultsUrl" :
"/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcCEMA0/results",
"soqlCompatible" : true,
"url" : "/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcCEMA0"
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
}, {
"describeUrl" :
"/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcCNMA0/describe",
"developerName" : "MyAccounts",
"id" : "00BD0000005WcCNMA0",
"label" : "My Accounts",
"resultsUrl" :
"/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcCNMA0/results",
"soqlCompatible" : true,
"url" : "/services/data/v60.0/sobjects/Account/listviews/00BD0000005WcCNMA0"
} ],
"nextRecordsUrl" : null,
"size" : 6,
"sobjectType" : "Account"
}
REST API を使用してナレッジをサポートする
ナレッジサポート REST API を使用して、承認済みユーザーとゲストユーザーの両方が自身の表示可能なデータ
カテゴリとその関連記事を取得できます。このリソースは REST API バージョン 38.0 以降で使用できます。
承認済みユーザーには、UserProfile.apiEnabled 権限、組織でナレッジが有効になっていること、記事タ
イプに対する参照権限、および記事の表示を制御するその他のナレッジ固有の権限または設定が必要です。
ゲストユーザーには、関連サイトで [サポート API へのゲストアクセス] 設定が有効になっていること、組織
でナレッジが有効になっていること、ゲストユーザーへの表示を制御する記事チャネルおよび記事タイプに対
する参照権限が必要です。
279
REST API を使用してナレッジをサポートするリファレンス

===== PAGE 290 =====
構文
URI
/services/data/vXX.X/support
メソッド
GET
形式
JSON、XML
認証
Authorization: Bearer token
例
レスポンスボディの例
{
"dataCategoryGroups" : "/services/data/vXX.X/support/dataCategoryGroups",
"knowledgeArticles" : "/services/data/vXX.X/support/knowledgeArticles"
:
}
このセクションの内容:
Data Category Groups
現在のユーザーが参照可能なデータカテゴリグループを取得します。このリソースは REST API バージョン
38.0 以降で使用できます。
Data Category Detail
指定されたカテゴリのデータカテゴリの詳細と子カテゴリを取得します。このリソースは API バージョン
38.0 以降で使用できます。
Articles List
検索またはクエリによって、指定された言語およびカテゴリのオンライン記事のページを取得します。こ
のリソースは REST API バージョン 38.0 以降で使用できます。
Articles Details
ユーザーがアクセスできるすべての記事項目を取得します。このリソースは、REST API バージョン 38.0 以降
は記事 ID で利用でき、バージョン 44.0 以降は記事の URL 名で利用できます。
Data Category Groups
現在のユーザーが参照可能なデータカテゴリグループを取得します。このリソースは REST API バージョン 38.0
以降で使用できます。
Salesforce ナレッジが組織で有効になっている必要があります。このリソースは API バージョン 38.0 以降で使用
できます。「Salesforce がサポートする言語は?」で使用されている言語コード形式を使用してください。
ユーザーが参照可能なデータカテゴリのみが返されます。ユーザーはカテゴリグループ内のいくつかのサブツ
リーを参照できる場合があるため、各グループ内でユーザーが参照可能な最上位カテゴリが返されます。
280
Data Category Groupsリファレンス

===== PAGE 291 =====
構文
URI
/services/data/vXX.X/support/dataCategoryGroups
メソッド
GET
形式
JSON、XML
認証
Authorization: Bearer token
HTTP ヘッダー
Accept: 省略可能。application/json または application/xml のいずれかです。
Accept-language: 省略可能。カテゴリを翻訳する言語。HTTP Accept-Language ヘッダーのいずれかの ISO-639 言
語の略語および ISO-3166 国コードサブタグ。指定できる言語は 1 つのみです。原語が指定されない場合、翻
訳されていない表示ラベルが返されます。
入力:
string sObjectName: 必須。KnowledgeArticleVersion のみ。
boolean topCategoriesOnly: 省略可能。デフォルトは true です。
• true の場合、最上位カテゴリのみを返します。
• false の場合、ツリー全体を返します。
メモ: すべての入力パラメーターで大文字と小文字が区別されます。
出力:
サイトのコンテキストで現在のユーザーが参照可能で有効なデータカテゴリグループのリスト。ID、名前、
表示ラベル、および現在のユーザーが参照可能な最上位カテゴリまたはデータカテゴリグループツリー全
体を返します。指定された言語がある場合、表示ラベルはその言語に翻訳されている必要があります。
• Data Category Group List
このペイロードは、他の要求でデータカテゴリとそれに関連する記事を返すために使用できる有効な
ルートデータカテゴリグループのリストです。
{
"categoryGroups": [ Data Category Group, ....],
}
メモ: 指定されたエンティティ (sObjectName によって指定) に関連する有効なグループのみを返
します。KnowledgeArticleVersion のみがサポートされています。
• Data Category Group
個々のデータカテゴリグループとそのルートカテゴリを表します。
{
"name": String, // the unique name of the category group
"label": String, // returns the translated version if it is available
"objectUsage" : String, // currently only "KnowledgeArticleVersion" is available.
281
Data Category Groupsリファレンス

===== PAGE 292 =====
"topCategories": [ Data Category Summary, ....]
}
• Data Category Summary
データカテゴリ情報の概要を提供します。Summary 応答と Detail 応答のプロパティは共通です。これは、
関連するリソースから必要な情報のみを提供するためです。
{
"name": String, // the unique name of the category
"label": String, // returns the translated version if it is available
"url": URL, // the url points to the data category detail API
"childCategories": [ Data Category Summary, ....] // null if topCategoriesOnly is
true
}
メモ:  URL プロパティは、このデータカテゴリを表す一意のリソース (この場合は Data Category Detail
API) への事前計算されたパスです。
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/support/dataCategoryGroups?sObjectName=KnowledgeArticleVersion
-H "Authorization: Bearer token"
レスポンスボディの例
{
"categoryGroups" : [ {
"label" : "Doc",
"name" : "Doc",
"objectUsage" : "KnowledgeArticleVersion",
"topCategories" : [ {
"childCategories" : null,
"label" : "All",
"name" : "All",
"url" :
"/services/data/v60.0/support/dataCategoryGroups/Doc/dataCategories/All?sObjectName=KnowledgeArticleVersion"
} ]
}, {
"label" : "Manual",
"name" : "Manual",
"objectUsage" : "KnowledgeArticleVersion",
"topCategories" : [ {
"childCategories" : null,
"label" : "All",
"name" : "All",
"url" :
"/services/data/v60.0/support/dataCategoryGroups/Manual/dataCategories/All?sObjectName=KnowledgeArticleVersion"
282
Data Category Groupsリファレンス

===== PAGE 293 =====
} ]
} ]
}
Data Category Detail
指定されたカテゴリのデータカテゴリの詳細と子カテゴリを取得します。このリソースは API バージョン 38.0
以降で使用できます。
Salesforce ナレッジが組織で有効になっている必要があります。「Salesforce がサポートする言語は?」で使用され
ている言語コード形式を使用してください。
構文
URI
/services/data/vXX.X/support/dataCategoryGroups/group/dataCategories/category
メソッド
GET
形式
JSON、XML
認証
Authorization: Bearer token
HTTP ヘッダー
Accept: 省略可能。application/json または application/xml のいずれかです。
Accept-language: 省略可能。カテゴリを翻訳する言語。HTTP Accept-Language ヘッダーのいずれかの ISO-639 言
語の略語および ISO-3166 国コードサブタグ。指定できる言語は 1 つのみです。原語が指定されない場合、翻
訳されていない表示ラベルが返されます。
入力:
string sObjectName: 必須。KnowledgeArticleVersion のみ。
出力:
カテゴリおよび子カテゴリのリストの詳細 (名前、表示ラベルなど)。
• Data Category Detail
データカテゴリの階層表現が重要な場合に使用されます。子プロパティには子データカテゴリのリスト
が含まれます。
{
"name": String, // the unique name of the category
"label": String, // returns the translated version if it is available
"url": URL,
"childCategories": [ Data Category Summary, ....],
}
メモ: カテゴリを現在のユーザーが参照可能でない場合、戻り値は空です。
283
Data Category Detailリファレンス

===== PAGE 294 =====
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/support/dataCategoryGroups/Doc/dataCategories/All?sObjectName=KnowledgeArticleVersion
-H "Authorization: Bearer token"
レスポンスボディの例
{
"childCategories" : [ {
"childCategories" : null,
"label" : "Help",
"name" : "Help",
"url" :
"/services/data/v60.0/support/dataCategoryGroups/Doc/dataCategories/Help?sObjectName=KnowledgeArticleVersion"
}, {
"childCategories" : null,
"label" : "QA",
"name" : "QA",
"url" :
"/services/data/v60.0/support/dataCategoryGroups/Doc/dataCategories/QA?sObjectName=KnowledgeArticleVersion"
} ],
"label" : "All",
"name" : "All",
"url" :
"/services/data/v60.0/support/dataCategoryGroups/Doc/dataCategories/All?sObjectName=KnowledgeArticleVersion"
}
Articles List
検索またはクエリによって、指定された言語およびカテゴリのオンライン記事のページを取得します。このリ
ソースは REST API バージョン 38.0 以降で使用できます。
構文
URI
/services/data/vXX.X/support/knowledgeArticles
メソッド
GET
形式
JSON、XML
認証
Authorization: Bearer token
HTTP ヘッダー
Accept: 省略可能。application/json または application/xml のいずれかです。
284
Articles Listリファレンス

===== PAGE 295 =====
Accept-language: 必須。記事は、ユーザーの組織で有効になっている言語で記述されている必要がありま
す。
• 言語コードが有効でない場合、「言語コードが有効でないか、ナレッジでサポートされていません。」
というエラーメッセージが返されます。
• 言語コードが有効であるが、ナレッジでサポートされていない場合、「無効な言語コードです。言語が
ナレッジ言語設定に含まれていることを確認してください。」というエラーメッセージが返されます。
入力:
string q: 省略可能。SOSL 検索を実行します。クエリ文字列が null または空であるか指定されていない場合、
SOQL クエリが実行されます。
文字 ? と * はワイルドカード検索に使用されます。文字 (、)、および " は、複雑な検索語に使用されま
す。https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/sforce_api_calls_sosl_find.htmを参照してく
ださい。
string channel: 省略可能。デフォルトはユーザーのコンテキストです。チャネル値の詳細は、「有効な
channel 値」を参照してください。
• App: 内部 Salesforce ナレッジアプリケーションで参照可能
• Pkb: 公開知識ベースで参照可能
• Csp: カスタマーポータルで参照可能
• Prm: パートナーポータルで参照可能
string categories  (json の対応付け形式 {"group1":"category1","group2":"category2",...} ) )
省略可能。デフォルトは None です。カテゴリグループはグループ:カテゴリの各ペア内で一意である必要が
あります。そうでない場合は、ARGUMENT_OBJECT_PARSE_ERROR が発生します。データカテゴリ条件の
数は 3 つまでに制限されています。この数を超えると、INVALID_FILTER_VALUE が発生します。
string queryMethod : 値は AT, BELOW, ABOVE, ABOVE_OR_BELOW です。カテゴリが指定されている場合
のみ有効です。デフォルトは ABOVE_OR_BELOW です。
string sort: 省略可能。並び替え可能な項目名 LastPublishedDate, CreatedDate, Title, ViewScore
です。デフォルトは LastPublishedDate で、クエリおよび検索の関連性に使用されます。
メモ: ViewScore で並び替える場合、使用できるのはクエリのみで、検索には使用できず、ページ
ネーションはサポートされません。結果は 1 ページのみ返されます。
string order: 省略可能。ASC または DESC。デフォルトは DESC です。sort が有効な場合のみ有効です。
integer pageSize: 省略可能。デフォルトは 20 です。有効な範囲は 1 ～ 100 です。
integer pageNumber : 省略可能。デフォルトは 1 です。
出力:
指定された言語およびカテゴリで、現在のユーザーが参照可能なオンライン記事のページ。
• Article Page
記事のページ。個々のエントリは、サイズを最小限に保つために記事の概要になっています。
{
"articles": [ Article Summary, … ], // list of articles
"currentPageUrl": URL, // the article list API with current page number
285
Articles Listリファレンス

===== PAGE 296 =====
"nextPageUrl": URL, // the article list API with next page number,
which can be null if there are no more articles.
"pageNumber": Int // the current page number, starting at 1.
}
メモ:  API ではページングがサポートされます。応答の各ページには、ページへの URL および記事の
次のページへの URL が含まれています。
メモ: ユーザー入力パラメーターがデフォルト値の場合、API はこのパラメーターをcurrentPageUrl
または nextPageUrl に表示しません。
• Article Summary
記事の応答のリストに使用される記事の概要。Article Detail 表現と同様のプロパティがあります。これ
は、一方がもう一方のスーパーセットであるためです。
{
"id": Id, // articleId
"articleNumber": String,
"articleType": String, // apiName of the article type, available in API v44.0
and later
"title": String,
"urlName": String, // available in API v44.0 and later
"summary": String,
"url": URL, // to the Article Detail API
"viewCount": Int, // view count in the interested channel
"viewScore": double (in xxx.xxxx precision), // view score in the interested
channel.
"upVoteCount": int, // up vote count in the interested channel.
"downVoteCount": int, // down vote count in the interested channel.
"lastPublishedDate": Date // last publish date in ISO8601 format
"categoryGroups": [ Data Category Group, …. ]}
「url」プロパティは常に Article Details リソースのエンドポイントを指し示します。有効なチャネル値の
詳細は、channel パラメーターの説明を参照してください。
• Data Category Group
個別のデータカテゴリグループ、ルートカテゴリ、およびグループ内で選択されたデータカテゴリのリ
ストです。
{
"groupName": String, // the unique name of the category group
"groupLabel": String, // returns the translated version
"selectedCategories": [ Data Category Summary, … ]
}
• Data Category Summary
データカテゴリ情報の概要を提供します。Summary 応答と Detail 応答のプロパティは共通です。
{
"categoryName": String, // the unique name of the category
"categoryLabel": String, // returns the translated version, per the API
language specified
286
Articles Listリファレンス

===== PAGE 297 =====
"url": String // returns the url for the DataCategory REST API.
}
メモ:  Article List API の Data Category Group および Data Category Summary の出力は、Data Category Groups API
の出力とは異なります。
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/support/knowledgeArticles?sort=ViewScore&channel=Pkb&pageSize=3
HTTP Headers:
Content-Type: application/json; charset=UTF-8
Accept: application/json
Accept-Language: en-US
レスポンスボディの例
{
"articles" : [ {
"articleNumber" : "000001002",
"categoryGroups" : [ ],
"downVoteCount" : 0,
"id" : "kA0xx000000000BCAQ",
"lastPublishedDate" : "2015-02-25T02:07:18Z",
"summary" : "With this online Chinese input tool, you can type Chinese characters
through your web browser without installing any Chinese input software in your system.
The Chinese online input tool uses the popular Pin Yin input method. It is a fast and
convenient tool to input Chinese on English OS environments.",
"title" : "Long text test",
"upVoteCount" : 0,
"url" : "/services/data/v60.0/support/knowledgeArticles/kA0xx000000000BCAQ",
"viewCount" : 4,
"viewScore" : 100.0
}, {
"articleNumber" : "000001004",
"categoryGroups" : [ ],
"downVoteCount" : 0,
"id" : "kA0xx000000000LCAQ",
"lastPublishedDate" : "2016-06-21T21:11:02Z",
"summary" : "The number of characters required for complete coverage of all these
languages' needs cannot fit in the 256-character code space of 8-bit character encodings,
requiring at least a 16-bit fixed width encoding or multi-byte variable-length encodings.
\r\n\r\nAlthough CJK encodings have common character sets, the encodings often used to
represent them have been developed separately by different East Asian governments and
software companies, and are mutually incompatible. Unicode has attempted, with some
controversy, to unify the character sets in a process known as Han unification.\r\n\r\nCJK
character encodings should consist minimally of Han characters p",
"title" : "Test Images",
"upVoteCount" : 0,
"url" : "/services/data/v60.0/support/knowledgeArticles/kA0xx000000000LCAQ",
287
Articles Listリファレンス

===== PAGE 298 =====
"viewCount" : 0,
"viewScore" : 0.0
}, {
"articleNumber" : "000001012",
"categoryGroups" : [ ],
"downVoteCount" : 0,
"id" : "kA0xx000000006GCAQ",
"lastPublishedDate" : "2016-06-21T21:10:48Z",
"summary" : null,
"title" : "Test Draft 2",
"upVoteCount" : 0,
"url" : "/services/data/v60.0/support/knowledgeArticles/kA0xx000000006GCAQ",
"viewCount" : 0,
"viewScore" : 0.0
} ],
"currentPageUrl" :
"/services/data/v60.0/support/knowledgeArticles?channel=Pkb&amp;pageSize=3&amp;sort=ViewScore",
"nextPageUrl" : null,
"pageNumber" : 1
}
使用方法
Salesforce ナレッジが組織で有効になっている必要があります。このリソースは API バージョン 38.0 以降で使用
できます。カスタムファイル項目は、バイナリストリームへのリンクを返すため、サポートされていません。
「Salesforce がサポートする言語は?」で使用されている言語コード形式を使用してください。
有効な channel 値
• string channel オプションを使用して、一致する記事が表示される場合、次の値が有効です。
– App  – 内部 Salesforce ナレッジアプリケーションで参照可能
– Pkb  – 公開知識ベースで参照可能
– Csp  – カスタマーポータルで参照可能
– Prm  – パートナーポータルで参照可能
• channel が指定されていない場合、ユーザーの種別によってデフォルト値が決まります。
– ゲストユーザーの Pkb
– カスタマーポータルユーザーの Csp
– パートナーポータルユーザーの Prm
– 他の種別のユーザーの App
• channel が指定されている場合、指定された値を使用して記事を取得できます。
– ゲストユーザー、カスタマーポータルユーザー、パートナーポータルユーザーの場合、指定されたチャ
ネルがユーザーがアクセスできるチャネルと異なる場合はエラーが返されます。
– ゲストユーザー、カスタマーポータルユーザー、パートナーポータルユーザー以外のすべてのユーザー
の場合は、指定されたチャネル値が使用されます。
288
Articles Listリファレンス

===== PAGE 299 =====
Articles Details
ユーザーがアクセスできるすべての記事項目を取得します。このリソースは、REST API バージョン 38.0 以降は
記事 ID で利用でき、バージョン 44.0 以降は記事の URL 名で利用できます。
Salesforce ナレッジが組織で有効になっている必要があります。このリソースは API バージョン 38.0 以降で使用
できます。カスタムファイル項目は、バイナリストリームへのリンクを返すため、サポートされていません。
「Salesforce がサポートする言語は?」で使用されている言語コード形式を使用してください。
ルックアップカスタム項目は、ルックアップエンティティ種別に応じてゲストユーザーに表示されます。たと
えば、ユーザーは表示されますが、ケースと取引先は表示されません。次の標準項目は、レイアウトに含まれ
ている場合でもゲストユーザーには表示されません。
• archivedBy
• isLatestVersion
• translationCompletedDate
• translationImportedDate
• translationExportedDate
• versionNumber
• visibleInInternalApp
• visibleInPKB
• visibleToCustomer
• visbileToPartner
有効な channel 値
• string channel オプションを使用して、一致する記事が表示される場合、次の値が有効です。
– App  – 内部 Salesforce ナレッジアプリケーションで参照可能
– Pkb  – 公開知識ベースで参照可能
– Csp  – カスタマーポータルで参照可能
– Prm  – パートナーポータルで参照可能
• channel が指定されていない場合、ユーザーの種別によってデフォルト値が決まります。
– ゲストユーザーの Pkb
– カスタマーポータルユーザーの Csp
– パートナーポータルユーザーの Prm
– 他の種別のユーザーの App
• channel が指定されている場合、指定された値を使用して記事を取得できます。
– ゲストユーザー、カスタマーポータルユーザー、パートナーポータルユーザーの場合、指定されたチャ
ネルがユーザーがアクセスできるチャネルと異なる場合はエラーが返されます。
– ゲストユーザー、カスタマーポータルユーザー、パートナーポータルユーザー以外のすべてのユーザー
の場合は、指定されたチャネル値が使用されます。
289
Articles Detailsリファレンス

===== PAGE 300 =====
構文
メソッド
GET
形式
JSON、XML
認証
Authorization: Bearer token
エンドポイント
/services/data/vXX.X/support/knowledgeArticles/articleId_or_articleUrlName
HTTP ヘッダー
Accept: 省略可能。application/json または application/xml のいずれかです。
Accept-language: 必須。記事は、ユーザーの組織で有効になっている言語で記述されている必要がありま
す。
• 言語コードが有効でない場合、「言語コードが有効でないか、ナレッジでサポートされていません。」
というエラーメッセージが返されます。
• 言語コードが有効であるが、ナレッジでサポートされていない場合、「無効な言語コードです。言語が
ナレッジ言語設定に含まれていることを確認してください。」というエラーメッセージが返されます。
入力:
string channel: 省略可能。デフォルトはユーザーのコンテキストです。チャネル値の詳細は、「有効な
channel 値」を参照してください。
• App: 内部 Salesforce ナレッジアプリケーションで参照可能
• Pkb: 公開知識ベースで参照可能
• Csp: カスタマーポータルで参照可能
• Prm: パートナーポータルで参照可能
boolean updateViewStat: 省略可能。デフォルトは true です。true の場合、API は、合計参照数だけでなく指
定されたチャネルの参照数も更新します。
boolean isUrlName: 省略可能。デフォルトは false です。true の場合、エンドポイントの最後の部分が記事 ID
ではなく URL 名であることを示します。API v44.0 以降で使用できます。
出力:
記事がオンラインで現在のユーザーに対して表示可能な場合の記事の詳細項目。
• Article Detail
記事の完全な詳細。記事の表示に使用される完全なメタデータおよびレイアウト主導項目が含まれま
す。Article Summary 表現と同じプロパティがすべて含まれます。
{
"id": Id, // articleId,
"articleNumber": String,
"articleType": String, // apiName of the article type, available in API
v44.0 and later
"title": String,
"urlName": String, // available in API v44.0 and later
290
Articles Detailsリファレンス

===== PAGE 301 =====
"summary": String,
"url": URL,
"versionNumber": Int,
"createdDate": Date, // in ISO8601 format
"createdBy": User Summary (ページ 291),
"lastModifiedDate": Date, // in ISO8601 format
"lastModifiedBy": User Summary (ページ 291),
"lastPublishedDate": Date, // in ISO8601 format
"layoutItems": [ Article Field, ... ], // standard and custom fields visible
to the user, sorted based on the layouts of the article type.
"categories": [ Data Category Groups, ... ],
"appUpVoteCount": Int,
"cspUpVoteCount": Int,
"prmUpVoteCount": Int,
"pkbUpVoteCount": Int,
"appDownVoteCount": Int,
"cspDownVoteCount": Int,
"prmDownVoteCount": Int,
"pkbDownVoteCount": Int,
"allViewCount": Int,
"appViewCount": Int,
"cspViewCount": Int,
"prmViewCount": Int,
"pkbViewCount": Int,
"allViewScore": Double,
"appViewScore": Double,
"cspViewScore": Double,
"prmViewScore": Double,
"pkbViewScore": Double
}
• User Summary
{
"id": String
"isActive": boolean // true/false
"userName": String // login name
"firstName": String
"lastName": String
"email": String
"url": String // to the chatter user detail url:
/services/data/vXX.X/chatter/users/{userId}, for guest user, it will return null.
}
• Article Field
記事情報の個別の項目。Article Detail 内にシステム管理者のレイアウトで必要な順序で表示されます。
{
"type": Enum, // see the Notes
"name": String, // In API v43.0 and earlier, the developer name. In
API v44.0 and later, the API name.
"label": String, // label
"value": String,
}
291
Articles Detailsリファレンス

===== PAGE 302 =====
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/support/knowledgeArticles/kA0xx000000000LCAQ
HTTP Headers:
Content-Type: application/json; charset=UTF-8
Accept: application/json
Accept-Language: en-US
レスポンスボディの例
{
"allViewCount" : 17,
"allViewScore" : 100.0,
"appDownVoteCount" : 0,
"appUpVoteCount" : 0,
"appViewCount" : 17,
"appViewScore" : 100.0,
"articleNumber" : "000001004",
"categoryGroups" : [ ],
"createdBy" : {
"email" : "user@company.com",
"firstName" : "Test",
"id" : "005xx000001SvoMAAS",
"isActive" : true,
"lastName" : "User",
"url" : "/services/data/v60.0/chatter/users/005xx000001SvoMAAS",
"userName" : "admin@salesforce.org"
},
"createdDate" : "2016-06-21T21:10:54Z",
"cspDownVoteCount" : 0,
"cspUpVoteCount" : 0,
"cspViewCount" : 0,
"cspViewScore" : 0.0,
"id" : "kA0xx000000000LCAQ",
"lastModifiedBy" : {
"email" : "user@company.com",
"firstName" : "Test",
"id" : "005xx000001SvoMAAS",
"isActive" : true,
"lastName" : "User",
"url" : "/services/data/v60.0/chatter/users/005xx000001SvoMAAS",
"userName" : "admin@salesforce.org"
},
"lastModifiedDate" : "2016-06-21T21:11:02Z",
"lastPublishedDate" : "2016-06-21T21:11:02Z",
"layoutItems" : [ {
"label" : "Out of Date",
"name" : "IsOutOfDate",
"type" : "CHECKBOX",
"value" : "false"
}, {
292
Articles Detailsリファレンス

===== PAGE 303 =====
"label" : "sample",
"name" : "sample",
"type" : "PICK_LIST",
"value" : null
}, {
"label" : "Language",
"name" : "Language",
"type" : "PICK_LIST",
"value" : "en_US"
}, {
"label" : "MyNumber",
"name" : "MyNumber",
"type" : "NUMBER",
"value" : null
}, {
"label" : "My File",
"name" : "My_File",
"type" : "FILE",
"value" : null
} ],
"pkbDownVoteCount" : 0,
"pkbUpVoteCount" : 0,
"pkbViewCount" : 0,
"pkbViewScore" : 0.0,
"prmDownVoteCount" : 0,
"prmUpVoteCount" : 0,
"prmViewCount" : 0,
"prmViewScore" : 0.0,
"summary" : "The number of characters required for complete coverage of all these
languages' needs cannot fit in the 256-character code space of 8-bit character encodings,
requiring at least a 16-bit fixed width encoding or multi-byte variable-length encodings.
\r\n\r\nAlthough CJK encodings have common character sets, the encodings often used to
represent them have been developed separately by different East Asian governments and
software companies, and are mutually incompatible. Unicode has attempted, with some
controversy, to unify the character sets in a process known as Han unification.\r\n\r\nCJK
character encodings should consist minimally of Han characters p",
"title" : "Test Images",
"url" : "/services/data/v60.0/support/knowledgeArticles/kA0xx000000000LCAQ",
"versionNumber" : 7
}
使用方法
パラメーター化された検索
SOSL 句の代わりにパラメーターを使用して簡単な REST 検索を実行します。GET メソッドで URI にパラメーター
を指定します。または POST メソッドを使用してリクエストボディに複雑な検索を作成します。
293
パラメーター化された検索リファレンス

===== PAGE 304 =====
URI にパラメーターを使用した検索
SOSL を使用する代わりに、単純な URI パラメーターを使用して検索結果を取得します。長い SOSL クエリを定義
せずに、基本的なクエリを作成します。この API は単純な用途の場合に使用します。URI には、FIND
searchString  IN ALL FIELDS の代わりに、検索文字列を入力するだけです。このリソースは REST API バージョン
36.0 以降で使用できます。
構文
URI
/services/data/vXX.X/parameterizedSearch/?q=searchString
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
必須グローバルパラメーター
説明名前
適切に URL 符号化された検索文字列。q
メモ:  SOSL 句はサポートされていません。
バージョン 36.0 以降で利用できます。
省略可能なグローバルパラメーター
説明データ型名前
単一値。組織が Salesforce ナレッジ記事または回答を使用する場合は、
dataCategory を指定して、すべての検索結果を 1 つのデータカテゴリ
に基づいて絞り込みます。
たとえば、dataCategory=GlobalCategory__c below
NorthAmerica__c と指定します。
stringdataCategory
dataCategories を使用する場合は、sobject と必要なすべてのパラ
メーターを使用して、Salesforce ナレッジ記事または回答種別を指定しま
す。
次に例を示します。
q=tourism&sobject=KnowledgeArticleVersion&KnowledgeArticleVersion.where=
language='en_US'+and+publishStatus='online'&KnowledgeArticleVersion.fields=
id,title&dataCategory=Location__c+Below+North_America__c
294
URI にパラメーターを使用した検索リファレンス

===== PAGE 305 =====
説明データ型名前
複数の dataCategory 条件が必要な場合は、POST メソッドで
dataCategories を使用します。
単一値。指定された各 sobject  (GET) または sobjects  (POST) で返される
結果の最大数。
defaultLimit の最大値は 2000 です。
stringdefaultLimit
1 つ以上の sobject を指定する必要があります。
GET の例: defaultLimit=10&sobject=Account&sobject=Contact。
Account.limit=10 のように sobject.limit=value を使用して
sobject 制限が指定された場合、そのオブジェクトではこのパラメー
ターは無視されます。
単一値。ディビジョン項目に基づいて検索結果を絞り込みます。
たとえば、GET メソッドでは division=global のように指定します。
stringdivision
ID ではなく名前でディビジョンを指定します。
特定のディビジョン内のすべての検索には、global ディビジョンも含
まれます。
指定された各 sobject に対する応答で返される、カンマで区切られた 1
つ以上の項目のリスト。1 つ以上の sobject をグローバルレベルで指定
する必要があります。
たとえば、fields=id&sobject=Account&sobject=Contact のよう
に指定します。
stringfields
グローバル fields パラメーターは、sobject.fields=field names
を使用して sobject が指定されている場合は上書きされます。たとえ
ば、Contact.fields=id,FirstName,LastName は id のみを返すグ
ローバル設定を上書きします。
指定されていない場合、検索結果には指定されたオブジェクトのすべて
の項目に一致するレコードの ID が含まれます。
関数
次の省略可能な関数は、fields パラメーター内で使用されます。
• toLabel: 応答項目値をユーザーの言語に翻訳します。たとえば、
Lead.fields=id,toLabel(Status) です。この関数には、追加設
定が必要です。
• convertCurrency: 応答通貨項目をユーザーの通貨に変換します。た
とえば、Opportunity.fields=id,convertCurrency(Amount)で
す。この関数には、追加設定が必要です。マルチ通貨が組織で有効に
なっている必要があります。
295
URI にパラメーターを使用した検索リファレンス

===== PAGE 306 =====
説明データ型名前
• format: ローカライズされた書式設定を標準およびカスタムの数値、
日付、時刻、通貨項目に適用します。たとえば、
「Opportunity.fields=id,format(Amount)」などです。
別名指定は、toLabel、convertCurrency、および format の fields
内でサポートされます。さらに、クエリに同じ項目が複数回含まれると
きは、別名指定が必要です。例:
Opportunity.fields=id,format(Amount) AliasAmount
検索する項目範囲。1 つ以上の範囲値を指定した場合、見つかったすべ
てのオブジェクトの項目が返されます。
次のいずれかの値を使用します。
stringin
• ALL
• NAME
• EMAIL
• PHONE
• SIDEBAR
この句は、記事、ドキュメント、フィードコメント、フィード項目、ファ
イル、商品、およびソリューションには適用されません。これらのオブ
ジェクトのいずれかが指定されている場合、検索は特定の項目に制限さ
れず、すべての項目が検索されます。
応答でメタデータが返されるかどうかを指定します。デフォルトではメ
タデータは返されません。応答にメタデータを含めるには、検索結果で
stringmetadata
返される項目の表示ラベルを返す LABELS 値を使用します。例:
?q=Acme&metadata=LABELS
検索結果をカンマ区切りのリストで絞り込みます。
ネットワーク ID は Experience Cloud サイト ID を表します。
stringnetWorkIds
単一値。返された結果セットへの開始行オフセット。
offset の最大値は 2000 です。
stringoffset
このパラメーターを使用して指定できる sobject は 1 つのみです。
単一値。指定されたすべての sobject パラメーターで返される結果の
最大数。
overallLimit の最大値は 2000 です。
stringoverallLimit
単一値。商品検索結果を Product2 オブジェクトのみの価格表 ID で絞り込
みます。価格表 ID は、検索する商品に関連付けられている必要がありま
stringpricebookId
す。例:
?q=laptop&sobject=product2&pricebookId=01sxx0000002MffAAE
296
URI にパラメーターを使用した検索リファレンス

===== PAGE 307 =====
説明データ型名前
Salesforce ナレッジ記事、ケース、ケースコメント、フィード、フィード
コメント、アイデア、アイデアのコメントの検索結果で返される対象の
stringsnippet
長さ (スニペット文字の最大数)。snippet パラメーターはコンテキスト
の抜粋を表示し、検索結果で各記事の検索語を強調表示します。スニペッ
トの結果は、記事の検索結果での検索語との一致を区別するために使用
されます。対象の長さは 50 ～ 1000 文字で指定できます。
スニペットと強調表示は、メール、テキスト、およびテキストエリア (ロ
ングおよびリッチ) 項目から生成されます。部分一致の場合、またはスニ
ペットが含まれる項目へのアクセス権がユーザーにない場合、スニペッ
トは表示されません。スニペットが表示されるのは、ページに返される
結果が 20 件以下の場合のみです。
次の 1 つ以上の sobject 値を指定する必要があります。
• サフィックス __kav の付いた記事タイプ名 (特定の記事タイプを検索
する場合)。
• KnowledgeArticleVersion (すべての記事タイプを検索する場合)。
• ケース、ケースコメント、フィード、フィードコメント、アイデア、
アイデアのコメントの種別を検索するには、Case、CaseComment、
FeedItem、FeedComment、Idea、IdeaComment を使用します。
たとえば、「q=tourism&sobject=Case&snippet=500」などです。
応答で返されるオブジェクト。有効なオブジェクト種別である必要があ
ります。
複数の sobject 値を使用できます (例:
sobject=Account&sobject=Contact)。
stringsobject
指定されていない場合、検索結果にはすべてのオブジェクトの ID が含ま
れます。
ユーザーの検索にスペル修正が有効になっているかどうかを示します。
true に設定すると、スペル修正をサポートする検索のスペル修正が有
効になります。デフォルト値は true です。
例:
q=Acme&sobject=Account&Account.fields=id&spellCorrection=true
booleanspellCorrection
true の値を指定すると、Salesforce ナレッジ記事の検索でのみ使用される
キーワードが追跡されます。
指定されていない場合、デフォルト値の false が適用されます。
stringupdateTracking
true の値を指定すると、記事の参照統計が更新されます。Salesforce ナ
レッジ記事の検索でのみ有効です。
指定されていない場合、デフォルト値の false が適用されます。
stringupdateViewStat
297
URI にパラメーターを使用した検索リファレンス

===== PAGE 308 =====
sobject レベルのパラメーター
次の省略可能なパラメーターは、検索結果をさらに絞り込むために GET メソッドの sobject パラメーター
と併用できます。これらの設定は、グローバルレベルで指定された設定を上書きします。
形式は、sobject.parameter です (例: Account.fields)。これらのパラメーターを使用するには、
sobject を指定する必要があります (例: sobject=Account&Account.fields=id,name)。
説明デー
タ型
名前
応答で返される、カンマで区切られた 1 つ以上の項目のリスト。
たとえば、KnowledgeArticleVersion.fields=id,title です。
stringfields
sobject で返される最大行数を指定します。
たとえば、Account.limit=10 です。
stringlimit
構文 orderBy = field {ASC|DESC} [NULLS_{FIRST|LAST}] を使用して結果項
目の順序を制御します。
例: Account.orderBy=Name
stringorderBy
• ASC: 昇順。デフォルト。
• DESC: 降順。
• NULLS_FIRST: null のレコードを結果の先頭に配置します。デフォルト。
• NULLS_LAST: null のレコードを結果の最後に配置します。
このオブジェクトの検索結果を特定の項目値で絞り込みます。
たとえば、Account.where = conditionExpression です。この WHERE 句の
conditionExpression は、構文 fieldExpression [logicalOperator
fieldExpression2 ... ] を使用します。
stringwhere
論理演算子と比較演算子を使用して、複数の項目式を条件式に追加します。たとえ
ば、KnowledgeArticleVersion.where=publishstatus='online' and
language='en_US' です。
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/parameterizedSearch/?q=Acme&sobject=Account&Account.fields=id,name&Account.limit=10
298
URI にパラメーターを使用した検索リファレンス

===== PAGE 309 =====
リクエストボディにパラメーターを使用した検索
リクエストボディにパラメーターを定義して検索します。検索クエリの実行方法をより詳細に制御できる高度
な検索にアクセスできます。また、複数の DataCategories、ネットワーク (サイト)、orderBy 制約、検索条件を使
用した絞り込みが可能です。このリソースは REST API バージョン 36.0 以降で使用できます。
構文
URI
/services/data/vXX.X/parameterizedSearch/
形式
JSON、XML
HTTP のメソッド
POST
認証
Authorization: Bearer token
必須グローバルパラメーター
説明名前
適切に URL 符号化された検索文字列。q
メモ:  SOSL 句はサポートされていません。
バージョン 36.0 以降で利用できます。
省略可能なグローバルパラメーター
説明データ型名前
組織が Salesforce ナレッジ記事または回答を使用する場合は、1 つ以上の
データカテゴリに基づいて、すべての結果を絞り込みます。
dataCategories を使用する場合は、sobjects と必要なパラメーター
を使用して、Salesforce ナレッジ記事また回答種別を指定します。
dataCategoriesFilter[]dataCategories
次に例を示します。
{
"q":"Acme",
"fields":["id", "title"],
"sobjects":[{"name":"KnowledgeArticleVersion",
"where":"language='en_US' and publishstatus='draft'"}],
"dataCategories":[
{"groupName" : "location__c", "operator":"below",
"categories":["North_America__c"]}
299
リクエストボディにパラメーターを使用した検索リファレンス

===== PAGE 310 =====
説明データ型名前
]
}
単一値。指定された各 sobject  (GET) または sobjects  (POST) で返される
結果の最大数。
defaultLimit の最大値は 2000 です。
stringdefaultLimit
1 つ以上の sobject を指定する必要があります。
GET の例: defaultLimit=10&sobject=Account&sobject=Contact。
Account.limit=10 のように sobject.limit=value を使用して
sobject 制限が指定された場合、そのオブジェクトではこのパラメー
ターは無視されます。
単一値。ディビジョン項目に基づいて検索結果を絞り込みます。
たとえば、GET メソッドでは division=global のように指定します。
stringdivision
ID ではなく名前でディビジョンを指定します。
特定のディビジョン内のすべての検索には、global ディビジョンも含
まれます。
指定された各 sobjects に対する応答で返される、1 つ以上の項目の配
列。1 つ以上の sobjects をグローバルレベルで指定する必要がありま
す。
次に例を示します。
{
string[]fields
"q":"Acme",
"fields":["Id", "Name", "Phone"],
"sobjects":[{"name": "Account"},
{"name": "Contact", "fields":["Id",
"FirstName", "LastName"]},
{"name": "Lead"}]
}
グローバル fields パラメーターは、sobjectsFilter[] 項目が指定さ
れている場合は上書きされます。たとえば、前の例の Contact では、
Id、Name、Phone のグローバル項目の代わりに Id、FirstName、
LastName が返されます。
指定されていない場合、検索結果には指定されたオブジェクトのすべて
の項目に一致するレコードの ID が含まれます。
関数
次の省略可能な関数は、fields パラメーター内で使用されます。
300
リクエストボディにパラメーターを使用した検索リファレンス

===== PAGE 311 =====
説明データ型名前
• toLabel: 応答項目値をユーザーの言語に翻訳します。この関数には、
追加設定が必要です。次に例を示します。
{
...
"sobjects":[ {"name": "Lead", "fields":["Id",
"toLabel(Status)"]},
...
}
• convertCurrency: 応答通貨項目をユーザーの通貨に変換します。こ
の関数には、追加設定が必要です。マルチ通貨が組織で有効になって
いる必要があります。次に例を示します。
{
...
"sobjects":[ {"name": "Opportunity", "fields":["Id",
"convertCurrency(Amount)"]}]
...
}
• format: ローカライズされた書式設定を標準およびカスタムの数値、
日付、時刻、通貨項目に適用します。次に例を示します。
{
...
"sobjects":[ {"name": "Opportunity", "fields":["Id",
"format(Amount)"]}]
...
}
別名指定は、toLabel、convertCurrency、および format の fields
内でサポートされます。さらに、クエリに同じ項目が複数回含まれると
きは、別名指定が必要です。次に例を示します。
{
...
"sobjects":[ {"name": "Opportunity", "fields":["Id",
"format(Amount) AliasAmount"]}]
...
}
検索する項目範囲。1 つ以上の範囲値を指定した場合、見つかったすべ
てのオブジェクトの項目が返されます。
次のいずれかの値を使用します。
stringin
• ALL
• NAME
• EMAIL
301
リクエストボディにパラメーターを使用した検索リファレンス

===== PAGE 312 =====
説明データ型名前
• PHONE
• SIDEBAR
この句は、記事、ドキュメント、フィードコメント、フィード項目、ファ
イル、商品、およびソリューションには適用されません。これらのオブ
ジェクトのいずれかが指定されている場合、検索は特定の項目に制限さ
れず、すべての項目が検索されます。
応答でメタデータが返されるかどうかを指定します。デフォルトではメ
タデータは返されません。応答にメタデータを含めるには、検索結果で
stringmetadata
返される項目の表示ラベルを返す LABELS 値を使用します。例:
?q=Acme&metadata=LABELS
検索結果を配列で絞り込みます。
ネットワーク ID は Experience Cloud サイト ID を表します。
string[]netWorkIds
単一値。返された結果セットへの開始行オフセット。
offset の最大値は 2000 です。
stringoffset
このパラメーターを使用して指定できる sobject は 1 つのみです。
単一値。指定されたすべての sobject パラメーターで返される結果の
最大数。
overallLimit の最大値は 2000 です。
stringoverallLimit
単一値。商品検索結果を Product2 オブジェクトのみの価格表 ID で絞り込
みます。価格表 ID は、検索する商品に関連付けられている必要がありま
stringpricebookId
す。例:
?q=laptop&sobject=product2&pricebookId=01sxx0000002MffAAE
Salesforce ナレッジ記事、ケース、ケースコメント、フィード、フィード
コメント、アイデア、アイデアのコメントの検索結果で返される対象の
stringsnippet
長さ (スニペット文字の最大数)。snippet パラメーターはコンテキスト
の抜粋を表示し、検索結果で各記事の検索語を強調表示します。スニペッ
トの結果は、記事の検索結果での検索語との一致を区別するために使用
されます。対象の長さは 50 ～ 1000 文字で指定できます。
スニペットと強調表示は、メール、テキスト、およびテキストエリア (ロ
ングおよびリッチ) 項目から生成されます。部分一致の場合、またはスニ
ペットが含まれる項目へのアクセス権がユーザーにない場合、スニペッ
トは表示されません。スニペットが表示されるのは、ページに返される
結果が 20 件以下の場合のみです。
次の 1 つ以上の sobject 値を指定する必要があります。
• サフィックス __kav の付いた記事タイプ名 (特定の記事タイプを検索
する場合)。
302
リクエストボディにパラメーターを使用した検索リファレンス

===== PAGE 313 =====
説明データ型名前
• KnowledgeArticleVersion (すべての記事タイプを検索する場合)。
• ケース、ケースコメント、フィード、フィードコメント、アイデア、
アイデアのコメントの種別を検索するには、Case、CaseComment、
FeedItem、FeedComment、Idea、IdeaComment を使用します。
たとえば、「q=tourism&sobject=Case&snippet=500」などです。
応答で返されるオブジェクト。有効なオブジェクト種別が含まれている
必要があります。必須パラメーターと併用します。
次に例を示します。
{
sobjectsFilter[]sobjects
"q":"Acme",
"fields":["id", "title"],
"sobjects":[{"name":"Solution__kav",
"where":"language='en_US' and publishstatus='draft'"},
{"name":"FAQ__kav", "where":"language='en_US'
and publishstatus='draft'"}]
}
指定されていない場合、検索結果にはすべてのオブジェクトの ID が含ま
れます。
ユーザーの検索にスペル修正が有効になっているかどうかを示します。
true に設定すると、スペル修正をサポートする検索のスペル修正が有
効になります。デフォルト値は true です。
例:
q=Acme&sobject=Account&Account.fields=id&spellCorrection=true
booleanspellCorrection
true の値を指定すると、Salesforce ナレッジ記事の検索でのみ使用される
キーワードが追跡されます。
指定されていない場合、デフォルト値の false が適用されます。
stringupdateTracking
true の値を指定すると、記事の参照統計が更新されます。Salesforce ナ
レッジ記事の検索でのみ有効です。
指定されていない場合、デフォルト値の false が適用されます。
stringupdateViewStat
dataCategoriesFilter[] パラメーター
パラメーターは、表に示された順序 (groupName、operator、categories) で指定する必要があります。
303
リクエストボディにパラメーターを使用した検索リファレンス

===== PAGE 314 =====
説明デー
タ型
名前
絞り込むデータカテゴリグループの名前。stringgroupName
有効な値は次のとおりです。stringoperator
• ABOVE
• ABOVE_OR_BELOW
• AT
• BELOW
絞り込むカテゴリの名前。string[]categories
sobjectsFilter[] パラメーター
説明デー
タ型
名前
sobject に対する応答で返される、1 つ以上の項目の配列。string[]fields
sobject で返される最大行数を指定します。stringlimit
応答で返される sobject の名前。stringname
構文 "orderBy" : "field {ASC|DESC} [NULLS_{FIRST|LAST}]" を使用して結
果項目の順序を制御します。
次に例を示します。
{
...
stringorderBy
"sobjects":[ {"name": "Account", "fields":["Id", "name"], "orderBy":
"Name DESC Nulls_last"}]
...
}
• ASC: 昇順。デフォルト。
• DESC: 降順。
• NULLS_FIRST: null のレコードを結果の先頭に配置します。デフォルト。
• NULLS_LAST: null のレコードを結果の最後に配置します。
このオブジェクトの検索結果を特定の項目値で絞り込みます。
たとえば、where : conditionExpression です。この WHERE 句の
conditionExpression は、構文 fieldExpression [logicalOperator
fieldExpression2 ... ] を使用します。
stringwhere
論理演算子と比較演算子を使用して、複数の項目式を条件式に追加します。
304
リクエストボディにパラメーターを使用した検索リファレンス

===== PAGE 315 =====
例
リクエストボディの例
{
"q":"Smith",
"fields" : ["id", "firstName", "lastName"],
"sobjects":[{"fields":["id", "NumberOfEmployees"],
"name": "Account",
"limit":20},
{"name": "Contact"}],
"in":"ALL",
"overallLimit":100,
"defaultLimit":10
}
Portability
Portability リソースは、Salesforce Privacy Center での可搬性ポリシーの作成時に識別したオブジェクトと項目から
顧客情報をコンパイルします。REST API バージョン 50.0 以降を使用している場合は、複数のレコードから顧客
の個人識別情報 (PII) を特定できます。データの可搬性により、組織のプラットフォームに保存されている PII の
コピーを顧客が取得するための権利に対応できます。一般データ保護規則 (GDPR) などのプライバシー規制に準
拠するには、データの可搬性に関する要求が出されてから 1 か月以内に実行する必要があります。
Portability 要求のためのデータのコンパイル
データ主体の個人識別情報 (PII) を Portability リソースの POST メソッドを使用して 1 つのファイルに集計します。
PII は、取引先、取引先責任者、個人、リード、個人取引先、およびユーザーオブジェクトのデータを含んでい
ます。ファイルをダウンロードする URL、ポリシーファイル ID、ポリシーを作成するときに選択したすべての
オブジェクトと項目に関する情報を含む応答を受信します。ポリシーファイル ID を使用し、GET メソッドに
よって Portability リソースを実行します。このリソースは REST API バージョン 50.0 以降で使用できます。
Portability リソースを使用するには、ModifyAllData または PrivacyDataAccess ユーザー権限を持っている必要があり
ます。Salesforce システム管理者からこれらの権限が付与されていることを確認してください。
構文
URI
/services/data/vXX.X/consent/dsr/rtp/execute
形式
JSON
HTTP のメソッド
POST
認証
Authorization: Bearer token
305
Portabilityリファレンス

===== PAGE 316 =====
リクエストボディ
{
“dataSubjectId”:”<root ID>”,
“policyName”:”<policyName>”
}
要求パラメーター
説明パラメーター
要求を行う顧客の ID。ID は 15 または 18 文字で、取引先、取引先責任
者、個人、リード、個人取引先、およびユーザーオブジェクトに表示
されます。
dataSubjectId
有効なポリシーの名前。これには dataSubjectId パラメーター内のオブ
ジェクトが含まれます。
policyName
例
リクエストの例
curl -X POST
https://MyDomainName.my.salesforce.com/services/data/v60.0/consent/dsr/rtp/execute -H
"Authorization: Bearer token" -H "Content-Type: application/json" -d
"@exampleRequestBody.json"
レスポンスボディの例
{
“status" : "SUCCESS",
"warnings" : [ ],
"result" : {
"policyFileStatus" : "In Progress",
"policyFileUrl" :
"https://MyDomainName.my.salesforce.com/servlet/policyFileDownload?file=0jeS70000004CBO",
"policyFileId" : "0jeS70000004CBO"
}
}
Portability 要求の状況の取得
Portability GET 要求を使用して、Portability POST 要求の状況を確認します。POST メソッド応答のポリシーファイル
ID を使用して GET メソッドを実行します。このリソースは REST API バージョン 50.0 以降で使用できます。
Portability API を使用するには、ModifyAllData または PrivacyDataAccess ユーザー権限を持っている必要があります。
Salesforce システム管理者からこれらの権限が付与されていることを確認してください。
レスポンスボディには、次の情報が含まれます。
306
Portability 要求の状況の取得リファレンス

===== PAGE 317 =====
説明値
コンパイルされているファイルの状況。値は、In Progress (処理中)、Complete
(完了)、Failed (失敗) です。
policyFileStatus
コンパイル後にファイルをダウンロードできるサーブレットの URL。policyFileURL
POST メソッド応答で返される、コンパイルされているファイルの ID。ID
は 15 文字です。
policyFileID
メモ:  Spring ‘21 リリース以降、プライバシーセンターでは、60 日後に Portability API で生成されたファイル
が自動的に削除されます。ファイルが削除される 7 日前にアラームを受信します。
構文
URI
/services/data/vXX.X/consent/dsr/rtp/execute
形式
JSON
HTTP のメソッド
GET
認証
Authorization: Bearer token
リクエストボディ
なし
要求パラメーター
説明パラメーター
POST メソッド応答で返される、コンパイルされているファイルの ID。
ID は 15 文字です。
policyFileId
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/consent/dsr/rtp/execute?policyFileId=0jeS70000004CBO
-H "Authorization: Bearer token"
レスポンスボディの例
{
“status" : "SUCCESS",
"warnings" : [ ],
307
Portability 要求の状況の取得リファレンス

===== PAGE 318 =====
"result" : {
"policyFileStatus" : "Failed",
"policyFileUrl" :
"https://MyDomainName.my.salesforce.com/servlet/policyFileDownload?file=0jeS70000004CBO",
"policyFileId" : "0jeS70000004CBO"
}
}
Process Approvals
すべての承認プロセスにアクセスします。特定のレコードが承認プロセスをサポートしていて、承認プロセス
がすでに定義されている場合、そのレコードを送信するためにも使用できます。現在のユーザーが割り当てら
れた承認者である場合、レコードを承認および却下できます。
このセクションの内容:
プロセス承認の取得
すべての承認プロセスのリストを取得します。このリソースは REST API バージョン 30.0 以降で使用できま
す。
プロセス承認の申請、承認、却下
特定のレコードが承認プロセスをサポートしていて、承認プロセスがすでに定義されている場合、そのレ
コードを送信します。現在のユーザーが割り当てられた承認者である場合、レコードを承認および却下で
きます。このリソースは REST API バージョン 30.0 以降で使用できます。
Process Approvals の HTTP ヘッダーの返送
Process Approvals リソースに GET 要求を送信したときに返されるヘッダーのみを返します。これにより、コン
テンツを取得する前に、GET 要求で返されたヘッダー値を確認できます。このリソースは REST API バージョ
ン 30.0 以降で使用できます。
プロセス承認の取得
すべての承認プロセスのリストを取得します。このリソースは REST API バージョン 30.0 以降で使用できます。
構文
URI
/services/data/vXX.X/process/approvals/
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
308
Process Approvalsリファレンス

===== PAGE 319 =====
要求パラメーター
不要
例
「すべての承認プロセスのリストを取得する」を参照してください。
プロセス承認の申請、承認、却下
特定のレコードが承認プロセスをサポートしていて、承認プロセスがすでに定義されている場合、そのレコー
ドを送信します。現在のユーザーが割り当てられた承認者である場合、レコードを承認および却下できます。
このリソースは REST API バージョン 30.0 以降で使用できます。
POST 要求を使用して一括承認を行う場合、成功した要求はコミットされ、失敗した要求からはエラーが返さ
れます。
構文
URI
/services/data/vXX.X/process/approvals/
形式
JSON、XML
HTTP のメソッド
POST
認証
Authorization: Bearer token
要求パラメーター
不要
リクエストボディ
リクエストボディには、次の情報を含むプロセス要求の配列が含まれます。
説明型名前
実行するアクション (Submit、Approve、または Reject) を表
します。
stringactionType
承認レコードを要求した申請者の ID。IDcontextActorId
動作の対象となる項目の ID。IDcontextId
この要求に関連付けられた履歴ステップに追加されるコメント。stringcomments
プロセスが引き続き承認の詳細を要求する場合、次の要求に割り
当てられるユーザー ID。
ID[]nextApproverIds
プロセス定義の開発者名または ID。stringprocessDefinitionNameOrId
プロセス定義名または ID が null ではない場合にプロセスの開始条
件を評価するか (true)、否か (false) を決定します。プロセス定義名
booleanskipEntryCriteria
309
プロセス承認の申請、承認、却下リファレンス

===== PAGE 320 =====
説明型名前
または ID が指定されていない場合、この引数は無視され、標準
の評価がプロセスの順序に基づいて行われます。この要求で設定
されていなければ、デフォルトでは開始条件はスキップされませ
ん。
レスポンスボディ
レスポンスボディには、次の情報を含むプロセス結果の配列が含まれます。
説明型名前
この承認ステップに現在割り当てられているユーザーの ID。ID[]actorIds
処理されているオブジェクト。IDentityId
要求が失敗した場合に返されるエラーのセット。Error[]errors
処理用に提出されるオブジェクトに関連付けられている
ProcessInstance の ID。
IDinstanceId
現在のプロセスインスタンスの状態 (個別のオブジェクトではな
く、全体のプロセスインスタンス)。有効値は、「Approved」、
「Rejected」、「Removed」、または「Pending」です。
stringinstanceStatus
ProcessInstanceWorkitem 項目を示す、大文字と小文字が区別されな
い ID (保留中の承認要求セット)。
ID[]newWorkItemIds
処理または承認が正常に完了した場合、true。booleansuccess
例
• 「承認を受けるレコードを送信する」を参照してください。
• 「レコードを承認する」を参照してください。
• 「レコードを却下する」を参照してください。
• 「一括承認」を参照してください。
Process Approvals の HTTP ヘッダーの返送
Process Approvals リソースに GET 要求を送信したときに返されるヘッダーのみを返します。これにより、コンテ
ンツを取得する前に、GET 要求で返されたヘッダー値を確認できます。このリソースは REST API バージョン 30.0
以降で使用できます。
310
Process Approvals の HTTP ヘッダーの返送リファレンス

===== PAGE 321 =====
構文
URI
/services/data/vXX.X/process/approvals/
形式
JSON、XML
HTTP のメソッド
HEAD
認証
Authorization: Bearer token
要求パラメーター
不要
例
リクエストの例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/process/approvals/ -H
"Authorization: Bearer token"
レスポンスボディの例
HTTP/1.1 200 OK
Date: Mon, 21 Nov 2022 22:56:26 GMT
Process Rules
すべての有効なワークフロールールのリストにアクセスします。レコードまたは項目を取得するには、GET メ
ソッドを使用します。HTTP ヘッダーの情報を取得するには、HEAD メソッドを使用します。すべての有効なワー
クフロールールをトリガーするには、POST メソッドを使用します。
特定の sObject に関連付けられたすべてのワークフロールールにアクセスするには、「sObject のプロセスルー
ルのリスト」のリソースを使用してください。特定の sObject に関連付けられた特定のワークフロールールに
アクセスするには、「sObject のプロセスルール」のリソースを使用してください。
REST API を使用して、クロスオブジェクトワークフロールールを呼び出すことはできません。
このセクションの内容:
プロセスルールの取得
有効なワークフロールールをすべて取得します。このリソースは REST API バージョン 30.0 以降で使用できま
す。
プロセスルールをトリガーする
有効なワークフロールールをすべてトリガーします。評価条件に関係なく、指定された ID に関連するすべ
てのルールが評価されます。すべての ID は、同じオブジェクトのレコードの ID である必要があります。こ
のリソースは REST API バージョン 30.0 以降で使用できます。
311
Process Rulesリファレンス

===== PAGE 322 =====
プロセスルールの HTTP ヘッダーの返送
Process Rules リソースに GET 要求を送信したときに返されるヘッダーのみを返します。これにより、コンテ
ンツを取得する前に、GET 要求で返されたヘッダー値を確認できます。このリソースは REST API バージョン
30.0 以降で使用できます。
プロセスルールの取得
有効なワークフロールールをすべて取得します。このリソースは REST API バージョン 30.0 以降で使用できます。
構文
URI
/services/data/vXX.X/process/rules/
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
要求パラメーター
不要
例
「プロセスルールのリストを取得する」を参照してください。
プロセスルールをトリガーする
有効なワークフロールールをすべてトリガーします。評価条件に関係なく、指定された ID に関連するすべて
のルールが評価されます。すべての ID は、同じオブジェクトのレコードの ID である必要があります。このリ
ソースは REST API バージョン 30.0 以降で使用できます。
構文
URI
/services/data/vXX.X/process/rules/
形式
JSON、XML
HTTP のメソッド
POST
認証
Authorization: Bearer token
312
プロセスルールの取得リファレンス

===== PAGE 323 =====
要求パラメーター
不要
リクエストボディ
リクエストボディには、コンテキスト ID の配列が含まれます。
説明型名前
動作の対象となる項目の ID の配列。ID[]contextIds
例
「プロセスルールをトリガーする」を参照してください。
プロセスルールの HTTP ヘッダーの返送
Process Rules リソースに GET 要求を送信したときに返されるヘッダーのみを返します。これにより、コンテンツ
を取得する前に、GET 要求で返されたヘッダー値を確認できます。このリソースは REST API バージョン 30.0 以降
で使用できます。
構文
URI
/services/data/vXX.X/process/rules/
形式
JSON、XML
HTTP のメソッド
HEAD
認証
Authorization: Bearer token
要求パラメーター
不要
例
リクエストの例
curl -X HEAD --head
https://MyDomainName.my.salesforce.com/services/data/v60.0/process/rules/ -H
"Authorization: Bearer token"
レスポンスボディの例
HTTP/1.1 200 OK
Date: Mon, 21 Nov 2022 22:56:26 GMT
313
プロセスルールの HTTP ヘッダーの返送リファレンス

===== PAGE 324 =====
sObject のプロセスルール
sObject の有効なワークフロールールにアクセスします。レコードまたは項目を取得するには、GET メソッドを
使用します。HTTP ヘッダーの情報を取得するには、HEAD メソッドを使用します。ワークフロールールをトリ
ガーするには、POST メソッドを使用します。
REST API を使用して、クロスオブジェクトワークフロールールを呼び出すことはできません。
すべてのワークフロールールにアクセスするには、Process Rules リソースを使用します。特定の sObject に関連
付けられた特定のワークフロールールにアクセスするには、「sObject のプロセスルールのリスト」のリソース
を使用してください。
このセクションの内容:
sObject のプロセスルールの取得
特定の sObject の特定のワークフロールールの項目を取得します。
sObject のプロセスルールのトリガー
評価条件に関係なく、有効なワークフロールールをトリガーします。
sObject のプロセスルールの HTTP ヘッダーの返送
sObject の特定のプロセスルールについて、Process Rules リソースに GET 要求を送信したときに返されるヘッ
ダーのみを返します。これにより、コンテンツを取得する前に、GET 要求で返されたヘッダー値を確認でき
ます。
sObject のプロセスルールの取得
特定の sObject の特定のワークフロールールの項目を取得します。
REST API を使用して、クロスオブジェクトワークフロールールを呼び出すことはできません。
URI
/services/data/vXX.X/process/rules/sObjectName/workflowRuleId
適用開始バージョン
30.0
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
要求パラメーター
不要
314
sObject のプロセスルールリファレンス

===== PAGE 325 =====
使用例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/process/rules/Account/01QD0000000APli
-H "Authorization: Bearer token"
リクエストボディの例
不要
JSON レスポンスボディの例
{
"actions" : [ {
"id" : "01VD0000000D2w7",
"name" : "ApprovalProcessTask",
"type" : "Task"
} ],
"description" : null,
"id" : "01QD0000000APli",
"name" : "My Rule",
"namespacePrefix" : null,
"object" : "Account"
}
sObject のプロセスルールのトリガー
評価条件に関係なく、有効なワークフロールールをトリガーします。
URI
/services/data/vXX.X/process/rules/sObjectName/workflowRuleId
適用開始バージョン
30.0
形式
JSON、XML
HTTP のメソッド
POST
認証
Authorization: Bearer token
要求パラメーター
不要
リクエストボディ
不要
使用例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/process/rules/Account/01XXX000000XxxXXX
-H "Authorization: Bearer token"
315
sObject のプロセスルールのトリガーリファレンス

===== PAGE 326 =====
JSON レスポンスボディの例
{
"errors" : null,
"success" : true
}
sObject のプロセスルールの HTTP ヘッダーの返送
sObject の特定のプロセスルールについて、Process Rules リソースに GET 要求を送信したときに返されるヘッダー
のみを返します。これにより、コンテンツを取得する前に、GET 要求で返されたヘッダー値を確認できます。
URI
/services/data/vXX.X/process/rules/sObjectName/workflowRuleId
適用開始バージョン
30.0
形式
JSON、XML
HTTP のメソッド
HEAD
認証
Authorization: Bearer token
要求パラメーター
不要
使用例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/process/rules/Account/01XXX000000/
-H "Authorization: Bearer token"
リクエストボディの例
不要
レスポンスボディの例
HTTP/1.1 200 OK
Date: Mon, 21 Nov 2022 22:56:26 GMT
sObject のプロセスルールのリスト
sObject のすべての有効なワークフロールールにアクセスします。レコードまたは項目を取得するには、GET メ
ソッドを使用します。HTTP ヘッダーの情報を取得するには、HEAD メソッドを使用します。
REST API を使用して、クロスオブジェクトワークフロールールを呼び出すことはできません。
316
sObject のプロセスルールの HTTP ヘッダーの返送リファレンス

===== PAGE 327 =====
すべてのワークフロールールにアクセスするには、Process Rules リソースを使用します。特定の sObject に関連
付けられた特定のワークフロールールにアクセスするには、「sObject のプロセスルール」のリソースを使用し
てください。
このセクションの内容:
sObject のプロセスルールの取得
sObject の有効なワークフロールールをすべて取得します。このリソースは REST API バージョン 30.0 以降で使
用できます。
sObject の複数のプロセスルールの HTTP ヘッダーの返送
sObject のすべてのプロセスルールについて、Process Rules リソースに GET 要求を送信したときに返されるヘッ
ダーのみを返します。これにより、コンテンツを取得する前に、GET 要求で返されたヘッダー値を確認でき
ます。このリソースは REST API バージョン 30.0 以降で使用できます。
sObject のプロセスルールの取得
sObject の有効なワークフロールールをすべて取得します。このリソースは REST API バージョン 30.0 以降で使用
できます。
構文
URI
/services/data/vXX.X/process/rules/sObject
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
要求パラメーター
不要
リクエストボディ
不要
例
リクエストの例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/process/rules/Account
-H "Authorization: Bearer token"
レスポンスボディの例
{
317
sObject のプロセスルールの取得リファレンス

===== PAGE 328 =====
"rules" : {
"Account" : [ {
"actions" : [ {
"id" : "01VD0000000D2w7",
"name" : "ApprovalProcessTask",
"type" : "Task"
} ],
"description" : null,
"id" : "01QD0000000APli",
"name" : "My Rule",
"namespacePrefix" : null,
"object" : "Account"
} ]
}
}
sObject の複数のプロセスルールの HTTP ヘッダーの返送
sObject のすべてのプロセスルールについて、Process Rules リソースに GET 要求を送信したときに返されるヘッ
ダーのみを返します。これにより、コンテンツを取得する前に、GET 要求で返されたヘッダー値を確認できま
す。このリソースは REST API バージョン 30.0 以降で使用できます。
構文
URI
/services/data/vXX.X/process/rules/sObject
形式
JSON、XML
HTTP のメソッド
HEAD
認証
Authorization: Bearer token
要求パラメーター
不要
リクエストボディ
不要
例
リクエストの例
curl -X HEAD --head
https://MyDomainName.my.salesforce.com/services/data/v60.0/process/rules/Account/ -H
"Authorization: Bearer token"
318
sObject の複数のプロセスルールの HTTP ヘッダーの返送リファレンス

===== PAGE 329 =====
レスポンスボディの例
HTTP/1.1 200 OK
Date: Mon, 21 Nov 2022 22:56:26 GMT
Product Schedules
商談商品の収益スケジュールと数量スケジュールを操作します。商談商品に対して複数の分割を使用して、商
品スケジュールを確立または再確立します。スケジュール内のすべての分割を削除します。
このリソースは REST API バージョン 43.0 以降で使用できます。API バージョン 46.0 以降では、設定済みおよび再
設定済みスケジュールは、カスタム項目、入力規則、Apex トリガーに対応しています。
このセクションの内容:
商品スケジュールの取得
商談商品の収益スケジュールと数量スケジュールを取得します。このリソースは REST API バージョン 43.0 以
降で使用できます。
商品スケジュールの作成
商談商品に対して複数の分割を使用して、商品スケジュールを確立または再確立します。このリソースは
REST API バージョン 43.0 以降で使用できます。API バージョン 46.0 以降では、設定済みおよび再設定済みスケ
ジュールは、カスタム項目、入力規則、Apex トリガーに対応しています。
商品スケジュールの削除
商談商品の収益または数量スケジュールのすべての分割を削除します。すべてのスケジュールを削除する
と、削除トリガーも起動されます。このリソースは REST API バージョン 43.0 以降で使用できます。
商品スケジュールの取得
商談商品の収益スケジュールと数量スケジュールを取得します。このリソースは REST API バージョン 43.0 以降
で使用できます。
構文
URI
/services/data/vXX.X/sobjects/OpportunityLineItem/OpportunityLineItemId/OpportunityLineItemSchedules
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
リクエストボディ
None
319
Product Schedulesリファレンス

===== PAGE 330 =====
要求パラメーター
None
商品スケジュールの作成
商談商品に対して複数の分割を使用して、商品スケジュールを確立または再確立します。このリソースは REST
API バージョン 43.0 以降で使用できます。API バージョン 46.0 以降では、設定済みおよび再設定済みスケジュー
ルは、カスタム項目、入力規則、Apex トリガーに対応しています。
構文
URI
/services/data/vXX.X/sobjects/OpportunityLineItem/OpportunityLineItemId/OpportunityLineItemSchedules
形式
JSON、XML
HTTP のメソッド
PUT
認証
Authorization: Bearer token
要求パラメーター
説明パラメーター
スケジュールの種別。OpportunityLineItemSchedules を
確立する場合は必須です。有効な値には、
Quantity、Revenue、Both があります。
type
数量スケジュール内で繰り返されるまたは分割され
る単位数の合計。0 以外の整数である必要がありま
す。
quantity
商品に数量スケジュールが指定されている場合、そ
の種類。有効な値は、Divideまたは Repeatです。
quantityScheduleType
商品に数量スケジュールが指定されている場合、ス
ケジュールでカバーされている時間。有効な値は、
quantityScheduleInstallmentPeriod
Daily、Weekly、Monthly、Quarterly、または
Yearly です。
商品に数量スケジュールが指定されている場合、ス
ケジュールの回数。1 ～ 150 の整数を指定できます。
quantityScheduleInstallmentsNumber
数量スケジュールを開始する日付。形式は
YYYY-MM-DD です。
quantityScheduleStartDate
繰り返されるまたは分割される収益の金額。revenue
320
商品スケジュールの作成リファレンス

===== PAGE 331 =====
説明パラメーター
商品に収益スケジュールが指定されている場合、そ
の種類。有効な値は、Divideまたは Repeatです。
revenueScheduleType
商品に収益スケジュールが指定されている場合、ス
ケジュールでカバーされている時間。有効な値は、
revenueScheduleInstallmentPeriod
Daily、Weekly、Monthly、Quarterly、または
Yearly です。
商品に収益スケジュールが指定されている場合、イ
ンストールの回数。1 ～ 150 の整数を指定できます。
revenueScheduleInstallmentsNumber
収益スケジュールを開始する日付。形式は
YYYY-MM-DD です。
revenueScheduleStartDate
例
商談商品に対して数量と収益によるスケジュールを確立します。
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/OpportunityLineItem/00kR0000001WJJAIA4/OpportunityLineItemSchedules
-H "Authorization: Bearer token"
JSON リクエストボディ
{
"type": "Both",
"quantity": 100,
"quantityScheduleType": "Repeat",
"quantityScheduleInstallmentPeriod": "Monthly",
"quantityScheduleInstallmentsNumber": 12,
"quantityScheduleStartDate": "2018-09-15",
"revenue": 100,
"revenueScheduleType": "Repeat",
"revenueScheduleInstallmentPeriod": "Monthly",
"revenueScheduleInstallmentsNumber": 12,
"revenueScheduleStartDate": "2018-09-15"
}
商談商品に対して収益によるスケジュールのみを確立します。
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/OpportunityLineItem/00kR0000001WJJAIA4/OpportunityLineItemSchedules
-H "Authorization: Bearer token"
JSON リクエストボディ
{
"type": “Revenue”,
"revenue": 100,
"revenueScheduleType": “Divide”,
"revenueScheduleInstallmentPeriod": “Quarterly”,
321
商品スケジュールの作成リファレンス
