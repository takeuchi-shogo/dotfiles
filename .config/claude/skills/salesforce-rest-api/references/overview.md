# REST API の概要（アーキテクチャ・認証・ヘッダー・エラー応答）

> 出典: Salesforce『REST API 開発者ガイド』日本語版 (api_rest.pdf, 2026-03-31 生成, Spring '26 相当)
> PDF ページ 11–32。pypdf による自動抽出テキストのため、表組みのレイアウトが崩れている場合がある。

## 収録セクション

- REST API の概要 (PAGE 11)
  - REST API について (PAGE 12)
  - リリースノート (PAGE 12)
  - サポートされているエディションと必要な権限 (PAGE 12)
  - REST リソースと要求 (PAGE 13)
  - REST API のアーキテクチャ (PAGE 15)
  - 接続アプリケーションおよび OAuth 2.0 による認証 (PAGE 17)
  - ヘッダー (PAGE 17)
  - cURL を使用した REST 要求の送信 (PAGE 26)
  - Salesforce CORS 許可リストの設定 (PAGE 28)
  - Date および DateTime の有効な書式 (PAGE 29)
  - 状況コードとエラー応答 (PAGE 30)
  - API の有効期限のポリシー (PAGE 31)

---

===== PAGE 11 =====
第 1 章 REST API の概要
REST API によって、Salesforce のデータにプログラムを使用してアクセスできます。REST
API は柔軟性と拡張性に優れているため、Salesforce をアプリケーションに統合した
り、大規模で複雑な操作を行ったりするときには最善の選択肢となります。
トピック:
• REST API について
• REST API リリース
ノート このガイドでは、リリース環境の設定や、データアクセスに関するための高度な詳
細情報について説明します。ただし、REST API を理解および使用するには、ソフト• サポートされてい
るエディションと
必要な権限
ウェア開発、Web サービス、および Salesforce ユーザーインターフェースについての
基本的な知識が必要です。
すぐに使用する場合には、基本的な起動や実行方法が説明されているクイックスター
トガイドを参照してください。
• REST リソースと要
求
Salesforce API についてさらに詳しく確認したい場合は、リンクのリストを参照してく
ださい。
• REST API のアーキテ
クチャ
• 接続アプリケー
ションおよび OAuth
2.0 による認証
ヒント:  Salesforce REST API は、Salesforce オブジェクトと連携するように設計され
ています。Salesforce オブジェクトの概要と詳細な情報については、『Salesforce
プラットフォームのオブジェクトリファレンス』を参照してください。
• ヘッダー
関連トピック:
Trailhead: Lightning プラットフォーム API の基礎
• cURL を使用した
REST 要求の送信
• Salesforce CORS 許
可リストの設定
• Date および
DateTime の有効な
書式
• 状況コードとエ
ラー応答
• API の有効期限のポ
リシー
1

===== PAGE 12 =====
REST API について
REST API は Web インターフェースの 1 つであり、Salesforce のユーザーインターフェースを使用することなく
Salesforce データにアクセス可能になります。API アクセスによって、自由に操作を実行したり、Salesforce をアプ
リケーションに統合したりできます。
REST API ツールを使用して、Salesforce のエンドポイントに HTTP 要求を送信することで、Salesforce のデータを作
成、操作、および検索できます。要求を送信する場所に応じて、異なる情報 (リソースと呼びます) にアクセス
し、操作を行います。リソースには、レコード、クエリ結果、メタデータなどがあります。
REST API は、RESTful アーキテクチャを利用して、わかりやすく一貫したインターフェースを提供しています。
REST API 最大の利点は、データのアクセスにツールがさほど必要にならないことです。SOAP API よりも操作はシ
ンプルですが、豊富な機能を備えています。
REST API はレコードへのアクセスとクエリに適しています。一方、他の Bulk 2.0 API、Metadata API、Connect REST API
などの Salesforce API は、特定のタスクに対応する追加機能を提供します。
関連トピック:
REST リソースと要求
REST API のアーキテクチャ
REST API リリースノート
REST API の最新の更新や変更点については、Salesforce のリリースノートを参照してください。
REST API を含む Salesforce Platform に影響する更新や変更については、API のリリースノートを参照してください。
REST API 専用の新しいコール、変更されたコール、および廃止されたコールとその他の変更点については、
Salesforce リリースノートの「REST API」を参照してください。
サポートされているエディションと必要な権限
Salesforce API を使用して Salesforce の組織やデータにアクセスするには、API アクセスが有効な組織とユーザーの
両方が必要です。API アクセスをサポートする Salesforce Edition は複数あり、ユーザーに API への権限を付与する
方法もいくつかあります。
API アクセスをサポートするエディション
API アクセスは、Enterprise Edition、Performance Edition、Unlimited Edition、Developer Edition の組織でデフォルトで有
効になっています。Professional Edition の組織では、アドオンとして API アクセスを追加できます。詳細は、
「Salesforce ヘルプ: Your Account アプリケーションを使用した製品とライセンスの追加」を参照するか、Salesforce
のアカウントエグゼクティブにお問い合わせください。
API アクセスが可能でない組織に API 要求を送信した場合、Salesforce は API_DISABLED_FOR_ORG エラーを返し
ます。
2
REST API についてREST API の概要

===== PAGE 13 =====
本番組織の設定とライブデータを保護するために、動的な開発やテストには、Developer Edition 組織、Sandbox、
またはスクラッチ組織のような分離された環境を使用することをお勧めします。準備ができたら、成功した変
更を本番組織に移行できます。
API ユーザー権限
API コールを行うには、ユーザーが割り当てられているユーザープロファイルで「API の有効化」権限が有効に
なっている必要があります。この権限は、一部のプロファイルではデフォルトで有効になっています。たとえ
ば、Developer Edition 組織にある多くのプロファイルで有効になっています。また、サポートされているエディ
ションでは、Salesforce インテグレーションユーザーライセンスを使用して、システム間インテグレーション
ユーザーに組織への完全なアクセス権を与えながら、操作は API のみに制限することができます。詳細は、
Salesforce ヘルプの「インテグレーションユーザーへの API 限定アクセス権の付与」を参照してください。
関連トピック:
自分専用の Developer Edition を入手する
スクラッチ組織
Sandbox
Salesforce DX 開発者ガイド
REST リソースと要求
REST API は、リソースの使用状況に基づいています。リソースは、レコード、レコードのコレクション、クエ
リ結果、メタデータ、API 情報など、Salesforce のデータの一部を表します。各リソースは URI (Uniform Resource
Identifier) で公開され、対応する URI に HTTP 要求を送信することでアクセスできます。
どのリソースにアクセスするかと、どのように HTTP 要求を作成するかに応じて、次のような何種類かの操作
を実行できます。
• 利用可能な API バージョンの決定
• Salesforce 組織のアクセス制限
• オブジェクトのメタデータの取得
• レコードの作成、参照、更新、および削除
• データの照会と検索
HTTP 要求はさまざまなソフトウェアツールによって送信できるため、要求の実際の内容が、このガイドの cURL
の例とは異なる場合があります。ただし、どのように要求を送信しても、その要素は変わりません。一般的な
要求は、次の要素から構成されます。
• URI
• HTTP のメソッド
• ヘッダー
• リクエストボディ (GET 要求の場合は必須ではない)
3
REST リソースと要求REST API の概要

===== PAGE 14 =====
URI
URI は、Salesforce のリソースへのパスです。URI はリソースごとに変わりますが、基本的な構造は同じです。
https://MyDomainName.my.salesforce.com/services/data/vXX.X/resource/
https:// を使用して安全にリソースにアクセスします。
MyDomainName は自分の Salesforce 組織のサブドメインで置き換えてください。Salesforce は複数のサーバーイン
スタンス上で動作するため、このガイドの例では特定のインスタンスの代わりに MyDomainName を使用して
います。
XX.X は、使用する API のバージョンに置き換えます。利用可能なバージョンのリストについては、「バージョ
ン」 (ページ 141)リソースにアクセスして確認できます。
resource をリソースへのパスの残り部分に置き換えます。リソースによっては、特定のレコードを識別する
ための ID などのパラメーターをパスに含めることができます。各リソースの URI は、このガイドの「リファレ
ンス」セクションで確認できます。
sObject リソースは、Salesforce の標準オブジェクトやカスタムオブジェクトへアクセスします。オブジェクトに
ついての詳細は、『Salesforce プラットフォームのオブジェクトリファレンス』を参照してください。
メモ:  URI の一部分には、ID のように大文字と小文字が区別される部分があります。他のオブジェクト名
や項目名などの URI の部分は大文字と小文字が区別されません。要求が正常に処理されない場合は、URI
をこのガイドの例と比較して、大文字と小文字が正しく入力されているかどうかを確認してください。
HTTP のメソッド
REST API は、https://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html の仕様に従った標準の HTTP 要求メソッド (HEAD、
GET、POST、PATCH、PUT、DELETE) をサポートしています。
各メソッドの目的は、リソースによって異なります。各メソッドを使用する方法やタイミングについては、本
ガイドの「リファレンス」セクションにある該当するリソースのページを確認してください。
ヘッダー
ヘッダーは、HTTP 要求のパラメーターを渡したり、オプションをカスタマイズしたりするために使用します。
REST API では、いくつかの標準の HTTP ヘッダーに加えて、Salesforce 固有のカスタムヘッダーもサポートされて
います。
例で使用されている、一般的なヘッダーは次のとおりです。
• HTTP Accept — クライアントが受け入れるレスポンスボディの形式を示します。可能な値は
application/json および application/xml です。値が欠落しているか、誤った形式である場合、デ
フォルトでは application/json が使用されます。
• HTTP Content-type — 要求に添付するリクエストボディの形式を示します。可能な値は application/json
および application/xml です。
• HTTP Authorization — クライアントを認証するための OAuth 2.0 アクセストークンを提供します。REST API では、
Bearer 認証タイプがサポートされています。
4
REST リソースと要求REST API の概要

===== PAGE 15 =====
• 圧縮ヘッダー — 要求または応答を圧縮します。詳細は、「圧縮ヘッダー」 (ページ 10)を参照してくださ
い。
• 条件付き要求ヘッダー — アクセスしたレコードを前提条件と照らし合わせて検証します。詳細は、「条件
付き要求ヘッダー」 (ページ 11)を参照してください。
リクエストのボディ
リクエストボディとは、要求に含めることができるリッチ入力のことで、レコードの作成や更新のための項目
値など追加の情報を指定できます。リクエストボディには、JSON 形式または XML 形式を使用できます。
メモ:  GET メソッドでアクセスするリソースには、リクエストボディを添付する必要はありません。
HTTP Content-Type ヘッダーは、リクエストボディのファイル形式を示すために使用します。cURL を使用して要
求を送信する場合は、—data-binary または -d オプションを使用して、JSON または XML ファイルを要求に添
付します。
関連トピック:
cURL を使用した REST 要求の送信
Java 開発者環境の設定
REST API のアーキテクチャ
REST API は、RESTful の標準的な原則に従い、その特性を備えています。
クライアントサーバー
クライアントアプリケーションは、Salesforce REST API から独立しているため、それぞれが個別に管理および
更新されます。
ステートレス
クライアントからサーバーへの各要求には、要求を理解するのに必要なすべての情報が含まれている必要
があります。サーバーに格納されたコンテキストは使用しないでください。ただし、リソースの表現は URI
を使用して相互接続されるため、クライアントは状態が変わっても進行できます。
キャッシュの動作
応答にはキャッシュ可能かどうかを示すラベルが付加されます。
統一されたインターフェース
すべてのリソースには、HTTPS を介した汎用インターフェースを使用してアクセスします。
名前付きリソース
すべてのリソースには、Lightning Platform エンドポイントの後にベース URI を続けた形式で名前が付けられま
す。詳細情報と具体的な例については、「REST リソースと要求」を参照してください。
階層化されたコンポーネント
クライアントとサーバーの間には、プロキシサーバーやゲートウェイなどを介すことができます。
REST API には、標準的な RESTful の原則に加えて、重要な特性がアーキテクチャに組み込まれており、アプリケー
ションを開発する際に理解および考慮する必要があります。
5
REST API のアーキテクチャREST API の概要

===== PAGE 16 =====
認証
REST API では、OAuth 2.0 (セキュアな API 認証を可能にするオープンプロトコル) がサポートされています。詳
細は、Salesforce ヘルプの「OAuth によるアプリケーションの認証」を参照してください。
JSON および XML のサポート
UTF-8 の JSON 要求がサポートされます。この要求がデフォルトです。UTF-8 と UTF-16 の XML 要求がサポート
されます。XML 応答は UTF-8 で提供されます。HTTP ACCEPT ヘッダーを使用して、JSON と XML のいずれか
を指定できます。
バージョン 57.0 以前では、URI に json や xml を付加できます。例: /Account/001D000000INjVe.json。
ただし、推奨されるのは HTTP ACCEPT ヘッダーを使用して、JSON または XML を指定することです。
バージョン 58.0 以降では、URI に JSON や XML を付加することはサポートされていません。
圧縮
圧縮は、帯域幅の負荷を軽減します。この目的で REST API とクライアントの間で送信されるメッセージは圧
縮されます。REST API では HTTP 1.1 仕様での定義に従い、gzip と deflate の圧縮をサポートしています。「圧縮
ヘッダー」を参照してください。
条件付き要求
応答のキャッシュは、いくかの例外を除いて、HTTP 1.1 の仕様で定義された標準に準拠する条件付き要求
ヘッダーによってサポートされています。「条件付き要求ヘッダー」を参照してください。
クロスオリジンリソース共有
クロスオリジンリソース共有 (CORS) を使用すると、Web ブラウザーで他のオリジンからのリソースを要求
できます。たとえば、CORS を使用すると、https://www.example.com にある JavaScript コードで
https://www.salesforce.com からのリソースを要求できます。Web ブラウザーで JavaScript から、サポートされて
いる Salesforce API、Apex REST リソース、および Lightning Out にアクセスするには、コードを提供するオリジ
ンを Salesforce CORS 許可リストに追加します。「Web ブラウザーからのクロスオリジン要求の実行」を参照
してください。
Salesforce ID の長さ
レスポンスボディでの Salesforce ID は常に 18 文字です。リクエストボディでは、15 文字または 18 文字の ID
を使用できます。
メソッドの上書き
使用する HTTP ライブラリで任意の HTTP メソッド名の上書きまたは設定が許可されていない場合に HTTP メ
ソッドを上書きするには、要求パラメーター _HttpMethod を使用します。
POST https://instance_name/services/data/v60.0/chatter/
/chatter/users/me/conversations/03MD0000000008KMAQ
?_HttpMethod=PATCH&read=true
メモ: _HttpMethod パラメーターでは、大文字と小文字が区別されます。すべての値で大文字と小文
字を正しく区別してください。
HTTPS
クライアントとサーバー間の通信はすべて HTTPS で行います。
6
REST API のアーキテクチャREST API の概要

===== PAGE 17 =====
接続アプリケーションおよび OAuth 2.0 による認証
クライアントアプリケーションが REST API リソースにアクセスするには、クライアントアプリケーションが安
全な訪問者として認証される必要があります。この認証を実装するには、接続アプリケーションおよび OAuth
2.0 認証フローを使用します。
接続アプリケーションの設定
接続アプリケーションは、クライアントアプリケーションの代わりに REST API リソースへのアクセスを要求し
ます。接続アプリケーションがアクセスを要求するためには、OAuth 2.0 プロトコルを使用して組織の REST API
に統合されている必要があります。OAuth 2.0 は、トークンの交換を通してアプリケーション間の安全なデータ
共有を認証するオープンプロトコルです。
接続アプリケーションの設定手順は、Salesforce ヘルプの「接続アプリケーションの作成」を参照してくださ
い。具体的には、「API インテグレーション用の OAuth 設定の有効化」の手順に従います。
OAuth 認証フローの適用
OAuth 認証フローは、クライアントアプリケーションにリソースサーバーの REST API リソースへの制限付きア
クセス権を付与します。クライアントアプリケーションへのアクセスを承認するプロセスは各 OAuth フローで
異なりますが、一般的なフローは 3 つの主要なステップで構成されます。
1. クライアントアプリケーションの代わりに、接続アプリケーションが認証フローを開始するために REST API
リソースへのアクセスを要求します。
2. 応答として、認証サーバーはアクセストークンを接続アプリケーションに付与します。
3. リソースサーバーは、これらのアクセストークンを検証し、保護された REST API リソースへのアクセスを承
認します。
OAuth 認証フローを確認および選択して、接続アプリケーションに適用します。サポートされる各フローにつ
いての詳細は、Salesforce ヘルプの「OAuth 認証フロー」を参照してください。
その他のリソース
Salesforce は、接続アプリケーションと OAuth の理解に役立つ次のリソースを用意しています。
• Salesforce ヘルプ: 接続アプリケーション
• Salesforce ヘルプ: OAuth によるアプリケーションの認証
• Salesforce ヘルプ: OpenID Connect トークンイントロスペクション
• Trailhead: 接続アプリケーションを使用してインテグレーションを構築する
ヘッダー
REST API は、要求ヘッダーと応答ヘッダーの両方を含む、いくつかの標準およびカスタム HTTP ヘッダーをサ
ポートしています。
7
接続アプリケーションおよび OAuth 2.0 による認証REST API の概要

===== PAGE 18 =====
このセクションの内容:
Assignment Rule ヘッダー
Assignment Rule ヘッダーは、取引先、ケース、またはリードの作成時または更新時に適用される要求ヘッ
ダーです。有効化されていると、有効な割り当てルールが使用されます。無効化されていると、有効な割
り当てルールは適用されません。有効な AssignmentRule ID が指定されていると、AssignmentRule が適用されま
す。要求にヘッダーが指定されていないと、REST API のデフォルトにより有効な割り当てルールが使用され
ます。
Call Options ヘッダー
REST API リソースにアクセスするために使用するクライアントのオプションを指定します。たとえば、デ
フォルトの名前空間プレフィックスを指定すれば、コードにプレフィックスを指定する必要はありません。
圧縮ヘッダー
REST API の要求や応答を圧縮するには、圧縮ヘッダーを使用します。圧縮によって、要求に必要な帯域幅を
減らせますが、クライアント側ではより多くの処理能力が必要になります。ほとんどの場合、この負荷の
移動によって、アプリケーションの全体的なパフォーマンスが向上します。
条件付き要求ヘッダー
リソースにアクセスする前に検証するには、条件付き要求ヘッダーを使用します。ヘッダーに前提条件を
設定することで、その前提条件を満足する場合にのみ要求が成功するようになります。この機能により、
Salesforce のデータを更新する際に、ミスを防止したり、古い要求を拒否できるようになります。条件付き
要求ヘッダーには、応答のキャッシュなどのさまざまな手法を実装できます。
重複ルールヘッダー
重複ルールのオプションを設定します。Salesforce は、重複ルールを使用して、作成、更新、または更新/挿
入されるレコードが既存のレコードと重複していないかを確認します。重複ルールは重複管理の一部です。
Limit Info ヘッダー
この応答ヘッダーは、REST API への各要求で返されます (ただし、バージョン URI、/ へのコールを除きます。
これは組織の制限に含まれないためです)。この情報を使用して API 制限を監視できます。
MRU ヘッダー
作成、更新、更新/挿入、取得されたレコードで最後に使用した (MRU) 項目が更新されるかどうかを定義し
ます。MRU 項目は Salesforce ユーザーインターフェースのサイドバーの [最近使ったデータ] セクションに表
示されます。このヘッダーは、API バージョン 60.0 以降で使用できます。
Package Version ヘッダー
クライアントによって参照される各パッケージのバージョンを指定します。パッケージバージョンは、パッ
ケージに含まれる一連のコンポーネントと動作を識別する番号です。このヘッダーは、Apex REST Web サー
ビスをコールするときのパッケージバージョンの指定にも使用されます。
Query Options ヘッダー
クエリ結果のバッチサイズなど、クエリで使用するオプションを指定します。この要求ヘッダーは、Query
リソースで使用します。
Warning ヘッダー
このヘッダーは、警告が発生した場合に返されます。たとえば、非推奨バージョンの API を使用すると、こ
のヘッダーが返されます。
8
ヘッダーREST API の概要

===== PAGE 19 =====
Assignment Rule ヘッダー
Assignment Rule ヘッダーは、取引先、ケース、またはリードの作成時または更新時に適用される要求ヘッダー
です。有効化されていると、有効な割り当てルールが使用されます。無効化されていると、有効な割り当て
ルールは適用されません。有効な AssignmentRule ID が指定されていると、AssignmentRule が適用されます。要求
にヘッダーが指定されていないと、REST API のデフォルトにより有効な割り当てルールが使用されます。
メモ: このヘッダーは、結果として取引先、ケース、またはリードの作成または更新に間接的に繋がる
REST API コールが実行されると適用されます。たとえば、1 つのレコードを更新するコールにこのヘッダー
を使用し、その更新によって 1 つのケースを更新する Apex トリガーが実行されると、この割り当てルー
ルが適用されます。
ヘッダーの項目名と値
項目名
Sforce-Auto-Assign
項目値
• TRUE。作成済みまたは更新済みの取引先、ケース、またはリードに、有効な割り当てルールが適用さ
れます。
• FALSE。作成済みまたは更新済みの取引先、ケース、またはリードに、有効な割り当てルールは適用さ
れません。
• 有効な AssignmentRule ID。作成済みの取引先、ケース、またはリードに、指定の AssignmentRule が適用さ
れます。
TRUE と FALSE では、大文字と小文字は区別されません。
要求にヘッダーが指定されていない場合、デフォルト値は TRUE です。
例
Sforce-Auto-Assign: FALSE
Call Options ヘッダー
REST API リソースにアクセスするために使用するクライアントのオプションを指定します。たとえば、デフォ
ルトの名前空間プレフィックスを指定すれば、コードにプレフィックスを指定する必要はありません。
Call Options ヘッダーは、sObject Basic Information、sObject Rows、sObject Rows by External ID、Query、QueryAll、および
Search で使用できます。Bulk API および Bulk API 2.0 でもサポートされます。
ヘッダーの項目名と値
項目名
Sforce-Call-Options
項目値
• client  — 要求を送信するクライアントの識別子として使用される文字列。この文字列はログファイル
に表示され、要求を送信したクライアントを追跡するのに役立ちます。
9
Assignment Rule ヘッダーREST API の概要

===== PAGE 20 =====
• defaultNamespace  — 要求のデフォルト名前空間として使用される開発者名前空間プレフィックス。
要求では、このヘッダー項目を使用して、名前空間を指定せずに管理パッケージの項目名が解決されま
す。(Bulk API ではサポートされません。)
例
開発者名前空間プレフィックスが battle で、パッケージに botId というカスタム項目がある場合、デフォ
ルトの名前空間に次のコールオプションヘッダーを設定します。
Sforce-Call-Options: client=caseSensitiveToken; defaultNamespace=battle
その後で次のようなクエリを実行します。
/services/data/vXX.X/query/?q=SELECT+Id+botID__c+FROM+Account
この場合、実際に照会される項目は、battle__botId__c です。
このヘッダーを使用すると、名前空間プレフィックスを指定せずにクライアントコードを作成することができ
ます。上の例でヘッダーを使用しない場合は、battle__botId__c を記述する必要があります。
この項目が設定され、クエリでも名前空間を指定している場合、応答にはプレフィックスは含まれません。た
とえば、このヘッダーを battle に設定し、SELECT+Id+battle__botID__c+FROM+Account のようなクエ
リを発行すると、応答は battle_botId__c 要素ではなく、botId__c 要素を使用します。
describe 情報を取得するときに defaultNamespace 項目は無視されるため、名前空間プレフィックスと、同じ
名前のカスタム項目との間で混乱が生じることはありません。
圧縮ヘッダー
REST API の要求や応答を圧縮するには、圧縮ヘッダーを使用します。圧縮によって、要求に必要な帯域幅を減
らせますが、クライアント側ではより多くの処理能力が必要になります。ほとんどの場合、この負荷の移動に
よって、アプリケーションの全体的なパフォーマンスが向上します。
REST API では HTTP 1.1 仕様の定義に従って、gzip と deflate の圧縮アルゴリズムがサポートされています。どちら
を使用するか未定の場合は、deflate よりも gzip を使用する方が一般的です。
ヒント: パフォーマンス向上のため、HTTP 1.1 の仕様に従ったクライアント側での圧縮のサポートをお勧
めします。
要求の圧縮
要求を圧縮するには、Content-Encoding: gzip または Content-Encoding: deflate ヘッダーを含めま
す。REST API は、処理前にすべての要求を展開します。
この例の要求は gzip で圧縮されています。
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/ -H
"Authorization: Bearer access-token" -H "Content-Type: application/json" -H
"Content-Encoding: gzip" —data-binary @new-account.json -X POST
10
圧縮ヘッダーREST API の概要

===== PAGE 21 =====
応答の圧縮
応答が圧縮されるのは、要求に Accept-Encoding: gzip ヘッダーまたは Accept-Encoding: deflate
ヘッダーが含まれている場合のみです。Accept-Encoding が指定されている場合でも、REST API では応答を圧縮す
る必要はありませんが、通常は圧縮されます。圧縮されている場合、応答には圧縮アルゴリズムを含む
Content-Encoding ヘッダーが含まれており、クライアント側で展開方法を把握できます。
この要求の例では、圧縮された応答を求めています。
curl
https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/0015e000009sS0DAAU
-H "Authorization: Bearer access-token" -H "Content-Type: application/json" -H
"Accept-Encoding: gzip" -X GET
条件付き要求ヘッダー
リソースにアクセスする前に検証するには、条件付き要求ヘッダーを使用します。ヘッダーに前提条件を設定
することで、その前提条件を満足する場合にのみ要求が成功するようになります。この機能により、Salesforce
のデータを更新する際に、ミスを防止したり、古い要求を拒否できるようになります。条件付き要求ヘッダー
には、応答のキャッシュなどのさまざまな手法を実装できます。
条件付き要求ヘッダーでは、厳しい入力規則と緩い入力規則の 2 種類の検証が可能です。厳しい入力規則で
は、前提条件と Salesforce のリソースが正確に一致するかどうかがチェックされます。厳しい入力規則ヘッダー
には、If-Match と If-None-Match があり、これらでエンティティタグ (ETag) を使用して、前提条件と
Salesforce のレコードを比較します。
緩い入力規則では、Salesforce のリソースに対して前提条件がチェックされますが、両者が同一であることは保
証されません。緩い入力規則ヘッダーには、If-Modified-Since や If-Unmodified-Since などがあり、
前提条件と Salesforce のレコードの最終更新日が比較されます。
REST API の条件付きヘッダーは HTTP 1.1 の仕様に準拠しますが、次の例外があります。
• PATCH または POST 要求の If-Match、If-None-Match、または If-Unmodified-Since に無効なヘッダー
値を含めた場合、400 Bad Request 状況コードが返されます。
• If-Range ヘッダーはサポートされていません。
• DELETE 要求はサポートされません。
ETag
ETag ヘッダーは、sObject Rows リソースにアクセスするときに返される応答ヘッダーです。後続の要求の
If-Match および If-None-Match 要求ヘッダーがコンテンツに変更があるかどうかを判断するために使用す
るコンテンツのハッシュです。
このヘッダーは、sObject Rows (取引先レコードのみ) リソースでサポートされています。
この例では、REST API が返す ETag を示しています。
ETag: "U5iWijwWbQD18jeiXwsqxeGpZQk=-gzip"
ETag ヘッダーの HTTP 1.1 仕様については、www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.19 を参照してくだ
さい。
11
条件付き要求ヘッダーREST API の概要

===== PAGE 22 =====
If-Match
If-Match ヘッダーは、ETag のリストを含む sObject Rows の要求ヘッダーです。要求しているレコードの ETag
が、ヘッダーで前提条件として指定した ETag と一致する場合は、要求が処理されます。いずれの ETag とも一
致しない場合は、412 Precondition Failed 状況コードが返され、要求は処理されません。
このヘッダーは、sObject Rows (取引先レコードのみ) リソースをサポートしています。
次の例では、要求に If-Match ヘッダーが含まれています。
If-Match: "Jbjuzw7dbhaEG3fd90kJbx6A0ow=-gzip", "U5iWijwWbQD18jeiXwsqxeGpZQk=-gzip"
If-Match ヘッダーの HTTP 1.1 仕様については、www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.24 を参照して
ください。
If-None-Match
If-None-Match ヘッダーは、If-Match の逆数である sObject Rows の要求ヘッダーです。要求しているレコー
ドの ETag がヘッダーに指定した ETag と一致する場合は、要求が処理されません。GET または HEAD 要求では 304
Not Modified 状況コードが返され、PATCH 要求では 412 Precondition Failed 状況コードが返されます。
このヘッダーは、sObject Rows (取引先レコードのみ) リソースをサポートしています。
次の例では、要求に If-None-Match ヘッダーが含まれています。
If-None-Match: "Jbjuzw7dbhaEG3fd90kJbx6A0ow=-gzip", "U5iWijwWbQD18jeiXwsqxeGpZQk=-gzip"
If-None-Match ヘッダーの HTTP 1.1 仕様については、www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.26 を参
照してください。
If-Modified-Since
If-Modified-Since ヘッダーは、時間ベースの要求ヘッダーです。要求は、ヘッダーで指定した日時以降に
データが変更された場合にのみ処理されます。いずれの ETag とも一致しない場合は、304 Not Modified 状況コー
ドが返され、要求は処理されません。
このヘッダーでサポートされているリソースは、sObject Rows、sObject Describe、Describe Global、および Invocable
Actions です。
次の例では要求に If-Modified-Since ヘッダーが含まれています。
If-Modified-Since: Tue, 10 Aug 2015 00:00:00 GMT
If-Modified-Since ヘッダーの HTTP 1.1 仕様については、www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.25
を参照してください。
If-Unmodified-Since
If-Unmodified-Since ヘッダーは、If-Modified-Since の逆数である要求ヘッダーです。要求に
If-Unmodified-Since ヘッダーを追加して実行する場合、この要求は指定した日付以降にデータが変更されていな
い場合にのみ処理されます。いずれの ETag とも一致しない場合は、412 Precondition Failed 状況コードが返され、
要求は処理されません。
12
条件付き要求ヘッダーREST API の概要

===== PAGE 23 =====
このヘッダーでサポートされているリソースは、sObject Rows、sObject Describe、Describe Global、および Invocable
Actions です。
次の例では要求に If-Unmodified-Since ヘッダーが含まれています。
If-Unmodified-Since: Tue, 10 Aug 2015 00:00:00 GMT
If-Unmodified-Sinceヘッダーの HTTP 1.1 仕様については、www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.28
を参照してください。
重複ルールヘッダー
重複ルールのオプションを設定します。Salesforce は、重複ルールを使用して、作成、更新、または更新/挿入
されるレコードが既存のレコードと重複していないかを確認します。重複ルールは重複管理の一部です。
このヘッダーは、API バージョン 52.0 以降で使用できます。
ヘッダーの項目名と値
すべての項目のデフォルト値は false です。
項目名
allowSave
項目値
• true  — ユーザーはアラートを確認したり、重複レコードを保存したりできます。アクションに対して
アラートが有効になっている場合に適用できます。
• false — ユーザーはアラートを確認することも、重複レコードを保存することもできません。アクショ
ンに対してアラートが有効になっている場合に適用できます。
項目名
includeRecordDetails
項目値
• true  — 重複レコードのすべての項目を返します。
• false  — 項目ではなく、重複レコード ID を返します。
項目名
runAsCurrentUser
項目値
• true  — 重複ルールの実行時、現在のユーザーの共有ルールを使用します。
• false  — 重複ルールの実行時、現在のユーザーの共有ルールではなく、システムの共有ルールを使用
します。
13
重複ルールヘッダーREST API の概要

===== PAGE 24 =====
例
ユーザーがアラートを確認したり、重複レコードを保存したりできるようにします。重複項目のレコードが返
され、現在のユーザーの共有ルールが適用されることを指定します。これで、レコードが作成、更新、および
更新/挿入されるときに、これらの重複管理設定オプションが適用されるようになりました。
Sforce-Duplicate-Rule-Header: allowSave=true, includeRecordDetails=true,
runAsCurrentUser=true
Limit Info ヘッダー
この応答ヘッダーは、REST API への各要求で返されます (ただし、バージョン URI、/ へのコールを除きます。
これは組織の制限に含まれないためです)。この情報を使用して API 制限を監視できます。
ヘッダーの項目名と値
項目名
Sforce-Limit-Info
項目値
• api-usage  — コールが行われた組織の 1 日あたりの API の使用量を指定します。最初の数値は使用され
た API コール数で、2 番目の数値は組織の API 制限数です。
ヘッダーで返される値は、標準の REST API の制限および使用量を表します。ただし、Salesforce Functions を使
用してコールを実行した場合は除きます。Salesforce Functions を使用して実行されたコールは、Functions 固有
の割り当てから描画されます。
例
Sforce-Limit-Info: api-usage=10018/100000
関連トピック:
Salesforce Functions Guide (Salesforce Functions ガイド): Functions Limits (Functions の制限)
MRU ヘッダー
作成、更新、更新/挿入、取得されたレコードで最後に使用した (MRU) 項目が更新されるかどうかを定義しま
す。MRU 項目は Salesforce ユーザーインターフェースのサイドバーの [最近使ったデータ] セクションに表示され
ます。このヘッダーは、API バージョン 60.0 以降で使用できます。
メモ: このヘッダーは、レコードを作成、更新、更新/挿入、取得する REST API でサポートされます。これ
らの API の例については、「関連トピック」セクションの「sObject Rows」および「sObject Rows by External
ID」を参照してください。SOQL を介してレコードを照会するために使用される REST API では MRU は更新さ
れないため、ヘッダー項目は MRU に影響せず、常に false に設定されています。
14
Limit Info ヘッダーREST API の概要

===== PAGE 25 =====
ヘッダーの項目名と値
SOQL を介してレコードを照会する REST API を除き、すべての項目のデフォルト値は true に設定されます。デ
フォルト値は変更される可能性があります。
API コールのみを実行するインテグレーションユーザーの場合、パフォーマンスの向上のために、この項目を
false に設定することをお勧めします。API のみを使用するインテグレーションユーザーは Salesforce ユーザー
インターフェースを使用しないため、MRU は関連しません。
項目名
updateMru
項目値
• true  — [ 設定] の [ユーザー] ページでユーザーの [MRU 更新なし] 項目が有効になっていなければ、関連
レコードで MRU を更新します。この項目を有効にする方法についての詳細は、「関連トピック」セク
ションの「ユーザーの編集」ページを参照してください。
• false  — 関連レコードで MRU を更新しません。
例
レコードで MRU が更新されることを示します。
Sforce-Mru: updateMru=true
関連トピック:
sObject Rows
sObject Rows by External ID
Salesforce ヘルプ: ユーザーの編集
Package Version ヘッダー
クライアントによって参照される各パッケージのバージョンを指定します。パッケージバージョンは、パッ
ケージに含まれる一連のコンポーネントと動作を識別する番号です。このヘッダーは、Apex REST Web サービス
をコールするときのパッケージバージョンの指定にも使用されます。
Package Version ヘッダーは、Describe Global、sObject Describe、sObject Basic Information、sObject Rows、sObject Layouts、
Query、QueryAll、Search、および sObject Rows by External ID リソースで使用できます。
ヘッダーの項目名と値
項目名と値
x-sfdc-packageversion-[namespace]: xx.x では、[namespace] が管理パッケージの固有の名前空
間で、xx.x がパッケージバージョンです。
例
x-sfdc-packageversion-clientPackage: 1.0
15
Package Version ヘッダーREST API の概要

===== PAGE 26 =====
Query Options ヘッダー
クエリ結果のバッチサイズなど、クエリで使用するオプションを指定します。この要求ヘッダーは、Query リ
ソースで使用します。
ヘッダーの項目名と値
項目名
Sforce-Query-Options
項目値
• batchSize  — クエリ要求に対して返されるレコード数を指定する数値。子オブジェクトは、バッチサ
イズのレコード数に反映されます。たとえば、リレーションクエリの場合、返される親行ごとに複数の
子オブジェクトが返されます。
デフォルト値は 2,000、最小値は 200、最大値は 2,000 です。要求されるバッチサイズが、実際のバッチサ
イズになるとは限りません。必要に応じて、パフォーマンスを最大化するために変更が行われます。
例
Sforce-Query-Options: batchSize=1000
Warning ヘッダー
このヘッダーは、警告が発生した場合に返されます。たとえば、非推奨バージョンの API を使用すると、この
ヘッダーが返されます。
ヘッダーの項目名と値
項目名
Warning
項目値
warningCode warningMessage
API のバージョンが非推奨であるという警告の場合、warningCode は 299 となります。
例
Warning: 299 - "This API is deprecated and will be removed by Summer '22. Please see
https://help.salesforce.com/articleView?id=000351312 for details."
cURL を使用した REST 要求の送信
このガイドの例では、cURL ツールを使用して HTTP 要求を送信し、Salesforce のリソースへのアクセスや、リソー
スの作成および操作を行います。要求の送信に別のツールを使用している場合は、cURL の例と同じ要素を使用
して要求を送信できます。
16
Query Options ヘッダーREST API の概要

===== PAGE 27 =====
cURL は、多くの Linux システムや macOS システムにあらかじめインストールされています。Windows バージョン
は、curl.haxx.se/ からダウンロードできます。Windows で HTTPS を使用する場合、システムが SSL の cURL 要件を満
たしていることを確認してください。
メモ:  cURL はオープンソースのツールであり、Salesforce ではサポートされていません。
リクエストボディの添付
多くの例には、要求のデータを含んだ JSON または XML ファイルのリクエストボディがあります。cURL を使用
する場合は、これらのファイルをローカルシステムに保存し、—data-binary または -d オプションを使用して要
求に添付します。
次の例では、new-account.json ファイルが添付されています。
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/sobjects/Account/ -H
"Authorization Bearer access-token" -H “Content-Type: application/json” —data-binary
@new-account.json -X POST
アクセストークンでの感嘆符の使用について
cURL の例を実行すると、OAuth アクセストークンに感嘆符 (!) の特殊文字が存在するため、macOS および Linux シ
ステムではエラーが発生する場合があります。このエラーを回避するには、感嘆符をエスケープするか単一引
用符で囲みます。
アクセストークンが二重引用符で囲まれている場合、アクセストークンで感嘆符をエスケープするには、感嘆
符の前にバックスラッシュ (\!) を挿入します。たとえば、この cURL コマンドのアクセストークン文字列では、
感嘆符 (!) がエスケープされています。
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/ -H "Authorization: Bearer
00D50000000IehZ\!AQcAQH0dMHEXAMPLEzmpkb58urFRkgeBGsxL_QJWwYMfAbUeeG7c1EXAMPLEDUkWe6H34r1AAwOR8B8fLEz6nEXAMPLE"
また、アクセストークンを一重引用符で囲むこともできます。
curl https://MyDomainName.my.salesforce.com/services/data/v60.0/ -H 'Authorization: Bearer
00D50000000IehZ!AQcAQH0dMHEXAMPLEzmpkb58urFRkgeBGsxL_QJWwYMfAbUeeG7c1EXAMPLEDUkWe6H34r1AAwOR8B8fLEz6nEXAMPLE'
関連トピック:
Java 開発者環境の設定
17
cURL を使用した REST 要求の送信REST API の概要

===== PAGE 28 =====
Salesforce CORS 許可リストの設定
エディション
使用可能なインター
フェース: Salesforce Classic
(使用できない組織もあり
ます) および Lightning
Experience
使用可能なエディション:
Developer Edition、
Enterprise Edition、
Performance Edition、およ
び Unlimited Edition
API アクセスが有効な場合
に使用可能なエディショ
ン: Professional Edition
ユーザ権限
作成、参照、更新、およ
び削除する
• 「すべてのデータの編
集」
クロスオリジンリソース共有 (CORS) を使用すると、Web ブラウザーで他のオリ
ジンからのリソースを要求できます。たとえば、CORS を使用すると、
https://www.example.com にある Web アプリケーションの JavaScript スクリプ
トで https://www.salesforce.com からのリソースを要求できます。Web ブ
ラウザーの JavaScript コードから、サポートされている Salesforce API、Apex REST リ
ソース、および Lightning Out へのアクセスを許可するには、要求元のオリジンを
Salesforce CORS 許可リストに追加します。自分の組織から Web ブラウザーで要求
を送信できる Lightning アプリケーションの場合、Lightning アプリケーションへの
要求は承認された URL からでない限り CORS 許可リストによって阻止されます。
次の Salesforce テクノロジーで CORS がサポートされています。
• Apex REST
• Bulk API
• Bulk API 2.0
• Connect REST API
• Lightning Out
• REST API
• CRM Analytics REST API
• ユーザーインターフェース API
要求コードを提供するオリジンを CORS 許可リストに追加します。CORS をサポー
トするブラウザーが、許可リスト内のオリジンに要求を行うと、Salesforce はオ
リジンを含む Access-Control-Allow-Origin  HTTP ヘッダーと、追加の CORS
HTTP ヘッダーを返します。オリジンが許可リストにない場合は、Salesforce が HTTP
状況コード 403 を返します。
1. [設定] で、[クイック検索] ボックスに「CORS」と入力して、[CORS] を選択します。
2. [新規] を選択します。
3. オリジンの URL パターンにリソースを入力します。
ヒント: オリジンの URL パターンは、ブラウザーのアドレスバーに表示される URL とは必ずしも一致し
ません。
4. 変更内容を保存します。
オリジンの URL パターンには、HTTPS プロトコル (localhost を使用しない場合) とドメイン名が含まれている必要
があります。またポートを含めることができます。ワイルドカード文字 (*) はサポートされますが、第 2 レベ
ルドメイン名の前にある必要があります。たとえば、https://*.example.com では、example.com のすべ
てのサブドメインが許可リストに追加されます。
オリジンの URL パターンに IP アドレスを使用できます。ただし、同じアドレスに解決される IP アドレスとドメ
インは同じオリジンではなく、それらを CORS 許可リストに異なるエントリとして追加する必要があります。
API バージョン 53 (Winter '22) 以降では、Google Chrome™ および Mozilla® Firefox® のブラウザー拡張機能をリソースと
して使用できます。Chrome 拡張機能では、chrome-extension:// のプレフィックスと、数字や大文字を含
18
Salesforce CORS 許可リストの設定REST API の概要

===== PAGE 29 =====
まない 32 文字の文字列を使用する必要があります。たとえば、
chrome-extension://abdkkegmcbiomijcbdaodaflgehfffed のようになります。Firefox の拡張機能は、
moz-extension:// のプレフィックスと、小文字と英数字から成る 8-4-4-4-12 の形式の文字列を使用する必要
があります。たとえば、moz-extension://1234ab56-78c9-1df2-3efg-4567891hi1j2 のようになりま
す。
CORS の稼働前テストで REST リソースを要求したときに成功の応答を取得しても、実際の要求に対して失敗の
応答を受け取ることがあります。この食い違いは、稼働前テストの後、要求が出される前にリソースが削除さ
れた場合に発生します。また、リソースが存在しない場合にも発生します。CORS の稼働前テストでは、サー
バー間でリソースの受け渡しが可能かどうかを確認しますが、特定のリソースが存在するかどうかは確認され
ません。CORS の稼働前の要求は、通常、ブラウザーによって自動的に発行されます。
メモ: 特定の OAuth エンドポイント CORS でアクセスするには、別の要件を満たす必要があります。
https://help.salesforce.com/s/articleView?id=sf.remoteaccess_oauth_endpoints_cors.htm を参照してください。
Date および DateTime の有効な書式
dateTime 項目と date 項目に対して正しい形式を指定します。
dateTime
dateTime 型の項目を使用するときは、yyyy-MM-ddTHH:mm:ss.SSS+/-HH:mm または
yyyy-MM-ddTHH:mm:ss.SSSZ という形式を使用します。
• yyyy は 4 桁の年号
• MM は 2 桁の月 (01 ～ 12)
• dd は 2 桁の日付 (01 ～ 31)
• 「T」はこの後に時刻が記述されることを示す区切り文字
• HH は 2 桁の時間 (00 ～ 23)
• mm は 2 桁の分 (00 ～ 59)
• ss は 2 桁の秒 (00 ～ 59)
• SSS は省略可能な 3 桁のミリ秒 (000 ～ 999)
• +/-Hh:mm は、Zulu (UTC) タイムゾーンオフセット
• 「Z」はタイムゾーンが UTC であることを示す
UTC の dateTime にタイムゾーンを追加すると、日付と時刻をそのタイムゾーンの値で示せます。たとえば、
「2002-10-10T12:00:00+05:00」は「2002-10-10T12:00:00Z」より 5 時間早いことを示します (UTC の
「2002-10-10T07:00:00Z」)。「2002-10-10T00:00:00+05:00」は「2002-10-10T00:00:00Z」より 5 時間早いことを示します
(UTC の「2002-10-09T19:00:00Z」)。「W3C XML Schema Part 2: DateTime Datatype」を参照してください。
date
date 項目を指定するには、yyyy-MM-dd 形式を使用します。
メモ: date のオフセットの指定はサポートされていません。
19
Date および DateTime の有効な書式REST API の概要

===== PAGE 30 =====
状況コードとエラー応答
エラーが発生した場合、または応答が正常な場合のどちらでも、応答ヘッダーには HTTP コードが含まれ、レ
スポンスボディには通常、次の情報が含まれます。
• HTTP 応答コード
• HTTP 応答コードに付随するメッセージ
• エラーが発生した項目またはオブジェクト (応答がエラーに関する情報を返す場合)
説明HTTP 応答コード
GET 要求、HEAD 要求、および一部の PATCH 要求の「OK」成功コードです。200
POST 要求および一部の PATCH 要求の「Created」成功コードです。201
DELETE 要求および一部の PATCH 要求の「No Content」成功コードです。204
外部 ID が複数のレコードに存在する場合に返される値です。レスポンスボディには、一
致するレコードのリストが含まれます。
300
要求のコンテンツが、指定された日時から変更されていません。日時は
If-Modified-Since ヘッダーで指定されます。例については、「オブジェクトのメタ
データの変更の取得」を参照してください。
304
要求が実行されませんでした。通常、JSON または XML のボディに含まれるエラーが原因
です。
400
使用されたセッション ID または OAuth トークンが期限切れか無効です。レスポンスボディ
に message および errorCode が含まれます。
401
要求が却下されました。ログインユーザーに適切な権限があることを確認してください。
エラーコードが REQUEST_LIMIT_EXCEEDED の場合、組織の API 要求の制限を超えています。
403
要求されたリソースが見つかりませんでした。URI にエラーがないか確認し、共有の問題
がないことを確認してください。
404
Request-Line に指定されたメソッドは、URI に指定されたリソースには許可されていませ
ん。
405
リソースの現在の状態との競合が原因で要求を完了できませんでした。API バージョンが
要求しているリソースに対応していることを確認してください。
409
要求されたリソースは、廃止または削除されました。このリソースへの参照はすべて、
削除するか更新してください。
410
要求ヘッダーでクライアントが指定した 1 つ以上の前提条件を満たしていないため、要
求は実行されませんでした。たとえば、要求に If-Unmodified-Since ヘッダーが含ま
れていて、指定した日付以降にデータが変更された場合などです。
412
URI の長さが 16,384 バイトの制限を超えています。414
要求内のエンティティは、指定されたメソッドではサポートされていない形式です。415
20
状況コードとエラー応答REST API の概要

===== PAGE 31 =====
説明HTTP 応答コード
Salesforce Edge には、このリクエストホストで使用可能な転送情報がありません。Salesforce
カスタマーサポートにお問い合わせください。
420
要求は、条件付きでないため実行されませんでした。If-Matchなどの条件付き要求ヘッ
ダーの 1 つを要求に追加して、再送信してください。
428
URI とヘッダーの組み合わせの長さが 16,384 バイトの制限を超えています。431
Lightning Platform 内でエラーが発生したため、要求を完了できませんでした。Salesforce カ
スタマーサポートにお問い合わせください。
500
Salesforce Edge が Salesforce インスタンスと正常に通信できませんでした。502
サーバーは要求を処理できません。これは通常、サーバーがメンテナンスのために停止
しているか、過負荷の状態になっている場合に発生します。
503
例: ID が不正
JSON または XML (request_body.json または request_body.xml) を使用する要求に存在しない ID を使用
した場合。
[
{
"fields" : [ "Id" ],
"message" : "Account ID: id value of incorrect type: 001900K0001pPuOAAU",
"errorCode" : "MALFORMED_ID"
}
]
リソースが存在しない
存在しないリソースを要求した場合。たとえば、誤ったスペルのオブジェクト名を使用してレコードの作
成を試みた場合など。
[
{
"message" : "The requested resource does not exist",
"errorCode" : "NOT_FOUND"
}
]
API の有効期限のポリシー
どの REST API バージョンがサポートされているか、サポートされていないか、または利用できないかを確認し
ます。
Salesforce は、各 API バージョンを最初のリリース日から最低 3 年間サポートします。API の品質およびパフォー
マンスを改善するために、3 年を超えるバージョンのサポートは停止される場合があります。
Salesforce は、廃止予定の API バージョンを使用するお客様に、そのバージョンのサポートが終了する最低 1 年
前までに通知します。
21
API の有効期限のポリシーREST API の概要

===== PAGE 32 =====
バージョン廃止情報バージョンサポート状況Salesforce API バージョ
ン
サポート済み。バージョン 31.0 ～ 60.0
Salesforce Platform API バージョン 21.0 ～ 30.0 の廃
止
Summer ’22 以降、次のバージョンが
非推奨となり、Salesforce でサポート
されなくなりました。
Summer ’25 以降は、これらのバージョ
ンは廃止されて使用できなくなりま
す。
バージョン 21.0 ～ 30.0
Salesforce Platform API バージョン 7.0 ～ 20.0 の廃
止
Summer ’22 以降、次のバージョンが
廃止されて使用できなくなりまし
た。
バージョン 7.0 ～ 20.0
廃止された API バージョンからリソースを要求したり、操作を使用したりすると、REST API によって 410:GONE
エラーコードが返されます。
古い API バージョンやサポートされていない API バージョンで実行された要求を識別するには、API 合計使用量
イベント種別を使用します。
22
API の有効期限のポリシーREST API の概要
