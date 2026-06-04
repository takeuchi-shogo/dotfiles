# リファレンス後半: Composite・Composite Graph・Batch・sObject Tree・sObject Collections

> 出典: Salesforce『REST API 開発者ガイド』日本語版 (api_rest.pdf, 2026-03-31 生成, Spring '26 相当)
> PDF ページ 398–449。pypdf による自動抽出テキストのため、表組みのレイアウトが崩れている場合がある。

## 収録セクション

  - Composite (PAGE 398)
  - Composite Graph (PAGE 414)
  - Composite Batch (PAGE 423)
  - sObject Tree (PAGE 428)
  - sObject コレクション (PAGE 435)

---

===== PAGE 398 =====
{
"context" : "primary",
"color" : "66895F",
"theme" : "theme4"
},
...
}
...
}
Composite
一連の REST API 要求を 1 回の POST 要求で実行するか、他の複合リソースのリストを GET 要求で取得します。
このセクションの内容:
Composite を使用した要求の送信
一連の REST API 要求を単一のコールで実行します。1 つの要求の出力を、後続の要求の入力として使用でき
ます。要求のレスポンスボディと HTTP 状況は、1 つのレスポンスボディで返されます。一連の要求全体が
API の制限に単一のコールとして計上されます。
複合リソースのリストの取得
他の複合リソースの URI のリストを取得します。
Composite を使用した要求の送信
一連の REST API 要求を単一のコールで実行します。1 つの要求の出力を、後続の要求の入力として使用できま
す。要求のレスポンスボディと HTTP 状況は、1 つのレスポンスボディで返されます。一連の要求全体が API の
制限に単一のコールとして計上されます。
Composite コールの要求はサブ要求と呼ばれます。サブ要求はすべて同じユーザーのコンテキスト内で実行さ
れます。サブ要求のボディで、サブ要求のレスポンスに対応付けられる参照 ID を指定します。その後、JavaScript
ライクな参照表記を使用して、後のサブ要求の url または body 項目でこの ID を参照できます。
たとえば、次の Composite リクエストボディには 2 つのサブ要求が含まれます。最初のサブ要求は取引先を作
成し、出力を refAccount として指定します。2 番目のサブ要求は、サブ要求のボディで refAccount を参
照して、新しい取引先を親とする取引先責任者を作成します。
{
"compositeRequest" : [{
"method" : "POST",
"url" : "/services/data/v60.0/sobjects/Account",
"referenceId" : "refAccount",
"body" : { "Name" : "Sample Account" }
},{
"method" : "POST",
"url" : "/services/data/v60.0/sobjects/Contact",
"referenceId" : "refContact",
"body" : {
"LastName" : "Sample Contact",
388
Compositeリファレンス

===== PAGE 399 =====
"AccountId" : "@{refAccount.id}"
}
}]
}
サブ要求のエラーによって Composite リクエスト全体がロールバックされるか、または連動するサブ要求のみ
がロールバックされるかを指定できます。サブ要求ごとにヘッダーを指定することもできます。
Composite は次のリソースでサポートされます。
• sObject Rows by External ID (ページ 161) を含み、sObject Blob Get を除くすべての sObject リソース
(/services/data/vXX.X/sobjects/)
• Query リソース (/services/data/vXX.X/query/?q=soql)
• QueryAll リソース (/services/data/vXX.X/queryAll/?q=soql)
• SObject コレクションリソース (/services/data/vXX.X/composite/sobjects)。API バージョン 43.0 以降
で利用できます。
メモ: 1 回のコールに最大 25 個のサブ要求を含めることができます。これらのサブ要求のうち最大 5 個を
sObject コレクションまたはクエリ操作とすることができます (「Query」要求や「QueryAll」要求など)。
構文
URI
/services/data/vXX.X/composite
形式
JSON
HTTP のメソッド
POST
認証
Authorization: Bearer token
パラメーター
不要
リクエストボディ
Composite リクエストボディ
レスポンスボディ
Composite レスポンスボディ
例
Composite リソースの使用例は「単一の API コールでの連動要求の実行」および「取引先の更新、取引先責任者
の作成、および連結オブジェクトとのリンク」を参照してください。
このセクションの内容:
Composite サブ要求の結果
Composite サブ要求の結果では、サブ要求の結果を記述します。
389
Composite を使用した要求の送信リファレンス

===== PAGE 400 =====
Composite リクエストボディ
Composite リソースを使用して実行するサブ要求のコレクションを記述します。
Composite Collection Input
このリクエストボディには、エラーをロールバックする方法を指定する allOrNone フラグと実行するサブ要
求を含む compositeRequest コレクションが含まれます。
プロパティ
必須か省略可
能
説明型名前
省略可能サブ要求の処理中にエラーが発生した場合に何をす
べきかを指定します。値が true の場合、Composite
BooleanallOrNone
要求全体がロールバックされます。最上位レベルの
要求は HTTP 200 を返し、各サブ要求の応答が含まれ
ます。
値が false の場合、失敗したサブ要求に連動しな
い残りのサブ要求が実行されます。連動サブ要求は
実行されません。
どちらのケースでも、最上位レベルの要求は HTTP
200 を返し、各サブ要求の応答が含まれます。
メモ:  Composite 要求に sObject Collections 要求が
含まれている場合、sObject Collections 要求の
allOrNoneパラメーターも結果に影響する場
合があります。「Composite 要求および
Collections 要求の allOrNone パラメーター」を参
照してください。
省略可能API で、関係のないサブ要求を順に並べて、それら
を一括処理するか (true)、しないか (false) を制御
します。
BooleancollateSubrequests
サブ要求が順に並べられると、処理速度は速くなり
ますが、実行順序は保証されません (サブ要求の間
で明示的な依存関係がある場合を除きます)。
並べ替えが無効になっている場合、サブ要求は受信
された順番に実行されます。
有効な HTTP ヘッダーを含むサブ要求は並べ替える
ことができません。
API バージョン 49.0 以降では、デフォルト値は true
です。バージョン 48.0 では、デフォルト値は false
です。
390
Composite を使用した要求の送信リファレンス

===== PAGE 401 =====
必須か省略可
能
説明型名前
各サブ要求が、次の条件を満たす場合に並べ替える
ことができます。
• HTTP メソッドが同じ場合。
• リソースの API バージョンが同じ場合。
• リソースの親が /sobjects リソースの場合。
• サブ要求のグループに存在する sObject リソース
が 5 つ以下。
メモ: 項目間に暗黙的な依存関係はあるが、
明示的な依存関係はない場合は、並べ替えで
問題が発生する場合があります。たとえば、
次のものを作成する要求を検討します。
• 取引先
• 取引先に関連する取引先責任者
• 取引先名に依存するトリガーを持つカスタ
ムオブジェクト。
明示的な依存関係がないため、取引先および
カスタムオブジェクトは並べ替えられます。
ただし、取引先が最初に作成される保証はな
いため、カスタムオブジェクトのトリガーが
失敗する場合があります。
このような関係があり、実行順序を制御する
必要がある場合は、collateSubrequestsを
false に設定します。
API バージョン 48.0 以降で利用できます。(以前のバー
ジョンの場合、サブ要求を並べ替えることができま
せん)。
必須実行するサブ要求のコレクション。Composite
Subrequest[]
compositeRequest
JSON の例
{
"allOrNone" : true,
"collateSubrequests": true,
"compositeRequest" : [{
Composite Subrequest
},{
Composite Subrequest
},{
391
Composite を使用した要求の送信リファレンス

===== PAGE 402 =====
Composite Subrequest
}]
}
Composite サブ要求
サブ要求のリソース、メソッド、ヘッダー、本文、および参照 ID が含まれます。
プロパティ
必須か省略可能説明型名前
省略可能サブ要求の入力ボディ。
型は url プロパティに指定された要求に応じて異
なります。参照可能な型は、DateTime、String、
不特定body
Boolean、Byte、Character、Short、Integer、Long、
Double、Float です。
省略可能サブ要求に含める要求ヘッダーとその値。次の 3 つ
のヘッダーを除き、要求されたリソースによってサ
Map<String,
String>
httpHeaders
ポートされる任意のヘッダーを含めることができま
す。
• Accept
• Authorization
• Content-Type
サブ要求は、最上位レベルの要求からこれら 3 つの
ヘッダーの値を継承します。サブ要求では、これら
のヘッダーを指定しないでください。指定すると、
最上位レベルの要求は失敗し、HTTP 400 応答が返さ
れます。
メモ: 有効な HTTP ヘッダーを含むサブ要求は
並べ替えることができないため、要求の処理
速度が低下します。
必須要求するリソースに使用するメソッド。可能な値は
POST、PUT、PATCH、GET、および DELETE  (大文字
Stringmethod
と小文字を区別) です。有効なメソッドのリストは、
要求するリソースに関するドキュメントを参照して
ください。
必須サブ要求の応答に対応付けられる参照 ID で、後のサ
ブ要求で応答を参照するために使用できます。
StringreferenceId
referenceId はサブ要求の本文または URL で参照
できます。次の構文を使用して参照を含めます:
@{referenceId.FieldName}。
392
Composite を使用した要求の送信リファレンス

===== PAGE 403 =====
必須か省略可能説明型名前
参照 ID では 2 つの演算子を使用できます。
. 演算子は、応答の JSON オブジェクトの項目を参照
します。たとえば、あるサブ要求で取引先レコード
のデータを取得して、参照 ID Account1Data を出
力に割り当てるとします。後のサブ要求で次のよう
な取引先名を参照できます:
@{Account1Data.Name}。
[] 演算子は、応答で JSON コレクションをインデッ
クス付けします。たとえば、1 つのサブ要求でsObject
Basic Information リソースを使用して取引先基本情報
を要求し、参照 ID AccountInfo を出力に割り当て
るとします。応答の一部に、最近作成された取引先
のコレクションが含められます。最近使ったデータ
のコレクションで最初の取引先の ID を参照できま
す。例: @{AccountInfo.recentItems[0].Id}。
応答のコンテキストで意味をなす限り、各演算子を
再帰的に使用できます。たとえば、取引先の複合住
所項目の請求先市区郡コンポーネントを参照する場
合: @{NewAccount.BillingAddress.city}。
referenceIdは大文字と小文字が区別されるため、
参照している項目の大文字/小文字に注意を払って
ください。「使用状況」を参照してください。
メモ:
• referenceId は、先頭を文字または数字
にする必要があります。
• referenceIdには、文字、数字、アンダー
スコア (「_」) のみを使用する必要があり
ます。
必須要求するリソース。Stringurl
• URL には、サブ要求がサポートするクエリ文字列
パラメーターを含めることができます。クエリ
文字列は、URL 符号化されている必要がありま
す。
• パラメーターを使用して、レスポンスボディを
絞り込むことができます。
• URL は /services/data/vXX.X/ で始まる必要
があります。
393
Composite を使用した要求の送信リファレンス

===== PAGE 404 =====
JSON の例
例 1
{
"method" : "GET",
"url" : "/services/data/v60.0/sobjects/Account/describe",
"httpHeaders" : { "If-Modified-Since" : "Tue, 31 May 2016 18:00:00 GMT" },
"referenceId" : "AccountInfo"
}
例 2
{
"method" : "POST",
"url" : "/services/data/v60.0/sobjects/Account",
"referenceId" : "refAccount",
"body" : { "Name" : "Sample Account" }
}
例 3
{
"method" : "GET",
"url" : "/services/data/v60.0/sobjects/Account/@{refAccount.id}",
"referenceId" : "NewAccountFields"
}
例 4
{
"method" : "PATCH",
"url" : "/services/data/v60.0/sobjects/Account/ExternalAcctId__c/ID12345",
"referenceID" : "NewAccount",
"body" : { "Name" : "Acme" }
}
使用方法
referenceId は大文字と小文字が区別されるため、参照している項目の大文字/小文字に注意することが
重要です。同じ項目でも、コンテキストによって異なる大文字/小文字が使用されることがあります。たと
えば、レコードを作成する場合、ID 項目は応答で id と表示されます。ただし、sObject Rows リソースを使
用してレコードのデータにアクセスする場合、ID 項目は Id と表示されます。例 3 の @{refAccount.id}
参照は有効です。例 2 に示すように refAccount が POST からの応答を参照するためです。
@{refAccount.Id} と同様、代わりに Id を使用する場合 (すべて小文字ではなく大文字と小文字を併用)、
参照 ID は大文字/小文字が間違っているため、要求の送信時にエラーが表示されます。
メモ: 1 回のコールに最大 25 個のサブ要求を含めることができます。これらのサブ要求のうち最大 5 個
を sObject コレクションまたはクエリ操作とすることができます (「Query」要求や「QueryAll」要求な
ど)。
Composite レスポンスボディ
Composite 要求の結果を記述します。
394
Composite を使用した要求の送信リファレンス

===== PAGE 405 =====
Composite の結果
プロパティ
説明型名前
サブ要求の結果のコレクションComposite Subrequest
Result (ページ 395)[]
compositeResponse
JSON の例
{
"compositeResponse" : [{
Composite Subrequest Result
},{
Composite Subrequest Result
},{
Composite Subrequest Result
}]
}
Composite サブ要求の結果
Composite サブ要求の結果では、サブ要求の結果を記述します。
プロパティ
説明型名前
このサブ要求のレスポンスボディ。
詳細は、サブ要求リソースのドキュ
メントを参照してください。
データ型は、サブ要求の応答種別
によって異なります。
body
サブ要求がエラーを返す場合、ボ
ディにはエラーコードとエラーメッ
セージが含まれます。エラー応答
についての詳細は「状況コードと
エラー応答」を参照してください。
このサブ要求のレポートヘッダー
とその値。Composite リソースは
Map<String, String>httpHeaders
Content-Length ヘッダーをサポート
しないため、サブ要求のレスポン
スにも最上位レベルのレスポンス
にもこのヘッダーは含まれません。
このサブ要求の HTTP 状況コード。
Composite 要求で allOrNone が true
IntegerhttpStatusCode
395
Composite を使用した要求の送信リファレンス

===== PAGE 406 =====
説明型名前
に設定されていて、サブ要求がエ
ラーを返す場合、他のすべてのサ
ブ要求は 400 HTTP 状況コードを返し
ます。
サブ要求で指定された参照 ID。この
プロパティにより、サブ要求をそ
StringreferenceId
の結果に容易に関連付けることが
できます。
例
{
"body": {
"id": "001R00000064wdtIAA",
"success": true,
"errors": []
},
"httpHeaders": {
"Location": "/services/data/v60.0/sobjects/Account/001R00000064wdtIAA"
},
"httpStatusCode": 201,
"referenceId": "refAccount"
}
次の例は、Contact の作成中にエラーが発生したサブ要求への応答を示します。
{
"body" : [ {
"message" : "Email: invalid email address: Not a real email address",
"errorCode" : "INVALID_EMAIL_ADDRESS",
"fields" : [ "Email" ]
} ],
"httpHeaders" : { },
"httpStatusCode" : 400,
"referenceId" : "badContact"
}
参照 ID に無効な文字が含まれていた場合の動作および応答
referenceId には、文字、数字、アンダースコア (「_」) のみを使用する必要があります。
無効な文字があった場合の API の動作は、API バージョンとリリースによって異なります。(API バージョンは、
Composite 要求の作成に使用されたものです。ただし、このバージョンはサブ要求の url パラメーターに指定
された API バージョンと必ずしも同じではありません)。
たとえば、以下の要求を検討します。この要求では、次の操作が試みられます。
• 「Cloudy Consulting」という取引先を作成する。
• 取引先「Mary Smith」を作成して、取引先 Cloudy Consulting にリンクする。
396
Composite を使用した要求の送信リファレンス

===== PAGE 407 =====
• さらに、「Easy Spaces」という新しい取引先を作成する。
最初の参照 ID、refNewAccount[1] に無効な文字が含まれています。
{
"allOrNone": false,
"compositeRequest": [
{
"method": "POST",
"body": {
"name": "Cloudy Consulting"
},
"url": "/services/data/vXX.X/sobjects/Account/",
"referenceId": "refNewAccount[1]"
},
{
"method": "POST",
"body": {
"AccountId": "@{refNewAccount[1].id}",
"FirstName": "Mary",
"LastName": "Smith”
},
"url": "/services/data/vXX.X/sobjects/Contact",
"referenceId": "refNewContact"
},
{
"method": "POST",
"body": {
"name": "Easy Spaces"
},
"url": "/services/data/vXX.X/sobjects/Account/",
"referenceId": "refNewAccount2"
}
]
}
バージョン 51.0 以前
API バージョン 51.0 以前の場合、参照 ID に無効な文字が含まれていると、その参照 ID を使用するすべてのサブ
要求が失敗します。この例の場合の応答を次に示します。
HTTP/1.1 200 OK
{
"compositeResponse" : [
{
"body" : {
"id" : "001R0000006hfeZIAQ",
"success" : true,
"errors" : [ ]
},
"httpHeaders" : {
"Location" : "/services/data/v51.0/sobjects/Account/001R0000006hfeZIAQ"
},
"httpStatusCode" : 201,
"referenceId" : "refNewAccount[1]"
397
Composite を使用した要求の送信リファレンス

===== PAGE 408 =====
},
{
"body" : [
{
"errorCode" : "PROCESSING_HALTED",
"message" : "Invalid reference specified. No value for refNewAccount[1].id
found in refNewAccount.
}
],
"httpHeaders" : { },
"httpStatusCode" : 400,
"referenceId" : "refNewContact"
},
{
"body" : {
"id" : "001R0000006hfeeIAA",
"success" : true,
"errors" : [ ]
},
"httpHeaders" : {
"Location" : "/services/data/v51.0/sobjects/Account/001R0000006hfeeIAA"
},
"httpStatusCode" : 201,
"referenceId" : "refNewAccount2"
}
]
}
2 つの取引先が作成されます (最初の取引先が参照 ID 内の無効な文字を使用していても)。ただし、(無効な文字
を含む参照 ID を使用して) 取引先を作成する試みは失敗します。
以前のリリースでのバージョン 51.0 以前の応答
上記の応答は、Summer ’21 以降のリリースのものです。Summer ’21 より前のリリースの場合、応答内の「(」ま
たは「[」を含む問題のある参照 ID は、切り捨てられました。したがって、応答は次のようになりました。
{
"compositeResponse" : [
{
"body" : {
"id" : "001R0000006hfeZIAQ",
"success" : true,
"errors" : [ ]
},
"httpHeaders" : {
"Location" : "/services/data/v51.0/sobjects/Account/001R0000006hfeZIAQ"
},
"httpStatusCode" : 201,
"referenceId" : "refNewAccount"
},
...
}
Summer ’21 リリース以降、参照 ID は、問題があっても切り捨てられなくなりました。この変更により、応答と
要求の各部をより簡単に突き合わせることができます。
398
Composite を使用した要求の送信リファレンス

===== PAGE 409 =====
バージョン 52.0 以降
API バージョン 52.0 以降の場合、参照 ID に無効な文字が含まれていると、要求全体が失敗します。上記の例に
対する応答を次に示します。
HTTP/1.1 400 Bad Request
[
{
"message" : "Provided referenceId ('refNewAccount[1]') must start with a letter or
a number, and it can contain only letters, numbers and underscores ('_').",
"errorCode" : "JSON_PARSER_ERROR"
}
]
まとめ
Null 項目への参照に関する動作
Null 項目への参照がある場合の API の動作は、API のバージョンによって異なります。(API バージョンは、Composite
要求の作成に使用されたものです。ただし、このバージョンはサブ要求の url パラメーターに指定された API
バージョンと必ずしも同じではありません)。
メモ: この動作は、親要求が sObject Rowsリソース (例: /services/data/vXX.X/sobjects/Contact/id)
を使用しているリクエストにのみ適用されます。
399
Composite を使用した要求の送信リファレンス

===== PAGE 410 =====
たとえば、次の要求について考えてみましょう。この要求は、既存の取引先責任者を探して、
@{refContact.FirstName} と @{refContact.LastName} を使用してレコードを作成します。
POST https://MyDomainName.my.salesforce.com/services/data/vXX.X/composite -H "Authorization:
Bearer token"
"compositeRequest" : [
{
"method" : "GET",
"url" :
"/services/data/v51.0/sobjects/Contact/003RO0000016kOuYAI?fields=FirstName,LastName",
"referenceId" : "refContact"
},
{
"method" : "POST",
"url" : "/services/data/v51.0/sobjects/Contact",
"referenceId" : "newContact",
"body" : {
"FirstName" : "@{refContact.FirstName}",
"LastName" : "@{refContact.LastName}",
"AccountId" : "001RO000001nGCdYAM"
}
}
]
}
では、取引先責任者の名が NULL (未設定) の場合はどうなるかについて考えてみます。
バージョン 51.0 以前の応答
API バージョン 51.0 以前では、取引先責任者の FirstName 項目が null であることが原因で、連動サブ要求が失敗
します。
{
"compositeResponse" : [
{
"body" : {
"attributes" : {
"type" : "Contact",
"url" : "/services/data/v51.0/sobjects/Contact/003RO0000016kOuYAI"
},
"FirstName" : null,
"LastName" : "Wong",
"Id" : "003RO0000016kOuYAI"
},
"httpHeaders" : { },
"httpStatusCode" : 200,
"referenceId" : "refContact"
},
{
"body" : [
{
"errorCode" : "PROCESSING_HALTED",
"message" : "Invalid reference specified. No value for refContact.FirstName
found in refContact.
400
Composite を使用した要求の送信リファレンス

===== PAGE 411 =====
Provided referenceId ('refContact.FirstName') must start with a letter or a
number,
and it can contain only letters, numbers and underscores ('_')."
}
],
"httpHeaders" : { },
"httpStatusCode" : 400,
"referenceId" : "newContact"
}
]
}
この例では、allOrNone が false に設定されていることを想定しています。true の場合、Composite 要求全体が
ロールバックされます。「Composite 要求および Collections 要求の allOrNone パラメーター」を参照してくださ
い。
バージョン 52.0 以降の応答
API バージョン 52.0 以降では、要求が成功します。
{
"compositeResponse" : [
{
"body" : {
"attributes" : {
"type" : "Contact",
"url" : "/services/data/v51.0/sobjects/Contact/003RO0000016kOuYAI"
},
"FirstName" : null,
"LastName" : "Wong",
"Id" : "003RO0000016kOuYAI"
},
"httpHeaders" : { },
"httpStatusCode" : 200,
"referenceId" : "refContact"
},
{
"body" : {
"id" : "003RO0000016kRAYAY",
"success" : true,
"errors" : [ ]
},
"httpHeaders" : {
"Location" : "/services/data/v51.0/sobjects/Contact/003RO0000016kRAYAY"
},
"httpStatusCode" : 201,
"referenceId" : "newContact"
}
]
}
401
Composite を使用した要求の送信リファレンス

===== PAGE 412 =====
親要求で指定されていない項目への参照に関する動作
連動サブ要求では、常に親リクエストで明示的に選択されている項目のみを使用する必要があります。この方
法のとおりに設定しなかった場合、API の動作は API バージョンによって異なります。(API バージョンは、
Composite 要求の作成に使用されたものです。ただし、このバージョンはサブ要求の url パラメーターに指定
された API バージョンと必ずしも同じではありません)。
たとえば、以下の要求を検討します。この要求では、次の操作が試みられます。
1. 特定の取引先責任者を見つけます。
2. @{refContact.records[0].AccountId} を使用して取引先責任者の取引先 ID を取得します。
ただし、親要求は AccountId を明示的に照会していません。
POST https://MyDomainName.my.salesforce.com/services/data/vXX.X/composite -H "Authorization:
Bearer token"
{
"compositeRequest" : [
{
"method" : "GET",
"url" : "/services/data/v51.0/query?q=select Id, Account.Name from Contact where
Id='003RO0000016kOuYAI'",
"referenceId" : "refContact"
},
{
"method" : "GET",
"url" : "/services/data/v50.0/query?q=select Name from Account where Id =
'@{refContact.records[0].AccountId}'",
"referenceId" : "refAccount"
}
]
}
バージョン 51.0 以前の応答
API バージョン 51.0 以前では、まれにこのような要求が成功する場合があります。
メモ: ただし、このような要求がときどき成功するという事実は、決して当てにはなりません。親要求の
結果から項目を使用する場合は、必ず親要求でその項目を明示的に選択する必要があります。
バージョン 52.0 以降の応答
API バージョン 52.0 以降では、次の要求は常に失敗します。
{
"compositeResponse" : [
{
"body" : {
"totalSize" : 1,
"done" : true,
"records" : [
{
"attributes" : {
"type" : "Contact",
"url" : "/services/data/v51.0/sobjects/Contact/003RO0000016kOuYAI"
402
Composite を使用した要求の送信リファレンス

===== PAGE 413 =====
},
"Id" : "003RO0000016kOuYAI",
"Account" : {
"attributes" : {
"type" : "Account",
"url" : "/services/data/v51.0/sobjects/Account/001RO000001nGbUYAU"
},
"Name" : "City Medical Center"
}
}
]
},
"httpHeaders" : { },
"httpStatusCode" : 200,
"referenceId" : "refContact"
},
{
"body" : [
{
"errorCode" : "PROCESSING_HALTED",
"message" : "Invalid reference specified. No value for
refContact.records[0].AccountId found in refContact.
Provided referenceId ('refContact.records[0].AccountId') must start with a
letter or a number, and it can contain
only letters, numbers and underscores ('_')."
}
],
"httpHeaders" : { },
"httpStatusCode" : 400,
"referenceId" : "refAccount"
}
]
}
このような要求が正常に機能するには、親要求で AccountId を明示的に取得する必要があります。
{
"compositeRequest" : [
{
"method" : "GET",
"url" : "/services/data/v51.0/query?q=select Id, Account.Name, AccountId from
Contact where Id='003RO0000016kOuYAI'",
"referenceId" : "refContact"
},
{
"method" : "GET",
"url" : "/services/data/v50.0/query?q=select Name from Account where Id =
'@{refContact.records[0].AccountId}'",
"referenceId" : "refAccount"
}
]
}
403
Composite を使用した要求の送信リファレンス

===== PAGE 414 =====
複合リソースのリストの取得
他の複合リソースの URI のリストを取得します。
構文
URI
/services/data/vXX.X/composite
形式
JSON
HTTP のメソッド
GET
認証
Authorization: Bearer token
パラメーター
不要
リクエストボディ
不要
例
リクエストの例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/composite/ -H
"Authorization: Bearer token"
レスポンスボディの例
{
"tree": "/services/data/v54.0/composite/tree",
"batch": "/services/data/v54.0/composite/batch",
"sobjects": "/services/data/v54.0/composite/sobjects",
"graph": "/services/data/v54.0/composite/graph"
}
Composite Graph
Composite Graph リソースにより、Composite Graph 操作を送信できます。このリソースは REST API バージョン 50.0
以降で使用できます。
メモ: 要求のレスポンスボディと HTTP 状況は、1 つのレスポンスボディで返されます。要求全体が API の
制限に単一のコールとして計上されます。
404
複合リソースのリストの取得リファレンス

===== PAGE 415 =====
構文
URI
/services/data/vXX.X/composite/graph
形式
JSON
HTTP のメソッド
POST
認証
Authorization: Bearer token
要求のパラメーター
なし
リクエストボディ
{
"graphId" : "graphId",
"compositeRequest" : [
compositeSubrequest,
compositeSubrequest,
...
]
}
ここで、それぞれの compositeSubrequest は Composite サブ要求です。
レスポンスボディ
{
"graphs" : [
{
"graphId" : "graphId",
"graphResponse" : {
"compositeResponse" : [
compositeSubrequestResult,
compositeSubrequestResult,
compositeSubrequestResult,
...
]
},
"isSuccessful" : flag
},
...
]
}
405
Composite Graphリファレンス

===== PAGE 416 =====
説明型名前
グラフ応答の配列。graphs
グラフの識別子。StringgraphId
要求の応答。ObjectgraphResponse
グラフの各ノードの結果。Composite サブ要求の結果 (ページ
395)の配列。
compositeResponse
このグラフが正常に処理されたか
(true)、否か (false)。
BooleanisSuccessful
例
リクエストの例
curl -X POST https://MyDomainName.my.salesforce.com/services/data/v60.0/composite/graph
-H "Authorization: Bearer token" -H "Content-Type: application/json" -d
"@graphRequestBody.json"
リクエストボディの例
{
"graphs" : [
{
"graphId" : "1",
"compositeRequest" : [
{
"url" : "/services/data/v60.0/sobjects/Account/",
"body" : {
"name" : "Cloudy Consulting"
},
"method" : "POST",
"referenceId" : "reference_id_account_1"
},
{
"url" : "/services/data/v60.0/sobjects/Contact/",
"body" : {
"FirstName" : "Nellie",
"LastName" : "Cashman",
"AccountId" : "@{reference_id_account_1.id}"
},
"method" : "POST",
"referenceId" : "reference_id_contact_1"
},
{
"url" : "/services/data/v60.0/sobjects/Opportunity/",
"body" : {
"CloseDate" : "2024-05-22",
"StageName" : "Prospecting",
"Name" : "Opportunity 1",
406
Composite Graphリファレンス

===== PAGE 417 =====
"AccountId" : "@{reference_id_account_1.id}"
},
"method" : "POST",
"referenceId" : "reference_id_opportunity_1"
}
]
},
{
"graphId" : "2",
"compositeRequest" : [
{
"url" : "/services/data/v60.0/sobjects/Account/",
"body" : {
"name" : "Easy Spaces"
},
"method" : "POST",
"referenceId" : "reference_id_account_2"
},
{
"url" : "/services/data/v60.0/sobjects/Contact/",
"body" : {
"FirstName" : "Charlie",
"LastName" : "Dawson",
"AccountId" : "@{reference_id_account_2.id}"
},
"method" : "POST",
"referenceId" : "reference_id_contact_2"
}
]
}
]
}
レスポンスボディの例
{
"graphs" : [
{
"graphId" : "1",
"graphResponse" : {
"compositeResponse" : [
{
"body" : {
"id" : "001R00000064wc7IAA",
"success" : true,
"errors" : [ ]
},
"httpHeaders" : {
"Location" :
"/services/data/v60.0/sobjects/Account/001R00000064wc7IAA"
},
"httpStatusCode" : 201,
"referenceId" : "reference_id_account_1"
},
{
407
Composite Graphリファレンス

===== PAGE 418 =====
"body" : {
"id" : "003R000000DDMlTIAX",
"success" : true,
"errors" : [ ]
},
"httpHeaders" : {
"Location" :
"/services/data/v60.0/sobjects/Contact/003R000000DDMlTIAX"
},
"httpStatusCode" : 201,
"referenceId" : "reference_id_contact_1"
},
{
"body" : {
"id" : "006R0000003FPYxIAO",
"success" : true,
"errors" : [ ]
},
"httpHeaders" : {
"Location" :
"/services/data/v60.0/sobjects/Opportunity/006R0000003FPYxIAO"
},
"httpStatusCode" : 201,
"referenceId" : "reference_id_opportunity_1"
}
]
},
"isSuccessful" : true
},
{
"graphId" : "2",
"graphResponse" : {
"compositeResponse" : [
{
"body" : {
"id" : "001R00000064wc8IAA",
"success" : true,
"errors" : [ ]
},
"httpHeaders" : {
"Location" :
"/services/data/v60.0/sobjects/Account/001R00000064wc8IAA"
},
"httpStatusCode" : 201,
"referenceId" : "reference_id_account_2"
},
{
"body" : {
"id" : "003R000000DDMlUIAX",
"success" : true,
"errors" : [ ]
},
"httpHeaders" : {
"Location" :
408
Composite Graphリファレンス

===== PAGE 419 =====
"/services/data/v60.0/sobjects/Contact/003R000000DDMlUIAX"
},
"httpStatusCode" : 201,
"referenceId" : "reference_id_contact_2"
}
]
},
"isSuccessful" : true
}
]
}
Composite サブ要求
Composite サブ要求では、Composite Graph リソースを使用して実行するサブ要求を記述します。
プロパティ
説明型名前
省略可能。不特定body
サブ要求の入力ボディ。
内容は url プロパティに指定された要求に応じて異なります。
参照可能な型は、DateTime、String、Boolean、Byte、Character、Short、
Integer、Long、Double、Float です。
省略可能。Map<String, String>httpHeaders
サブ要求に含める要求ヘッダーとその値。次の 3 つのヘッダーを
除き、要求されたリソースによってサポートされる任意のヘッ
ダーを含めることができます。
• Accept
• Authorization
• Content-Type
サブ要求は、最上位レベルの要求からこれら 3 つのヘッダーの値
を継承します。サブ要求では、これらのヘッダーを指定しない
でください。指定すると、最上位レベルの要求は失敗し、HTTP
400 応答が返されます。
有効な HTTP ヘッダーを含むサブ要求は並べ替えることができな
いため、要求の処理速度が低下します。
必須。Stringmethod
要求するリソースに使用するメソッド。可能な値は DELETE、GET、
PATCH、および POST (大文字と小文字を区別) です。有効なメソッ
409
Composite サブ要求リファレンス

===== PAGE 420 =====
説明型名前
ドのリストは、要求するリソースに関するドキュメントを参照
してください。
このメソッドは、Composite Graph 要求を送信するために使用され
る POST メソッドとは異なります。ここで指定された方法は、url
で指定されたリソースで動作する (グラフ内) メソッドです。
• url が /services/data/vXX.X/sobject/sObject の場
合、POST がサポートされます。(「sObject Basic Information」を
参照)。
• url が /services/data/vXX.X/sobject/sObject/id の
場合、DELETE、GET、および PATCH がサポートされます。
(「sObject Rows」を参照)。
• url が
/services/data/vXX.X/sobject/sObject/customFieldName/externalId
の場合、DELETE、GET、PATCH、および POST がサポートされま
す。PATCH を使用して外部 ID を介して更新/挿入できます。
(「外部 ID を使用してレコードを挿入/更新 (Upsert) する」を参
照)。
必須。StringreferenceId
サブ要求の応答に対応付けられる参照 ID で、後のサブ要求で応
答を参照するために使用できます。referenceId はサブ要求の
本文または URL で参照できます。次の構文を使用して参照を含め
ます: @{referenceId.FieldName}。
参照 ID では 2 つの演算子を使用できます。
. 演算子は、応答の JSON オブジェクトの項目を参照します。た
とえば、あるサブ要求で取引先レコードのデータを取得して、
参照 ID Account1Data を出力に割り当てるとします。後のサブ
要求で次のような取引先名を参照できます:
@{Account1Data.Name}。
[] 演算子は、応答で JSON コレクションをインデックス付けしま
す。たとえば、1 つのサブ要求で sObject Basic Information リソース
を使用して取引先基本情報を要求し、参照 ID AccountInfo を出
力に割り当てるとします。応答の一部に、最近作成された取引
先のコレクションが含められます。最近使ったデータのコレク
ションで最初の取引先の ID を参照できます。例:
@{AccountInfo.recentItems[0].Id}。
応答のコンテキストで意味をなす限り、各演算子を再帰的に使
用できます。たとえば、取引先の複合住所項目の請求先市区郡
410
Composite サブ要求リファレンス

===== PAGE 421 =====
説明型名前
コンポーネントを参照する場合:
@{NewAccount.BillingAddress.city}。
referenceId は大文字と小文字が区別されるため、参照してい
る項目の大文字/小文字に注意を払ってください。「使用状況」
を参照してください。
• referenceId は、先頭を文字または数字にする必要があり
ます。
• referenceId には、文字、数字、アンダースコア (「_」) の
みを使用する必要があります。
必須。Stringurl
要求するリソース。
• URL には、サブ要求がサポートするクエリ文字列パラメーター
を含めることができます。クエリ文字列は、URL 符号化され
ている必要があります。
• パラメーターを使用して、レスポンスボディを絞り込むこと
ができます。
• 次の URL のみがサポートされています。
– /services/data/vXX.X/sobject/sObject
– /services/data/vXX.X/sobject/sObject/id
– /services/data/vXX.X/sobject/sObject/customFieldName/externalId
• バージョン番号 XX.X は 50.0 以降である必要があります。
例
例 1
{
"body" : {
"Name" : "Sample Account"
},
"method" : "POST",
"referenceId" : "refAccount",
"url" : "/services/data/v60.0/sobjects/Account"
}
例 2
{
"method" : "GET",
"referenceId" : "NewAccountFields",
411
Composite サブ要求リファレンス

===== PAGE 422 =====
"url" : "/services/data/v60.0/sobjects/Account/@{refAccount.id}"
}
使用方法
referenceId は大文字と小文字が区別されるため、参照している項目の大文字/小文字に注意することが重要
です。同じ項目でも、コンテキストによって異なる大文字/小文字が使用されることがあります。たとえば、
レコードを作成する場合、ID 項目は応答で id と表示されます。ただし、sObject Rows リソースを使用してレ
コードのデータにアクセスする場合、ID 項目は Id と表示されます。例 2 の @{refAccount.id} 参照は有効
です。例 1 に示すように refAccount が POST からの応答を参照するためです。@{refAccount.Id} と同様、
代わりに Id を使用する場合 (すべて小文字ではなく大文字と小文字を併用)、参照 ID は大文字/小文字が間違っ
ているため、要求の送信時にエラーが表示されます。
1 つの要求でグラフの失敗の最大数に達すると、残りのグラフの処理が停止します。応答には、
PROCESSING_HALTEDエラーと、失敗したグラフに関する情報が含まれます。現在の制限については、「Composite
Graph の制限」を参照してください。
結果
サブ要求の結果は、他の Composite 要求の結果と同じです。「Composite サブ要求の結果」 (ページ 395)を参照し
てください。
Composite Graph の制限
次の制限は、Composite Graph リソースに固有です。Composite Graph API リソースに適用されるすべての制限の包
括的なリストについては、プラットフォームの API 制限と割り当てを確認してください。
グラフの全般的な制限
制限項目
751 つのペイロードのグラフの最大数。
15グラフの最大深度。
5001 つのグラフで使用されるノードの最大数。
151 つのペイロードの異なるノードの最大数。
異なる API バージョンまたは異なる種別のオブジェク
トのリソースを使用している場合、ノードは異なると
みなされます。
次に例を示します。
• /services/data/v50.0/sobjects/account と
/services/data/v52.0/sobjects/account は
異なるとみなされます。
412
Composite Graph の制限リファレンス

===== PAGE 423 =====
制限項目
• /services/data/vXX.X/sobjects/account と
/services/data/vXX.X/sobjects/contact は
異なるとみなされます。
141 つの要求内のグラフの失敗の最大数。
ノードの制限
制限項目
500
(たとえば、1 つのグラフに 500 個のノードを含めるこ
とも、50 個のグラフそれぞれに 10 個のノードを含め
ることもできます)。
1 つのペイロードでサポートされるノードの最大数。
関連トピック:
API 要求の制限と割り当て
Composite Batch
1 回の要求で最大 25 個のサブ要求を実行します。バッチ内のサブ要求のレスポンスボディと HTTP 状況は、1 つ
のレスポンスボディで返されます。各サブ要求は、レート制限に反映されます。
バッチ内の各要求はサブ要求と呼ばれます。サブ要求はすべて同じユーザーのコンテキスト内で実行されま
す。各サブ要求は独立しており、相互に情報を渡すことはできません。サブ要求は、リクエストボディ内の順
序に従って実行されます。サブ要求が正常に実行されると、データがコミットされます。コミットは、以降の
サブ要求の出力に反映されます。サブ要求が失敗した場合、前のサブ要求で行われたコミットはロールバック
されません。バッチ要求が 10 分以内に完了しない場合、バッチはタイムアウトし、残りのサブ要求は実行さ
れません。
次のリソースとリソースグループの一括処理は、API バージョン 34.0 以降で使用できます。
• Limits — /services/data/vXX.X/limits
• sObject リソース (sObject Blob Retrieve と sObject Rich Text Image Retrieve を除く) —
/services/data/vXX.X/sobjects/
• Query — /services/data/vXX.X/query/?q=soql
• QueryAll — /services/data/vXX.X/queryAll/?q=soql
• Search — /services/data/vXX.X/search/?q=sosl
• Connect リソース — /services/data/vXX.X/connect/
• Chatter リソース — /services/data/vXX.X/chatter/
次のリソースとリソースグループの一括処理は、API バージョン 35.0 以降で使用できます。
413
Composite Batchリファレンス

===== PAGE 424 =====
• Actions — vXX.X/actions
各サブ要求でアクセスされるリソースの API バージョンは 34.0 以降で、かつ最上位レベルの要求の Batch バー
ジョン以前である必要があります。たとえば、/services/data/v35.0/composite/batch への Batch 要求
を行う場合、バージョン 34.0 または 35.0 のリソースにアクセスするサブ要求を含めることができます。ただ
し、/services/data/v34.0/composite/batch への Batch 要求を行う場合は、バージョン 34.0 のリソース
にアクセスするサブ要求のみを含めることができます。
構文
URI
/services/data/vXX.X/composite/batch
形式
JSON、XML
HTTP メソッド
POST
認証
Authorization: Bearer token
パラメーター
不要
リクエストボディ
Batch リクエストボディ (ページ 414)
レスポンスボディ
Batch レスポンスボディ (ページ 417)
例
Composite Batch リソースの使用例は、「1 回の要求でレコードを更新してその項目値を取得する」 (ページ 110)
を参照してください。
Batch リクエストボディ
Composite Batch リソースを使用して実行するサブ要求のコレクションを記述します。
Batch Collection Input
このリクエストボディには、実行するサブ要求で構成される batchRequests コレクションが含まれます。
プロパティ
必須か省略可
能
説明型名前
必須実行するサブ要求のコレクション。Subrequest[]batchRequests
414
Batch リクエストボディリファレンス

===== PAGE 425 =====
必須か省略可
能
説明型名前
省略可能サブ要求が失敗した場合に、一括処理を停止するか
どうかを制御します。デフォルトは、false です。
値が false で、バッチ内のサブ要求が完了しない
場合、Salesforce は、バッチ内の後続のサブ要求を実
行しようと試みます。
BooleanhaltOnError
値が true で、HTTP 応答 400 番台または 500 番台の
エラーが含まれるためにバッチ内のサブ要求が完了
しない場合、Salesforce は実行を停止します。また、
後続のサブ要求ごとに HTTP 412 状況コードと
BATCH_PROCESSING_HALTED エラーメッセージを
返します。/composite/batchへの最上位要求は、
HTTP 200 を返し、応答内の hasErrors プロパティ
が true に設定されます。
この設定は、サブ要求処理中にのみ適用され、最初
の要求の並列化中には適用されません。Subrequest
要求データの構文エラーなど、並列化中にエラーが
検出された場合、Salesforce は haltOnError の値に
関わらず、以降のサブ要求の処理を中止して、HTTP
400 Bad Request エラーを返します。これが発生
する一例は、サブ要求に無効なmethod または url
項目が含まれていた場合です。
ルート XML タグ
<batch>
JSON の例
{
"batchRequests" : [
{
"method" : "PATCH",
"url" : "v60.0/sobjects/account/001D000000K0fXOIAZ",
"richInput" : {"Name" : "NewName"}
},{
"method" : "GET",
"url" : "v60.0/sobjects/account/001D000000K0fXOIAZ?fields=Name,BillingPostalCode"
}]
}
サブ要求
サブ要求のリソース、メソッド、および付随情報が含まれます。
415
Batch リクエストボディリファレンス

===== PAGE 426 =====
プロパティ
必須か省略可能説明型名前
省略可能マルチパート要求のバイナリパートの名前。
1 つのバッチ要求で複数のバイナリパートがアップ
ロードされると、この値が要求とバイナリパートの
StringbinaryPartName
対応付けに使用されます。名前の競合を防止するた
めに、バッチ要求内の各 binaryPartName プロパ
ティには一意の値を使用します。
この値が存在する場合、binaryPartNameAlias値
も存在する必要があります。
省略可能バイナリボディパートの Content-Disposition ヘッダー
の name パラメーター。リソースごとに異なる値を
StringbinaryPartNameAlias
使用します。「Blob データを挿入または更新する」
を参照してください。
この値が存在する場合、binaryPartName 値も存
在する必要があります。
必須要求するリソースに使用するメソッド。有効なメ
ソッドのリストは、要求するリソースに関するド
キュメントを参照してください。
Stringmethod
省略可能要求の入力ボディ。
型は url プロパティに指定された要求に応じて異
なります。
richInput
必須要求するリソース。Stringurl
• URL には、サブ要求がサポートするクエリ文字列
パラメーターを含めることができます。クエリ
文字列は、URL 符号化されている必要がありま
す。
• パラメーターを使用して、レスポンスボディを
絞り込むことができます。
• サブ要求レベルでヘッダーを適用することはで
きません。
ルート XML タグ
<request>
416
Batch リクエストボディリファレンス

===== PAGE 427 =====
JSON の例
{
"method" : "GET",
"url" : "v60.0/sobjects/account/001D000000K0fXOIAZ?fields=Name,BillingPostalCode"
}
Batch レスポンスボディ
Composite Batch 要求の結果を記述します。
Batch Results
プロパティ
説明型名前
結果セットに HTTP 状況コードが 400 番台または 500 番台の
結果が 1 つ以上ある場合は true、それ以外の場合は
false。
BooleanhasErrors
サブ要求の結果のコレクション。Subrequest Result[]results
JSON の例
{
"hasErrors" : false,
"results" : [{
"statusCode" : 204,
"result" : null
},{
"statusCode" : 200,
"result": {
"attributes" : {
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001D000000K0fXOIAZ"
},
"Name" : "NewName",
"BillingPostalCode" : "94105",
"Id" : "001D000000K0fXOIAZ"
}
}]
}
417
Batch レスポンスボディリファレンス

===== PAGE 428 =====
Subrequest Result
プロパティ
説明型名前
このサブ要求のレスポンスボディ。データ型は、サブ要
求の応答種別によっ
て異なります。
result
重要: 結果がエ
ラーの場合、
このデータ型
はエラーメッ
セージとエ
ラーコードが
含まれるコレ
クションで
す。
このサブ要求の状況を示す HTTP 状況コード。IntegerstatusCode
JSON の例
{
"attributes" : {
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001D000000K0fXOIAZ"
},
"Name" : "NewName",
"BillingPostalCode" : "94015",
"Id" : "001D000000K0fXOIAZ"
}
sObject Tree
指定されたタイプのルートレコードを持つ 1 つ以上の sObject ツリーを作成します。sObject ツリーは、同じルー
トレコードを持つネストされた親-子レコードのコレクションです。
要求データには、レコード階層、必須および省略可能な項目値、各レコードの種類、および各レコードの参照
ID を指定します。オブジェクトは、要求にリストされている順に作成されます。成功すると、応答には作成さ
れたレコードの ID が含まれます。レコードの作成中にエラーが発生した場合、要求全体が失敗します。この
場合、応答にはエラーが発生したレコードの参照 ID とエラー情報のみが含まれます。要求のレスポンスボディ
と HTTP 状況は、1 つのレスポンスボディで返されます。要求全体が API の制限に単一のコールとして計上され
ます。
要求には、次の内容を指定できます。
• すべてのツリーの合計で最大 200 件のレコード
418
sObject Treeリファレンス

===== PAGE 429 =====
• 最大 5 件の異なるタイプのレコード
• 深さが最大 5 レベルの sObject ツリー
sObject ツリーに含まれるレコードが 1 件の場合があるため、このリソースを使用して同じタイプで関連がない
レコードを最大 200 件作成できます。
要求が処理されてレコードが作成されると、次のレコードのグループごとに、トリガー、プロセス、および
ワークフロールールが別個に起動されます。
• 要求のすべての sObject ツリーのルートレコード
• 同じタイプのすべての第 2 レベルのレコード (たとえば、要求内のすべての sObject ツリーの第 2 レベルの取
引先責任者など)
• 同じタイプのすべての第 3 レベルのレコード
• 同じタイプのすべての第 4 レベルのレコード
• 同じタイプのすべての第 5 レベルのレコード
構文
URI
/services/data/vXX.X/composite/tree/sObjectName
形式
JSON、XML
HTTP メソッド
POST
認証
Authorization: Bearer token
パラメーター
不要
リクエストボディ
sObject Tree リクエストボディ (ページ 419)
レスポンスボディ
sObject Tree レスポンスボディ (ページ 423)
例
• 同じタイプで関連のないレコードを作成する例は、「複数のレコードを作成する」 (ページ 114)を参照して
ください。
• ネストされたレコードを作成する例は、「ネストされたレコードを作成する」 (ページ 112)を参照してくだ
さい。
sObject Tree リクエストボディ
sObject Tree リソースを使用して作成する sObject ツリーのコレクションを記述します。
419
sObject Tree リクエストボディリファレンス

===== PAGE 430 =====
重要: 可能な場合は、Equality の会社の値に一致するように、含めない用語を変更しました。顧客の実装に
対する影響を回避するために、一部の用語は変更されていません。
sObject Tree Collection Input
このリクエストボディには、sObject ツリーで構成される records コレクションが含まれます。
プロパティ
必須か省略可能説明型名前
必須作成するレコードツリーのコレクショ
ン。各ツリーのルートレコードタイプ
sObject Tree Input[]records
は、sObject Tree URI に指定された sObject
に対応する必要があります。
ルート XML タグ
<SObjectTreeRequest>
JSON の例
{
"records" :[{
"attributes" : {"type" : "Account", "referenceId" : "ref1"},
"name" : "SampleAccount",
"phone" : "1234567890",
"website" : "www.salesforce.com",
"numberOfEmployees" : "100",
"industry" : "Banking",
"Contacts" : {
"records" : [{
"attributes" : {"type" : "Contact", "referenceId" : "ref2"},
"lastname" : "Smith",
"title" : "President",
"email" : "sample@salesforce.com"
},{
"attributes" : {"type" : "Contact", "referenceId" : "ref3"},
"lastname" : "Evans",
"title" : "Vice President",
"email" : "sample@salesforce.com"
}]
}
},{
"attributes" : {"type" : "Account", "referenceId" : "ref4"},
"name" : "SampleAccount2",
"phone" : "1234567890",
"website" : "www.salesforce2.com",
"numberOfEmployees" : "100",
"industry" : "Banking"
}]
}
420
sObject Tree リクエストボディリファレンス

===== PAGE 431 =====
XML の例
<SObjectTreeRequest>
<records type="Account" referenceId="ref1">
<name>SampleAccount</name>
<phone>1234567890</phone>
<website>www.salesforce.com</website>
<numberOfEmployees>100</numberOfEmployees>
<industry>Banking</industry>
<Contacts>
<records type="Contact" referenceId="ref2">
<lastname>Smith</lastname>
<title>President</title>
<email>sample@salesforce.com</email>
</records>
<records type="Contact" referenceId="ref3">
<lastname>Evans</lastname>
<title>Vice President</title>
<email>sample@salesforce.com</email>
</records>
</Contacts>
</records>
<records type="Account" referenceId="ref4">
<name>SampleAccount2</name>
<phone>1234567890</phone>
<website>www.salesforce2.com</website>
<numberOfEmployees>100</numberOfEmployees>
<industry>Banking</industry>
</records>
</SObjectTreeRequest>
sObject Tree Input
sObject ツリーは、他の sObject ツリーとして表されるルートレコード、そのデータ、およびその子レコードが
含まれる再帰的データ構造です。
プロパティ
必須か省略可能説明型名前
必須このレコードの属性。attributes プロパティには
2 つのサブプロパティが含まれます。
コレクショ
ン
attributes
• type  (必須) — このレコードのタイプ。
• referenceId  (必須) — このレコードの参照 ID。
要求のコンテキスト内で一意であり、英数字で
始まる必要があります。
XML で、records 要素内に属性を含めます。
必須このレコードの必須項目と項目値。項目に依存必須オブジェクト
項目
421
sObject Tree リクエストボディリファレンス

===== PAGE 432 =====
必須か省略可能説明型名前
省略可能このレコードの省略可能な項目と項目値。項目に依存省略可能なオブ
ジェクト項目
省略可能このレコードの子リレーション (取引先の子取引先
責任者など)。子リレーションは、主従関係または参
sObject Tree
Collection
Input
子リレーション
照関係になります。オブジェクトの有効な子リレー
ションを表示するには、sObject Describe リソースま
たは Schema Builder を使用します。このプロパティの
値は、子 sObject ツリーが含まれる sObject Tree Collection
Input です。
ルート XML タグ
<records>
JSON の例
{
"attributes" : {"type" : "Account", "referenceId" : "ref1"},
"name" : "SampleAccount",
"phone" : "1234567890",
"website" : "www.salesforce.com",
"NumberOfEmployees" : "100",
"industry" : "Banking",
"Contacts" : {
"records" : [{
"attributes" : {"type" : "Contact", "referenceId" : "ref2"},
"lastname" : "Smith",
"title" : "President",
"email" : "sample@salesforce.com"
},{
"attributes" : {"type" : "Contact", "referenceId" : "ref3"},
"lastname" : "Evans",
"title" : "Vice President",
"email" : "sample@salesforce.com"
}]
}
}
XML の例
<records type="Account" referenceId="ref1">
<name>SampleAccount</name>
<phone>1234567890</phone>
<website>www.salesforce.com</website>
<numberOfEmployees>100</numberOfEmployees>
<industry>Banking</industry>
<Contacts>
<records type="Contact" referenceId="ref2">
<lastname>Smith</lastname>
<title>President</title>
422
sObject Tree リクエストボディリファレンス

===== PAGE 433 =====
<email>sample@salesforce.com</email>
</records>
<records type="Contact" referenceId="ref3">
<lastname>Evans</lastname>
<title>Vice President</title>
<email>sample@salesforce.com</email>
</records>
</Contacts>
</records>
sObject Tree レスポンスボディ
sObject Tree 要求の結果を記述します。
プロパティ
説明型名前
レコード作成時にエラーが発生した場合は true、それ以
外の場合は false。
BooleanhasErrors
成功した場合は、results に要求された各レコードの参
照 ID とその新しいレコード ID が含まれます。失敗した場
Collectionresults
合は、エラーが発生したレコードの参照 ID、エラー状況
コード、エラーメッセージ、およびエラーに関連する項
目のみが含まれます。重複した参照 ID がある場合は、
results に重複した ID のインスタンスごとに 1 つの項目
が含まれます。
成功時の JSON の例
{
"hasErrors" : false,
"results" : [{
"referenceId" : "ref1",
"id" : "001D000000K0fXOIAZ"
},{
"referenceId" : "ref4",
"id" : "001D000000K0fXPIAZ"
},{
"referenceId" : "ref2",
"id" : "003D000000QV9n2IAD"
},{
"referenceId" : "ref3",
"id" : "003D000000QV9n3IAD"
}]
}
423
sObject Tree レスポンスボディリファレンス

===== PAGE 434 =====
成功時の XML の例
<?xml version="1.0" encoding="UTF-8"?>
<SObjectTreeResponse>
<hasErrors>false</hasErrors>
<results>
<id>001D000000K0fXOIAZ</id>
<referenceId>ref1</referenceId>
</results>
<results>
<id>001D000000K0fXPIAZ</id>
<referenceId>ref4</referenceId>
</results>
<results>
<id>003D000000QV9n2IAD</id>
<referenceId>ref2</referenceId>
</results>
<results>
<id>003D000000QV9n3IAD</id>
<referenceId>ref3</referenceId>
</results>
</SObjectTreeResponse>
失敗時の JSON の例
{
"hasErrors" : true,
"results" : [{
"referenceId" : "ref2",
"errors" : [{
"statusCode" : "INVALID_EMAIL_ADDRESS",
"message" : "Email: invalid email address: 123",
"fields" : [ "Email" ]
}]
}]
}
失敗時の XML の例
<SObjectTreeResponse>
<hasErrors>true</hasErrors>
<results>
<errors>
<fields>Email</fields>
<message>Email: invalid email address: 123</message>
<statusCode>INVALID_EMAIL_ADDRESS</statusCode>
</errors>
<referenceId>ref2</referenceId>
</results>
</SObjectTreeResponse>
424
sObject Tree レスポンスボディリファレンス

===== PAGE 435 =====
sObject コレクション
1 つの要求で複数のレコードに対してアクションを実行します。sObject コレクションを使用することで、クラ
イアントとサーバー間の往復回数を抑えられます。要求のレスポンスボディと HTTP 状況は、1 つのレスポンス
ボディで返されます。要求全体が API の制限に単一のコールとして計上されます。このリソースは API バージョ
ン 42.0 以降で使用できます。
sObject Collections 要求のパラメーター、リクエストボディ、レスポンスボディは HTTP のメソッドによって異な
ります。詳細は、特定の操作を参照してください。
sObject Collections を使用したレコードの作成
sObject コレクションを使用した POST 要求によって、最大 200 件のレコードを追加し、SaveResult オブジェクト
のリストを返します。エラーが発生した場合に要求全体をロールバックするかどうかを選択できます。
• リストには最大 200 個のオブジェクトを含めることができます。
• リストには異なる種別のオブジェクトを含めることができ、カスタムオブジェクトも使用できます。
• 各オブジェクトには属性の対応付けが含まれている必要があります。対応付けには type の値が含まれて
いる必要があります。
メモ:  sObject コレクションを使用して blob データを挿入する場合は、他の値も属性の対応付けに必要
となります。詳細は、「sObject コレクションを使用した blob レコードのコレクションの挿入」を参照
してください。
• オブジェクトは、リストされている順に作成されます。SaveResult オブジェクトは、作成要求が指定された
順に返されます。
• リクエストボディに複数の種別のオブジェクトが含まれている場合は、チャンクとして処理されます。た
とえば、受信したオブジェクトが {account1, account2, contact1, account3} の場合、要求は次の
ように 3 つのチャンクで処理されます: {{account1, account2}, {contact1}, {account3}}.。1 つ
の要求で最大で 10 個のチャンクを処理できます。
• 複数のオブジェクト種別のレコードを作成する場合、いずれかのオブジェクト種別が Salesforce の [設定] 領
域の機能に関連していると、1 回のコールでは作成することができません。
要求が適切な形式でない場合、API は 400 Bad Request  HTTP 状況を返します。要求の構文を修正し、再試行
してください。要求が適切な形式の場合、API は 200 OK  HTTP 状況を返します。項目が正常に処理された場合、
success フラグがその項目で表示されます。エラー情報は errors 配列で返されます。
構文
URI
/services/data/vXX.X/composite/sobjects
形式
JSON、XML
HTTP のメソッド
POST
425
sObject コレクションリファレンス

===== PAGE 436 =====
認証
Authorization: Bearer token
パラメーター
説明パラメーター
省略可能。いずれかのオブジェクトの作成が失敗したときに要求全体
をロールバックするのか (true)、それとも要求内のその他のオブジェ
allOrNone
クトの作成を個別に続行するのかを示します。デフォルトは、false
です。
メモ:  Composite 要求に sObject Collections 要求が組み込まれている
場合、Composite 要求の allOrNone パラメーターも結果に影響
する場合があります。「Composite 要求および Collections 要求の
allOrNone パラメーター」を参照してください。
必須。sObjects のリスト。sObject コレクションを使用する POST 要求で
は、各オブジェクトの type 属性を設定しますが、id 項目はどのオ
ブジェクトに対しても設定しません。
records
例
リクエストの例
curl -X POST
https://MyDomainName.my.salesforce.com/services/data/v60.0/composite/sobjects/ -H
"Authorization: Bearer token" -H "Content-Type: application/json" -d
"@exampleRequestBody.json"
リクエストボディの例
{
"allOrNone" : false,
"records" : [{
"attributes" : {"type" : "Account"},
"Name" : "example.com",
"BillingCity" : "San Francisco"
}, {
"attributes" : {"type" : "Contact"},
"LastName" : "Johnson",
"FirstName" : "Erica"
}]
}
レスポンスボディの例
HTTP/1.1 200 OK
[
{
"id" : "001RM000003oLnnYAE",
426
sObject Collections を使用したレコードの作成リファレンス

===== PAGE 437 =====
"success" : true,
"errors" : [ ]
},
{
"id" : "003RM0000068xV6YAI",
"success" : true,
"errors" : [ ]
}
]
レスポンスボディの例 (一部の項目でエラーが発生し、allOrNone が false の場合)
HTTP/1.1 200 OK
[
{
"success" : false,
"errors" : [
{
"statusCode" : "DUPLICATES_DETECTED",
"message" : "Use one of these records?",
"fields" : [ ]
}
]
},
{
"id" : "003RM0000068xVCYAY",
"success" : true,
"errors" : [ ]
}
]
レスポンスボディの例 (一部の項目でエラーが発生し、allOrNone が true の場合)
HTTP/1.1 200 OK
[
{
"success" : false,
"errors" : [
{
"statusCode" : "DUPLICATES_DETECTED",
"message" : "Use one of these records?",
"fields" : [ ]
}
]
},
{
"success" : false,
"errors" : [
{
"statusCode" : "ALL_OR_NONE_OPERATION_ROLLED_BACK",
"message" : "Record rolled back because not all records were valid and the
request was using AllOrNone header",
"fields" : [ ]
427
sObject Collections を使用したレコードの作成リファレンス

===== PAGE 438 =====
}
]
}
]
sObject Collections を使用したレコードの取得
sObject コレクションを使用した GET 要求によって、同じオブジェクト種別の 1 件以上のレコードを取得しま
す。指定された種別の個々のレコードを表す sObject のリストが返されます。返される sObject の数は、要求で
渡される ID の数と一致します。
指定する ID が約 800 件までであれば、URL の長さが原因で HTTP 414 エラー「URI too long (URI が長すぎま
す)」が発生するのを回避できます。
メモ: sObject Blob Retrieve (ページ 167) リソースは、JSON または XML 形式のデータではなくバイナリデータを
返すため、複合 API 要求と互換性がありません。Blob データを取得するには、代わりに、個別の sObject Blob
Retrieve 要求を実行します。
• 無効な項目名や参照権限を持っていない項目名を指定した場合は「HTTP 400 Bad Request (HTTP 400
無効な要求)」が返されます。
• オブジェクトへのアクセス権を持っていない場合や、渡された ID が無効の場合、配列は、そのオブジェク
トに null を返します。
構文
URI
/services/data/vXX.X/composite/sobjects/sObject
形式
JSON、XML
HTTP のメソッド
GET
認証
Authorization: Bearer token
パラメーター
説明パラメーター
必須。返すオブジェクトの 1 つ以上の ID のリスト。すべての ID は同じ
オブジェクト種別に属している必要があります。
recordIds
必須。応答に含める項目のリスト。指定する項目名が有効であり、各
項目の参照レベルの権限を持っている必要があります。
fieldNames
428
sObject Collections を使用したレコードの取得リファレンス

===== PAGE 439 =====
例
リクエストの例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/composite/sobjects/Account?ids=001xx000003DGb1AAG,001xx000003DGb0AAG,001xx000003DGb9AAG&fields=id,name
-H "Authorization: Bearer token"
レスポンスボディの例
[
{
"attributes" : {
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001xx000003DGb1AAG"
},
"Id" : "001xx000003DGb1AAG",
"Name" : "Acme"
},
{
"attributes" : {
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001xx000003DGb0AAG"
},
"Id" : "001xx000003DGb0AAG",
"Name" : "Global Media"
},
null
]
リクエストボディでの sObject コレクションを使用したレコードの取
得
sObject コレクションを使用した POST 要求によって、同じオブジェクト種別の 1 件以上のレコードを取得しま
す。指定された種別の個々のレコードを表す sObject のリストが返されます。返される sObject の数は、要求で
渡される ID の数と一致します。
要求で、同じ object 型のレコードを 2,000 レコードまで取得できます。
• 無効な項目名や参照権限を持っていない項目名を指定した場合は「HTTP 400 Bad Request (HTTP 400
無効な要求)」が返されます。
• オブジェクトへのアクセス権を持っていない場合や、渡された ID が無効の場合、配列は、そのオブジェク
トに null を返します。
メモ: sObject Blob Retrieve (ページ 167) リソースは、JSON または XML 形式のデータではなくバイナリデータを
返すため、複合 API 要求と互換性がありません。Blob データを取得するには、代わりに、個別の sObject Blob
Retrieve 要求を実行します。
429
リクエストボディでの sObject コレクションを使用した
レコードの取得
リファレンス

===== PAGE 440 =====
構文
URI
/services/data/vXX.X/composite/sobjects/sObject
形式
JSON、XML
HTTP のメソッド
POST
認証
Authorization: Bearer token
リクエストボディ
{
"ids" : ["recordIds"],
"fields" : ["fieldName"]
}
パラメーター
説明パラメーター
必須。返すオブジェクトの 1 つ以上の ID のリスト。すべての ID は同じ
オブジェクト種別に属している必要があります。
recordIds
必須。応答に含める項目のリスト。指定する項目名が有効であり、各
項目の参照レベルの権限を持っている必要があります。
fieldNames
例
リクエストの例
curl -X POST
https://MyDomainName.my.salesforce.com/services/data/v60.0/composite/sobjects/Account
-H "Authorization: Bearer token" -H "Content-Type: application/json" -d
"@exampleRequestBody.json"
リクエストボディの例
{
"ids" : ["001xx000003DGb1AAG", "001xx000003DGb0AAG", "001xx000003DGb9AAG"],
"fields" : ["id", "name"]
}
レスポンスボディの例
[
{
"attributes" : {
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001xx000003DGb1AAG"
},
430
リクエストボディでの sObject コレクションを使用した
レコードの取得
リファレンス

===== PAGE 441 =====
"Id" : "001xx000003DGb1AAG",
"Name" : "Acme"
},
{
"attributes" : {
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001xx000003DGb0AAG"
},
"Id" : "001xx000003DGb0AAG",
"Name" : "Global Media"
},
null
]
sObject Collections を使用したレコードの更新
sObject コレクションを使用した PATCH 要求によって、最大 200 件のレコードを更新し、SaveResult オブジェクト
のリストを返します。エラーが発生した場合に要求全体をロールバックするかどうかを選択できます。
• リストには最大 200 個のオブジェクトを含めることができます。
• リストには異なる種別のオブジェクトを含めることができ、カスタムオブジェクトも使用できます。
• 各オブジェクトには属性の対応付けが含まれている必要があります。対応付けには type の値が含まれて
いる必要があります。
メモ:  sObject コレクションを使用して blob データを更新する場合は、他の値も属性の対応付けに必要
となります。詳細は、「sObject コレクションを使用した blob レコードのコレクションの挿入」を参照
してください。
• 各オブジェクトには id 項目が含まれ、有効な ID 値が設定されている必要があります。
• オブジェクトは、リストされている順に更新されます。SaveResult オブジェクトは、更新要求が指定された
順に返されます。
• リクエストボディに複数の種別のオブジェクトが含まれている場合は、チャンクとして処理されます。た
とえば、受信したオブジェクトが {account1, account2, contact1, account3} の場合、要求は次の
ように 3 つのチャンクで処理されます: {{account1, account2}, {contact1}, {account3}}.。1 つ
の要求で最大で 10 個のチャンクを処理できます。
• 複数のオブジェクト種別のレコードを更新する場合、いずれかのオブジェクト種別が Salesforce の [設定] 領
域の機能に関連していると、1 回のコールでは更新することができません。
要求が適切な形式でない場合、API は 400 Bad Request  HTTP 状況を返します。要求の構文を修正し、再試行
してください。要求が適切な形式の場合、API は 200 OK  HTTP 状況を返します。項目が正常に処理された場合、
success フラグがその項目で表示されます。エラー情報は errors 配列で返されます。
構文
URI
/services/data/vXX.X/composite/sobjects/
形式
JSON、XML
431
sObject Collections を使用したレコードの更新リファレンス

===== PAGE 442 =====
HTTP のメソッド
PATCH
認証
Authorization: Bearer token
パラメーター
説明パラメーター
省略可能。いずれかのオブジェクトの更新が失敗したときに要求全体
をロールバックするのか (true)、それとも要求内のその他のオブジェ
allOrNone
クトの更新を個別に続行するのかを示します。デフォルトは、false
です。
メモ:  Composite 要求に sObject Collections 要求が組み込まれている
場合、Composite 要求の allOrNone パラメーターも結果に影響
する場合があります。「Composite 要求および Collections 要求の
allOrNone パラメーター」を参照してください。
必須。レコードのリスト。各レコードの id 属性と type 属性を設定
します。
records
例
リクエストの例
curl -X PATCH
https://MyDomainName.my.salesforce.com/services/data/v60.0/composite/sobjects/ -H
"Authorization: Bearer token" -H "Content-Type: application/json" -d
"@exampleRequestBody.json"
リクエストボディの例
{
"allOrNone" : false,
"records" : [{
"attributes" : {"type" : "Account"},
"id" : "001xx000003DGb2AAG",
"NumberOfEmployees" : 27000
},{
"attributes" : {"type" : "Contact"},
"id" : "003xx000004TmiQAAS",
"Title" : "Lead Engineer"
}]
}
レスポンスボディの例
HTTP/1.1 200 OK
[
432
sObject Collections を使用したレコードの更新リファレンス

===== PAGE 443 =====
{
"id" : "001RM000003oCprYAE",
"success" : true,
"errors" : [ ]
},
{
"id" : "003RM0000068og4YAA",
"success" : true,
"errors" : [ ]
}
]
レスポンスボディの例 (一部の項目でエラーが発生し、allOrNone が false の場合)
HTTP/1.1 200 OK
[
{
"id" : "001RM000003oCprYAE",
"success" : true,
"errors" : [ ]
},
{
"success" : false,
"errors" : [
{
"statusCode" : "MALFORMED_ID",
"message" : "Contact ID: id value of incorrect type: 001xx000003DGb2999",
"fields" : [
"Id"
]
}
]
}
]
レスポンスボディの例 (一部の項目でエラーが発生し、allOrNone が true の場合)
HTTP/1.1 200 OK
[
{
"id" : "001RM000003oCprYAE",
"success" : false,
"errors" : [
{
"statusCode" : "ALL_OR_NONE_OPERATION_ROLLED_BACK",
"message" : "Record rolled back because not all records were valid and the
request was using AllOrNone header",
"fields" : [ ]
}
]
},
{
"success" : false,
433
sObject Collections を使用したレコードの更新リファレンス

===== PAGE 444 =====
"errors" : [
{
"statusCode" : "MALFORMED_ID",
"message" : "Contact ID: id value of incorrect type: 001xx000003DGb2999",
"fields" : [
"Id"
]
}
]
}
]
sObject Collections を使用したレコードの更新/挿入
sObject コレクションを使用した PATCH 要求によって、外部 ID 項目に基づいて最大 200 件のレコードを作成また
は更新 (更新/挿入) します。このメソッドでは、UpsertResult オブジェクトのリストを返します。エラーが発生し
た場合に要求全体をロールバックするかどうかを選択できます。この要求は、API バージョン 46 以降で使用で
きます。
• リストには最大 200 個のオブジェクトを含めることができます。
• リストには要求 URI で指定された種別のオブジェクトのみを含めることができます。
• リクエストボディの各オブジェクトには属性の対応付けが含まれている必要があります。対応付けには
type の値が含まれている必要があります。
メモ:  sObject コレクションを使用して blob データを挿入する場合は、他の値も属性の対応付けに必要
となります。詳細は、「sObject コレクションを使用した blob レコードのコレクションの挿入」を参照
してください。
• オブジェクトは、リクエストボディでリストされている順に作成または更新されます。UpsertResult オブジェ
クトも同じ順序で返されます。
• サポートされるのは外部 ID のみです。レコード ID は使用しないでください。
要求が適切な形式でない場合、API は 400 Bad Request  HTTP 状況を返します。要求の構文を修正し、再試行
してください。要求が適切な形式の場合、API は 200 OK  HTTP 状況を返します。項目が正常に処理された場合、
success フラグがその項目で表示されます。エラー情報は errors 配列で返されます。
構文
URI
/services/data/vXX.X/composite/sobjects/SobjectName/ExternalIdFieldName
形式
JSON、XML
HTTP のメソッド
PATCH
認証
Authorization: Bearer token
434
sObject Collections を使用したレコードの更新/挿入リファレンス

===== PAGE 445 =====
パラメーター
説明パラメーター
省略可能。いずれかのオブジェクトの作成が失敗したときに要求全体
をロールバックするのか (true)、それとも要求内のその他のオブジェ
allOrNone
クトの作成を個別に続行するのかを示します。デフォルトは、false
です。
メモ:  Composite 要求に sObject Collections 要求が組み込まれている
場合、Composite 要求の allOrNone パラメーターも結果に影響
する場合があります。「Composite 要求および Collections 要求の
allOrNone パラメーター」を参照してください。
必須。sObjects のリスト。sObject コレクションを使用する PATCH 要求で
は、各オブジェクトの type 属性を設定します。どのオブジェクトに
records
も id 項目は設定しません。代わりに、要求 URI で指定された外部 ID
項目を、使用します。
例
リクエストの例
curl -X PATCH
https://MyDomainName.my.salesforce.com/services/data/v60.0/composite/sobjects/Account/MyExtId__c
-H "Authorization: Bearer token" -H "Content-Type: application/json" -d
"@exampleRequestBody.json"
リクエストボディの例
{
"allOrNone" : false,
"records" : [{
"attributes" : {"type" : "Account"},
"Name" : "Company One",
"MyExtId__c" : "AAA"
}, {
"attributes" : {"type" : "Account"},
"Name" : "Company Two",
"MyExtId__c" : "BBB"
}]
}
レスポンスボディの例
HTTP/1.1 200 OK
[
{
"id": "001xx0000004GxDAAU",
"success": true,
"errors": [],
435
sObject Collections を使用したレコードの更新/挿入リファレンス

===== PAGE 446 =====
"created": true
},
{
"id": "001xx0000004GxEAAU",
"success": true,
"errors": [],
"created": false
}
]
レスポンスボディの例 (一部の項目でエラーが発生し、allOrNone が false の場合)
HTTP/1.1 200 OK
[
{
"id" : "001xx0000004GxDAAU",
"success" : true,
"errors" : [ ]
},
{
"success" : false,
"errors" : [
{
"statusCode" : "MALFORMED_ID",
"message" : "Contact ID: id value of incorrect type: 001xx0000004GxEAAU",
"fields" : [
"Id"
]
}
]
}
]
レスポンスボディの例 (一部の項目でエラーが発生し、allOrNone が true の場合)
HTTP/1.1 200 OK
[
{
"id" : "001xx0000004GxDAAU",
"success" : false,
"errors" : [
{
"statusCode" : "ALL_OR_NONE_OPERATION_ROLLED_BACK",
"message" : "Record rolled back because not all records were valid and the
request was using AllOrNone header",
"fields" : [ ]
}
]
},
{
"success" : false,
"errors" : [
{
436
sObject Collections を使用したレコードの更新/挿入リファレンス

===== PAGE 447 =====
"statusCode" : "MALFORMED_ID",
"message" : "Contact ID: id value of incorrect type: 001xx0000004GxEAAU",
"fields" : [
"Id"
]
}
]
}
]
関連トピック:
sObject Rows by External ID
sObject Collections を使用したレコードの削除
sObject コレクションを使用した DELETE 要求によって、最大 200 件のレコードを削除し、DeleteResult オブジェク
トのリストを返します。エラーが発生した場合に要求全体をロールバックするかどうかを選択できます。
• DeleteResult オブジェクトは、削除するオブジェクトの ID が指定された順に返されます。
• 複数のオブジェクト種別のレコードを削除する場合、いずれかのオブジェクト種別が Salesforce の [設定] 領
域の機能に関連していると、1 回のコールでは削除することができません。
要求が適切な形式でない場合、API は 400 Bad Request  HTTP 状況を返します。要求の構文を修正し、再試行
してください。要求が適切な形式の場合、API は 200 OK  HTTP 状況を返します。項目が正常に処理された場合、
success フラグがその項目で表示されます。エラー情報は errors 配列で返されます。
構文
URI
/services/data/vXX.X/composite/sobjects?ids=recordId,recordId
形式
JSON、XML
HTTP のメソッド
DELETE
認証
Authorization: Bearer token
パラメーター
説明パラメーター
省略可能。いずれかのオブジェクトの削除が失敗したときに要求全体
をロールバックするのか (true)、それとも要求内のその他のオブジェ
allOrNone
クトの削除を個別に続行するのかを示します。デフォルトは、false
です。
メモ:  Composite 要求に sObject Collections 要求が組み込まれている
場合、Composite 要求の allOrNone パラメーターも結果に影響
437
sObject Collections を使用したレコードの削除リファレンス

===== PAGE 448 =====
説明パラメーター
する場合があります。「Composite 要求および Collections 要求の
allOrNone パラメーター」を参照してください。
必須。最大 200 個の削除するオブジェクトの ID のリスト。異なるオブ
ジェクト種別の ID を含めることができ、カスタムオブジェクトも使用
できます。
ids
例
リクエストの例
curl -X DELETE
https://MyDomainName.my.salesforce.com/services/data/v60.0/composite/sobjects?ids=001xx000003DGb2AAG,003xx000004TmiQAAS&allOrNone=false
-H "Authorization: Bearer token"
レスポンスボディの例
HTTP/1.1 200 OK
[
{
"id" : "001RM000003oLrHYAU",
"success" : true,
"errors" : [ ]
},
{
"id" : "001RM000003oLraYAE",
"success" : true,
"errors" : [ ]
}
]
レスポンスボディの例 (一部の項目でエラーが発生し、allOrNone が false の場合)
HTTP/1.1 200 OK
[
{
"id" : "001RM000003oLrfYAE",
"success" : true,
"errors" : [ ]
},
{
"success" : false,
"errors" : [
{
"statusCode" : "MALFORMED_ID",
"message" : "malformed id 001RM000003oLrB000",
"fields" : [ ]
}
438
sObject Collections を使用したレコードの削除リファレンス

===== PAGE 449 =====
]
}
]
レスポンスボディの例 (一部の項目でエラーが発生し、allOrNone が true の場合)
HTTP/1.1 200 OK
[
{
"id" : "001RM000003oLruYAE",
"success" : false,
"errors" : [
{
"statusCode" : "ALL_OR_NONE_OPERATION_ROLLED_BACK",
"message" : "Record rolled back because not all records were valid and the
request was using AllOrNone header",
"fields" : [ ]
}
]
},
{
"success" : false,
"errors" : [
{
"statusCode" : "MALFORMED_ID",
"message" : "malformed id 001RM000003oLrB000",
"fields" : [ ]
}
]
}
]
439
sObject Collections を使用したレコードの削除リファレンス