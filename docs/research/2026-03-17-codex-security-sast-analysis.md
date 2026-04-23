---
status: active
last_reviewed: 2026-04-23
---

# Why Codex Security Doesn’t Include a SAST Report 深掘り調査

**調査日**: 2026-03-17  
**対象**: OpenAI 公式記事「Why Codex Security Doesn’t Include a SAST Report」と関連する Codex Security docs / FAQ / threat model docs  
**確認ソース**:

- <https://openai.com/index/why-codex-security-doesnt-include-sast/>
- <https://openai.com/index/codex-security-now-in-research-preview/>
- <https://developers.openai.com/codex/security/>
- <https://developers.openai.com/codex/security/setup>
- <https://developers.openai.com/codex/security/threat-model>
- <https://developers.openai.com/codex/security/faq>

---

## Executive Summary

この記事の主張は「SAST は不要」ではない。むしろ OpenAI は FAQ で明示的に、**Codex Security は SAST を置き換えるものではなく補完するもの**だと述べている。

この記事が本当に言っているのは次の 2 点。

1. **Codex Security の起点を SAST findings list にしない**
   - 理由は、source-to-sink の結果から入ると、探索範囲、前提、評価がそのツールの worldview に引っ張られるから。
2. **挙動と invariant を起点にして、validation で確証を上げる**
   - repo 固有の threat model と実コード文脈から入り、必要なら小さな slice、micro-fuzzer、z3、sandboxed validation まで使って「本当に成立する脆弱性か」を確かめる。

したがって、Codex Security のポジショニングは **behavior-first の security research agent** であって、deterministic な scanner の代替ではない。

---

## 1. 記事の中心主張

### 1.1 SAST は dataflow に最適化されている

記事はまず、SAST の典型モデルを「untrusted source から sink までの flow を追うもの」と整理している。
これは多くの real bug を拾える一方で、実コードでは indirection、dynamic dispatch、callbacks、reflection、framework-heavy な control flow により近似が必要になる。

ただし、OpenAI の批判の軸はそこだけではない。
本丸は、**たとえ dataflow を正しく追えても、“防御が本当に効いているか” は別問題**だという点にある。

### 1.2 難しい脆弱性は「チェックがあるのに意味を満たしていない」タイプ

記事は `sanitize_html()` の例で、「サニタイザを呼んだ」という事実と「その rendering context で安全になった」は別だと説明する。
つまり問題は「sink に届いたか」だけではなく、**checks が system が期待する constraint を本当に保っているか**にある。

これは source-to-sink より広い問題設定で、validation・normalization・parser behavior・downstream transformation をまとめて考えないといけない。

### 1.3 具体例は “validation before decoding”

記事の代表例は open redirect 系の transformation-chain bug である。

- `redirect_url` を allowlist regex で検査する
- その後 URL decode する
- decode 後の値を redirect handler に渡す

ここで大事なのは「regex check があるか」ではなく、**decode 後に解釈される値まで本当に constraint できているか**である。
記事はこの種のバグを、order-of-operations mistake、partial normalization、parsing ambiguity、validation と interpretation の mismatch として捉えている。

要するに、見えている dataflow よりも、**変換列の前後で invariant が崩れるか**が本質、という立場である。

---

## 2. Codex Security の設計思想

### 2.1 Start from behavior, then validate

記事と docs を合わせて読むと、Codex Security の基本設計はかなり一貫している。

- repo-specific threat model を作る
- real code context から likely vulnerabilities を探す
- high-signal issue を isolated environment で validation する
- evidence と patch candidate を付けて人に渡す

これは product announcement と docs overview / FAQ でも繰り返されている。

### 2.2 repo 固有 context が起点

docs では、Codex Security は repo ごとに **threat model** を作り、scan context・prioritization・review に使うとされている。
threat model には少なくとも次を含めるべきだと説明される。

- entry points と untrusted inputs
- trust boundaries と auth assumptions
- sensitive data paths や privileged actions
- チームが優先して見たい領域

これは単なる補助メモではなく、**finding の ranking そのものに影響する scan-time context** として扱われている。

### 2.3 validation は “あると良い” ではなく中核

FAQ では pipeline を 4 段階に整理している。

1. Analysis
2. Commit scanning
3. Validation
4. Patching

ここで validation は optional garnish ではなく、false positive を減らす主工程として書かれている。
FAQ はさらに、validation 時には sandbox 内で commands / tests を実行し、exit code、stdout、stderr、test results、artifacts を evidence として残すと説明している。

### 2.4 記事の “micro-fuzzers / z3 / PoC” は強いメッセージ

記事本文の中で最も重要なのは、Codex Security が必要に応じて以下までやると明言している点である。

- smallest testable slice への還元
- micro-fuzzers の生成
- constraints across transformations の reasoning
- satisfiability question としての formalization
- Python + `z3-solver` の利用
- compiled debug build を含む end-to-end PoC

これはかなり強い主張で、Codex Security を単なる “LLM がコードを読んで怪しいと指摘するツール” ではなく、**semantic reasoning + validation harness を持つ agent** として位置づけている。

---

## 3. なぜ SAST report を seed しないのか

記事は「SAST report も入力にして agent が deeper reasoning すればよいのでは」という自然な反論に対して、3 つの failure mode を挙げている。

### 3.1 Premature narrowing

findings list を起点にすると、agent の探索が「既にツールが見た領域」に偏る。
その結果、同じ region、同じ abstraction、同じ脆弱性観に effort を再投下しやすい。

これは言い換えると、**探索空間の先験分布を SAST に握られる**ということである。

### 3.2 Implicit judgments の持ち込み

SAST findings には、sanitization、validation、trust boundary に関する暗黙の前提が埋め込まれている。
その前提が間違っていたり不完全でも、agent は “investigate” ではなく “confirm or dismiss” に寄りやすくなる。

ここで OpenAI が守りたいのは、agent を triager にしすぎず、**security researcher 的な仮説生成器として保つこと**だと読める。

### 3.3 評価が濁る

pipeline の入口に SAST output を置くと、agent 自身が見つけたものと inherited したものを切り分けにくくなる。
OpenAI はこれを capability measurement 上の問題として挙げている。

これはかなり重要で、記事は product design の説明であると同時に、**agent 自身の性能評価のためにも seed しない**と言っている。

---

## 4. この記事は SAST 否定論ではない

これは FAQ でかなり明確に補強されている。

- Codex Security は SAST を **replace** しない
- SAST は broad deterministic coverage を引き続き提供する
- Codex Security は semantic reasoning と automated validation を足す

つまり OpenAI の立場は次の分業で理解するのが正確である。

| レイヤ | 主な役割 |
|---|---|
| SAST | predictable な source-to-sink / known pattern / secure coding standard |
| Codex Security | repo 固有の context、semantic mismatch、validation、triage 圧縮、patch candidate |
| Human review | exploitability、business impact、最終判断 |

この構図を見る限り、記事のタイトルは挑発的だが、内容自体はかなり穏当である。
言っているのは **“SAST report から始めるのは Codex Security の役割定義に合わない”** であって、**“SAST を外せ”** ではない。

---

## 5. docs / FAQ と突き合わせて見える実態

### 5.1 実際の pipeline は commit-by-commit

overview と setup docs では、Codex Security は connected GitHub repository を **commit by commit** に scan し、初回は selected history window を backfill すると説明している。
つまり 1 回きりの snapshot scanner というより、**repository history と増分変更を追う security workflow** に近い。

### 5.2 threat model 編集が第一の tuning knob

threat model docs は、「結果がずれているなら最初に edit すべきは threat model」と書いている。
これは記事の “behavior-first” を product UX に落としたものだと考えられる。

静的 findings list の filter 調整より先に、**system overview / trust boundary / auth assumption を直す**わけである。

### 5.3 patch は auto-apply されない

FAQ は、patch は recommended remediation であって、自動適用されないと明記する。
PR を GitHub に push できても、それは reviewer が inspect した後である。

この点は security product として重要で、**validation evidence は返すが、自律的 remediation までは踏み込まない**という境界が引かれている。

### 5.4 build は必須ではないが、validation では必要になりうる

FAQ によれば、scan 自体は compile step なしでも可能。
ただし auto-validation では reproduction のために build を試すことがある。

ここから分かるのは、Codex Security の主戦場が AST や compile artifact ではなく、**repository context + executable repro if available** だということ。

---

## 6. dotfiles リポジトリへの示唆

この repo ですぐ活かせる示唆は 3 つある。

### 6.1 `profiles.security` の役割を “semantic review” として明確化する

現状の [.codex/AGENTS.md](../../.codex/AGENTS.md) では `profiles.security` を深い security analysis 用として定義している。
今回の記事に寄せるなら、ここで強調すべきなのは scanner 的な pattern match ではなく、次の観点である。

- trust boundary が本当に成立しているか
- auth / validation / sanitization の順序が invariant を守っているか
- parse / decode / normalize 後も constraint が残るか
- state / workflow / authorization mismatch がないか

### 6.2 `security-reviewer` への入力は findings list より project context を先にする

この repo の Claude 側 `security-reviewer` や Codex 側 `profiles.security` を強化するなら、入力の順番は次がよい。

1. 対象変更の目的
2. trust boundary
3. sensitive path
4. attack surface
5. その後に diff / suspicious area

SAST や lint findings は補助 evidence として後置きする方が、記事の思想に整合する。

### 6.3 “再現できたか” を evidence として残す

記事と FAQ を読む限り、Codex Security の本質は reproduction evidence で triage を圧縮することにある。
この repo でも security review を深めるなら、「怪しい」だけで終えず、可能なら次まで残すべきである。

- 再現コマンド
- exit code
- test / log
- どの invariant が壊れたか

つまり、security review の completion criteria を **finding list** ではなく **evidence-backed finding list** に寄せるべき、という示唆である。

---

## 7. この記事の限界と open questions

### 7.1 強い主張だが、coverage boundary はまだ粗い

記事は semantic / invariant 問題への強さを語るが、どの vulnerability class にどれだけ強いかを定量的には示していない。
precision 改善や false positive 改善の数字は preview post にあるが、class 別の recall/precision は不明。

### 7.2 validation は強いが、環境依存性が大きい

FAQ では isolated container で validation するとされるが、repro に必要な infra、secrets、third-party dependencies がある場合にどこまで現実的に再現できるかは docs だけでは分からない。

### 7.3 SAST との orchestration はまだ product 外

「replace しない」は明言されている一方で、SAST と Codex Security をどう運用的に組み合わせると最も良いかは、この一連の docs では深く語られていない。
ここは利用側で workflow を設計する余地が大きい。

---

## 8. 結論

この記事を一文で要約するとこうなる。

**Codex Security は、“source-to-sink の一覧を賢く仕分けるツール” ではなく、“repo 固有の意図と invariant から入り、必要なら再現までして確証を上げる security research agent” として設計されている。**

そのため、

- SAST を不要とは言わない
- ただし SAST findings list を起点にしない
- 起点は repo context と threat model
- 差別化の中核は validation evidence

という整理になる。

dotfiles への持ち帰りとしては、security review を強くする方向は「ルールを増やすこと」より、**trust boundary / invariant / reproduction evidence を最初から review contract に含めること**だと考えるのが自然である。

---

## Sources

- OpenAI, “Why Codex Security Doesn’t Include a SAST Report” (March 16, 2026)  
  <https://openai.com/index/why-codex-security-doesnt-include-sast/>
- OpenAI, “Codex Security: now in research preview” (March 6, 2026)  
  <https://openai.com/index/codex-security-now-in-research-preview/>
- OpenAI Developers, “Codex Security”  
  <https://developers.openai.com/codex/security/>
- OpenAI Developers, “Codex Security setup”  
  <https://developers.openai.com/codex/security/setup>
- OpenAI Developers, “Improving the threat model”  
  <https://developers.openai.com/codex/security/threat-model>
- OpenAI Developers, “FAQ”  
  <https://developers.openai.com/codex/security/faq>
