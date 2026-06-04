# クイックスタートと実践例（CRUD・クエリ・Blob・承認・イベント監視・複合リソース）

> 出典: Salesforce『REST API 開発者ガイド』日本語版 (api_rest.pdf, 2026-03-31 生成, Spring '26 相当)
> PDF ページ 33–139。pypdf による自動抽出テキストのため、表組みのレイアウトが崩れている場合がある。

## 収録セクション

- クイックスタート (PAGE 33)
  - cURL の使用 (PAGE 34)
  - ステップ 1: Salesforce Developer Edition へのサインアップ (PAGE 34)
  - ステップ 2: 認証を設定する (PAGE 35)
  - ステップ 3: サンプルコードを説明する (PAGE 37)
  - その他のツールの使用 (PAGE 42)
- 例 (PAGE 43)
  - 組織に関する情報の取得 (PAGE 44)
  - オブジェクトメタデータの使用 (PAGE 53)
  - レコードの操作 (PAGE 56)
  - Lightning Experience の一連の行動の削除 (PAGE 74)
  - 検索とクエリの使用 (PAGE 75)
  - リッチテキストエリア項目から画像を取得 (PAGE 88)
  - Blob データを挿入または更新する (PAGE 89)
  - blob データの取得 (PAGE 95)
  - 最近参照した情報の操作 (PAGE 96)
  - ユーザーパスワードの管理 (PAGE 98)
  - 承認プロセスとプロセスルールの操作 (PAGE 100)
  - イベント監視の使用 (PAGE 106)
  - 複合リソースの使用 (PAGE 114)

---

===== PAGE 33 =====
第 2 章 クイックスタート
REST API を設定および実行するには、Salesforce にいくつかの基本的な要求を送信しま
す。このクイックスタートでは、基本的な環境の設定と、REST API を使ったレコード
トピック:
• cURL の使用 の更新について説明します。REST API はさまざまな方法で設定および使用できます
が、ここでは、無料の Developer Edition と cURL を使用する方法を紹介します。• ステップ 1:
Salesforce Developer
Edition へのサイン
アップ
• ステップ 2: 認証を
設定する
• ステップ 3: サンプ
ルコードを説明す
る
• その他のツールの
使用
23

===== PAGE 34 =====
cURL の使用
Salesforce に要求するために使用できる書式を cURL を使って確認します。このクイックスタートでは cURL の例
を使用しますが、REST 要求を実行可能なツールや開発環境はすべて使用できます。
このガイドの例を理解できるように cURL に十分に習熟してください。また、これらの例は、ご使用のツール
に応じて書き換えてください。リクエストボディを含むファイルを添付するには、アクセストークンを適切に
書式設定する必要があります。クイックスタートに取り組んでいる間は、cURL の使用に役立つ以下のヒントを
参照してください。cURL の詳細は、「curl.se」を参照してください。
リクエストボディの添付
多くの例には、要求のデータを含んだ JSON または XML ファイルのリクエストボディがあります。cURL を使用
する場合は、これらのファイルをローカルシステムに保存し、—data-binary または -d オプションを使用し
て要求に添付します。
次の例では、new-account.json ファイルが添付されています。
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/ -H
'Authorization Bearer
00DE0X0A0M0PeLE!AQcAQH0dMHEXAMPLEzmpkb58urFRkgeBGsxL_QJWwYMfAbUeeG7c1EXAMPLEDUkWe6H34r1AAwOR8B8fLEz6nEXAMPLE'
-H "Content-Type: application/json" —d @new-account.json -X POST
アクセストークンでの感嘆符の使用
cURL の例を実行すると、OAuth アクセストークンに感嘆符 (!) が存在するため、macOS および Linux システムでは
エラーが発生する場合があります。このエラーを回避するには、感嘆符をエスケープするか単一引用符で囲み
ます。アクセストークンが二重引用符で囲まれている場合、アクセストークンで感嘆符をエスケープするに
は、感嘆符の前にバックスラッシュを挿入します。
\!
たとえば、この cURL コマンドのアクセストークン文字列では、感嘆符 (!) がエスケープされています。
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/ -H "Authorization: Bearer
00DE0X0A0M0PeLE\!AQcAQH0dMHEXAMPLEzmpkb58urFRkgeBGsxL_QJWwYMfAbUeeG7c1EXAMPLEDUkWe6H34r1AAwOR8B8fLEz6nEXAMPLE"
アクセストークンを一重引用符で囲んで感嘆符をエスケープしないこともできます。
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/ -H 'Authorization: Bearer
00DE0X0A0M0PeLE!AQcAQH0dMHEXAMPLEzmpkb58urFRkgeBGsxL_QJWwYMfAbUeeG7c1EXAMPLEDUkWe6H34r1AAwOR8B8fLEz6nEXAMPLE'
重要: 一重、二重を問わずすべての引用符は、曲線引用符ではなく直線引用符にする必要があります。
ステップ 1: Salesforce Developer Edition へのサインアップ
Developer Edition は簡単に入手できる無料ソリューションなので、Salesforce のテストや開発のために使用するこ
とができます。
Developer Edition アカウントにサインアップするには、developer.salesforce.com/signup にアクセスして
ください。
24
cURL の使用クイックスタート

===== PAGE 35 =====
メモ:  Developer Edition のデータのディスク使用の上限は 5 MB です。この制限のために以降の例の作業がで
きなくなることはありません。
開発用の Sandbox がある場合は、ここで紹介する例に使用できます。
始める前に、Salesforce ヘルプの「ユーザー権限」の手順に従って、ユーザープロファイルに「API の有効化」の
権限があることを確認してください。
関連トピック:
ナレッジ記事: API へのアクセス権を持つ Salesforce エディション
ステップ 2: 認証を設定する
REST API では、要求を正常に送信するには認証によって取得するアクセストークンが必要です。独自の接続ア
プリケーションを作成して認証を行うこともできますが、このクイックスタートの例では、容易に作業を進め
られるように Salesforce CLI を使用しています。Salesforce CLI は、認証が可能な接続アプリケーションで、設定の
作業は不要です。
Salesforce CLI でのアクセストークンの取得
Salesforce CLI から取得したアクセストークン (「ベアラートークン」とも呼ばれる) を使用して、cURL 要求を認
証します。
1. Salesforce CLI をインストールまたは更新します。
a. Salesforce CLI がすでにインストールされている場合は、「Salesforce CLI の更新」の手順に従って更新しま
す。
b. Salesforce CLI のインストールが必要な場合は、ご使用のオペレーティングシステムに対応した最新バー
ジョンをインストールしてください。
c. インストールを確認します。
2. Salesforce CLI を使用して開発者組織にログインします。
sf org login web
ブラウザーが開き、https://login.salesforce.com のページが表示されます。
3. ブラウザーで、ユーザーのログイン情報を使用して開発者組織にログインします。
4. ブラウザーで [許可] をクリックして、アクセスを許可します。
コマンドラインに次のような確認メッセージが表示されます。
Successfully authorized juliet.capulet@empathetic-wolf-g5qddtr.com with org ID
00D5fORGIDEXAMPLE
5. コマンドラインで組織に関する認証情報を表示して、アクセストークンを取得します。
sf org display --target-org <username>
25
ステップ 2: 認証を設定するクイックスタート

===== PAGE 36 =====
次に例を示します。
sf org display --target-org juliet.capulet@empathetic-wolf-g5qddtr.com
コマンド出力の例を次に示します。
=== Org Description
KEY VALUE
───────────────
────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Access Token
00DE0X0A0M0PeLE!AQcAQH0dMHEXAMPLEzmpkb58urFRkgeBGsxL_QJWwYMfAbUeeG7c1EXAMPLEDUkWe6H34r1AAwOR8B8fLEz6nEXAMPLE
Api Version 59.0
Client Id PlatformCLI
Created By jules@sf.com
Created Date 2023-11-16T20:35:21.000+0000
Dev Hub Id jules@sf.com
Edition Developer
Expiration Date 2023-11-23
Id 00D5fORGIDEXAMPLE
Instance Url https://MyDomainName.my.salesforce.com
Org Name Dreamhouse
Signup Username juliet.capulet@empathetic-wolf-g5qddtr.com
Status Active
Username juliet.capulet@empathetic-wolf-g5qddtr.com
コマンド出力内にある長いアクセストークン文字列とインスタンス URL 文字列をメモします。cURL 要求を
行うには、これらの両方の文字列が必要です。
メモ: アクセストークが期限切れになった後に新しいトークンを取得するには、このステップを繰り
返して認証情報を表示してください。
Salesforce CLI のショートカット (省略可能)
認証が成功したら、今後 Salesforce CLI での認証を簡素化するために、cURL ワークフローで次のショートカット
(省略可能) を試します。
私の組織をリスト表示する
sf org list
作成した組織または認証先の組織をすべてリスト表示します。
私の組織を開く
sf org open --target-org <username>
指定の組織 (ユーザー名またはエイリアスで指定した組織) をブラウザーで開きます。Salesforce CLI コマンドの
org login web を使用してこの組織での認証がすでに成功しているため、ログイン情報を再指定する必要は
ありません。
26
ステップ 2: 認証を設定するクイックスタート

===== PAGE 37 =====
私の組織のアクセストークンを表示する
sf org display --target-org <username>
該当する場合、出力には、アクセストークン、クライアント ID、接続状況、組織 ID、インスタンス URL、ユー
ザー名、別名が含まれています。
私のユーザー名の別名を設定する
便宜上、ユーザー名の別名を作成すると、Salesforce 文字列をすべて入力しなくても済むようになります。たと
えば、次のユーザー名があるとします。
juliet.capulet@empathetic-wolf-g5qddtr.com
代わりに、次のような別名を作成できます。
dev
この例の別名を設定するには、次を実行します。
sf alias set dev juliet.capulet@empathetic-wolf-g5qddtr.com
スクリプトでこれらのコマンドを使用する
--json フラグを呼び出して CLI の JSON 出力を使用します。JSON 出力を要求すると、出力形式の一貫性が保た
れるため、スクリプトの実行に最適です。--json フラグを使用しない場合は、CLI の出力形式が変化する場合
があります。
関連トピック
• Salesforce CLI 設定ガイド
• Salesforce CLI コマンドリファレンス
関連トピック:
Salesforce ヘルプ: OAuth によるアプリケーションの認証
ステップ 3: サンプルコードを説明する
Salesforce の異なる種別のリソースにアクセスするには、一連の REST 要求を実行します。これらの例を試す前
に、このクイックスタートのステップ 1 で前提条件をすべて満たし、アクセストークンを取得していることを
確認してください。
これらの例は、コピー/貼り付けして cURL で送信できます。ただし、先にベース URI の MyDomainName を
Salesforce ドメインに置き換えてください。REST 要求の仕組みの詳細は、「REST リソースと要求」 (ページ 3)を
参照してください。
Salesforce バージョンを取得する
使用可能な Salesforce バージョンのそれぞれに関する情報を取得するには、Versions 要求を送信します。この場
合、要求に認証は必要ありません。
curl https://MyDomainName.my.salesforce.com/services/data/
27
ステップ 3: サンプルコードを説明するクイックスタート

===== PAGE 38 =====
この要求の出力は、応答ヘッダーを含めて、すべての有効なバージョンを指定します。結果には複数の値が含
まれる場合があります。
Content-Length: 88
Content-Type: application/json;
charset=UTF-8 Server:
[
{
"label":"Spring '11",
"url":"/services/data/v21.0",
"version":"21.0"
}
...
]
リソースのリストを取得する
Salesforce (この例ではバージョン 60.0) で使用可能なリソースのリストを取得するには、Resources by Version 要求
を送信します。
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/ -H "Authorization: Bearer
access_token"
この要求の出力は、sobjects が、Salesforce バージョン 60.0 で使用可能なリソースの 1 つであることを示しま
す。
{
"sobjects" : "/services/data/v60.0/sobjects",
"search" : "/services/data/v60.0/search",
"query" : "/services/data/v60.0/query",
"recent" : "/services/data/v60.0/recent"
}
使用可能なオブジェクトのリストを取得する
使用可能なオブジェクトのリストを要求するには、Describe Global 要求を送信します。
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/ -H "Authorization:
Bearer access_token"
この要求の出力は、Account オブジェクトが使用可能であることを示します。
Transfer-Encoding: chunked
Content-Type: application/json;
charset=UTF-8 Server:
{
"encoding" : "UTF-8",
"maxBatchSize" : 200,
"sobjects" : [ {
"name" : "Account",
"label" : "Account",
"custom" : false,
28
ステップ 3: サンプルコードを説明するクイックスタート

===== PAGE 39 =====
"keyPrefix" : "001",
"updateable" : true,
"searchable" : true,
"labelPlural" : "Accounts",
"layoutable" : true,
"activateable" : false,
"urls" : { "sobject" : "/services/data/v60.0/sobjects/Account",
"describe" : "/services/data/v60.0/sobjects/Account/describe",
"rowTemplate" : "/services/data/v60.0/sobjects/Account/{ID}" },
"createable" : true,
"customSetting" : false,
"deletable" : true,
"deprecatedAndHidden" : false,
"feedEnabled" : false,
"mergeable" : true,
"queryable" : true,
"replicateable" : true,
"retrieveable" : true,
"undeletable" : true,
"triggerable" : true },
},
...
オブジェクトの基本情報を取得する
使用可能な Account オブジェクトのメタデータの基本情報を取得するには、sObject Basic Information要求を送信し
ます。
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/ -H
"Authorization: Bearer access_token"
この要求の出力は、名前や表示ラベルなどの Account オブジェクトの基本属性と、最近使用された取引先のリ
ストを示します。
{
"objectDescribe" :
{
"name" : "Account",
"updateable" : true,
"label" : "Account",
"keyPrefix" : "001",
...
"replicateable" : true,
"retrieveable" : true,
"undeletable" : true,
"triggerable" : true
},
"recentItems" :
[
{
"attributes" :
29
ステップ 3: サンプルコードを説明するクイックスタート

===== PAGE 40 =====
{
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001D000000INjVeIAL"
},
"Id" : "001D000000INjVeIAL",
"Name" : "asdasdasd"
},
...
]
}
項目のリストを取得する
詳細情報を取得するには、sObject Describe 要求を送信します。
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/describe/
-H "Authorization: Bearer access_token"
この要求の出力は、その項目の属性や子リレーションなど、Account オブジェクトのさらに詳細な情報を示し
ます。
{
"name" : "Account",
"fields" :
[
{
"length" : 18,
"name" : "Id",
"type" : "id",
"defaultValue" : { "value" : null },
"updateable" : false,
"label" : "Account ID",
...
},
...
],
"updateable" : true,
"label" : "Account",
...
"urls" :
{
"uiEditTemplate" : "https://MyDomainName.my.salesforce.com/{ID}/e",
"sobject" : "/services/data/v60.0/sobjects/Account",
"uiDetailTemplate" : "https://MyDomainName.my.salesforce.com/{ID}",
"describe" : "/services/data/v60.0/sobjects/Account/describe",
"rowTemplate" : "/services/data/v60.0/sobjects/Account/{ID}",
"uiNewRecord" : "https://MyDomainName.my.salesforce.com/001/e"
},
"childRelationships" :
[
{
30
ステップ 3: サンプルコードを説明するクイックスタート

===== PAGE 41 =====
"field" : "ParentId",
"deprecatedAndHidden" : false,
...
},
...
],
"createable" : true,
"customSetting" : false,
...
}
SOQL クエリを実行する
Account の name のすべての値を取得する SOQL クエリを実行するには、Query 要求を送信します。
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/query?q=SELECT+name+from+Account
-H "Authorization: Bearer access_token"
出力で、使用可能な取引先名がリストされます。それぞれの名前の前にある属性には取引先の ID が含まれま
す。
{
"done" : true,
"totalSize" : 14,
"records" :
[
{
"attributes" :
{
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001D000000IRFmaIAH"
},
"Name" : "Test 1"
},
{
"attributes" :
{
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001D000000IomazIAB"
},
"Name" : "Test 2"
},
...
]
}
メモ:  SOQL についての詳細は、『SOQL および SOSL リファレンス』を参照してください。
31
ステップ 3: サンプルコードを説明するクイックスタート

===== PAGE 42 =====
レコードの項目を更新する
取引先の 1 つを取得し、市区郡 (請求先) を更新するには、sObject Rows 要求を送信します。オブジェクトを更新
するには、新しい市区郡 (請求先) の情報を含む patchaccount.json というテキストファイルを作成します。
{
"BillingCity" : "Fremont"
}
REST 要求に、この JSON ファイルを指定します。cURL 表記には、データを指定する場合、—d オプションが必要
です。詳細は、http://curl.haxx.se/docs/manpage.html を参照してください。
また、REST リソースを更新するために使用する PATCH メソッドを指定します。次の cURL コマンドは、ID 項目
を使用して指定された Account オブジェクトを取得し、その市区郡 (請求先) を更新します。
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/001D000000IroHJ
-H "Authorization: Bearer access_token" -H "Content-Type: application/json" --data-binary
@patchaccount.json -X PATCH
レスポンスボディはなく、ヘッダーのみが返されます。
HTTP/1.1 204 No Content
Server:
Content-Length: 0
請求先が Fremont に変更されたことを確認するには、取引先のページを更新します。
その他のツールの使用
その他のツールを使用して、Salesforce 組織からデータを取得できます。
cURL を使用しない場合は、別のツールを使用して API を実行できます。選択できるツールには、次のものがあ
ります。
• Salesforce CLI。
• Postman (サードパーティのツール)。詳細は、「Postman API Client Trailhead module (Postman API クライアント
Trailhead モジュール)」を参照してください。
これらのツールは、多くの API 要求を作成して送信するプロセスを簡素化する機能を備えています。
32
その他のツールの使用クイックスタート

===== PAGE 43 =====
第 3 章 例
このセクションでは、例を示しながら、REST API リソースを使用してオブジェクト、
組織情報、クエリの使用などさまざまなタスクを実行する方法を説明します。
トピック:
• 組織に関する情報
の取得 REST API リソースの完全なリファレンス情報は、「リファレンス (ページ130)」を参照
してください。• オブジェクトメタ
データの使用
• レコードの操作
• Lightning Experience
の一連の行動の削
除
• 検索とクエリの使
用
• リッチテキストエ
リア項目から画像
を取得
• Blob データを挿入
または更新する
• blob データの取得
• 最近参照した情報
の操作
• ユーザーパスワー
ドの管理
• 承認プロセスとプ
ロセスルールの操
作
• イベント監視の使
用
• 複合リソースの使
用
33

===== PAGE 44 =====
組織に関する情報の取得
このセクションの例では、REST API リソースを使用して、組織で使用できるすべてのオブジェクトのリストな
ど、組織レベルの情報を取得します。
このセクションの内容:
使用可能な REST API バージョンをリストする
バージョン、表示ラベル、および各バージョンのルートへのリンクなど、現在使用できる各 REST API バー
ジョンについての概要情報をリストするには、Versions リソースを使用します。バージョンのリストを取得
するための認証は必要ありません。
組織の制限をリストする
Limits リソースを使用し、組織の制限をリストします。
使用可能な REST リソースをリストする
指定された API バージョンで使用可能なリソースをリストするには、Resources by Versionリソースを使用しま
す。このリソースは、その他のリソースそれぞれの名前と URI を提供します。
オブジェクトのリストを取得する
組織で使用できるオブジェクトおよびログインユーザーが使用できるオブジェクトをリストするには、
Describe Global リソースを使用します。このリソースは、組織の文字コードとクエリで許可される最大バッ
チサイズも返します。
メタデータが変更された場合にオブジェクトのリストを取得する
Describe Global リソースおよび If-Modified-Since  HTTP ヘッダーを使用して、オブジェクトのメタデータ
が変更されたかどうかを判別できます。
使用可能な REST API バージョンをリストする
バージョン、表示ラベル、および各バージョンのルートへのリンクなど、現在使用できる各 REST API バージョ
ンについての概要情報をリストするには、Versions リソースを使用します。バージョンのリストを取得するた
めの認証は必要ありません。
使用例
curl https://MyDomainName.my.salesforce.com/services/data/ -H "Authorization: Bearer
token"
リクエストボディの例
不要
JSON レスポンスボディの例
[
{
"label" : "Spring '11",
"url" : "/services/data/v21.0",
"version" : "21.0"
},
{
34
組織に関する情報の取得例

===== PAGE 45 =====
"label" : "Summer '11",
"url" : "/services/data/v22.0",
"version" : "22.0"
},
{
"label" : "Winter '12",
"url" : "/services/data/v23.0",
"version" : "23.0"
}
...
]
XML レスポンスボディの例
<?xml version="1.0" encoding="UTF-8"?>
<Versions>
<Version>
<label>Spring &apos;11</label>
<url>/services/data/v21.0</url>
<version>21.0</version>
</Version>
<Version>
<label>Summer &apos;11</label>
<url>/services/data/v22.0</url>
<version>22.0</version>
</Version><Version>
<label>Winter &apos;12</label>
<url>/services/data/v23.0</url>
<version>23.0</version>
</Version>
...
</Versions>
関連トピック:
Versions
組織の制限をリストする
Limits リソースを使用し、組織の制限をリストします。
• Max は組織の制限です。
• Remaining は組織に残されているコールまたはイベント数です。
使用例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/limits/ -H
"Authorization: Bearer token" -H "X-PrettyPrint:1"
リクエストボディの例
不要
35
組織の制限をリストする例

===== PAGE 46 =====
レスポンスボディの例
{
"ActiveScratchOrgs": {
"Max": 3,
"Remaining": 3
},
"AnalyticsExternalDataSizeMB": {
"Max": 40960,
"Remaining": 40960
},
"ConcurrentAsyncGetReportInstances": {
"Max": 200,
"Remaining": 200
},
"ConcurrentEinsteinDataInsightsStoryCreation": {
"Max": 5,
"Remaining": 5
},
"ConcurrentEinsteinDiscoveryStoryCreation": {
"Max": 2,
"Remaining": 2
},
"ConcurrentSyncReportRuns": {
"Max": 20,
"Remaining": 20
},
"DailyAnalyticsDataflowJobExecutions": {
"Max": 60,
"Remaining": 60
},
"DailyAnalyticsUploadedFilesSizeMB": {
"Max": 51200,
"Remaining": 51200
},
"DailyFunctionsApiCallLimit" : {
"Max" : 235000,
"Remaining" : 235000
},
"DailyApiRequests": {
"Max": 5000,
"Remaining": 4937
},
"DailyAsyncApexExecutions": {
"Max": 250000,
"Remaining": 250000
},
"DailyAsyncApexTests": {
"Max": 500,
"Remaining": 500
},
"DailyBulkApiBatches": {
"Max": 15000,
"Remaining": 15000
36
組織の制限をリストする例

===== PAGE 47 =====
},
"DailyBulkV2QueryFileStorageMB": {
"Max": 976562,
"Remaining": 976562
},
"DailyBulkV2QueryJobs": {
"Max": 10000,
"Remaining": 10000
},
"DailyDeliveredPlatformEvents" : {
"Max" : 10000,
"Remaining" : 10000
},
"DailyDurableGenericStreamingApiEvents": {
"Max": 10000,
"Remaining": 10000
},
"DailyDurableStreamingApiEvents": {
"Max": 10000,
"Remaining": 10000
},
"DailyEinsteinDataInsightsStoryCreation": {
"Max": 1000,
"Remaining": 1000
},
"DailyEinsteinDiscoveryPredictAPICalls": {
"Max": 50000,
"Remaining": 50000
},
"DailyEinsteinDiscoveryPredictionsByCDC": {
"Max": 5000000,
"Remaining": 5000000
},
"DailyEinsteinDiscoveryStoryCreation": {
"Max": 100,
"Remaining": 100
},
"DailyGenericStreamingApiEvents": {
"Max": 10000,
"Remaining": 10000
},
"DailyScratchOrgs": {
"Max": 6,
"Remaining": 6
},
"DailyStandardVolumePlatformEvents": {
"Max": 10000,
"Remaining": 10000
},
"DailyStreamingApiEvents": {
"Max": 10000,
"Remaining": 10000
},
"DailyWorkflowEmails": {
37
組織の制限をリストする例

===== PAGE 48 =====
"Max": 100000,
"Remaining": 100000
},
"DataStorageMB": {
"Max": 1024,
"Remaining": 1024
},
"DurableStreamingApiConcurrentClients": {
"Max": 20,
"Remaining": 20
},
"FileStorageMB": {
"Max": 1024,
"Remaining": 1024
},
"HourlyAsyncReportRuns": {
"Max": 1200,
"Remaining": 1200
},
"HourlyDashboardRefreshes": {
"Max": 200,
"Remaining": 200
},
"HourlyDashboardResults": {
"Max": 5000,
"Remaining": 5000
},
"HourlyDashboardStatuses": {
"Max": 999999999,
"Remaining": 999999999
},
"HourlyLongTermIdMapping": {
"Max": 100000,
"Remaining": 100000
},
"HourlyManagedContentPublicRequests": {
"Max": 50000,
"Remaining": 50000
},
"HourlyODataCallout": {
"Max": 20000,
"Remaining": 20000
},
"HourlyPublishedPlatformEvents": {
"Max": 50000,
"Remaining": 50000
},
"HourlyPublishedStandardVolumePlatformEvents": {
"Max": 1000,
"Remaining": 1000
},
"HourlyShortTermIdMapping": {
"Max": 100000,
"Remaining": 100000
38
組織の制限をリストする例

===== PAGE 49 =====
},
"HourlySyncReportRuns": {
"Max": 500,
"Remaining": 500
},
"HourlyTimeBasedWorkflow": {
"Max": 1000,
"Remaining": 1000
},
"MassEmail": {
"Max": 5000,
"Remaining": 5000
},
"MonthlyEinsteinDiscoveryStoryCreation": {
"Max": 500,
"Remaining": 500
},
"Package2VersionCreates": {
"Max": 6,
"Remaining": 6
},
"Package2VersionCreatesWithoutValidation": {
"Max": 500,
"Remaining": 500
},
"PermissionSets": {
"Max": 1500,
"Remaining": 1499,
"CreateCustom": {
"Max": 1000,
"Remaining": 999
}
},
"PrivateConnectOutboundCalloutHourlyLimitMB": {
"Max": 0,
"Remaining": 0
},
"SingleEmail": {
"Max": 5000,
"Remaining": 5000
},
"StreamingApiConcurrentClients": {
"Max": 20,
"Remaining": 20
}
}
使用可能な REST リソースをリストする
指定された API バージョンで使用可能なリソースをリストするには、Resources by Versionリソースを使用します。
このリソースは、その他のリソースそれぞれの名前と URI を提供します。
39
使用可能な REST リソースをリストする例

===== PAGE 50 =====
例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/ -H "Authorization:
Bearer token"
リクエストボディの例
不要
JSON レスポンスボディの例
{
"tooling" : "/services/data/v60.0/tooling",
"metadata" : "/services/data/v60.0/metadata",
"eclair" : "/services/data/v60.0/eclair",
"folders" : "/services/data/v60.0/folders",
"prechatForms" : "/services/data/v60.0/prechatForms",
"contact-tracing" : "/services/data/v60.0/contact-tracing",
"jsonxform" : "/services/data/v60.0/jsonxform",
"chatter" : "/services/data/v60.0/chatter",
"payments" : "/services/data/v60.0/payments",
"tabs" : "/services/data/v60.0/tabs",
"appMenu" : "/services/data/v60.0/appMenu",
"quickActions" : "/services/data/v60.0/quickActions",
"queryAll" : "/services/data/v60.0/queryAll",
"commerce" : "/services/data/v60.0/commerce",
"wave" : "/services/data/v60.0/wave",
"iot" : "/services/data/v60.0/iot",
"analytics" : "/services/data/v60.0/analytics",
"search" : "/services/data/v60.0/search",
"smartdatadiscovery" : "/services/data/v60.0/smartdatadiscovery",
"identity" : "https://MyDomainName.my.salesforce.com/id/
00DRO0000008aXd2AI/005RO000000HfnkYAC",
"composite" : "/services/data/v60.0/composite",
"parameterizedSearch" : "/services/data/v60.0/parameterizedSearch",
"fingerprint" : "/services/data/v60.0/fingerprint",
"theme" : "/services/data/v60.0/theme",
"nouns" : "/services/data/v60.0/nouns",
"domino" : "/services/data/v60.0/domino",
"event" : "/services/data/v60.0/event",
"serviceTemplates" : "/services/data/v60.0/serviceTemplates",
"recent" : "/services/data/v60.0/recent",
"connect" : "/services/data/v60.0/connect",
"licensing" : "/services/data/v60.0/licensing",
"limits" : "/services/data/v60.0/limits",
"process" : "/services/data/v60.0/process",
"dedupe" : "/services/data/v60.0/dedupe",
"async-queries" : "/services/data/v60.0/async-queries",
"query" : "/services/data/v60.0/query",
"jobs" : "/services/data/v60.0/jobs",
"localizedvalue" : "/services/data/v60.0/localizedvalue",
"mobile" : "/services/data/v60.0/mobile",
"emailConnect" : "/services/data/v60.0/emailConnect",
"consent" : "/services/data/v60.0/consent",
"tokenizer" : "/services/data/v60.0/tokenizer",
"compactLayouts" : "/services/data/v60.0/compactLayouts",
40
使用可能な REST リソースをリストする例

===== PAGE 51 =====
"sobjects" : "/services/data/v60.0/sobjects",
"actions" : "/services/data/v60.0/actions",
"support" : "/services/data/v60.0/support"
}
XML レスポンスボディの例
<?xml version="1.0" encoding="UTF-8"?>
<urls>
<tooling>/services/data/v60.0/tooling</tooling>
<metadata>/services/data/v60.0/metadata</metadata>
<eclair>/services/data/v60.0/eclair</eclair>
<folders>/services/data/v60.0/folders</folders>
<prechatForms>/services/data/v60.0/prechatForms</prechatForms>
<contact-tracing>/services/data/v60.0/contact-tracing</contact-tracing>
<jsonxform>/services/data/v60.0/jsonxform</jsonxform>
<chatter>/services/data/v60.0/chatter</chatter>
<payments>/services/data/v60.0/payments</payments>
<tabs>/services/data/v60.0/tabs</tabs>
<appMenu>/services/data/v60.0/appMenu</appMenu>
<quickActions>/services/data/v60.0/quickActions</quickActions>
<queryAll>/services/data/v60.0/queryAll</queryAll>
<commerce>/services/data/v60.0/commerce</commerce>
<wave>/services/data/v60.0/wave</wave>
<iot>/services/data/v60.0/iot</iot>
<analytics>/services/data/v60.0/analytics</analytics>
<search>/services/data/v60.0/search</search>
<smartdatadiscovery>/services/data/v60.0/smartdatadiscovery</smartdatadiscovery>
<identity>https://MyDomainName.my.salesforce.com/id/
00DRO0000008aXd2BI/005RO000000HfnkYAB</identity>
<composite>/services/data/v60.0/composite</composite>
<parameterizedSearch>/services/data/v60.0/parameterizedSearch</parameterizedSearch>
<fingerprint>/services/data/v60.0/fingerprint</fingerprint>
<theme>/services/data/v60.0/theme</theme>
<nouns>/services/data/v60.0/nouns</nouns>
<domino>/services/data/v60.0/domino</domino>
<event>/services/data/v60.0/event</event>
<serviceTemplates>/services/data/v60.0/serviceTemplates</serviceTemplates>
<recent>/services/data/v60.0/recent</recent>
<connect>/services/data/v60.0/connect</connect>
<licensing>/services/data/v60.0/licensing</licensing>
<limits>/services/data/v60.0/limits</limits>
<process>/services/data/v60.0/process</process>
<dedupe>/services/data/v60.0/dedupe</dedupe>
<async-queries>/services/data/v60.0/async-queries</async-queries>
<query>/services/data/v60.0/query</query>
<jobs>/services/data/v60.0/jobs</jobs>
<localizedvalue>/services/data/v60.0/localizedvalue</localizedvalue>
<mobile>/services/data/v60.0/mobile</mobile>
<emailConnect>/services/data/v60.0/emailConnect</emailConnect>
<consent>/services/data/v60.0/consent</consent>
<tokenizer>/services/data/v60.0/tokenizer</tokenizer>
<compactLayouts>/services/data/v60.0/compactLayouts</compactLayouts>
<sobjects>/services/data/v60.0/sobjects</sobjects>
<actions>/services/data/v60.0/actions</actions>
41
使用可能な REST リソースをリストする例

===== PAGE 52 =====
<support>/services/data/v60.0/support</support>
</urls>
詳細
ID リソースについての詳細は、「ID URL」を参照してください。
他のリソースについては、「リファレンス」を参照してください。
オブジェクトのリストを取得する
組織で使用できるオブジェクトおよびログインユーザーが使用できるオブジェクトをリストするには、Describe
Global リソースを使用します。このリソースは、組織の文字コードとクエリで許可される最大バッチサイズも
返します。
使用例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/ -H
"Authorization: Bearer token"
リクエストボディの例
不要
レスポンスボディの例
{
"encoding" : "UTF-8",
"maxBatchSize" : 200,
"sobjects" : [ {
"activateable" : false,
"custom" : false,
"customSetting" : false,
"createable" : true,
"deletable" : true,
"deprecatedAndHidden" : false,
"feedEnabled" : true,
"keyPrefix" : "001",
"label" : "Account",
"labelPlural" : "Accounts",
"layoutable" : true,
"mergeable" : true,
"mruEnabled" : true,
"name" : "Account",
"queryable" : true,
"replicateable" : true,
"retrieveable" : true,
"searchable" : true,
"triggerable" : true,
"undeletable" : true,
"updateable" : true,
"urls" : {
"sobject" : "/services/data/v60.0/sobjects/Account",
"describe" : "/services/data/v60.0/sobjects/Account/describe",
42
オブジェクトのリストを取得する例

===== PAGE 53 =====
"rowTemplate" : "/services/data/v60.0/sobjects/Account/{ID}"
},
},
...
]
}
メタデータが変更された場合にオブジェクトのリストを取得する
Describe Global リソースおよび If-Modified-Since  HTTP ヘッダーを使用して、オブジェクトのメタデータが
変更されたかどうかを判別できます。
Describe Global リソースを使用するときに、If-Modified-Since ヘッダーを EEE, dd MMM yyyy HH:mm:ss
z 形式の日付と共に含めることができます。このヘッダーを使用すると、指定した日付以降に使用可能なオブ
ジェクトのメタデータが変更された場合にのみ応答のメタデータが返されます。指定の日付以降にメタデータ
が変更されていない場合は、レスポンスボディなしで 304 Not Modified 状況コードが返されます。
次の例では、2015 年 3 月 23 日以降にオブジェクトが変更されていないことを前提としています。
Describe Global 要求の例
/services/data/v60.0/sobjects
要求で使用される If-Modified-Since ヘッダーの例
If-Modified-Since: Tue, 23 Mar 2015 00:00:00 GMT
レスポンスボディの例
レスポンスボディは返されない
応答状況コードの例
HTTP/1.1 304 Not Modified
Date: Wed, 25 Jul 2015 00:05:46 GMT
2015 年 3 月 23 日以降にオブジェクトに変更があった場合は、レスポンスボディにすべての使用可能なオブジェ
クトのメタデータが含まれます。「オブジェクトのリストを取得する」の例を参照してください。
オブジェクトメタデータの使用
このセクションの例では、REST API リソースを使用して、オブジェクトメタデータ情報を取得します。オブジェ
クトメタデータ情報の変更または作成についての詳細は、『メタデータ API 開発者ガイド』を参照してくださ
い。
このセクションの内容:
オブジェクトのメタデータの取得
オブジェクトのメタデータを取得するには、sObject Basic Information リソースを使用します。
オブジェクトの項目と他のメタデータを取得する
各項目、URL、および子リレーションに関する情報を含む、オブジェクトのすべてのメタデータを取得する
には、sObject Describe リソースを使用します。
43
メタデータが変更された場合にオブジェクトのリストを
取得する
例

===== PAGE 54 =====
オブジェクトのメタデータの変更の取得
sObject Describe リソースおよび If-Modified-Since  HTTP ヘッダーを使用して、オブジェクトのメタデー
タが変更されたかどうかを確認できます。
オブジェクトのメタデータの取得
オブジェクトのメタデータを取得するには、sObject Basic Information リソースを使用します。
Account メタデータを取得する場合の使用例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/ -H
"Authorization: Bearer token"
Account メタデータを取得する場合のリクエストボディの例
不要
Account メタデータを取得する場合のレスポンスボディの例
{
"objectDescribe" :
{
"name" : "Account",
"updateable" : true,
"label" : "Account",
"keyPrefix" : "001",
...
"replicateable" : true,
"retrieveable" : true,
"undeletable" : true,
"triggerable" : true
},
"recentItems" :
[
{
"attributes" :
{
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001D000000INjVeIAL"
},
"Id" : "001D000000INjVeIAL",
"Name" : "asdasdasd"
},
...
]
}
項目名やメタデータを含む、オブジェクトの完全な説明を取得するには、「オブジェクトのリストを取得す
る」を参照してください。
44
オブジェクトのメタデータの取得例

===== PAGE 55 =====
オブジェクトの項目と他のメタデータを取得する
各項目、URL、および子リレーションに関する情報を含む、オブジェクトのすべてのメタデータを取得するに
は、sObject Describe リソースを使用します。
例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/describe/
-H "Authorization: Bearer token"
リクエストボディの例
不要
レスポンスボディの例
{
"name" : "Account",
"fields" :
[
{
"length" : 18,
"name" : "Id",
"type" : "id",
"defaultValue" : { "value" : null },
"updateable" : false,
"label" : "Account ID",
...
},
...
],
"updateable" : true,
"label" : "Account",
"keyPrefix" : "001",
"custom" : false,
...
"urls" :
{
"uiEditTemplate" : "https://MyDomainName.my.salesforce.com/{ID}/e",
"sobject" : "/services/data/v60.0/sobjects/Account",
"uiDetailTemplate" : "https://MyDomainName.my.salesforce.com/{ID}",
...
},
"childRelationships" :
[
{
"field" : "ParentId",
"deprecatedAndHidden" : false,
45
オブジェクトの項目と他のメタデータを取得する例

===== PAGE 56 =====
...
},
....
],
"createable" : true,
"customSetting" : false,
...
}
リクエストボディの項目についての詳細は、『SOAP API 開発者ガイド』の「DescribesObjectResult」を参照して
ください。
オブジェクトのメタデータの変更の取得
sObject Describe リソースおよび If-Modified-Since  HTTP ヘッダーを使用して、オブジェクトのメタデータが
変更されたかどうかを確認できます。
sObject Describeリソースを使用するときに、If-Modified-Since ヘッダーを EEE, dd MMM yyyy HH:mm:ss
z 形式の日付と共に含めることができます。このヘッダーを使用すると、指定した日付以降にオブジェクトの
メタデータが変更された場合にのみ応答のメタデータが返されます。指定の日付以降にメタデータが変更され
ていないと、レスポンスボディなしで 304 Not Modified 状況コードが返されます。
次の例では、2013 年 7 月 3 日以降に新しいカスタム項目などの Merchandise__c オブジェクトに行われた変更が
ないことを前提としています。
sObject Describe 要求の例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Merchandise__c/describe
-H "Authorization: Bearer token" -H "If-Modified-Since: Wed, 3 Jul 2013 19:43:31 GMT"
レスポンスボディの例
レスポンスボディは返されない
応答状況コードの例
HTTP/1.1 304 Not Modified
Date: Fri, 12 Jul 2013 05:03:24 GMT
2013 年 7 月 3 日以降に Merchandise__c に変更があった場合は、レスポンスボディには Merchandise__c のメタデー
タが含まれます。例については、「オブジェクトの項目と他のメタデータを取得する」を参照してください。
レコードの操作
このセクションの例では、REST API リソースを使用してレコードの作成、取得、更新、削除とその他のレコー
ド関連操作を実行します。
46
オブジェクトのメタデータの変更の取得例

===== PAGE 57 =====
このセクションの内容:
レコードを作成する
新規レコードを作成するには、sObject Basic Informationリソースを使用します。要求データの必須項目値を指
定し、POST HTTP メソッドを使用して要求を送信します。コールが成功すると、レスポンスボディに新しい
レコードの ID が含まれます。
レコードを更新する
レコードを更新するには、sObject Rows リソースを使用します。要求データに更新するレコード情報を指定
し、リソースの PATCH メソッドを使用して、特定のレコードの ID を指定し、そのレコードを更新します。
1 つのファイルに含まれるレコードは、同じオブジェクト種別である必要があります。
レコードを削除する
レコードを削除するには、sObject Rows リソースを使用します。レコード ID を指定し、リソースの DELETE メ
ソッドを使用してレコードを削除します。
標準オブジェクトレコードから項目値を取得する
レコードから項目値を取得するには、sObject Rows リソースの GET メソッドを使用します。
Salesforce ID を使用して外部オブジェクトレコードから項目値を取得する
レコードから項目値を取得するには、sObject Rows リソースを使用します。fields パラメーターに取得す
る項目を指定し、リソースの GET メソッドを使用します。
外部 ID 標準項目を使用して外部オブジェクトレコードから項目値を取得する
レコードから項目値を取得するには、sObject Rows リソースを使用します。fields パラメーターに取得す
る項目を指定し、リソースの GET メソッドを使用します。
外部 ID を使用したレコードの取得
sObject Rows by External ID リソースの GET メソッドを使用して、特定の外部 ID でレコードを取得できます。
外部 ID を使用してレコードを挿入/更新 (Upsert) する
指定された外部 ID 項目の値に基づいて、レコードを作成するか、既存のレコードを挿入/更新 (Upsert) する
には、sObject Rows by External ID リソースを使用します。
フレンドリー URL を使用したリレーションのトラバース
標準およびカスタムオブジェクトのリレーション項目をトラバースするには、sObject Relationship リソースを
使用して、フレンドリー URL を作成します。この方法では、リレーションによって関連付けられたレコー
ドに直接アクセスできます。フレンドリー URL を使用する方が、リレーション項目からオブジェクト ID を
取得し、関連付けられたオブジェクト ID レコードを調べて、レコードにアクセスするよりも簡単です。
特定の時間枠に削除されたレコードのリストの取得
指定されたオブジェクトの削除されたレコードのリストを取得するには、sObject Get Deletedリソースを使用
します。特定のオブジェクトのレコードが削除された日時の範囲を指定します。削除されたレコードは削
除ログ (定期的に消去される) に書き込まれ、sObject 行、クエリなどのほとんどの操作対象から除外されま
す (ただし、QueryAll では削除されたレコードが結果に含まれます)。
特定の時間枠に更新されたレコードのリストの取得
指定されたオブジェクトの更新 (変更または追加) されたレコードのリストを取得するには、sObject Get Updated
リソースを使用します。特定のオブジェクトのレコードが更新された日時の範囲を指定します。
47
レコードの操作例

===== PAGE 58 =====
レコードを作成する
新規レコードを作成するには、sObject Basic Information リソースを使用します。要求データの必須項目値を指定
し、POST HTTP メソッドを使用して要求を送信します。コールが成功すると、レスポンスボディに新しいレコー
ドの ID が含まれます。
次の要求の例では、newaccount.json に指定された新しいレコードの項目値で新規 Account レコードを作成
します。この例では、名前項目のみが指定されていますが、他の Account 項目の値を指定することもできます。
新規 Account を作成する例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/ -H
"Authorization: Bearer token" -H "Content-Type: application/json" -d "@newaccount.json"
新規 Account を作成する場合のリクエストボディ newaccount.json ファイルの例
{
"Name" : "Express Logistics and Transport"
}
新規 Account が正常に作成された場合のレスポンスボディの例
{
"id" : "001D000000IqhSLIAZ",
"errors" : [ ],
"success" : true
}
レコードを更新する
レコードを更新するには、sObject Rows リソースを使用します。要求データに更新するレコード情報を指定し、
リソースの PATCH メソッドを使用して、特定のレコードの ID を指定し、そのレコードを更新します。1 つの
ファイルに含まれるレコードは、同じオブジェクト種別である必要があります。
次の例では、Account 内の請求先市区郡の情報 (BillingCity) が更新されます。更新するレコード情報は
patchaccount.json に指定されています。
Account オブジェクトを更新する例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/001D000000INjVe
-H "Authorization: Bearer token" -H "Content-Type: application/json" -d
@patchaccount.json -X PATCH
Account オブジェクトの項目を更新する場合のリクエストボディ patchaccount.json ファイルの例
{
"BillingCity" : "San Francisco"
}
Account オブジェクトの項目を更新する場合のレスポンスボディの例
戻り値なし
エラー応答
「状況コードとエラー応答」 (ページ 20)を参照してください。
48
レコードを作成する例

===== PAGE 59 =====
次の例では、Java と HttpClient を使用し、REST API を使用してレコードを更新します。HttpClient に PatchMethod が
ないため、PostMethod が上書きされてメソッド名として「PATCH」が返されます。この例では、オブジェクト
名とレコード ID が含まれるリソース URL が渡されていると想定します。
public static void patch(String url, String sid) throws IOException {
PostMethod m = new PostMethod(url) {
@Override public String getName() { return "PATCH"; }
};
m.setRequestHeader("Authorization", "OAuth " + sid);
Map<String, Object> accUpdate = new HashMap<String, Object>();
accUpdate.put("Name", "Patch test");
ObjectMapper mapper = new ObjectMapper();
m.setRequestEntity(new StringRequestEntity(mapper.writeValueAsString(accUpdate),
"application/json", "UTF-8"));
HttpClient c = new HttpClient();
int sc = c.executeMethod(m);
System.out.println("PATCH call returned a status code of " + sc);
if (sc > 299) {
// deserialize the returned error message
List<ApiError> errors = mapper.readValue(m.getResponseBodyAsStream(), new
TypeReference<List<ApiError>>() {} );
for (ApiError e : errors)
System.out.println(e.errorCode + " " + e.message);
}
}
private static class ApiError {
public String errorCode;
public String message;
public String [] fields;
}
任意の HTTP メソッド名の上書きまたは設定を許可しない HTTP ライブラリを使用している場合、POST 要求を送
信して、クエリ文字列パラメーター _HttpMethod を介して HTTP メソッドを上書きすることができます。こ
の PATCH の例では、PostMethod の行を上書きを使用しない行に置き換えることができます。
PostMethod m = new PostMethod(url + "?_HttpMethod=PATCH");
関連トピック:
sObject Rows
条件付き要求ヘッダー
レコードを削除する
レコードを削除するには、sObject Rowsリソースを使用します。レコード ID を指定し、リソースの DELETE メソッ
ドを使用してレコードを削除します。
49
レコードを削除する例

===== PAGE 60 =====
Account レコードを削除する場合の例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/001D000000INjVe
-H "Authorization: Bearer token" -X DELETE
リクエストボディの例
不要
レスポンスボディの例
戻り値なし
標準オブジェクトレコードから項目値を取得する
レコードから項目値を取得するには、sObject Rows リソースの GET メソッドを使用します。
省略可能な fields パラメーターを使用して取得する項目を指定できます。存在しない項目または項目レベル
セキュリティによってアクセスできなくなっている項目を指定した場合、400 エラー応答が返されます。
fields パラメーターを使用しない場合、要求によってすべての標準項目およびカスタム項目がレコードから
取得されます。これらの取得される項目は、オブジェクトの sObject Describe 要求によって返される項目と同じ
です。項目レベルセキュリティによってアクセスできなくなっている項目はレスポンスボディで返されませ
ん。
次の例では、Account から取引先番号 (AccountNumber) と請求先の郵便番号 (BillingPostalCode) を取得します。
Account レコードの項目から値を取得する例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/001D000000INjVe
?fields=AccountNumber,BillingPostalCode -H "Authorization: Bearer token"
リクエストボディの例
不要
レスポンスボディの例
{
"AccountNumber" : "CD656092",
"BillingPostalCode" : "27215",
}
Salesforce ID を使用して外部オブジェクトレコードから項目値を取得
する
レコードから項目値を取得するには、sObject Rowsリソースを使用します。fields パラメーターに取得する項
目を指定し、リソースの GET メソッドを使用します。
次の例では、Country__c カスタム項目が、データが大量ではない外部データソースに関連付けられた外部オ
ブジェクトから取得されます。
50
標準オブジェクトレコードから項目値を取得する例

===== PAGE 61 =====
Customer 外部オブジェクトの項目から値を取得する例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Customer__x/x01D0000000002RIAQ?fields=Country__c
-H "Authorization: Bearer token"
リクエストボディの例
不要
レスポンスボディの例
{
"attributes" : {
"type" : "Customer__x",
"url" : "/services/data/v60.0/sobjects/Customer__x/x01D0000000002RIAQ"
},
"Country__c" : "Argentina",
"Id" : "x01D0000000002RIAQ"
}
外部 ID 標準項目を使用して外部オブジェクトレコードから項目値を
取得する
レコードから項目値を取得するには、sObject Rowsリソースを使用します。fields パラメーターに取得する項
目を指定し、リソースの GET メソッドを使用します。
次の例では、Country__c カスタム項目が外部オブジェクトから取得されます。id  (CACTU) は Salesforce ID では
ありません。外部オブジェクトの外部 ID 標準項目です。
Customer 外部オブジェクトの項目から値を取得する例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Customer__x/CACTU?fields=Country__c
-H "Authorization: Bearer token"
リクエストボディの例
不要
レスポンスボディの例
{
"attributes" : {
"type" : "Customer__x",
"url" : "/services/data/v60.0/sobjects/Customer__x/CACTU"
},
"Country__c" : "Argentina",
"ExternalId" : "CACTU"
}
外部 ID を使用したレコードの取得
sObject Rows by External ID リソースの GET メソッドを使用して、特定の外部 ID でレコードを取得できます。
51
外部 ID 標準項目を使用して外部オブジェクトレコード
から項目値を取得する
例

===== PAGE 62 =====
次の例では、MerchandiseExtID__c 外部 ID 項目を持つ Merchandise__c カスタムオブジェクトがあると想定します。
外部 ID を使用して Merchandise__c レコードを取得する場合の使用例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Merchandise__c/MerchandiseExtID__c/123
-H "Authorization: Bearer token"
リクエストボディの例
不要
レスポンスボディの例
{
"attributes" : {
"type" : "Merchandise__c",
"url" : "/services/data/v60.0/sobjects/Merchandise__c/a00D0000008oWP8IAM"
},
"Id" : "a00D0000008oWP8IAM",
"OwnerId" : "005D0000001KyEIIA0",
"IsDeleted" : false,
"Name" : "Example Merchandise",
"CreatedDate" : "2012-07-12T17:49:01.000+0000",
"CreatedById" : "005D0000001KyEIIA0",
"LastModifiedDate" : "2012-07-12T17:49:01.000+0000",
"LastModifiedById" : "005D0000001KyEIIA0",
"SystemModstamp" : "2012-07-12T17:49:01.000+0000",
"Description__c" : "Merch with external ID",
"Price__c" : 10.0,
"Total_Inventory__c" : 100.0,
"Distributor__c" : null,
"MerchandiseExtID__c" : 123.0
}
外部 ID を使用してレコードを挿入/更新 (Upsert) する
指定された外部 ID 項目の値に基づいて、レコードを作成するか、既存のレコードを挿入/更新 (Upsert) するに
は、sObject Rows by External ID リソースを使用します。
重要: 可能な場合は、Equality の会社の値に一致するように、含めない用語を変更しました。顧客の実装に
対する影響を回避するために、一部の用語は変更されていません。
• 外部 ID が一致しない場合は、リクエストボディに従って新規レコードが作成されます。
• 外部 ID が一度だけ一致する場合は、リクエストボディに従ってレコードが更新されます。
• 外部 ID が複数回一致する場合は、300 エラーが報告され、レコードは作成も更新もされません。
以降のセクションでは、外部 ID リソースを使用して外部 ID でレコードを取得する方法とレコードを Upsert す
る方法を説明します。
メモ:  REST API では、upsert はレコード ID ではなく外部 ID を使用します。ただし、Apex では、upsert を外部
ID およびレコード ID と共に使用できます。REST API と Apex の両方を使用する場合は、この相違点に注意し
てください。
52
外部 ID を使用してレコードを挿入/更新 (Upsert) する例

===== PAGE 63 =====
新規レコードの Upsert
この例では、PATCH メソッドを使用して新規レコードを挿入します。外部 ID 項目「customExtIdField__c」がすで
に Account に追加されていると想定します。また、customExtIdField 値が 11999 の Account レコードがまだ存在して
いないと想定します。
まだ存在していないレコードを Upsert する例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/customExtIdField__c/11999
-H "Authorization: Bearer token" -H "Content-Type: application/json" -d @newrecord.json
-X PATCH
JSON リクエストボディ newrecord.json ファイルの例
{
"Name" : "California Wheat Corporation",
"Type" : "New Customer"
}
JSON 応答の例
成功を示す応答を次に示します。
{
"id" : "00190000001pPvHAAU",
"errors" : [ ],
"success" : true,
"created": true
}
HTTP 状況コードは 201 (Created) です。
メモ: created パラメーターが応答に表示されるのは、API バージョン 46.0 以降です。それより前の
バージョンでは表示されません。
エラー応答
外部 ID 項目が不正な場合は、次のような応答が返されます。
{
"message" : "The requested resource does not exist",
"errorCode" : "NOT_FOUND"
}
詳細は、「状況コードとエラー応答 (ページ 20)」を参照してください。
Id を外部 ID として使用した新規レコードの挿入
この例では、特殊なケースとして POST メソッドを使用し、Id 項目が外部 ID として処理されるレコードを挿入
します。Id の値は null であるため、要求から除外されます。このパターンは、異なる外部 ID によって複数
のレコードを Upsert するコードを記述していて、個別のリソースを要求したくない場合に役立ちます。Id を
使用する POST は、API バージョン 37.0 以降で使用できます。
53
外部 ID を使用してレコードを挿入/更新 (Upsert) する例

===== PAGE 64 =====
まだ存在していないレコードを挿入する例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/Id -H
"Authorization: Bearer token" -H "Content-Type: application/json" -d @newrecord.json
-X POST
JSON リクエストボディ newrecord.json ファイルの例
{
"Name" : "California Wheat Corporation",
"Type" : "New Customer"
}
JSON 応答の例
成功を示す応答を次に示します。
{
"id" : "001D000000Kv3g5IAB",
"success" : true,
"errors" : [ ],
"created": true
}
HTTP 状況コードは 201 (Created) です。
メモ: created パラメーターが応答に表示されるのは、API バージョン 46.0 以降です。それより前の
バージョンでは表示されません。
既存のレコードの Upsert
この例では、PATCH メソッドを使用して既存のレコードを更新します。外部 ID 項目「customExtIdField__c」がす
でに Account に追加されていて、customExtIdField 値が 11999 の Account レコードがすでに存在すると想定します。
要求では updates.json を使用して更新する項目値を指定します。
既存のレコードを Upsert する例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/customExtIdField__c/11999
-H "Authorization: Bearer token" -H "Content-Type: application/json" -d @updates.json
-X PATCH
JSON リクエストボディ updates.json ファイルの例
{
"BillingCity" : "San Francisco"
}
JSON 応答の例
API バージョン 46.0 以降では、HTTP 状況コードは 200 (OK) で、成功を示す応答は次のとおりです。
{
"id" : "001D000000Kv3g5IAB",
"success" : true,
"errors" : [ ],
54
外部 ID を使用してレコードを挿入/更新 (Upsert) する例

===== PAGE 65 =====
"created": false
}
API バージョン 45.0 以前では、HTTP 状況コードは 204 (No Content) で、レスポンスボディはありません。
エラー応答
外部 ID 値が一意でない場合、HTTP 状況コード 300 が返され、さらにクエリに一致したレコードのリストが
返されます。エラーについての詳細は、「状況コードとエラー応答 (ページ 20)」を参照してください。
外部 ID 項目が存在しない場合、エラーメッセージとコードが返されます。
{
"message" : "The requested resource does not exist",
"errorCode" : "NOT_FOUND"
}
レコードの Upsert と外部 ID との関連付け
オブジェクトでリレーションを使用して他のオブジェクトを参照する場合、REST API を使用し、レコードの挿
入/更新の両方を行うことができ、さらに外部 ID を使用して別のオブジェクトの参照できます。
次の例では、レコードを作成し、外部 ID を介して親レコードに関連付けます。次の条件を想定します。
• Merchandise__c カスタムオブジェクトには、外部 ID 項目 MerchandiseExtID__c がある。
• Line_Item__c カスタムオブジェクトには、外部 ID 項目 LineItemExtID__c と、Merchandise__c へのリレーションが
ある。
• MerchandiseExtID__c 値が 123 の Merchandise__c レコードが存在する。
• LineItemExtID__c 値が 456 の Line_Item__c レコードは存在しない。これは作成され、Merchandise__c レコードに
関連付けられるレコードです。
レコードを Upsert して関連オブジェクトを参照する例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Line_Item__c/LineItemExtID__c/456
-H "Authorization: Bearer token" -H "Content-Type: application/json" -d @new.json -X
PATCH
JSON リクエストボディ new.json ファイルの例
関連する Merchandise__c レコードは、Merchandise__c の外部 ID 項目を使用して参照されます。
{
"Name" : "LineItemCreatedViaExtID",
"Merchandise__r" :
{
"MerchandiseExtID__c" : 123
}
}
JSON 応答の例
成功を示す応答を次に示します。
{
"id" : "a02D0000006YUHrIAO",
"errors" : [ ],
55
外部 ID を使用してレコードを挿入/更新 (Upsert) する例

===== PAGE 66 =====
"success" : true,
"created": true
}
HTTP 状況コードは 201 (Created) です。
メモ: created パラメーターが応答に表示されるのは、API バージョン 46.0 以降です。それより前の
バージョンでは表示されません。
エラー応答
外部 ID 値が一意でない場合、HTTP 状況コード 300 が返され、さらにクエリに一致したレコードのリストが
返されます。エラーについての詳細は、「状況コードとエラー応答 (ページ 20)」を参照してください。
外部 ID 項目が存在しない場合、エラーメッセージとコードが返されます。
{
"message" : "The requested resource does not exist",
"errorCode" : "NOT_FOUND"
}
既存のレコードの更新には次の方法を使用することもできます。たとえば、上記の例の Line_Item__c を作成し
た場合、別の要求を使用して関連する Merchandise__c の更新を試みることができます。
レコードを更新する例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Line_Item__c/LineItemExtID__c/456
-H "Authorization: Bearer token" -H "Content-Type: application/json" -d @updates.json
-X PATCH
JSON リクエストボディ updates.json ファイルの例
ここでは、MerchandiseExtID__c 値が 333 の別の Merchandise__c レコードが存在すると想定します。
{
"Merchandise__r" :
{
"MerchandiseExtID__c" : 333
}
}
JSON 応答の例
API バージョン 46.0 以降では、HTTP 状況コードは 200 (OK) で、成功を示す応答は次のとおりです。
{
"id" : "001D000000Kv3g5IAB",
"success" : true,
"errors" : [ ],
"created": false
}
API バージョン 45.0 以前では、HTTP 状況コードは 204 (No Content) で、レスポンスボディはありません。
56
外部 ID を使用してレコードを挿入/更新 (Upsert) する例

===== PAGE 67 =====
リレーション種別が主従関係で、リレーションが親の変更を許可しないように設定されている場合、親の外部
ID を更新しようとすると、HTTP 状況コード 400 エラーとエラーコード INVALID_FIELD_FOR_INSERT_UPDATE が返さ
れます。
関連トピック:
sObject Rows by External ID
フレンドリー URL を使用したリレーションのトラバース
標準およびカスタムオブジェクトのリレーション項目をトラバースするには、sObject Relationship リソースを使
用して、フレンドリー URL を作成します。この方法では、リレーションによって関連付けられたレコードに直
接アクセスできます。フレンドリー URL を使用する方が、リレーション項目からオブジェクト ID を取得し、関
連付けられたオブジェクト ID レコードを調べて、レコードにアクセスするよりも簡単です。
重要: 可能な場合は、Equality の会社の値に一致するように、含めない用語を変更しました。顧客の実装に
対する影響を回避するために、一部の用語は変更されていません。
リレーション名は、リレーションの方向 (親から子または子から親) と関連オブジェクトの名前によって決まる
特定の規則に従います。規則については、『SOQL および SOSL リファレンス』の「リレーション名について」
を参照してください。
1 つの REST API コールで行うことができるリレーションのトラバース数には制限があります。これらの制限は、
『SOQL および SOSL リファレンス』の「リレーションクエリ制限について」に記載されている SOQL の制限と同
じです。リレーションをトラバースする場合は、次の制限に注意してください。
• 子-親リレーションを指定する場合、5 つ以下のレベルをトラバースできます。次の例では、2 つの子-親リ
レーションをトラバースします。
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/ChildOfChild__c/record
id/Child__r/ParentOfChild__r
• 親-子リレーションを指定する場合、1 つ以下のレベルをトラバースできます。次の例では、1 つの親-子リ
レーションをトラバースします。
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/ParentOfChild__c/record
id/Child__r
標準オブジェクトのトラバース
標準オブジェクト Contact には、標準オブジェクト Account に対するリレーション項目が含まれています。次の
例では、Contact レコードに関連する Account レコードを取得します。
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Contact/0035e00000PiemmAAB/Account
-H "Authorization: Bearer token"
標準オブジェクトのリレーションをトラバースする場合のリクエストボディの例
不要
57
フレンドリー URL を使用したリレーションのトラバース例

===== PAGE 68 =====
標準オブジェクトの単純なリレーションをトラバースする場合のレスポンスボディの例
{
"attributes": {
"type": "Account",
"url": "/services/data/v60.0/sobjects/Account/0015e00000TwULCAA3"
},
"Id": "0015e00000TwULCAA3",
"IsDeleted": false,
"Name": "relationshipAccountName",
"PhotoUrl": "/services/images/photo/0015e00000TwULCAA3",
"OwnerId": "0055e000003E8ooAAC",
"CreatedDate": "2021-11-06T17:38:40.000+0000",
"CreatedById": "0055e000003E8ooAAC",
"LastModifiedDate": "2021-11-06T17:38:40.000+0000",
"LastModifiedById": "0055e000003E8ooAAC",
"SystemModstamp": "2021-11-06T17:38:40.000+0000",
"LastActivityDate": null,
"LastViewedDate": "2021-11-06T17:40:50.000+0000",
"LastReferencedDate": "2021-11-06T17:40:50.000+0000"
}
単純なリレーションをトラバースする場合の例
Merchandise__c という名前のこのカスタムオブジェクトには、子 Distributor__c カスタムオブジェクトへの参
照関係項目が含まれています。次の例では、Merchandise__c レコードに関連する Distributor__c レコードを取
得します。
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Merchandise__c/a01D000000INjVe/Distributor__r
-H "Authorization: Bearer token"
単純なリレーションをトラバースする場合のリクエストボディの例
不要
単純なリレーションをトラバースする場合のレスポンスボディの例
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
"Location__c" : "San Francisco"
}
58
フレンドリー URL を使用したリレーションのトラバース例

===== PAGE 69 =====
リレーション名に関連付けられている関連レコードがない場合、リレーションをトラバースできないため、
REST API コールは失敗します。Merchandise__c レコードの Distributor__c 項目が null に設定されている場合、前
の例を使用すると、GET コールで 404 エラー応答が返されます。
リレーションクエリの制限を超えない限り、1 つの REST API コールで同じリレーション階層内の複数のリレー
ションをトラバースできます。Line_Item__c カスタムオブジェクトに Merchandise__c カスタムオブジェクトに対
する子リレーションがあり、Merchandise__c に子 Distributor__c カスタムオブジェクトもある場合、次のように
Line_Item__c レコードから Distributor__c レコードにアクセスできます。
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Line_Item__c/a02D0000006YL7XIAW/Merchandise__r/Distributor__r
-H "Authorization: Bearer token"
1 つのレコードに解決されるリレーションをトラバースする場合、PATCH および DELETE メソッドもサポートさ
れます。PATCH メソッドを使用して、関連レコードを更新できます。
PATCH を使用してリレーションレコードを更新する場合の例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Merchandise__c/a01D000000INjVe/Distributor__r
-H "Authorization: Bearer token" -d @update_info.json -X PATCH
update_info.json に含まれているリレーションレコードを更新する場合の JSON リクエストボディの例
{
"Location__c" : "New York"
}
リレーションレコードを更新する場合のレスポンスボディの例
戻り値なし
DELETE メソッドを使用して、関連レコードを削除できます。
DELETE を使用してリレーションレコードを削除する場合の例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Merchandise__c/a01D000000INjVe/Distributor__r
-H "Authorization: Bearer token" -X DELETE
リレーションレコードを削除する場合のレスポンスボディの例
不要
リレーションレコードを更新する場合のレスポンスボディの例
戻り値なし
複数のレコードのあるリレーションのトラバース
複数のレコードのあるリレーションをトラバースして、一連のレコードを含む応答を取得できます。複数のレ
コードに解決されるリレーションの場合、GET メソッドのみがサポートされます。
59
フレンドリー URL を使用したリレーションのトラバース例

===== PAGE 70 =====
複数のレコードのあるリレーションをトラバースする場合の例
Merchandise__c という名前のカスタムオブジェクトに Line_Item__c カスタムオブジェクトに対する主従関係
項目が含まれている場合、次の例では Merchandise__c レコードに関連する一連の Line_Item__c レコードが取
得されます。
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Merchandise__c/a01D000000INjVe/Line_Items__r
-H "Authorization: Bearer token"
複数のレコードのあるリレーションをトラバースする場合のリクエストボディの例
不要
複数のレコードのあるリレーションをトラバースする場合のレスポンスボディの例
この例の場合、2 つの Line_Item__c レコードが取得されています。
{
"done" : true,
"totalSize" : 2,
"records" :
[
{
"attributes" :
{
"type" : "Line_Item__c",
"url" : "/services/data/v60.0/sobjects/Line_Item__c/a02D0000006YL7XIAW"
},
"Id" : "a02D0000006YL7XIAW",
"IsDeleted" : false,
"Name" : "LineItem1",
"CreatedDate" : "2011-12-16T17:44:07.000+0000",
"CreatedById" : "005D0000001KyEIIA0",
"LastModifiedDate" : "2011-12-16T17:44:07.000+0000",
"LastModifiedById" : "005D0000001KyEIIA0",
"SystemModstamp" : "2011-12-16T17:44:07.000+0000",
"Unit_Price__c" : 9.75,
"Units_Sold__c" : 10.0,
"Merchandise__c" : "a00D0000008oLnXIAU",
"Invoice_Statement__c" : "a01D000000D85hkIAB"
},
{
"attributes" :
{
"type" : "Line_Item__c",
"url" : "/services/data/v60.0/sobjects/Line_Item__c/a02D0000006YL7YIAW"
},
"Id" : "a02D0000006YL7YIAW",
"IsDeleted" : false,
"Name" : "LineItem2",
"CreatedDate" : "2011-12-16T18:53:59.000+0000",
"CreatedById" : "005D0000001KyEIIA0",
"LastModifiedDate" : "2011-12-16T18:53:59.000+0000",
"LastModifiedById" : "005D0000001KyEIIA0",
60
フレンドリー URL を使用したリレーションのトラバース例

===== PAGE 71 =====
"SystemModstamp" : "2011-12-16T18:54:00.000+0000",
"Unit_Price__c" : 8.5,
"Units_Sold__c" : 8.0,
"Merchandise__c" : "a00D0000008oLnXIAU",
"Invoice_Statement__c" : "a01D000000D85hkIAB"
}
]
}
結果データの逐次化された構造は、REST API を使用して SOQL クエリを実行した結果データと同じ形式です。
REST API を使用した SOQL クエリの実行についての詳細は、「Query」 (ページ 322)を参照してください。
リレーション名に関連付けられている関連レコードがない場合、REST API コールで 200 応答が返され、レスポン
スボディにレコードデータはありません。この結果は、1 つのレコードに対する空のリレーションをトラバー
スした場合の結果 (404 エラー応答が返される) とは異なります。1 つのレコードの場合、PATCH または DELETE メ
ソッドで使用できる REST リソースに解決されるため、この動作が発生します。一方、複数のレコードの場合
は照会することしかできません。
複数のレコードのあるリレーションの最初の GET 要求クエリで結果の一部のみが返される場合、応答の最後に
nextRecordsUrl という項目が含まれます。たとえば、応答の最後で次のような項目が取得されます。
"nextRecordsUrl" : "/services/data/v60.0/query/01gD0000002HU6KIAW-2000"
インスタンスおよびセッション情報と共に提供された URL を使用してレコードの次のバッチを要求し、すべて
のレコードが取得されるまでこの操作を繰り返すことができます。これらの要求では nextRecordsUrl が使
用され、パラメーターは含まれません。レコードの最後のバッチには nextRecordsUrl 項目が含まれます。
残りの結果を取得する場合の使用例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/query/01gD0000002HU6KIAW-2000
-H "Authorization: Bearer token"
残りの結果を取得する場合のリクエストボディの例
不要
残りの結果を取得する場合のレスポンスボディの例
{
"done" : true,
"totalSize" : 3200,
"records" : [...]
}
結果項目の絞り込み
リレーションのトラバースでレコードを取得する場合、必要に応じて fields パラメーターを使用して、レ
コード項目のサブセットのみが返されるように指定できます。複数の項目はカンマで区切られます。次の例で
は、Merchandise__c レコードに関連付けられた Distributor__c レコードから Location__c 項目のみを取得します。
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Merchandise__c/a01D000000INjVe/Distributor__r?fields=Location__c
-H "Authorization: Bearer token"
61
フレンドリー URL を使用したリレーションのトラバース例

===== PAGE 72 =====
JSON 応答データは、次のようになります。
{
"attributes" :
{
"type" : "Distributor__c",
"url" : "/services/data/v60.0/sobjects/Distributor__c/a03D0000003DUhhIAG"
},
"Location__c" : "Chicago",
}
同様に、複数のレコードになる要求の場合、項目のリストを使用して、レコードセットで返される項目を指定
できます。たとえば、2 つの Line_Item__c レコードに関連付けられたリレーションがあるとします。これらの
レコードから Name 項目と Units_Sold__c 項目のみを取得する場合、次のコールを使用できます。
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Merchandise__c/a01D000000INjVe/Line_Items__r?fields=Name,Units_Sold__c
-H "Authorization: Bearer token"
応答データは、次のようになります。
{
"done" : true,
"totalSize" : 2,
"records" :
[
{
"attributes" :
{
"type" : "Line_Item__c",
"url" : "/services/data/v60.0/sobjects/Line_Item__c/a02D0000006YL7XIAW"
},
"Name" : "LineItem1",
"Units_Sold__c" : 10.0
},
{
"attributes" :
{
"type" : "Line_Item__c",
"url" : "/services/data/v60.0/sobjects/Line_Item__c/a02D0000006YL7YIAW"
},
"Name" : "LineItem2",
"Units_Sold__c" : 8.0
}
]
}
項目パラメーターセットにリストされている項目が有効なユーザーに表示されない場合、REST API コールは失
敗します。前の例では、Units_Sold_c 項目が項目レベルセキュリティで有効なユーザーに表示されない場合、
コールで 400 エラー応答が返されます。
62
フレンドリー URL を使用したリレーションのトラバース例

===== PAGE 73 =====
特定の時間枠に削除されたレコードのリストの取得
指定されたオブジェクトの削除されたレコードのリストを取得するには、sObject Get Deleted リソースを使用し
ます。特定のオブジェクトのレコードが削除された日時の範囲を指定します。削除されたレコードは削除ログ
(定期的に消去される) に書き込まれ、sObject 行、クエリなどのほとんどの操作対象から除外されます (ただし、
QueryAll では削除されたレコードが結果に含まれます)。
2013 年 5 月 5 日～ 2013 年 5 月 10 日に削除された Merchandise__c レコードのリストを取得する場合の使用例
curl https://MyDomainName.my/services/data/v60.0/sobjects/Merchandise__c/deleted/
?start=2013-05-05T00%3A00%3A00%2B00%3A00&end=2013-05-10T00%3A00%3A00%2B00%3A00 -H
"Authorization: Bearer token"
リクエストボディの例
不要
JSON レスポンスボディの例
{
"deletedRecords" :
[
{
"id" : "a00D0000008pQRAIA2",
"deletedDate" : "2013-05-07T22:07:19.000+0000"
}
],
"earliestDateAvailable" : "2013-05-03T15:57:00.000+0000",
"latestDateCovered" : "2013-05-08T21:20:00.000+0000"
}
XML レスポンスボディの例
<?xml version="1.0" encoding="UTF-8"?>
<Merchandise__c>
<deletedRecords>
<deletedDate>2013-05-07T22:07:19.000Z</deletedDate>
<id>a00D0000008pQRAIA2</id>
</deletedRecords>
<earliestDateAvailable>2013-05-03T15:57:00.000Z</earliestDateAvailable>
<latestDateCovered>2013-05-08T21:20:00.000Z</latestDateCovered>
</Merchandise__c>
特定の時間枠に更新されたレコードのリストの取得
指定されたオブジェクトの更新 (変更または追加) されたレコードのリストを取得するには、sObject Get Updated
リソースを使用します。特定のオブジェクトのレコードが更新された日時の範囲を指定します。
2013 年 5 月 6 日～ 2013 年 5 月 10 日に更新された Merchandise__c レコードのリストを取得する場合の使用例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Merchandise__c/updated/
?start=2013-05-06T00%3A00%3A00%2B00%3A00&end=2013-05-10T00%3A00%3A00%2B00%3A00 -H
"Authorization: Bearer token"
63
特定の時間枠に削除されたレコードのリストの取得例

===== PAGE 74 =====
リクエストボディの例
不要
JSON レスポンスボディの例
{
"ids" :
[
"a00D0000008pQR5IAM",
"a00D0000008pQRGIA2",
"a00D0000008pQRFIA2"
],
"latestDateCovered" : "2013-05-08T21:20:00.000+0000"
}
XML レスポンスボディの例
<?xml version="1.0" encoding="UTF-8"?>
<Merchandise__c>
<ids>a00D0000008pQR5IAM</ids>
<ids>a00D0000008pQRGIA2</ids>
<ids>a00D0000008pQRFIA2</ids>
<latestDateCovered>2013-05-08T21:20:00.000Z</latestDateCovered>
</Merchandise__c>
Lightning Experience の一連の行動の削除
HTTP DELETE メソッドを使用して、一連の IsRecurrence2 行動から 1 つ以上を削除します。1 つの行動、特定の行動
以降すべての行動、一連の行動全体を削除できます。
一連の行動から 1 つの行動を削除する
行動レコードを削除するには、sObject Rows (ページ156)リソースを使用します。一連の行動から 1 つの行動を削
除するには、行動 ID を指定し、リソースの DELETE メソッド (ページ 49)を使用してレコードを削除します。
一連の行動から複数またはすべての行動を削除する
一連の行動から特定の行動以降をすべて削除するには、行動 ID を指定し、リソースの DELETE メソッドを使用
してレコードを削除します。このメソッドをコールするとき、IsRecurrence2 が true、IsRecurrence2Exclusion が false
であることが必要です。
一連の行動全体を削除するには、一連の行動の最初の行動 ID を指定し、リソースの DELETE メソッドを使用し
てレコードを削除します。
一連の行動から複数またはすべての行動を削除する例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Event/00Uxx0000000000/fromThisEventOnwards
-H "Authorization: Bearer token" -X DELETE
64
Lightning Experience の一連の行動の削除例

===== PAGE 75 =====
リクエストボディの例
None needed
行動が正常に削除された場合のレスポンスボディの例
{
success: We’re deleting the selected events from the series. Wait for all events to be
removed.
}
考慮事項
特定の行動以降を削除する場合は、以下の行動からのコールはサポートされません。
• Recurrence2PatternStartDate の元の値より前の行動。
• 子行動として定義されている行動。
Salesforce 外から供給された一連の行動と、最初の行動の行動 ID が利用できない場合、一連のすべての行動を削
除できません。代わりに、特定の行動以降の行動を削除します。
検索とクエリの使用
このセクションの例では、REST API リソースを使用して、Salesforce Object Search Language (SOSL)、Salesforce Object
Query Language (SOQL)、およびその他の検索 API を使用したレコードの検索やクエリを実行します。SOSL および
SOQL についての詳細は、『SOQL および SOSL リファレンス』を参照してください。
このセクションの内容:
SOQL クエリを実行する
Query リソースを使用して、すべての結果を 1 つの応答で返す SOQL クエリを実行するか、必要に応じて結
果の一部と、ロケーターを返す SOQL クエリを実行します。そのロケーターを使えば残りの結果も取得でき
ます。
削除された項目を含む SOQL クエリを実行する
merge または delete で削除されたレコードの情報を含む SOQL クエリを実行するには、QueryAll リソースを使
用します。Query リソースでは削除された項目が自動的に除外されるため、Query ではなく QueryAll を使用し
ます。
クエリのパフォーマンスに関するフィードバックを取得する (ベータ)
Salesforce でクエリ、レポート、またはリストビューがどのように実行されるかについてフィードバックを
取得するには、explain パラメーターを指定して Query リソースを使用します。Salesforce では、各クエリ
を分析して、クエリ結果を取得するための最適な手段が検索されます。クエリおよびクエリ条件に応じて、
Salesforce ではインデックスまたは内部最適化が使用されます。クエリを実際に実行せずに Salesforce でクエ
リがどのように最適化されるかについての詳細を返すには、explain パラメーターを使用します。応答に
基づいて、クエリをセレクティブにするための条件を追加するなど、クエリのパフォーマンスを細かく調
整するかどうかを決定できます。
65
検索とクエリの使用例

===== PAGE 76 =====
文字列を検索する
SOSL 検索を実行するには、Search リソースを使用し、SOSL を使用しない簡単な RESTful 検索を実行するには、
Parameterized Search リソースを使用します。
デフォルトの検索範囲と検索順序の取得
Search Scope and Order リソースを使用して、ユーザーの検索結果ページの固定表示オブジェクトを含め、ロ
グインユーザーのデフォルトの検索範囲と検索順序を取得します。
オブジェクトの検索結果レイアウトの取得
Search Result Layouts リソースを使用して、クエリ文字列で指定された各オブジェクトの検索結果レイアウト
の設定を取得します。
関連項目の表示
関連レコードのリストを取得するには、Relevant Items リソースを使用します。
SOQL クエリを実行する
Query リソースを使用して、すべての結果を 1 つの応答で返す SOQL クエリを実行するか、必要に応じて結果の
一部と、ロケーターを返す SOQL クエリを実行します。そのロケーターを使えば残りの結果も取得できます。
次のクエリは、すべての Account レコードを対象に name 項目の値を要求します。
クエリを実行する場合の使用例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/query/?q=SELECT+name+from+Account
-H "Authorization: Bearer token"
クエリを実行する場合のリクエストボディの例
不要
クエリを実行する場合のレスポンスボディの例
{
"done" : true,
"totalSize" : 14,
"records" :
[
{
"attributes" :
{
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001D000000IRFmaIAH"
},
"Name" : "Test 1"
},
{
"attributes" :
{
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001D000000IomazIAB"
},
"Name" : "Test 2"
},
66
SOQL クエリを実行する例

===== PAGE 77 =====
...
]
}
SOQL クエリの残りの結果の取得
最初のクエリで結果の一部のみを返す場合、応答の最後に、次の nextRecordsUrl という項目が含まれま
す。
"nextRecordsUrl" : "/services/data/v60.0/query/01gD0000002HU6KIAW-2000"
この場合、レコードの次のバッチを要求し、すべてのレコードが取得されるまでこの操作を繰り返します。こ
れらの要求は nextRecordsUrl を使用し、パラメーターを含みません。
クエリの残りの結果を取得する場合の使用例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/query/01gD0000002HU6KIAW-2000
-H "Authorization: Bearer token"
クエリの残りの結果を取得する場合のリクエストボディの例
不要
クエリの残りの結果を取得する場合のレスポンスボディの例
{
"done" : true,
"totalSize" : 3214,
"records" : [...]
}
削除された項目を含む SOQL クエリを実行する
merge または delete で削除されたレコードの情報を含む SOQL クエリを実行するには、QueryAll リソースを使用し
ます。Query リソースでは削除された項目が自動的に除外されるため、Query ではなく QueryAll を使用します。
次のクエリは、削除された Merchandise__c レコードが 1 つある組織で、削除されたすべての Merchandise__c レ
コードを対象に Name 項目の値を要求します。同じクエリに QueryAll ではなく Query を使用した場合、レコード
は返されません。これは、Query では削除されたレコードがすべて結果セットから自動的に除外されるためで
す。
削除された Merchandise__c レコードのクエリを実行する場合の使用例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/queryAll/?q=SELECT+Name+from+Merchandise__c+WHERE+isDeleted+=+TRUE
-H "Authorization: Bearer token"
クエリを実行する場合のリクエストボディの例
不要
67
削除された項目を含む SOQL クエリを実行する例

===== PAGE 78 =====
クエリを実行する場合のレスポンスボディの例
{
"done" : true,
"totalSize" : 1,
"records" :
[
{
"attributes" :
{
"type" : "Merchandise__c",
"url" : "/services/data/v60.0/sobjects/Merchandise__c/a00D0000008pQRAIX2"
},
"Name" : "Merchandise 1"
},
]
}
SOQL クエリの残りの結果の取得
最初のクエリで結果の一部のみを返す場合、応答の最後に nextRecordsUrl という項目が含まれます。たと
えば、クエリの最後に次の属性があるとします。
"nextRecordsUrl" : "/services/data/v60.0/query/01gD0000002HU6KIAW-2000"
この場合、レコードの次のバッチを要求し、すべてのレコードが取得されるまでこの操作を繰り返します。こ
れらの要求は nextRecordsUrl を使用し、パラメーターを含みません。
nextRecordsUrl の URL に query が指定されている場合でも、最初の QueryAll 要求の残りの結果が提供され
ます。残りの結果には、最初のクエリに一致した削除されたレコードが含まれます。
残りの結果を取得する場合の使用例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/query/01gD0000002HU6KIAW-2000
-H "Authorization: Bearer token"
残りの結果を取得する場合のリクエストボディの例
不要
残りの結果を取得する場合のレスポンスボディの例
{
"done" : true,
"totalSize" : 3214,
"records" : [...]
}
68
削除された項目を含む SOQL クエリを実行する例

===== PAGE 79 =====
クエリのパフォーマンスに関するフィードバックを取得する (ベータ)
Salesforce でクエリ、レポート、またはリストビューがどのように実行されるかについてフィードバックを取得
するには、explain パラメーターを指定して Query リソースを使用します。Salesforce では、各クエリを分析し
て、クエリ結果を取得するための最適な手段が検索されます。クエリおよびクエリ条件に応じて、Salesforce で
はインデックスまたは内部最適化が使用されます。クエリを実際に実行せずに Salesforce でクエリがどのように
最適化されるかについての詳細を返すには、explain パラメーターを使用します。応答に基づいて、クエリ
をセレクティブにするための条件を追加するなど、クエリのパフォーマンスを細かく調整するかどうかを決定
できます。
メモ: この機能はベータサービスです。ベータサービスはお客様独自の裁量で試行するものとします。
ベータ機能の使用には、「Agreements and Terms」に記載されたベータサービス規約が適用されます。
応答には、最も最適なものから順に並び替えられた、1 つ以上のクエリ実行プランが含まれます。クエリ、レ
ポート、またはリストビューの実行時には最も最適なプランが使用されます。
explain を使用するときに返される項目についての詳細は、「Query Options ヘッダー」の explain パラメー
ターを参照してください。クエリをセレクティブにする方法についての詳細は、『Apex 開発者ガイド』の「非
常に大きい SOQL クエリの処理」を参照してください。
例: クエリのパフォーマンスに関するフィードバック
次のパフォーマンスフィードバッククエリでは、Merchandise__c を使用します。
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/query/?explain=
SELECT+Name+FROM+Merchandise__c+WHERE+CreatedDate+=+TODAY+AND+Price__c+>+10.0
パフォーマンスフィードバッククエリのレスポンスボディは、次のようになります。
{
"plans" : [ {
"cardinality" : 1,
"fields" : [ "CreatedDate" ],
"leadingOperationType" : "Index",
"notes" : [ {
"description" : "Not considering filter for optimization because unindexed",
"fields" : [ "IsDeleted" ],
"tableEnumOrId" : "Merchandise__c"
} ],
"relativeCost" : 0.0,
"sobjectCardinality" : 3,
"sobjectType" : "Merchandise__c"
}, {
"cardinality" : 1,
"fields" : [ ],
"leadingOperationType" : "TableScan",
"notes" : [ {
"description" : "Not considering filter for optimization because unindexed",
"fields" : [ "IsDeleted" ],
"tableEnumOrId" : "Merchandise__c"
} ],
"relativeCost" : 0.65,
"sobjectCardinality" : 3,
69
クエリのパフォーマンスに関するフィードバックを取得
する (ベータ)
例

===== PAGE 80 =====
"sobjectType" : "Merchandise__c"
} ]
}
この応答は、このクエリに対して 2 つの可能な実行プランが Salesforce で検出されたことを示しています。最初
のプランでは、このクエリのパフォーマンスを向上するために CreatedDate インデックス項目が使用されます。
2 つ目のプランでは、インデックスを使用せずにすべてのレコードがスキャンされます。クエリが実行される
と、最初のプランが使用されます。どちらのプランでも、IsDeleted 項目のインデックスが作成されていないた
め、削除済みとマークされているレコードを除外する場合に使用される 2 つ目の最適化がありません。
文字列を検索する
SOSL 検索を実行するには、Search リソースを使用し、SOSL を使用しない簡単な RESTful 検索を実行するには、
Parameterized Search リソースを使用します。
GET メソッドを使用した SOSL 検索の例
次の例では、Acme の SOSL 検索を実行します。この例の検索文字列は URL 符号化されている必要があります。
使用例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/search/?q=FIND+%7BAcme%7D
-H "Authorization: Bearer token"
リクエストボディの例
不要
レスポンスボディの例
{
"searchRecords" : [ {
"attributes" : {
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001D000000IqhSLIAZ"
},
"Id" : "001D000000IqhSLIAZ",
}, {
"attributes" : {
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001D000000IomazIAB"
},
"Id" : "001D000000IomazIAB",
} ]
}
GET メソッドを使用した、パラメーター化された検索の例
次の例では、Acme のパラメーター化された検索を実行します。この例の検索文字列は URL 符号化されている
必要があります。
70
文字列を検索する例

===== PAGE 81 =====
使用例
Acme を含むすべての結果のグローバル検索
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/parameterizedSearch/?q=Acme
-H "Authorization: Bearer token"
Acme を含む結果の取引先検索 (ID 項目と名前項目が返される)
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/parameterizedSearch/?q=Acme&sobject=Account&Account.fields=id,name&Account.limit=10
-H "Authorization: Bearer token"
リクエストボディの例
不要
レスポンスボディの例
{
"searchRecords" : [ {
"attributes" : {
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001D000000IqhSLIAZ"
},
"Id" : "001D000000IqhSLIAZ"
}, {
"attributes" : {
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001D000000IomazIAB"
},
"Id" : "001D000000IomazIAB"
} ]
}
metadata パラメーターを含むレスポンスボディの例
メモ: metadata パラメーターが返されるのは、要求で metadata=LABELS が指定されている場合の
みです。
{
"searchRecords" : [ {
"attributes" : {
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001D000000IqhSLIAZ"
},
"Id" : "001D000000IqhSLIAZ",
}, {
"attributes" : {
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001D000000IomazIAB"
},
"Id" : "001D000000IomazIAB",
} ],
"metadata" : {
"entityetadata" : [ {
71
文字列を検索する例

===== PAGE 82 =====
"entityName" : "Account",
"fieldMetadata" : [ {
"name" : "Name",
"label" : "Account Name"
} ]
} ]
}
}
POST メソッドを使用した、パラメーター化された検索の例
使用可能なすべての検索機能にアクセスする POST メソッドを使用してパラメーター化された検索を実行しま
す。
使用例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/parameterizedSearch
"Authorization: Bearer token" -H "Content-Type: application/json” -d "@search.json”
リクエストボディの例
不要
JSON ファイルの例
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
レスポンスボディの例
{
"searchRecords" : [ {
"attributes" : {
"type" : "Contact",
"url" : "/services/data/v60.0/sobjects/Contact/003xx000004TraiAAC"
},
"Id" : "003xx000004TraiAAC",
"FirstName" : "Smith",
"LastName" : "Johnson"
}, {
"attributes" : {
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001xx000003DHXnAAO"
},
"Id" : "001xx000003DHXnAAO",
72
文字列を検索する例

===== PAGE 83 =====
"NumberOfEmployees" : 100
} ]
}
関連トピック:
Search
パラメーター化された検索
デフォルトの検索範囲と検索順序の取得
Search Scope and Orderリソースを使用して、ユーザーの検索結果ページの固定表示オブジェクトを含め、ログイ
ンユーザーのデフォルトの検索範囲と検索順序を取得します。
次の例では、ログインユーザーのデフォルトのグローバル検索範囲は、サイト、アイデア、ケース、商談、取
引先、およびユーザーオブジェクトがレスポンスボディに返される順序で構成されます。
使用例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/search/scopeOrder -H
"Authorization: Bearer token"
リクエストボディの例
不要
レスポンスボディの例
[
{
"type":"Site",
"url":"/services/data/v60.0/sobjects/Site/describe"
},
{
"type":"Idea",
"url":"/services/data/v60.0/sobjects/Idea/describe"
},
{
"type":"Case",
"url":"/services/data/v60.0/sobjects/Case/describe"
},
{
"type":"Opportunity",
"url":"/services/data/v60.0/sobjects/Opportunity/describe"
},
{
"type":"Account",
"url":"/services/data/v60.0/sobjects/Account/describe"
},
{
"type":"User",
"url":"/services/data/v60.0/sobjects/User/describe"
}
]
73
デフォルトの検索範囲と検索順序の取得例

===== PAGE 84 =====
オブジェクトの検索結果レイアウトの取得
Search Result Layoutsリソースを使用して、クエリ文字列で指定された各オブジェクトの検索結果レイアウトの設
定を取得します。
使用例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/search/layout/?q=Account,Contact,Lead,Asset
"Authorization: Bearer token"
リクエストボディの例
不要
レスポンスボディの例
[ { "label" : "Search Results",
"limitRows" : 25,
"searchColumns" : [ { "field" : "Account.Name",
"format" : null,
"label" : "Account Name",
"name" : "Name"
},
{ "field" : "Account.Site",
"format" : null,
"label" : "Account Site",
"name" : "Site"
},
{ "field" : "Account.Phone",
"format" : null,
"label" : "Phone",
"name" : "Phone"
},
{ "field" : "User.Alias",
"format" : null,
"label" : "Account Owner Alias",
"name" : "Owner.Alias"
}
]
},
{ "label" : "Search Results",
"limitRows" : 25,
"searchColumns" : [ { "field" : "Contact.Name",
"format" : null,
"label" : "Name",
"name" : "Name"
},
{ "field" : "Account.Name",
"format" : null,
"label" : "Account Name",
"name" : "Account.Name"
},
{ "field" : "Account.Site",
"format" : null,
"label" : "Account Site",
74
オブジェクトの検索結果レイアウトの取得例

===== PAGE 85 =====
"name" : "Account.Site"
},
{ "field" : "Contact.Phone",
"format" : null,
"label" : "Phone",
"name" : "Phone"
},
{ "field" : "Contact.Email",
"format" : null,
"label" : "Email",
"name" : "Email"
},
{ "field" : "User.Alias",
"format" : null,
"label" : "Contact Owner Alias",
"name" : "Owner.Alias"
}
]
},
{ "label" : "Search Results",
"limitRows" : 25,
"searchColumns" : [ { "field" : "Lead.Name",
"format" : null,
"label" : "Name",
"name" : "Name"
},
{ "field" : "Lead.Title",
"format" : null,
"label" : "Title",
"name" : "Title"
},
{ "field" : "Lead.Phone",
"format" : null,
"label" : "Phone",
"name" : "Phone"
},
{ "field" : "Lead.Company",
"format" : null,
"label" : "Company",
"name" : "Company"
},
{ "field" : "Lead.Email",
"format" : null,
"label" : "Email",
"name" : "Email"
},
{ "field" : "Lead.Status",
"format" : null,
"label" : "Lead Status",
"name" : "toLabel(Status)"
},
{ "field" : "Name.Alias",
"format" : null,
"label" : "Owner Alias",
75
オブジェクトの検索結果レイアウトの取得例

===== PAGE 86 =====
"name" : "Owner.Alias"
}
]
},
]
関連項目の表示
関連レコードのリストを取得するには、Relevant Items リソースを使用します。
現在のユーザーの最も関連性の高いレコードリストを取得する場合の使用例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/relevantItems
-H "Authorization: Bearer token"
リクエストボディの例
不要
レスポンスボディの例
[ {
"apiName" : "Contact",
"key" : "003",
"label" : "Contacts",
"lastUpdatedId" : "135866748",
"recordIds" : [ "003xx000004TxBA" ]
}, { "apiName" : "Account",
"key" : "001",
"label" : "Accounts",
"lastUpdatedId" : "193640553",
"recordIds" : [ "001xx000003DWsT" ]
}, {
"apiName" : "User",
"key" : "005",
"label" : "Users",
"lastUpdatedId" : "-199920321",
"recordIds" : [ "005xx000001Svqw", "005xx000001SvwK", "005xx000001SvwA" ]
}, { "apiName" : "Case",
"key" : "069",
"label" : "Cases",
"lastUpdatedId" : "1033471693",
"recordIds" : [ "069xx0000000006", "069xx0000000001", "069xx0000000002" ]
} ]
特定のオブジェクトへの応答を絞り込む場合の使用例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/relevantItems?sobjects=Account,User
-H "Authorization: Bearer token"
リクエストボディの例
不要
76
関連項目の表示例

===== PAGE 87 =====
レスポンスボディの例
[ {
"apiName" : "Account",
"key" : "001",
"label" : "Accounts",
"lastUpdatedId" : "193640553",
"recordIds" : [ "001xx000003DWsT" ]
}, {
"apiName" : "User",
"key" : "005",
"label" : "Users",
"lastUpdatedId" : "102959935",
"recordIds" : [ "005xx000001Svqw", "005xx000001SvwK", "005xx000001SvwA" ]
} ]
ユーザーの現在の関連レコードリストを以前のバージョンと比較する場合の使用例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/relevantItems?lastUpdatedId=102959935
-H "Authorization: Bearer token"
リクエストボディの例
不要
応答ヘッダーの例
lastUpdatedId: 102959935
newResultSetSinceLastQuery: true
レスポンスボディの例
[ {
"apiName" : "User",
"key" : "003",
"label" : "Users",
"lastUpdatedId" : "102959935",
"recordIds" : [ "003xx000004TxBA" ]
}, {
"apiName" : "Account",
"key" : "001",
"label" : "Accounts",
"lastUpdatedId" : "193640553",
"recordIds" : [ "001xx000003DWsT" ]
}, {
"apiName" : "Case",
"key" : "005",
"label" : "Cases",
"lastUpdatedId" : "1740766611",
"recordIds" : [ "005xx000001Svqw", "005xx000001SvwA" ]
} ]
77
関連項目の表示例

===== PAGE 88 =====
特定のオブジェクトでユーザーの現在の関連レコードリストを以前のバージョンと比較する場合の使用例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/relevantItems?mode=MRU&sobjects=Account,Contact&Account.lastUpdatedId=102959935
-H "Authorization: Bearer token"
リクエストボディの例
不要
レスポンスボディの例
[ {
"apiName" : "Account",
"key" : "001",
"label" : "Accounts",
"lastUpdatedId" : "193640553",
"recordIds" : [ "001xx000003DWsT" ]
} ]
関連トピック:
sObject 関連項目
リッチテキストエリア項目から画像を取得
リッチテキストエリア項目から画像を取得するには、sObject Rich Text Image Get リソースを使用します。この例
では、LeadPhotoRichText__c というリードレコードのカスタムリッチテキスト項目から画像を取得しま
す。画像はすでにこの項目にアップロードされていることを前提とします。
画像参照 ID の取得
要求を使用して画像を取得するには、最初にリッチテキスト項目からrefid を取得する必要があります。リー
ドレコードの項目情報を取得するには、sObject Rows (ページ 156) リソースを使用します。
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Lead/00Q112222233333
-H "Authorization: Bearer token"
要求からの出力例を簡略化して次に示します。
{
"attributes": {
"type": "Lead",
"url": "/services/data/v51.0/sobjects/Lead/00Q112222233333"
},
"Id": "00Q112222233333",
"IsDeleted": false,
"MasterRecordId": null,
"LastName": "Smith",
"FirstName": "John",
78
リッチテキストエリア項目から画像を取得例

===== PAGE 89 =====
...
"LeadPhotoRichText__c": "<img alt=\"johnSmithPhoto\"
src=\"https://MyDomainName.documentforce.com/servlet/rtaImage?eid=a005e000007Dksm&amp;feoid=00N5e00000djU6Y&amp;refid=0EM5e000000B9LQ\"></img>"
}
画像の refid は 0EM5e000000B9LQ であることが LeadPhotoRichText__c 項目からわかります。この値は、次の
手順で画像を取得するために使用します。
画像の取得
画像を取得するには、リードレコード ID、リッチテキスト項目名、および画像の refid を使用します。応答
では、アップロード時と同じファイル種別のエンコードデータとして画像が返されます。--output filename
パラメーターを使用して、返されたデータを適切なファイル種別の画像ファイルとして保存します。
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Lead/00Q112222233333/richTextImageFields/LeadPhotoRichText__c/0EMR00000000A8V
-H "Authorization: Bearer token" --output "LeadPhoto.jpeg"
Blob データを挿入または更新する
sObject Basic Information (ページ 149)、sObject Rows (ページ 156)、または sObject Collections (ページ 425) リソースを使用
して、画像や PDF といった Salesforce のバイナリラージオブジェクト (blob) を挿入したり、更新したりできます。
任意の型のファイルやバイナリデータを、blob 項目を含む任意の標準オブジェクトにアップロードできます。
blob データを挿入および更新するには、マルチパートリクエストボディを作成します。リクエストボディの最
初のパートには、新しいレコードの説明や名前などの非バイナリ項目データが含まれます。2 つ目のパートに
は、アップロードするファイルのバイナリデータが含まれます。リクエストボディは、MIME マルチパートコ
ンテンツタイプ標準に準拠する必要があります。詳細は、W3C 標準のマルチパートコンテンツタイプに関する
説明を参照してください。
sObject Basic Information または sObject Rows リソースを使用する場合、アップロードの最大ファイルサイズは、
ContentVersion オブジェクトの場合は 2 GB、使用可能な他のすべての標準オブジェクトの場合は 500 MB です。
sObject Collections リソースを使用する場合、1 回の要求の全ファイルの最大合計サイズは 500 MB です。
メモ: 非マルチパートメッセージを使用して blob データを挿入/更新できますが、テキストデータは 50 MB
まで、base64 で符号化されたデータは 37.5 MB までに制限されます。
この後のセクションでは、マルチパートコンテンツタイプ要求を使用して blob データを挿入/更新する方法の
例を示します。これらの例のリクエストボディでは、JSON 形式を使用しています。
blob データを含む Document の挿入
次の要求およびリクエストボディの例では、PDF ファイルのバイナリデータを含む Document レコードを作成し
ます。リクエストボディでは、ファイル自体のバイナリデータだけではなく、FolderId など、Document オブ
ジェクトに必要な他の項目データも指定します。
79
Blob データを挿入または更新する例

===== PAGE 90 =====
Salesforce に新規 Document レコード用の Folder レコードがない場合は、sObject Basic Information リソースを使用し
て作成してから、この例に従ってください。Folder レコードの Type 項目が Document であることを確認しま
す。
ヒント: 要求を正常に送信すると、Salesforce Classic で新規 Document を表示できます。Salesforce Lightning の
ユーザーインターフェースには、Document は表示されません。
Document を作成する場合の要求の例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Document/ -H
"Authorization: Bearer token" -H "Content-Type: multipart/form-data;
boundary=\"boundary_string\"" --data-binary @NewDocument.json
Document を作成する場合のリクエストボディの例
このリクエストボディは、NewDocument.json のコンテンツを表します。ここでは、簡潔にするために
PDF コンテンツのバイナリデータは省略されて「Binary data goes here.」に置き換えられています。実際の要求
にはバイナリコンテンツ全体が含まれます。
--boundary_string
Content-Disposition: form-data; name="entity_document";
Content-Type: application/json
{
"Description" : "Marketing brochure for Q1 2011",
"Keywords" : "marketing,sales,update",
"FolderId" : "005D0000001GiU7",
"Name" : "Marketing Brochure Q1",
"Type" : "pdf"
}
--boundary_string
Content-Type: application/pdf
Content-Disposition: form-data; name="Body"; filename="2011Q1MktgBrochure.pdf"
Binary data goes here.
--boundary_string--
レスポンスボディの例
成功すると、新規 Document の ID が返されます。
{
"id" : "015D0000000N3ZZIA0",
"errors" : [ ],
"success" : true
}
エラー応答の例
{
"fields" : [ "FolderId" ],
"message" : "Folder ID: id value of incorrect type: 005D0000001GiU7",
"errorCode" : "MALFORMED_ID"
}
80
Blob データを挿入または更新する例

===== PAGE 91 =====
blob データを含む Document の更新
この例では、既存の Document レコードを更新します。リクエストボディのコンテンツに応じて、レコード項
目とそれに関連付けられているバイナリデータのいずれかまたは両方を更新できます。
レコード項目のみを更新する場合は、リクエストボディにマルチパートコンテンツタイプは不要です。
Document オブジェクトのバイナリデータを更新する場合の要求の例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/Document/015D0000000N3ZZIA0
-H "Authorization: Bearer token" -H "Content-Type: multipart/form-data;
boundary=\"boundary_string\"" --data-binary @UpdateDocument.json -X PATCH
Document オブジェクトのバイナリデータを更新する場合のリクエストボディの例
このリクエストボディは、UpdateDocument.json のコンテンツを表します。この例では、レコードのバ
イナリデータと Name 項目および Keywords 項目を更新します。バイナリデータのみを更新する場合は、
Name 項目と Keywords 項目を含むコード行を削除できます。
ここでは、簡潔にするために PDF コンテンツのバイナリデータは省略されて「Updated document binary goes
here.」に置き換えられています。実際の要求にはバイナリコンテンツ全体が含まれます。
--boundary_string
Content-Disposition: form-data; name="entity_content";
Content-Type: application/json
{
"Name" : "Marketing Brochure Q1 - Sales",
"Keywords" : "sales, marketing, first quarter"
}
--boundary_string
Content-Type: application/pdf
Content-Disposition: form-data; name="Body"; filename="2011Q1MktgBrochure.pdf"
Updated document binary data goes here.
--boundary_string--
Document オブジェクトの項目を更新する場合のレスポンスボディの例
戻り値なし
エラー応答
「状況コードとエラー応答」を参照してください。
ContentVersion の挿入
この例では、新規 ContentVersion を挿入します。ファイル自体のバイナリデータだけではなく、ReasonForChange
や PathOnClient など、他の項目の値も指定します。ContentVersion は、必ず ContentDocument に関連付けられ
ているため、このメッセージには ContentDocumentId が含まれます。
81
Blob データを挿入または更新する例

===== PAGE 92 =====
ヒント:  ContentVersion オブジェクトは update をサポートしていません。したがって ContentVersion を更新す
ることはできません。新しい ContentVersion を挿入することのみが可能です。変更の結果は、[コンテンツ]
タブで確認できます。
ContentVersion を挿入する場合の使用例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/ContentVersion
-H "Authorization: Bearer token" -H "Content-Type: multipart/form-data;
boundary=\"boundary_string\"" --data-binary @NewContentVersion.json
ContentVersion を挿入する場合のリクエストボディの例
このリクエストボディは、NewContentVersion.json ファイルの内容を表します。ここでは、簡潔にす
るために PDF コンテンツのバイナリデータは省略されて「Binary data goes here.」に置き換えられています。
実際の要求にはバイナリコンテンツ全体が含まれます。
--boundary_string
Content-Disposition: form-data; name="entity_content";
Content-Type: application/json
{
"ContentDocumentId" : "069D00000000so2",
"ReasonForChange" : "Marketing materials updated",
"PathOnClient" : "Q1 Sales Brochure.pdf"
}
--boundary_string
Content-Type: application/octet-stream
Content-Disposition: form-data; name="VersionData"; filename="Q1 Sales Brochure.pdf"
Binary data goes here.
--boundary_string--
ContentVersion を挿入する場合のレスポンスボディの例
{
"id" : "068D00000000pgOIAQ",
"errors" : [ ],
"success" : true
}
ContentVersion を挿入した場合のエラー応答
「状況コードとエラー応答」を参照してください。
sObject コレクションを使用した blob レコードのコレクションの挿入
この例では、新規 Document のコレクションを挿入します。ファイル自体のバイナリデータだけではなく、コ
レクションの各レコードの Description や Name など、他の項目データも指定します。
ヒント: 要求を正常に送信すると、Salesforce Classic で新規 Document を表示できます。Salesforce Lightning の
ユーザーインターフェースには、Document は表示されません。
82
Blob データを挿入または更新する例

===== PAGE 93 =====
属性
blob データに sObject コレクションを使用する場合は、リクエストボディの属性の対応付けで type 以外に
も特定の属性値を指定する必要があります。
説明パラメーター
blob データでは必須です。バイナリパートの一意の識別子です。binaryPartName
blob データでは必須です。バイナリデータが挿入または更新される項
目の名前です。
binaryPartNameAlias
Document を作成する場合の例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/composite/sobjects/ -H
"Authorization: Bearer token" -H "Content-Type: multipart/form-data;
boundary=\"boundary_string\"" --data-binary @newdocuments.json
Document を作成する場合のリクエストボディの例
このコードは、newdocuments.json のコンテンツです。ここでは、簡潔にするために PDF コンテンツの
バイナリデータは省略されて「Binary data goes here.」に置き換えられています。実際の要求にはバイナリコ
ンテンツ全体が含まれます。
--boundary_string
Content-Disposition: form-data; name="collection"
Content-Type: application/json
{
"allOrNone" : false,
"records" :
[
{
"attributes" :
{
"type" : "Document",
"binaryPartName": "binaryPart1",
"binaryPartNameAlias": "Body"
},
"Description" : "Marketing Brochure",
"FolderId" : "005xx000001Svs4AAC",
"Name" : "Brochure",
"Type" : "pdf"
},
{
"attributes" :
{
"type" : "Document",
"binaryPartName": "binaryPart2",
"binaryPartNameAlias": "Body"
},
"Description" : "Pricing Overview",
"FolderId" : "005xx000001Svs4AAC",
"Name" : "Pricing",
83
Blob データを挿入または更新する例

===== PAGE 94 =====
"Type" : "pdf"
}
]
}
--boundary_string
Content-Disposition: form-data; name="binaryPart1"; filename="Brochure.pdf"
Content-Type: application/pdf
Binary data goes here.
--boundary_string
Content-Disposition: form-data; name="binaryPart2"; filename="Pricing.pdf"
Content-Type: application/pdf
Binary data goes here.
--boundary_string--
Document を作成する場合のレスポンスボディの例
成功すると、新規 Document の ID が返されます。
[
{
"id": "015xx00000013QjAAI",
"errors": [],
"success": true
},
{
"id": "015xx00000013QkAAI",
"errors": [],
"success": true
}
]
詳細は、「sObject コレクション」を参照してください。
マルチパートメッセージの考慮事項
blob データを挿入/更新するときの、マルチパートメッセージの形式に関するいくつかの考慮事項を次に示し
ます。
境界文字列
• マルチパートリクエストボディの各パートを区分します。
• マルチパートリクエストの Content-Type ヘッダーに指定する必要があります。
• 70 文字まで入力できます。
• リクエストボディのどの部分にも出現しない文字列値である必要があります。
• 最初の境界文字列には、2 つのハイフン (--) プレフィックスを含めます。
• 最後の境界文字列には、2 つのハイフン (--) サフィックスを含めます。
84
Blob データを挿入または更新する例

===== PAGE 95 =====
Content-Disposition ヘッダー
• リクエストボディの各パートで必要です。
• 値として form-data が必要です。また、name 属性も必要です。
– リクエストボディの非バイナリパートでは、name 属性に任意の値を使用します。
– 1 つの Document の場合、リクエストボディのバイナリパートで name 属性を使用して、オブジェク
トの blob データ項目の名前を指定します。たとえば、Document オブジェクトの blob データ項目の名
前は Body です。
– sObject コレクションを使用して Document を挿入または更新する場合、リクエストボディの各バイナ
リパートで name 属性を使用して、そのパートの一意の識別子を指定します。これらの ID は、リク
エストボディの非バイナリパートによって参照されます。
• バイナリパートには、ローカルファイルの名前を表す filename 属性を含める必要があります。
Content-Type ヘッダー
• マルチパートリクエストボディの各パートで必要です。
• マルチパートリクエストボディの非バイナリパートでは、application/jsonおよび application/xml
コンテンツタイプをサポートします。
• マルチパートリクエストボディのバイナリパートでは、任意のコンテンツタイプをサポートします。
改行
マルチパートリクエストボディの各パートでは、ヘッダーとデータの間に改行を追加する必要があります。
例に示されているように、Content-Type および Content-Disposition ヘッダーは、改行によって JSON
またはバイナリデータから分離されています。
関連トピック:
sObject Basic Information
sObject Rows
sObject コレクション
blob データの取得
blob データの取得
特定のレコードの blob データを取得するには、sObject Blob Get リソースを使用します。blob データを取得する
には、blob データを含むレコードが Salesforce に存在している必要があります。
blob 項目があるのは、Attachment、ContentNote、ContentVersion、Document、Folder、Note などの特定の標準オブ
ジェクトのみです。
メモ:  sObject Blob Get リソースは、JSON または XML 形式のデータではなくバイナリデータを返すため、複
合 API 要求と互換性がありません。Blob データを取得するには、代わりに、個別の sObject Blob Get 要求を実
行します。
次の例では、「Blob データを挿入または更新する」 (ページ 79)で作成された Document レコードの blob データ
を取得します。
85
blob データの取得例

===== PAGE 96 =====
Document レコードから blob データを取得する例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Document/015D0000000N3ZZIA0/body
-H "Authorization: Bearer token"
リクエストボディの例
不要
レスポンスボディの例
Document の本文コンテンツがバイナリ形式で返されます。返されたデータがバイナリであるため、応答の
コンテンツタイプは JSON でも XML でもありません。返されたバイナリデータをファイルに保存すれば、バ
イナリデータの保管やアクセスが可能になります。
関連トピック:
Blob データを挿入または更新する
最近参照した情報の操作
このセクションの例では、REST API の Query リソースおよび Recently Viewed リソースを使用して最近参照したレ
コード情報をプログラムで取得および更新します。
このセクションの内容:
最近参照したレコードの表示
最近参照したレコードのリストを取得するには、Recently Viewed Items リソースを使用します。
最近参照したデータとしてレコードをマーク
REST API を使用して、最近参照したデータとしてレコードをマークするには、FOR VIEW 句または FOR
REFERENCE 句を指定して Query リソースを使用します。レコードを最近参照したデータとしてマークし、
レコードが参照された日時などの情報が正しく設定されていることを確認するには、SOQL を使用します。
最近参照したレコードの表示
最近参照したレコードのリストを取得するには、Recently Viewed Items リソースを使用します。
最近参照したレコードのうち最近の 2 件を取得する場合の使用例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/recent/?limit=2 -H
"Authorization: Bearer token"
リクエストボディの例
不要
レスポンスボディの例
{
"attributes" :
{
86
最近参照した情報の操作例

===== PAGE 97 =====
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/a06U000000CelH0IAJ"
},
"Id" : "a06U000000CelH0IAJ",
"Name" : "Acme"
},
{
"attributes" :
{
"type" : "Opportunity",
"url" : "/services/data/v60.0/sobjects/Opportunity/a06U000000CelGvIAJ"
},
"Id" : "a06U000000CelGvIAJ",
"Name" : "Acme - 600 Widgets"
}
最近参照したデータとしてレコードをマーク
REST API を使用して、最近参照したデータとしてレコードをマークするには、FOR VIEW 句または FOR
REFERENCE 句を指定して Query リソースを使用します。レコードを最近参照したデータとしてマークし、レ
コードが参照された日時などの情報が正しく設定されていることを確認するには、SOQL を使用します。
FOR VIEW は、モバイルアプリケーションなどのカスタムインターフェースまたはカスタムページからレコー
ドが参照された場合に、Salesforce に通知するために使用します。レコードがカスタムインターフェースから参
照されている場合は、FOR REFERENCE を使用します。レコードは、関連レコードが表示されるたびに参照さ
れます。詳細については、『SOQL および SOSL リファレンス』の「FOR VIEW」および「FOR REFERENCE」を参照し
てください。
1 つの取引先レコードを最近参照したデータとしてマークするクエリを実行する場合の使用例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/query/?q=SELECT+Name+FROM+Account+LIMIT+1+FOR+VIEW
-H "Authorization: Bearer token"
クエリを実行する場合のリクエストボディの例
不要
クエリを実行する場合のレスポンスボディの例
{
"done" : true,
"totalSize" : 1,
"records" :
[
{
"attributes" :
{
"type" : "Account",
"url" : "/services/data/v60.0/sobjects/Account/001D000000IRFmaIAH"
},
"Name" : "Acme"
},
87
最近参照したデータとしてレコードをマーク例

===== PAGE 98 =====
]
}
関連トピック:
Query
ユーザーパスワードの管理
このセクションの例では、REST API リソースを使用して、パスワードの設定やリセットなど、ユーザーパスワー
ドを管理します。
このセクションの内容:
ユーザーパスワードを管理する
ユーザーパスワードの設定やリセット、パスワードに関する情報の取得を行うには、sObject User Password リ
ソースを使用します。パスワードの有効期限の状況を取得するには HTTP GET メソッド、パスワードを設定
するには HTTP POST メソッド、パスワードをリセットするには HTTP DELETE メソッドを使用します。
ユーザーパスワードを管理する
ユーザーパスワードの設定やリセット、パスワードに関する情報の取得を行うには、sObject User Password リソー
スを使用します。パスワードの有効期限の状況を取得するには HTTP GET メソッド、パスワードを設定するには
HTTP POST メソッド、パスワードをリセットするには HTTP DELETE メソッドを使用します。
関連付けられたセッションには、特定のユーザーパスワード情報へのアクセス権が必要です。セッションに適
切な権限がない場合、これらのメソッドから HTTP エラー応答 403 が返されます。
これらのメソッドは、ユーザーとセルフサービスユーザーの両方に提供されています。セルフサービスユー
ザーのパスワードの管理では、REST API URL に、User の代わりに SelfServiceUser を使用します。
次に、ユーザーの現在のパスワード有効期限の状況を取得する例を示します。
現在のパスワード有効期限の状況を取得する場合の使用例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/User/005D0000001KyEIIA0/password
-H "Authorization: Bearer token"
現在のパスワード有効期限の状況を取得する場合のリクエストボディの例
不要
現在のパスワード有効期限の状況を取得する場合のレスポンスボディの例 (JSON)
{
"isExpired" : false
}
88
ユーザーパスワードの管理例

===== PAGE 99 =====
現在のパスワード有効期限の状況を取得する場合のレスポンスボディの例 (XML)
<Password>
<isExpired>false</isExpired>
</Password>
セッションの権限が不十分な場合のエラー応答の例
{
"message" : "You do not have permission to view this record.",
"errorCode" : "INSUFFICIENT_ACCESS"
}
次に、特定のユーザーのパスワードを変更する例を示します。
ユーザーパスワードを変更する場合の使用例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/User/005D0000001KyEIIA0/password
-H "Authorization: Bearer token" —H "Content-Type: application/json" —d @newpwd.json
—X POST
ファイル newpwd.json のコンテンツ
{
"NewPassword" : "myNewPassword1234"
}
ユーザーパスワードを変更する場合のレスポンスボディの例
パスワードが正しく変更された場合のレスポンスボディはありません。HTTP 状況コード 204 が返されます。
新規パスワードが組織のパスワード要件を満たしていない場合のエラー応答の例
{
"message" : "Your password must have a mix of letters and numbers.",
"errorCode" : "INVALID_NEW_PASSWORD"
}
最後に、ユーザーパスワードのリセットの例を示します。
ユーザーパスワードをリセットする場合の使用例
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/User/005D0000001KyEIIA0/password
-H "Authorization: Bearer token" —X DELETE
ユーザーパスワードをリセットする場合のリクエストボディの例
不要
ユーザーパスワードをリセットする場合のレスポンスボディの例 (JSON)
{
"NewPassword" : "2sv0xHAuM"
}
89
ユーザーパスワードを管理する例

===== PAGE 100 =====
ユーザーパスワードをリセットする場合のレスポンスボディの例 (XML)
<Result>
<NewPassword>2sv0xHAuM</NewPassword>
</Result>
関連トピック:
sObject User Password
承認プロセスとプロセスルールの操作
このセクションの例では、REST API リソースを使用して、承認プロセスとプロセスルールを操作します。
このセクションの内容:
すべての承認プロセスのリストを取得する
承認に関する情報を取得するには、Process Approvals リソースを使用します。
承認を受けるレコードを送信する
承認を受ける単一レコードまたはレコードのコレクションを送信するには、Process Approvals リソースを使
用します。各コールは、要求の配列を受け付けます。
レコードを承認する
単一レコードまたはレコードのコレクションを承認するには、Process Approvals リソースを使用します。各
コールは、要求の配列を受け付けます。現在のユーザーは、割り当てられた承認者である必要があります。
レコードを却下する
単一レコードまたはレコードのコレクションを却下するには、Process Approvals リソースを使用します。各
コールは、要求の配列を受け付けます。現在のユーザーは、割り当てられた承認者である必要があります。
一括承認
一括承認を行うには、Process Approvals リソースを使用します。異なる Process Approvals 要求のコレクション
を指定して、すべて一括して実行することができます。
プロセスルールのリストを取得する
プロセスルールに関する情報を取得するには、Process Rules リソースを使用します。
特定のプロセスルールを取得する
Process Rulesリソースを使用し、メタデータを取得するルールの sObjectName と workflowRuleId を指定
します。
プロセスルールをトリガーする
プロセスルールをトリガーするには、Process Rules リソースを使用します。評価条件に関係なく、指定され
た ID に関連するすべてのルールが評価されます。すべての ID は、同じオブジェクトのレコードの ID である
必要があります。
90
承認プロセスとプロセスルールの操作例

===== PAGE 101 =====
すべての承認プロセスのリストを取得する
承認に関する情報を取得するには、Process Approvals リソースを使用します。
使用例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/process/approvals/ -H
"Authorization: Bearer token"
リクエストボディの例
不要
JSON レスポンスボディの例
{
"approvals" : {
"Account" : [ {
"description" : null,
"id" : "04aD00000008Py9",
"name" : "Account Approval Process",
"object" : "Account",
"sortOrder" : 1
} ]
}
}
承認を受けるレコードを送信する
承認を受ける単一レコードまたはレコードのコレクションを送信するには、Process Approvalsリソースを使用し
ます。各コールは、要求の配列を受け付けます。
使用例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/process/approvals/ -H
"Authorization: Bearer token" -H "Content-Type: application/json" -d @submit.json"
リクエストボディ submit.json ファイルの例
次の例では、レコード「001D000000I8mIm」が、開始条件を省略し、送信者「005D00000015rZy」の代理とし
て、承認プロセス「PTO_Request_Process」のために送信されます。
{
"requests" : [{
"actionType": "Submit",
"contextId": "001D000000I8mIm",
"nextApproverIds": ["005D00000015rY9"],
"comments":"this is a test",
"contextActorId": "005D00000015rZy",
"processDefinitionNameOrId" : "PTO_Request_Process",
"skipEntryCriteria": "true"}]
}
91
すべての承認プロセスのリストを取得する例

===== PAGE 102 =====
JSON レスポンスボディの例
[ {
"actorIds" : [ "005D00000015rY9IAI" ],
"entityId" : "001D000000I8mImIAJ",
"errors" : null,
"instanceId" : "04gD0000000Cvm5IAC",
"instanceStatus" : "Pending",
"newWorkitemIds" : [ "04iD0000000Cw6SIAS" ],
"success" : true } ]
レコードを承認する
単一レコードまたはレコードのコレクションを承認するには、Process Approvalsリソースを使用します。各コー
ルは、要求の配列を受け付けます。現在のユーザーは、割り当てられた承認者である必要があります。
使用例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/process/approvals/ -H
"Authorization: Bearer token" -H "Content-Type: application/json" -d @approve.json"
リクエストボディ approve.json ファイルの例
{
"requests" : [{
"actionType" : "Approve",
"contextId" : "04iD0000000Cw6SIAS",
"nextApproverIds" : ["005D00000015rY9"],
"comments" : "this record is approved"}]
}
JSON レスポンスボディの例
[ {
"actorIds" : null,
"entityId" : "001D000000I8mImIAJ",
"errors" : null,
"instanceId" : "04gD0000000CvmAIAS",
"instanceStatus" : "Approved",
"newWorkitemIds" : [ ],
"success" : true
} ]
レコードを却下する
単一レコードまたはレコードのコレクションを却下するには、Process Approvalsリソースを使用します。各コー
ルは、要求の配列を受け付けます。現在のユーザーは、割り当てられた承認者である必要があります。
92
レコードを承認する例

===== PAGE 103 =====
使用例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/process/approvals/ -H
"Authorization: Bearer token" -H "Content-Type: application/json" -d @reject.json"
リクエストボディ reject.json ファイルの例
{
"requests" : [{
"actionType" : "Reject",
"contextId" : "04iD0000000Cw6cIAC",
"comments" : "This record is rejected."}]
}
JSON レスポンスボディの例
[ {
"actorIds" : null,
"entityId" : "001D000000I8mImIAJ",
"errors" : null,
"instanceId" : "04gD0000000CvmFIAS",
"instanceStatus" : "Rejected",
"newWorkitemIds" : [ ],
"success" : true
} ]
一括承認
一括承認を行うには、Process Approvals リソースを使用します。異なる Process Approvals 要求のコレクションを指
定して、すべて一括して実行することができます。
使用例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/process/approvals/ -H
"Authorization: Bearer token" -H "Content-Type: application/json" -d @bulk.json"
リクエストボディ bulk.json ファイルの例
{
"requests" :
[{
"actionType" : "Approve",
"contextId" : "04iD0000000Cw6r",
"comments" : "approving an account"
},{
"actionType" : "Submit",
"contextId" : "001D000000JRWBd",
"nextApproverIds" : ["005D00000015rY9"],
"comments" : "submitting an account"
},{
"actionType" : "Submit",
"contextId" : "003D000000QBZ08",
"comments" : "submitting a contact"
93
一括承認例

===== PAGE 104 =====
}]
}
JSON レスポンスボディの例
[ {
"actorIds" : null,
"entityId" : "001D000000I8mImIAJ",
"errors" : null,
"instanceId" : "04gD0000000CvmZIAS",
"instanceStatus" : "Approved",
"newWorkitemIds" : [ ],
"success" : true
}, {
"actorIds" : null,
"entityId" : "003D000000QBZ08IAH",
"errors" : null,
"instanceId" : "04gD0000000CvmeIAC",
"instanceStatus" : "Approved",
"newWorkitemIds" : [ ],
"success" : true
}, {
"actorIds" : [ "005D00000015rY9IAI" ],
"entityId" : "001D000000JRWBdIAP",
"errors" : null,
"instanceId" : "04gD0000000CvmfIAC",
"instanceStatus" : "Pending",
"newWorkitemIds" : [ "04iD0000000Cw6wIAC" ],
"success" : true
} ]
プロセスルールのリストを取得する
プロセスルールに関する情報を取得するには、Process Rules リソースを使用します。
使用例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/process/rules/ -H
"Authorization: Bearer token"
リクエストボディの例
不要
JSON レスポンスボディの例
{
"rules" : {
"Account" : [ {
"actions" : [ {
"id" : "01VD0000000D2w7",
"name" : "ApprovalProcessTask",
"type" : "Task"
} ],
94
プロセスルールのリストを取得する例

===== PAGE 105 =====
"description" : null,
"id" : "01QD0000000APli",
"name" : "My Rule",
"namespacePrefix" : null,
"object" : "Account"
} ]
}
}
特定のプロセスルールを取得する
Process Rules リソースを使用し、メタデータを取得するルールの sObjectName と workflowRuleId を指定し
ます。
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
プロセスルールをトリガーする
プロセスルールをトリガーするには、Process Rules リソースを使用します。評価条件に関係なく、指定された
ID に関連するすべてのルールが評価されます。すべての ID は、同じオブジェクトのレコードの ID である必要
があります。
使用例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/process/rules/ -H
"Authorization: Bearer token" -H "Content-Type: application/json" -d @rules.json"
95
特定のプロセスルールを取得する例

===== PAGE 106 =====
リクエストボディ rules.json ファイルの例
{
"contextIds" : [
"001D000000JRWBd",
"001D000000I8mIm",
"001D000000I8aaf"]
}
JSON レスポンスボディの例
{
"errors" : null,
"success" : true
}
イベント監視の使用
この例では、REST API イベント監視データを使用しています。このデータに含まれる情報は、組織の利用状況
のトレンドとユーザーの行動を評価する場合に役立ちます。イベント監視には、EventLogFile オブジェクトを介
して Lightning Platform SOAP API および REST API を通じてアクセスします。したがって、自分のバックエンドスト
レージやデータマートにログデータを統合して、複数の組織や分散されたシステムからのデータを相関するこ
とができます。
メモ: イベント監視を使用できるサポート対象のイベント種別については「Salesforce と Lightning Platform の
オブジェクトリファレンス: EventLogFile オブジェクト」を参照してください。
• ごくまれに 24 時間ログファイルが生成されないことがありますが、その場合は Salesforce カスタマーサポー
トにお問い合わせください。
• ログデータは参照専用です。ログデータは挿入、更新、または削除できません。
• 組織に生成されたファイルを判別するには、EventType 項目を使用します。
• イベントによって、リアルタイムにログデータが生成されます。ただし、1 日ごとのログファイルはイベン
トが実行された翌日のピーク時間以外に生成されます。そのため、1 日ごとのログファイルデータはイベン
トが発生してから少なくとも 1 日は使用できません。1 時間ごとのログファイルの場合、イベントの配信時
間や最終処理時間によっては、ログファイルでイベントが使用できるようになるまで、3 ～ 6 時間かかるこ
とが予想されます。ただし、それより長くかかることもあります。
• ログファイルは、その日またはその時間に [EventType] 項目に表示される、少なくとも 1 つの種別の 1 つ
のイベントが発生した場合に生成されます。イベントが発生していない場合、このファイルは生成されま
せん。
• ログファイルは、Event Monitoring ライセンスを持つ組織で CreatedDate から 30 日間使用でき、その後は
自動的に削除されます。すべての Developer Edition 組織では、ログファイルは 1 日間使用できます。
• すべてのイベント監視ログは、EventLogFileオブジェクトを介して API に公開されます。ただし、Event Monitoring
Analytics アプリケーションからアクセスする場合を除き、ユーザーインターフェースからアクセスすること
はできません。
• ログファイルは、組織のデータやファイルストレージの割り当てに反映されません。
96
イベント監視の使用例

===== PAGE 107 =====
• イベント監視ログファイルは、ユーザーの活動の記録のシステムではありません。これは信頼できる情報
源ですが、永続性はありません。Salesforce サイトの切り替え時、インスタンスの更新時、または計画外の
システム停止時にデータが失われる可能性があります。たとえば、Salesforce が本番組織インスタンスを移
動した場合、イベントログファイルのデータにギャップが生じる可能性があります。Salesforce はイベント
ログファイルのデータの整合性を維持し、データ損失を回避するための商業的に合理的な努力を払ってい
ます。Salesforce がサイトの切り替えやインスタンスの更新を実行する場合、自動化プロセスを使用してイ
ベントログを複製します。
• 1 時間ごとのログファイルを見れば、組織で発生した直近のイベントをレビューすることができます。ただ
し、1 時間ごとのイベントログファイルにはすべてのイベントログが取得されない場合があります。特に、
サイト切り替え、インスタンスリフレッシュ、または計画外のシステム停止時にはデータが失われる可能
性があります。完全なデータを得るには、1 時間ごとのログファイルを使用してください。
• イベント送信に失敗して回復に時間がかかり過ぎる場合は、ログファイルが必ず 1 回は届くように再送信
されます。その結果、これらの潜在的なログファイルではイベントデータが重複することがあります。ア
プリケーションで潜在的なログファイルが使用されている場合は、重複しているイベント配信がアプリケー
ションで処理されることを確認します。
• 1 日ごとの増分ログファイルが配信されると、その日に出力されたログをすべて含む新しいファイルで、元
のファイルが置き換えられます。最新のログファイルであることを確認するには、CreatedDate 項目を
チェックします。
• 常に新しいログファイルについて EventLogFile オブジェクトを照会して、潜在的なログを含めるようにする
ことをお勧めします。新しく作成されたログファイルを特定するには、EventLogFile CreatedDate 項目を使
用します。1 時間ごとおよび 1 日ごとの増分ログの配信方法は異なります。詳細は、「1 時間ごとのイベン
トログと 24 時間のイベントログの違い」を参照してください。
このセクションのすべてのクエリと例には、「イベントログファイルを参照」および「API の有効化」ユーザー
権限が必要です。「すべてのデータの参照」権限を持つユーザーは、イベント監視データも表示できます。
このセクションの内容:
REST を使用してイベント監視を記述する
項目、URL、および子リレーションに関する情報を含む、オブジェクトのすべてのメタデータを取得するに
は、sObject Describe リソースを使用します。
REST を使用してイベント監視データを照会する
レコードから項目値を取得するには、Queryリソースを使用します。fields パラメーターに取得する項目を指
定し、リソースの GET メソッドを使用します。
レコードからイベント監視コンテンツを取得する
特定のレコードの BLOB データを取得するには、sObject Blob Retrieve リソースを使用します。
cURL を REST で使用して大きなイベントログファイルをダウンロードする
イベントログファイルがツールで処理できないほど大きくなる場合があります。cURL などのコマンドライ
ンツールは、sObject Blob Get オブジェクトを使用して 100 MB を超えるファイルをダウンロードする方法の 1
つです。
97
イベント監視の使用例

===== PAGE 108 =====
イベント監視データの削除
ユーザーのログデータが含まれるイベントログファイルを削除できます。ログファイルを削除することに
よって、データ保護とプライバシーに関する規制に準拠し、他のユーザーがアクセス可能な情報を制御で
きます。イベントログから個別の行を削除することはできません。代わりに、ユーザーの活動が含まれる
ログファイル全体を削除する必要があります。
1 時間ごとのイベントログファイルのクエリまたは表示
組織のイベントを迅速に確認するには、最近の活動のイベントログファイルを 1 時間ごとに取得します。1
時間ごとのイベントログファイルによってセキュリティの異常やカスタムコードのパフォーマンスの問題
をすばやく確認できます。
REST を使用してイベント監視を記述する
項目、URL、および子リレーションに関する情報を含む、オブジェクトのすべてのメタデータを取得するには、
sObject Describe リソースを使用します。
例
REST API を使用して、イベントログファイルを記述できます。次のような GET 要求を使用します。
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/EventLogFile/describe
-H "Authorization: Bearer token"
未加工の応答の例
{
"actionOverrides" : [ ],
"activateable" : false,
"childRelationships" : [ ],
"compactLayoutable" : false,
"createable" : false,
"custom" : false,
"customSetting" : false,
"deletable" : false,
"deprecatedAndHidden" : false,
"feedEnabled" : false,
"fields" : [ {
"autoNumber" : false,
"byteLength" : 18,
"calculated" : false,
"calculatedFormula" : null,
"cascadeDelete" : false,
"caseSensitive" : false,
"controllerName" : null,
"createable" : false,
...
}
98
REST を使用してイベント監視を記述する例

===== PAGE 109 =====
REST を使用してイベント監視データを照会する
レコードから項目値を取得するには、Query リソースを使用します。fields パラメーターに取得する項目を指定
し、リソースの GET メソッドを使用します。
REST API を使用して、イベント監視データを照会できます。LogDate および EventType に基づいてイベント
監視レコードを取得するには、次のような GET 要求を使用します。
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/query?q=SELECT+Id+,+EventType+,+LogFile+
,+LogDate+,+LogFileLength+FROM+EventLogFile+WHERE+
LogDate+>+Yesterday+AND+EventType+=+'API' -H "Authorization: Bearer token"
未加工の応答の例
{
"totalSize" : 4,
"done" : true,
"records" : [ {
"attributes" : {
"type" : "EventLogFile",
"url" : "/services/data/v60.0/sobjects/EventLogFile/0ATD000000001bROAQ" }
"Id" : "0ATD000000001bROAQ",
"EventType" : "API",
"LogFile" : "/services/data/v60.0/sobjects/EventLogFile/0ATD000000001bROAQ/LogFile",
"LogDate" : "2014-03-14T00:00:00.000+0000",
"LogFileLength" : 2692.0
}, {
"attributes" : {
"type" : "EventLogFile",
"url" : "/services/data/v60.0/sobjects/EventLogFile/0ATD000000001SdOAI" },
"Id" : "0ATD000000001SdOAI",
"EventType" : "API",
"LogFile" :
"/services/data/v60.0/sobjects/EventLogFile/0ATD000000001SdOAI/LogFile",
"LogDate" : "2014-03-13T00:00:00.000+0000",
"LogFileLength" : 1345.0
}, {
"attributes" : {
"type" : "EventLogFile",
"url" : "/services/data/v60.0/sobjects/EventLogFile/0ATD000000003p1OAA" },
"Id" : "0ATD000000003p1OAA",
"EventType" : "API",
"LogFile" :
"/services/data/v60.0/sobjects/EventLogFile/0ATD000000003p1OAA/LogFile",
"LogDate" : "2014-06-21T00:00:00.000+0000",
"LogFileLength" : 605.0 },
{ "attributes" : {
"type" : "EventLogFile",
"url" : "/services/data/v60.0/sobjects/EventLogFile/0ATD0000000055eOAA" },
"Id" : "0ATD0000000055eOAA",
"EventType" : "API",
"LogFile" :
"/services/data/v60.0/sobjects/EventLogFile/0ATD0000000055eOAA/LogFile",
99
REST を使用してイベント監視データを照会する例

===== PAGE 110 =====
"LogDate" : "2014-07-03T00:00:00.000+0000",
"LogFileLength" : 605.0
} ]
}
レコードからイベント監視コンテンツを取得する
特定のレコードの BLOB データを取得するには、sObject Blob Retrieve リソースを使用します。
例
REST API を使用して、イベント監視の BLOB データを取得できます。次のような GET 要求を使用します。
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/EventLogFile/0ATD000000000pyOAA/LogFile
-H "Authorization: Bearer token"
レスポンスボディの例
イベント監視コンテンツがバイナリ形式で返されます。返されたデータがバイナリであるため、応答のコ
ンテンツタイプは JSON でも XML でもありません。
HTTP/1.1 200 OK
Date: Tue, 06 Aug 2013 16:46:10 GMT
Sforce-Limit-Info: api-usage=135/5000
Content-Type: application/octetstream
Transfer-Encoding: chunked
"EVENT_TYPE", "ORGANIZATION_ID", "TIMESTAMP","USER_ID", "CLIENT_IP",
"URI", "REFERRER_URI", "RUN_TIME"
"URI", "00DD0000000K5xD", "20130728185606.020", "005D0000001REDy",
"10.0.62.141", "/secur/contentDoor", "https-//login-salesforce-com/",
"11"
"URI", "00DD0000000K5xD", "20130728185556.930", "005D0000001REI0",
"10.0.62.141", "/secur/logout.jsp", "https-//MyDomainName-my-salesforce-com/00O/o",
"54"
"URI", "00DD0000000K5xD", "20130728185536.725", "005D0000001REI0",
"10.0.62.141", "/00OD0000001ckx3",
"https-//MyDomainName-my-salesforce-com/00OD0000001ckx3", "93"
cURL を REST で使用して大きなイベントログファイルをダウンロード
する
イベントログファイルがツールで処理できないほど大きくなる場合があります。cURL などのコマンドライン
ツールは、sObject Blob Get オブジェクトを使用して 100 MB を超えるファイルをダウンロードする方法の 1 つで
す。
100
レコードからイベント監視コンテンツを取得する例

===== PAGE 111 =====
例: 「X-PrettyPrint」ヘッダーと「-o」フラグを使用して大きなファイルを .csv 形式に出力する
次のコマンドは、ファイルをマシンのダウンロードフォルダーにダウンロードします。
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/EventLogFile/0AT30000000000uGAA/LogFile
-H "Authorization: Bearer token" -H "X-PrettyPrint:1" -o ~/downloads/outputLogFile.csv
大きなイベントログファイルをダウンロードする場合は圧縮することをお勧めします。「圧縮ヘッダー」を参
照してください。
イベント監視データの削除
ユーザーのログデータが含まれるイベントログファイルを削除できます。ログファイルを削除することによっ
て、データ保護とプライバシーに関する規制に準拠し、他のユーザーがアクセス可能な情報を制御できます。
イベントログから個別の行を削除することはできません。代わりに、ユーザーの活動が含まれるログファイル
全体を削除する必要があります。
イベントログファイルを削除するには、「イベント監視レコードを削除」ユーザー権限を含む権限セットを作
成し、この権限セットを自分のユーザーに割り当てます (または、ユーザー権限をカスタムプロファイルに割
り当てることもできます)。これで、これらのユーザーは、REST の Query リソースおよび Delete リソースまたは
SOAP の delete() を使用して、EventLogFile レコードを照会し、削除できます。
メモ: イベントログから個別の行を削除することはできません。データベースでは、イベントログファイ
ルが blob 形式で保存されているため、ユーザーの活動が含まれるログファイル全体を削除する必要があ
ります。
1. [設定] の [クイック検索] ボックスに「イベント」と入力し、[イベント監視設定] を選択します。
2. イベント監視データの削除を有効にします。このアクションは設定変更履歴に記録されます。
「イベント監視レコードを削除」ユーザー権限を権限セットに割り当てられるようになりました (または、
ユーザー権限をカスタムプロファイルに割り当てることもできます)。
3. [設定] の [クイック検索] ボックスに「権限」と入力し、[権限セット] を選択します。
4. 「イベント監視レコードを削除」ユーザー権限を含む権限セットを作成し、権限セットを保存します。
5. [設定] で、[クイック検索] ボックスに「ユーザー」と入力し、[ユーザー] を選択します。
6. イベント監視データの削除を許可するユーザーを選択します。
101
イベント監視データの削除例

===== PAGE 112 =====
7. このユーザーの [権限セットの割り当て] で、権限セットを割り当て、[保存] をクリックします。このアク
ションは設定変更履歴に記録されます。
この権限セット (または「イベント監視レコードを削除」ユーザー権限を含むカスタムプロファイル) に割
り当てられたユーザーがイベント監視データを削除できるようになりました。次のステップでは、API を使
用してデータを削除する方法について説明します。
8. 削除するユーザーの活動が含まれているログを見つけるには、EventLogFile オブジェクトを照会します。詳
細は、「REST を使用してイベント監視データを照会する」 (ページ 99)を参照してください。
9. 返されたログの ID をメモします。
10. レコードを削除するには、sObject Rows リソースを使用します。レコード ID を指定し、DELETE メソッドを使
用します。詳細は「レコードを削除する (ページ 49)」を参照してください。
1 時間ごとのイベントログファイルのクエリまたは表示
エディション
使用可能なエディション:
Enterprise Edition、
Performance Edition、
Unlimited Edition、および
Developer Edition
ユーザ権限
API およびクエリログファ
イルにアクセスする
• 「API の有効化とイベ
ントログファイルの参
照」
イベントログファイルを
参照する
• 「すべてのデータの参
照」
組織のイベントを迅速に確認するには、最近の活動のイベントログファイルを
1 時間ごとに取得します。1 時間ごとのイベントログファイルによってセキュリ
ティの異常やカスタムコードのパフォーマンスの問題をすばやく確認できます。
例
たとえば、ユーザーの異常な行動を監視するセキュリティアナリストであると
します。より頻繁にセキュリティシステムに更新情報を取り込むことで、1 ない
し 2 日後ではなく 1 時間以内に不審なイベントが発生したことのアラートを受け
ることができます。
次の例では、あなたが開発者であるとします。組織の複数の Apex の障害を特定
しており、Apex コードを事前にリファクタリングしてパフォーマンスを改善す
る必要があります。エンドユーザーからパフォーマンスの低下について苦情が
くる前に、1 時間ごとにログファイルを確認して問題を特定し、数時間でコード
を修正します。
考慮事項
• Event Monitoring Analytics アプリケーションと 1 時間ごとのイベントログファイ
ルのインテグレーションは使用できません。
• イベント配信と最終処理時間によっては、イベントの発生時からログファイ
ルでイベントが使用できるようになるまで 3 ～ 6 時間かかることが予想され
ます。ただし、それより長くかかることもあります。
• 処理の遅延が発生し、特定の時間のイベントログの到着が遅れる場合、そのイベント/日付/時間の新しい
ログファイルが作成され、新しいイベントのみがリストされます。新しいログファイルは、作成日と増分
シーケンス番号を使用して特定します。常に、各日付について、最後に処理されたイベントログファイル
を使用します。ただし、イベントログファイルがすでにサードパーティのアプリケーションに取り込まれ
ている場合は、そのアプリケーションで重複排除が必要になる場合があります。
時間ごとのログと日ごとのログの両方が有効になっている場合、日ごとの間隔では 1 つのファイルしか生
成されないため、各日のログシーケンス番号は常に 0 になります。CreatedDate は、ファイルがいつ生成され
たかを示します。CreatedDate が最後のログファイルをダウンロードした日付よりも後の場合は、未処理の
イベントが存在します。
102
1 時間ごとのイベントログファイルのクエリまたは表示例

===== PAGE 113 =====
ベストプラクティスとして、最後にダウンロードされたイベントログファイルの後に作成されたログを選
択するには、WHERE 句で CreatedDate を使用します。たとえば、最後のダウンロードファイルが 2018/02/01 の
PM 12 時の場合、WHERE 句で +CreatedDate+>+"2018-02-01T12:00:00Z" のように記述します。
• イベントログファイルのデータにはギャップが生じる可能性があります。特に、サイト切り替え、インス
タンスリフレッシュ、または計画外のシステム停止時に発生する可能性があります。ただし、サイトの切
り替えやインスタンスの更新の際、Salesforce はこのようなデータの損失を回避する商業上合理的な努力を
行うために、自動化プロセスを使用してイベントログを複製します。
• ごくまれに 24 時間ログファイルが生成されないことがありますが、その場合は Salesforce のサポートにお問
い合わせください。
このセクションの内容:
1 時間ごとのイベントログファイルのクエリ
1 時間ごとのログファイルは、24 時間のログファイルと同じ方法で照会します。
1 時間ごとのイベントログと 24 時間のイベントログの違い
24 時間ごとのイベントログファイルのほかに、約 1 時間ごとのログファイルを受信します。2 つのログの違
いを確認することで、必要なイベントデータを分析できるようにファイルを絞り込めます。
1 時間ごとのイベントログファイルのクエリ
1 時間ごとのログファイルは、24 時間のログファイルと同じ方法で照会します。
あなたはシステム管理者であるとします。最高セキュリティ責任者から、過去 2 時間で特定の取引先と商談を
変更した人を識別するように依頼されました。あなたは、EventLogFile オブジェクトを使用して、1 時間ごとの
URI イベントログファイルを照会し、ページ要求と要求の状況を確認します。EventLogFile からは 24 時間のログ
ファイルも返されるため、SOQL 構文を使用して、24 時間のログファイルを除外します。
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/query?q=SELECT+Id+,
+EventType+,+Interval+,+LogDate+,+LogFile+FROM+EventLogFile+WHERE+EventType+=+'URI'+
AND+Interval+=+'Hourly' -H "Authorization: Bearer token"
クエリの Interval=Hourly は、1 時間ごとのイベントログファイルデータのみが返されるようにするもので
す。または、Sequence を使用して、24 時間のイベントログファイルを除外できます (Sequence!=0)。1 時間
ごとのファイルと 24 時間のファイルの両方を取得するには、Sequence>=0 を使用します。
Sandbox 組織に URI イベントがある場合、クエリ結果にログファイルレコードが表示されます。イベントログ
ファイルをダウンロードして、CSV ファイルでデータを確認することもできます。詳細は、「Trailhead: イベン
トログファイルのダウンロードと視覚化」を参照してください。
1 時間ごとのイベントログと 24 時間のイベントログの違い
24 時間ごとのイベントログファイルのほかに、約 1 時間ごとのログファイルを受信します。2 つのログの違い
を確認することで、必要なイベントデータを分析できるようにファイルを絞り込めます。
103
1 時間ごとのイベントログファイルのクエリまたは表示例

===== PAGE 114 =====
24 時間のログファイル1 時間ごとのログファイル
活動について 24 時間ごとに 1 つのファイルが生成さ
れます。
活動について 1 時間ごとに 1 つ以上のファイルが生成
されます。
API による利用が可能で、Event Monitoring Analytics アプ
リケーションおよびサードパーティの視覚化アプリ
ケーションと統合できます。
API による利用が可能。サードパーティの視覚化アプ
リケーションに手動でデータをインポートできます。
EventLogFile オブジェクトのキー値は、次のとおりで
す。
EventLogFile オブジェクトのキー値は、次のとおりで
す。
• Interval  — Daily• Interval  — Hourly
• CreatedDate  — ログファイルが作成された時間
を示すタイムスタンプ。この項目を使用して、新
しいファイルを識別します。
• CreatedDate  — ログファイルが作成された時間
を示すタイムスタンプ。この項目を使用して、新
しいファイルを識別します。
• LogDate — イベントが発生したときの期間の開始
をマークするタイムスタンプ。たとえば、2016 年
• LogDate — イベントが発生したときの期間の開始
をマークするタイムスタンプ。たとえば、2016 年
3 月 7 日の午前 11:00 ～午後 12:00 の間に発生したイ 3 月 7 日にイベントが発生した場合、この項目の値
は 2016-03-07T00:00:00.000+0000 になります。ベントの場合、この項目の値は
2016-03-07T11:00:00.000Z になります。 • Sequence  — 0
• Sequence  — 1+ 。この値は、最新のイベントログ
ファイルが作成された後に同じ時間にイベントが
追加されると 1 ずつ増加していきます。後続の時
間では値が 1 にリセットされます。
1 時間ごとのイベントログについては、本書の「考慮
事項」も参照してください。
1 日ごとの増分ログファイルが配信されると、その日
に出力されたログをすべて含む新しいファイルで、元
1 時間ごとの増分ログファイルが配信されると、その
時間の新しいログを含むファイルが作成されます。
のファイルが置き換えられます。CreatedDate 項目
が更新されます。
Sequence 項目は、新規ファイルごとに増分されま
す。
メモ:  24 時間のイベント監視と同様に、過去 30 日間の 1 時間ごとのイベントログデータが利用可能です。
複合リソースの使用
このセクションの例では、複合リソースを使用して、クライアントとサーバー間の往復回数を最小限に抑える
ことでアプリケーションのパフォーマンスを高めます。
104
複合リソースの使用例

===== PAGE 115 =====
このセクションの内容:
単一の API コールでの連動要求の実行
次の例では、Composite リソースを使用して、複数の連動要求をすべて単一のコールで実行します。まず取
引先を作成してその情報を取得します。次に、取引先データおよび Composite リソースの参照 ID 機能を使用
して取引先責任者を作成し、取引先データに基づいて項目に値を入力します。その後、要求文字列でクエ
リパラメーターを使用して、取引先の所有者に関する特定の情報を取得します。最後に、特定の日付以降
メタデータが変更された場合は、取引先のメタデータを取得します。composite.json ファイルには、
Composite 要求とサブ要求のデータが含まれます。
取引先の更新、取引先責任者の作成、および連結オブジェクトとのリンク
次の例では、Composite リソースを使用して取引先のいくつかの項目を更新し、取引先責任者を作成し、2
つのレコードを AccountContactJunction という連結オブジェクトとリンクします。これらの要求はす
べて単一のコールで実行されます。composite.json ファイルには、Composite 要求とサブ要求のデータが
含まれます。
1 回の要求でレコードを更新してその項目値を取得する
1 回の API コールで複数の要求を実行するには、Composite Batch リソースを使用します。
取引先の更新/挿入と取引先責任者の作成
次の例では、Composite リソースを使用して取引先を更新/挿入し、取引先にリンクされた取引先責任者を作
成します。これらの要求はすべて単一のコールで実行されます。composite.jsonファイルには、Composite
要求とサブ要求のデータが含まれます。
ネストされたレコードを作成する
sObject Tree リソースを使用して、ルートレコードタイプを共有するネストされたレコードを作成できます。
たとえば、1 回の要求で、取引先とその子取引先責任者、さらに 2 件目の取引先とその子取引先および子取
引先責任者を作成できます。要求が処理されると、レコードが作成され、親と子が自動的に ID でリンクさ
れます。要求データに、レコード階層、必須および省略可能な項目値、各レコードのタイプ、および各レ
コードの参照 ID を指定し、リソースの POST メソッドを使用します。要求が成功すると、レスポンスボディ
には作成されたレコードの ID が含まれます。失敗すると、応答にはエラーが発生したレコードの参照 ID と
エラー情報のみが含まれます。
複数のレコードを作成する
リソースを使用してネストされたレコードを作成できますが、同じタイプで複数の関連しないレコードを
作成することもできます。1 回の要求で最大 200 件のレコードを作成できます。要求データに、各レコード
の必須および省略可能な項目値、各レコードのタイプ、および各レコードの参照 ID を指定し、リソースの
POST メソッドを使用します。要求が成功すると、レスポンスボディには作成されたレコードの ID が含まれ
ます。失敗すると、応答にはエラーが発生したレコードの参照 ID とエラー情報のみが含まれます。
Composite Graph の使用
Composite Graph により、1 回のコールで一連の REST API 要求を実行する Composite 要求の実行が強化されます。
Composite Graph の使用
次の例では、Composite Graph を使用する方法を示します。また、1 つの要求で複数の Composite Graph を使用
できる方法も示します。
105
複合リソースの使用例

===== PAGE 116 =====
Composite 要求および Collections 要求の allOrNone パラメーター
Composite 要求で sObject Collections を使用している場合、相互にやりとりできる 2 つ以上の allOrNone パラ
メーターが存在する場合があります。このパラメーターは Composite 要求と各 sObject Collections サブ要求に 1
つずつあります。
単一の API コールでの連動要求の実行
次の例では、Composite リソースを使用して、複数の連動要求をすべて単一のコールで実行します。まず取引
先を作成してその情報を取得します。次に、取引先データおよび Composite リソースの参照 ID 機能を使用して
取引先責任者を作成し、取引先データに基づいて項目に値を入力します。その後、要求文字列でクエリパラ
メーターを使用して、取引先の所有者に関する特定の情報を取得します。最後に、特定の日付以降メタデータ
が変更された場合は、取引先のメタデータを取得します。composite.json ファイルには、Composite 要求と
サブ要求のデータが含まれます。
単一の API コールでの連動要求の実行
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/composite/ -H
"Authorization: Bearer token -H "Content-Type: application/json" -d "@composite.json"
リクエストボディ composite.json ファイル
{
"allOrNone" : true,
"compositeRequest" : [{
"method" : "POST",
"url" : "/services/data/v60.0/sobjects/Account",
"referenceId" : "NewAccount",
"body" : {
"Name" : "Salesforce",
"BillingStreet" : "Landmark @ 1 Market Street",
"BillingCity" : "San Francisco",
"BillingState" : "California",
"Industry" : "Technology"
}
},{
"method" : "GET",
"referenceId" : "NewAccountInfo",
"url" : "/services/data/v60.0/sobjects/Account/@{NewAccount.id}"
},{
"method" : "POST",
"referenceId" : "NewContact",
"url" : "/services/data/v60.0/sobjects/Contact",
"body" : {
"lastname" : "John Doe",
"Title" : "CTO of @{NewAccountInfo.Name}",
"MailingStreet" : "@{NewAccountInfo.BillingStreet}",
"MailingCity" : "@{NewAccountInfo.BillingAddress.city}",
"MailingState" : "@{NewAccountInfo.BillingState}",
"AccountId" : "@{NewAccountInfo.Id}",
"Email" : "jdoe@salesforce.com",
"Phone" : "1234567890"
}
106
単一の API コールでの連動要求の実行例

===== PAGE 117 =====
},{
"method" : "GET",
"referenceId" : "NewAccountOwner",
"url" :
"/services/data/v60.0/sobjects/User/@{NewAccountInfo.OwnerId}?fields=Name,companyName,Title,City,State"
},{
"method" : "GET",
"referenceId" : "AccountMetadata",
"url" : "/services/data/v60.0/sobjects/Account/describe",
"httpHeaders" : {
"If-Modified-Since" : "Tue, 31 May 2016 18:13:37 GMT"
}
}]
}
Composite 要求の実行が成功した場合のレスポンスボディ
{
"compositeResponse" : [{
"body" : {
"id" : "001R00000033JNuIAM",
"success" : true,
"errors" : [ ]
},
"httpHeaders" : {
"Location" : "/services/data/v60.0/sobjects/Account/001R00000033JNuIAM"
},
"httpStatusCode" : 201,
"referenceId" : "NewAccount"
},{
"body" : {
all the account data
},
"httpHeaders" : {
"ETag" : "\"Jbjuzw7dbhaEG3fd90kJbx6A0ow=\"",
"Last-Modified" : "Fri, 22 Jul 2016 20:19:37 GMT"
},
"httpStatusCode" : 200,
"referenceId" : "NewAccountInfo"
},{
"body" : {
"id" : "003R00000025REHIA2",
"success" : true,
"errors" : [ ]
},
"httpHeaders" : {
"Location" : "/services/data/v60.0/sobjects/Contact/003R00000025REHIA2"
},
"httpStatusCode" : 201,
"referenceId" : "NewContact"
},{
"body" : {
"attributes" : {
"type" : "User",
107
単一の API コールでの連動要求の実行例

===== PAGE 118 =====
"url" : "/services/data/v60.0/sobjects/User/005R0000000I90CIAS"
},
"Name" : "Jane Doe",
"CompanyName" : "Salesforce",
"Title" : Director,
"City" : "San Francisco",
"State" : "CA",
"Id" : "005R0000000I90CIAS"
},
"httpHeaders" : { },
"httpStatusCode" : 200,
"referenceId" : "NewAccountOwner"
},{
"body" : null,
"httpHeaders" : {
"ETag" : "\"f2293620\"",
"Last-Modified" : "Fri, 22 Jul 2016 18:45:56 GMT"
},
"httpStatusCode" : 304,
"referenceId" : "AccountMetadata"
}]
}
取引先の更新、取引先責任者の作成、および連結オブジェクトとの
リンク
次の例では、Composite リソースを使用して取引先のいくつかの項目を更新し、取引先責任者を作成し、2 つの
レコードを AccountContactJunction という連結オブジェクトとリンクします。これらの要求はすべて単
一のコールで実行されます。composite.json ファイルには、Composite 要求とサブ要求のデータが含まれま
す。
取引先の更新、取引先責任者の作成、および連結オブジェクトとのリンク
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/composite/ -H
"Authorization: Bearer token -H "Content-Type: application/json" -d "@composite.json"
リクエストボディ composite.json ファイル
{
"allOrNone" : true,
"compositeRequest" : [{
"method" : "PATCH",
"url" : "/services/data/v60.0/sobjects/Account/001xx000003DIpcAAG",
"referenceId" : "UpdatedAccount",
"body" : {
"Name" : "Salesforce",
"BillingStreet" : "Landmark @ 1 Market Street",
"BillingCity" : "San Francisco",
"BillingState" : "California",
"Industry" : "Technology"
}
},{
108
取引先の更新、取引先責任者の作成、および連結オブ
ジェクトとのリンク
例

===== PAGE 119 =====
"method" : "POST",
"referenceId" : "NewContact",
"url" : "/services/data/v60.0/sobjects/Contact/",
"body" : {
"lastname" : "John Doe",
"Phone" : "1234567890"
}
},{
"method" : "POST",
"referenceId" : "JunctionRecord",
"url" : "/services/data/v60.0/sobjects/AccountContactJunction__c",
"body" : {
"accountId__c" : "001xx000003DIpcAAG",
"contactId__c" : "@{NewContact.id}"
}
}]
}
Composite 要求の実行が成功した場合のレスポンスボディ
{
"compositeResponse" : [{
"body" : null,
"httpHeaders" : { },
"httpStatusCode" : 204,
"referenceId" : "UpdatedAccount"
}, {
"body" : {
"id" : "003R00000025R22IAE",
"success" : true,
"errors" : [ ]
},
"httpHeaders" : {
"Location" : "/services/data/v60.0/sobjects/Contact/003R00000025R22IAE"
},
"httpStatusCode" : 201,
"referenceId" : "NewContact"
}, {
"body" : {
"id" : "a00R0000000iN4gIAE",
"success" : true,
"errors" : [ ]
},
"httpHeaders" : {
"Location" :
"/services/data/v60.0/sobjects/AccountContactJunction__c/a00R0000000iN4gIAE"
},
"httpStatusCode" : 201,
"referenceId" : "JunctionRecord"
}]
}
109
取引先の更新、取引先責任者の作成、および連結オブ
ジェクトとのリンク
例

===== PAGE 120 =====
1 回の要求でレコードを更新してその項目値を取得する
1 回の API コールで複数の要求を実行するには、Composite Batch リソースを使用します。
次の例では、1 回の要求で取引先の名前を更新し、その取引先の複数の項目値を取得します。batch.json
ファイルには、サブ要求データが含まれます。
1 回の要求でレコードを更新してその名前と請求先の郵便番号を照会する
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/composite/batch/ -H
"Authorization: Bearer token -H "Content-Type: application/json" -d "@batch.json"
リクエストボディ batch.json ファイル
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
サブ要求の実行が成功した場合のレスポンスボディ
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
関連トピック:
Composite Batch
110
1 回の要求でレコードを更新してその項目値を取得する例

===== PAGE 121 =====
取引先の更新/挿入と取引先責任者の作成
次の例では、Composite リソースを使用して取引先を更新/挿入し、取引先にリンクされた取引先責任者を作成
します。これらの要求はすべて単一のコールで実行されます。composite.json ファイルには、Composite 要
求とサブ要求のデータが含まれます。
取引先の更新/挿入と取引先責任者の作成
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/composite/ -H
"Authorization: Bearer token -H "Content-Type: application/json" -d "@composite.json"
リクエストボディ composite.json ファイル
{
"allOrNone" : true,
"compositeRequest": [{
"method": "PATCH",
"url": "/services/data/v60.0/sobjects/Account/ExternalAcctId__c/ID12345",
"referenceId": "NewAccount",
"body": {
"Name": "Acme"
}
},{
"method" : "POST",
"url" : "/services/data/v60.0/sobjects/Contact",
"referenceId" : "newContact",
"body" : {
"LastName" : "Harrison",
"AccountId" : "@{NewAccount.id}"
}
}]
}
Composite 要求の実行が成功した場合のレスポンスボディ
{
"compositeResponse" : [{
"body" : {
"id" : "0016g00000Wqu1EAAR",
"success" : true,
"errors" : [ ],
"created" : true
},
"httpHeaders" : {
"Location" : "/services/data/v60.0/sobjects/Account/0016g00000Wqu1EAAR"
},
"httpStatusCode" : 201,
"referenceId" : "NewAccount"
},{
"body" : {
"id" : "0036g00000WKnfLAAT",
"success" : true,
"errors" : [ ]
},
"httpHeaders" : {
111
取引先の更新/挿入と取引先責任者の作成例

===== PAGE 122 =====
"Location" : "/services/data/v60.0/sobjects/Contact/0036g00000WKnfLAAT"
},
"httpStatusCode" : 201,
"referenceId" : "newContact"
}]
}
関連トピック:
sObject Rows by External ID
ネストされたレコードを作成する
sObject Tree リソースを使用して、ルートレコードタイプを共有するネストされたレコードを作成できます。た
とえば、1 回の要求で、取引先とその子取引先責任者、さらに 2 件目の取引先とその子取引先および子取引先
責任者を作成できます。要求が処理されると、レコードが作成され、親と子が自動的に ID でリンクされます。
要求データに、レコード階層、必須および省略可能な項目値、各レコードのタイプ、および各レコードの参照
ID を指定し、リソースの POST メソッドを使用します。要求が成功すると、レスポンスボディには作成された
レコードの ID が含まれます。失敗すると、応答にはエラーが発生したレコードの参照 ID とエラー情報のみが
含まれます。
次の例では、2 セットのネストされたレコードを作成します。最初のセットには、取引先と 2 件の子取引先責
任者レコードが含まれます。2 つ目のセットには、取引先、1 件の子取引先レコード、および 1 件の子取引先
責任者レコードが含まれます。レコードデータは newrecords.json で指定されます。
2 件の新規取引先とその子レコードを作成する例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/composite/tree/Account/
-H "Authorization: Bearer token -H "Content-Type: application/json" -d "@newrecords.json"
2 件の新規取引先とその子レコードを作成するためのリクエストボディ newrecords.json ファイルの例
{
"records" :[{
"attributes" : {"type" : "Account", "referenceId" : "ref1"},
"name" : "SampleAccount1",
"phone" : "1234567890",
"website" : "www.salesforce.com",
"numberOfEmployees" : "100",
"industry" : "Banking",
"Contacts" : {
"records" : [{
"attributes" : {"type" : "Contact", "referenceId" : "ref2"},
"lastname" : "Smith",
"Title" : "President",
"email" : "sample@salesforce.com"
},{
"attributes" : {"type" : "Contact", "referenceId" : "ref3"},
"lastname" : "Evans",
"title" : "Vice President",
"email" : "sample@salesforce.com"
}]
112
ネストされたレコードを作成する例

===== PAGE 123 =====
}
},{
"attributes" : {"type" : "Account", "referenceId" : "ref4"},
"name" : "SampleAccount2",
"phone" : "1234567890",
"website" : "www.salesforce.com",
"numberOfEmployees" : "52000",
"industry" : "Banking",
"childAccounts" : {
"records" : [{
"attributes" : {"type" : "Account", "referenceId" : "ref5"},
"name" : "SampleChildAccount1",
"phone" : "1234567890",
"website" : "www.salesforce.com",
"numberOfEmployees" : "100",
"industry" : "Banking"
}]
},
"Contacts" : {
"records" : [{
"attributes" : {"type" : "Contact", "referenceId" : "ref6"},
"lastname" : "Jones",
"title" : "President",
"email" : "sample@salesforce.com"
}]
}
}]
}
レコードとリレーションが正常に作成された場合のレスポンスボディの例
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
},{
"referenceId" : "ref5",
"id" : "001D000000K0fXQIAZ"
},{
"referenceId" : "ref6",
"id" : "003D000000QV9n4IAD"
}]
}
113
ネストされたレコードを作成する例

===== PAGE 124 =====
要求が処理されると、6 件のレコードすべてが要求に指定された親-子リレーションで作成されます。
関連トピック:
sObject Tree
複数のレコードを作成する
リソースを使用してネストされたレコードを作成できますが、同じタイプで複数の関連しないレコードを作成
することもできます。1 回の要求で最大 200 件のレコードを作成できます。要求データに、各レコードの必須
および省略可能な項目値、各レコードのタイプ、および各レコードの参照 ID を指定し、リソースの POST メソッ
ドを使用します。要求が成功すると、レスポンスボディには作成されたレコードの ID が含まれます。失敗す
ると、応答にはエラーが発生したレコードの参照 ID とエラー情報のみが含まれます。
次の例では、4 件の新規取引先を作成します。レコードデータは newrecords.json で指定されます。
4 件の新規取引先を作成する例
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/composite/tree/Account/
-H "Authorization: Bearer token -H "Content-Type: application/json" -d "@newrecords.json"
4 件の新規取引先を作成する場合のリクエストボディ newrecords.json ファイルの例
{
"records" :[{
"attributes" : {"type" : "Account", "referenceId" : "ref1"},
"name" : "SampleAccount1",
"phone" : "1111111111",
"website" : "www.salesforce.com",
"numberOfEmployees" : "100",
"industry" : "Banking"
},{
"attributes" : {"type" : "Account", "referenceId" : "ref2"},
"name" : "SampleAccount2",
"phone" : "2222222222",
"website" : "www.salesforce2.com",
"numberOfEmployees" : "250",
"industry" : "Banking"
},{
"attributes" : {"type" : "Account", "referenceId" : "ref3"},
"name" : "SampleAccount3",
"phone" : "3333333333",
"website" : "www.salesforce3.com",
"numberOfEmployees" : "52000",
"industry" : "Banking"
},{
"attributes" : {"type" : "Account", "referenceId" : "ref4"},
"name" : "SampleAccount4",
"phone" : "4444444444",
"website" : "www.salesforce4.com",
"numberOfEmployees" : "2500",
"industry" : "Banking"
}]
}
114
複数のレコードを作成する例

===== PAGE 125 =====
レコードが正常に作成された場合のレスポンスボディの例
{
"hasErrors" : false,
"results" : [{
"referenceId" : "ref1",
"id" : "001D000000K1YFjIAN"
},{
"referenceId" : "ref2",
"id" : "001D000000K1YFkIAN"
},{
"referenceId" : "ref3",
"id" : "001D000000K1YFlIAN"
},{
"referenceId" : "ref4",
"id" : "001D000000K1YFmIAN"
}]
}
関連トピック:
sObject Tree
Composite Graph の使用
Composite Graph により、1 回のコールで一連の REST API 要求を実行する Composite 要求の実行が強化されます。
• 通常の Composite 要求では、一連の REST API 要求を単一のコールを実行できます。また、1 つの要求の出力
を、後続の要求の入力として使用できます。
• Composite Graph が通常の Composite 要求を拡張することで、より複雑で完全な一連の関連オブジェクトおよ
びレコードを組み合わせることができるようになります。
• また、Composite Graph によって、特定の一連の要求のステップをすべて完了にするか、またはすべて未終了
にすることができます。このオプションを使用すると、どの要求が成功したかを確認する必要がありませ
ん。
• 通常の Composite 要求では、サブ要求の数は 25 に制限されています。Composite Graph はこの制限を 500 に拡
大します。
Composite Graph の定義
一般に、グラフは接続されたノードのコレクションです。
115
Composite Graph の使用例

===== PAGE 126 =====
Composite Graph 操作のコンテキストでは、ノードは Composite サブ要求です。たとえば、ノードは次のような
Composite サブ要求になる場合があります。
{
"url" : "/services/data/v60.0/sobjects/Account/",
"body" : {
"name" : "Cloudy Consulting"
},
"method" : "POST",
"referenceId" : "reference_id_account_1"
}
各ノードで特徴的なのはレコードを表すエンドポイントです。
Composite Graph 要求は、次の URL のみをサポートします。
サポートされている HTTP メソッドURL
POST
「sObject Basic Information」を参照してください。
/services/data/vXX.X/sobjects/sObject
DELETE、GET、PATCH
「sObject Rows」を参照してください。
/services/data/vXX.X/sobjects/sObject/id
DELETE、GET、PATCH、POST
「sObject Rows by External ID」を参照してください。
/services/data/vXX.X/sobjects/sObject/customFieldName/externalId
Composite Graph は方向付けされる場合があります。つまり、あるノードで他のノードの情報を使用する場合が
あります。たとえば、取引先責任者を作成するノードが取引先ノードの ID を使用して取引先責任者を取引先
に関連付けることができます。
次に例を示します。
{
"graphs": [{
116
Composite Graph の使用例

===== PAGE 127 =====
"graphId": "graph1",
"compositeRequest": [{
"body": {
"name": "Cloudy Consulting"
},
"method": "POST",
"referenceId": "reference_id_account_1",
"url": "/services/data/v60.0/sobjects/Account/"
},
{
"body": {
"FirstName": "Nellie",
"LastName": "Cashman",
"AccountId": "@{reference_id_account_1.id}"
},
"method": "POST",
"referenceId": "reference_id_contact_1",
"url": "/services/data/v60.0/sobjects/Contact/"
}
]
}]
}
JSON での Composite Graph の定義
Composite Graph は JSON で次のように定義されます。
{
"graphId" : "graphId",
graph
}
つまり、次のようになります。ここで、各 compositeSubrequest は Composite サブ要求です。
{
"graphId" : "graphId",
"compositeRequest" : [
compositeSubrequest,
compositeSubrequest,
...
]
}
graphId パラメーターにより、応答を表示するときにグラフを識別できます。数値である必要はありません
が、次の制限に従う必要があります。
• 各 Composite Graph 操作内で一意である必要があります。
• 英数字で始まる必要があります。
• 40 文字未満である必要があります。
• ピリオド (「.」) を含めることはできません。
1 つの Composite Graph 要求で 1 つ以上の Composite Graph を使用できます。「Composite Graph の使用」を参照して
ください。
117
Composite Graph の使用例

===== PAGE 128 =====
例: Composite Graph 要求を使用して Account、Contact、Campaign、Opportunity、
Lead、CampaignMember を作成
この例では、次のアクションを実行する Composite Graph を示します。
1. Account 1 を作成する。
2. Account 1 の子として Account 2 を作成する。
3. 作成:
a. Account 2 にリンクされる Contact 1。
b. Contact 1 の部下である Contact 2。
c. Contact 2 の部下である Contact 3。
4. Campaign を作成する。
5. Account 2 および Campaign にリンクされる Opportunity を作成する。
6. Lead を作成する。
7. Lead および Campaign にリンクされる CampaignMember を作成する。
このグラフの JSON は次のようになります。
{
"graphId" : "1",
"compositeRequest" : [
{
"url" : "/services/data/v60.0/sobjects/Account/",
"body" : {
"name" : "Cloudy Consulting",
"description" : "Parent account"
},
"method" : "POST",
"referenceId" : "reference_id_account_1"
},
{
"url" : "/services/data/v60.0/sobjects/Account/",
"body" : {
"name" : "Easy Spaces",
118
Composite Graph の使用例

===== PAGE 129 =====
"description" : "Child account",
."ParentId" : "@{reference_id_account_1.id}"
},
"method" : "POST",
"referenceId" : "reference_id_account_2"
},
{
"url" : "/services/data/v60.0/sobjects/Contact/",
"body" : {
"FirstName" : "Sam",
"LastName" : "Steele",
"AccountId" : "@{reference_id_account_2.id}"
},
"method" : "POST",
"referenceId" : "reference_id_contact_1"
},
{
"url" : "/services/data/v60.0/sobjects/Contact/",
"body" : {
"FirstName" : "Charlie",
"LastName" : "Dawson",
"ReportsToId" : "@{reference_id_contact_1.id}"
},
"method" : "POST",
"referenceId" : "reference_id_contact_2"
},
{
"url" : "/services/data/v60.0/sobjects/Contact/",
"body" : {
"FirstName" : "Nellie",
"LastName" : "Cashman",
"ReportsToId" : "@{reference_id_contact_2.id}"
},
"method" : "POST",
"referenceId" : "reference_id_contact_3"
},
{
"url" : "/services/data/v60.0/sobjects/Campaign/",
"body" : {
"name" : "Spring Campaign"
},
"method" : "POST",
"referenceId" : "reference_id_campaign"
},
{
"url" : "/services/data/v60.0/sobjects/Opportunity/",
"body" : {
"name" : "Opportunity",
"stageName" : "Value Proposition",
"closeDate" : "2025-12-31",
"CampaignId" : "@{reference_id_campaign.id}",
"AccountId" : "@{reference_id_account_2.id}"
},
"method" : "POST",
119
Composite Graph の使用例

===== PAGE 130 =====
"referenceId" : "reference_id_opportunity"
},
{
"url" : "/services/data/v60.0/sobjects/Lead/",
"body" : {
"FirstName" : "Belinda",
"LastName" : "Mulroney",
"Company" : "Klondike Quarry",
"Email" : "bmulroney@example.com"
},
"method" : "POST",
"referenceId" : "reference_id_lead"
},
{
"url" : "/services/data/v60.0/sobjects/CampaignMember/",
"body" : {
"CampaignId" : "@{reference_id_campaign.id}",
"LeadId" : "@{reference_id_lead.id}"
},
"method" : "POST",
"referenceId" : "reference_id_campaignmember"
}
]
}
例: リソースに関する詳細を GET してから、Composite Graph 要求で使用
この例では、リソースで GET を使用してから、以降の要求でそのリソースのプロパティを使用する方法を示し
ます。
{
"graphs" : [
{
"graphId" : "graph1",
"compositeRequest" : [
{
"method" : "GET",
"url" : "/services/data/v60.0/sobjects/Account/001R0000003fSRrIAM",
"referenceId" : "refAccount"
},
{
"body" : {
"name" : "Amazing opportunity for @{refAccount.Name}",
"StageName" : "Stage 1",
"CloseDate" : "2025-06-01T23:28:56.782Z",
"AccountId" : "@{refAccount.Id}"
},
"method" : "POST",
"url" : "/services/data/v60.0/sobjects/Opportunity",
"referenceId" : "newOpportunity"
}
]
}
120
Composite Graph の使用例

===== PAGE 131 =====
]
}
グラフ深度
• 親を持たないノードは深度 1 とみなされます。
• もう 1 つのノードの深度は深度 1 からそのノードまでのグラフのエッジの最大数です。2 つのノード間の
エッジは、1 つのノードでもう 1 つのノードのプロパティ (@{reference_account.id} など) を使用して
いる場合に発生します。
AllOrNone パラメーター
標準のComposite 操作では、エラーが発生した場合の動作を制御するのは allOrNone パラメーターのみです。
値が true の場合、Composite 要求全体がロールバックされます。値が false の場合、失敗したサブ要求に連
動しない残りのサブ要求が実行されます。連動サブ要求が実行されないため、処理済みのレコードと未処理の
レコードが混在する場合があります。
Composite Graph には、各グラフがそのすべてのサブ要求を正常に完了するか、または完全にロールバックされ
るかが保証されるという利点があります。つまり、allOrNone パラメーターは暗黙的に各グラフで true に
なっているとみなされます。Composite Graph 要求で、処理済みのレコードと未処理のレコードが混在すること
はありません。
グラフの独立性を確保するために、次のルールが適用されます。
1. 1 つのグラフのサブ要求がもう 1 つのグラフのサブ要求を参照することはない。
2. 1 つの Composite Graph 操作の各グラフは独立している必要がある。1 つのグラフを正常に処理できなかった
場合、それによって同じ操作内の他のグラフの処理が妨げられるようなことがあってはなりません。
ベストプラクティス
一般にグラフは、できるだけ小さくしてください。たとえば、500 個のノードを含む 1 個のグラフを作成する
よりも、10 個のノードを含む 50 個のグラフを作成した方が効率的です。グラフを小さくすることには、次の
2 つの利点があります。
• あるグラフ内で 1 つの項目が失敗した場合、ロールバックされるのは、そのグラフ内の項目のみです。小
さいグラフの方が、エラーの特定や対処が容易です。
• サーバーでグラフを処理するときは、グラフを複数に分けて小さくした方が、処理の速度や効率が向上し
ます。
121
Composite Graph の使用例

===== PAGE 132 =====
例: Composite Graph ジョブの送信
Composite Graph ジョブを送信する方法を示す例については、「Composite Graph の使用」を参照してください。
Composite Graph の使用
次の例では、Composite Graph を使用する方法を示します。また、1 つの要求で複数の Composite Graph を使用でき
る方法も示します。
• 通常の Composite 要求では、一連の REST API 要求を単一のコールを実行できます。また、1 つの要求の出力
を、後続の要求の入力として使用できます。
• Composite Graph が通常の Composite 要求を拡張することで、より複雑で完全な一連の関連オブジェクトおよ
びレコードを組み合わせることができるようになります。
• また、Composite Graph によって、特定の一連の要求のステップをすべて完了にするか、またはすべて未終了
にすることができます。このオプションを使用すると、どの要求が成功したかを確認する必要がありませ
ん。
• 通常の Composite 要求では、サブ要求の数は 25 に制限されています。Composite Graph はこの制限を 500 に拡
大します。
要求を作成します。
curl -X POST curl https://MyDomainName.my.salesforce.com/services/data/v60.0/composite/graph
-H "Authorization: Bearer token" -H "Content-Type: application/json" --data @data.json
ここで、data.json ファイルにはグラフの定義が含まれます。リクエストボディの一般的な形式を次に示し
ます。
{
"graphs": [
{
"graphId": "graphId",
"compositeRequest": [
compositeSubrequest,
compositeSubrequest,
...
]
},
{
"graphId": "graphId",
"compositeRequest": [
compositeSubrequest,
compositeSubrequest,
...
]
},
...
]
}
ここで、compositeSubrequest は Composite サブ要求の結果 (ページ 395)です。
122
Composite Graph の使用例

===== PAGE 133 =====
たとえば、2 つの Composite Graph 要求でそれぞれ取引先を作成してから、関連レコードを作成します。
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
123
Composite Graph の使用例

===== PAGE 134 =====
},
"method" : "POST",
"referenceId" : "reference_id_contact_2"
}
]
}
]
}
応答は次のようになります。
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
"Location" : "/services/data/v60.0/sobjects/Account/001R00000064wc7IAA"
},
"httpStatusCode" : 201,
"referenceId" : "reference_id_account_1"
},
{
"body" : {
"id" : "003R000000DDMlTIAX",
"success" : true,
"errors" : [ ]
},
"httpHeaders" : {
"Location" : "/services/data/v60.0/sobjects/Contact/003R000000DDMlTIAX"
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
124
Composite Graph の使用例

===== PAGE 135 =====
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
"Location" : "/services/data/v60.0/sobjects/Account/001R00000064wc8IAA"
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
"Location" : "/services/data/v60.0/sobjects/Contact/003R000000DDMlUIAX"
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
詳細は、「Composite Graph の使用」を参照してください。
Composite 要求および Collections 要求の allOrNone パラメーター
Composite 要求で sObject Collections を使用している場合、相互にやりとりできる 2 つ以上の allOrNone パラメー
ターが存在する場合があります。このパラメーターは Composite 要求と各 sObject Collections サブ要求に 1 つずつ
あります。
• Composite 要求で allOrNone が true に設定されている場合、オールオアナッシングの動作は各 sObject
Collections サブ要求にも適用され、サブ要求の allOrNone の値が上書きされます。
125
Composite 要求および Collections 要求の allOrNone パラ
メーター
例

===== PAGE 136 =====
• Composite 要求で allOrNoneが false に設定されている場合、各 sObject Collections サブ要求はその allOrNone
の値に従って動作します。
たとえば、Composite 要求に sObject Collections 要求と取引先責任者を作成するための要求の 2 つの項目が含まれ
ているジョブで何が起こるかを考えてみましょう。sObject Collections 要求では 2 つの取引先を作成しようとしま
すが、そのうちの 1 つはすでに同じ情報の既存の取引先があるため失敗します。
POST https://MyDomainName.my.salesforce.com/services/data/v60.0/composite -H "Authorization:
Bearer token"
{
"allOrNone" : outerFlag,
"collateSubrequests" : false,
"compositeRequest" : [
{
"method" : "POST",
"url" : "/services/data/v60.0/composite/sobjects",
"body" : {
"allOrNone" : innerFlag,
"records" : [
{
"attributes" : { "type" : "Account" },
"Name" : "Northern Trail Outfitters",
"BillingCity" : "San Francisco"
},
{
"attributes" : { "type" : "Account" },
"Name" : "Easy Spaces",
"BillingCity" : "Calgary"
}
]
},
"referenceId" : "newAccounts"
},
{
"method" : "POST",
"url" : "/services/data/v60.0/sObject/Contact",
"body" : {
"FirstName" : "John",
"LastName" : "Smith"
},
"referenceId" : "newContact"
}
]
}
outerFlag パラメーターおよび innerFlag パラメーターは true または false であり、これによって 4 つ
のケースが考えられます。
ケース 1: outerFlag  = false、innerFlag  = false
この場合、どちらの要求でも allOrNone が true に設定されていないため、どちらの要求もロールバックさ
れません。1 つの取引先が作成され、1 つは失敗します。
126
Composite 要求および Collections 要求の allOrNone パラ
メーター
例

===== PAGE 137 =====
ケース 2: outerFlag  = false、innerFlag  = true
この場合、内側の sObject Collections 要求では allOrNone が true に設定されているため、ロールバックされま
す。外側の Composite 要求はロールバックされません。
ケース 3: outerFlag  = true、innerFlag  = true
この場合、両方の要求で allOrNone が true に設定されているため、両方の要求がロールバックされます。
127
Composite 要求および Collections 要求の allOrNone パラ
メーター
例

===== PAGE 138 =====
ケース 4: outerFlag  = true、innerFlag  = false
このケースのレスポンスボディは次のようになります。
{
"compositeResponse" : [
{
"body" : [
{
"id" : "001R00000066cndIAA",
"success" : true,
"errors" : [ ]
},
{
"success" : false,
"errors" : [
{
"statusCode" : "DUPLICATES_DETECTED",
"message" : "Use one of these records?",
"fields" : [ ]
}
]
}
],
"httpHeaders" : { },
"httpStatusCode" : 200,
"referenceId" : "collection1"
},
{
"body" : [
{
"errorCode" : "PROCESSING_HALTED",
"message" : "The transaction was rolled back since another operation in the
same transaction failed."
}
],
"httpHeaders" : { },
"httpStatusCode" : 400,
"referenceId" : "newContact"
128
Composite 要求および Collections 要求の allOrNone パラ
メーター
例

===== PAGE 139 =====
}
]
}
この場合、内側の sObject Collections 要求では allOrNone が false に設定されているため、すぐにはロール
バックされません。ただし、外側の Composite 要求では allOrNone が true に設定されているため、ロール
バックされ、これによって内側の sObject Collections 要求もロールバックされます。
メモ:  sObject Collections 要求のレスポンスボディで最初の取引先の作成で "success" : true と示されて
いる場合であっても、Composite 要求がロールバックされるため、取引先の作成がロールバックされるこ
とになります。最終的な結果として、新規の取引先は作成されません。
129
Composite 要求および Collections 要求の allOrNone パラ
メーター
例
