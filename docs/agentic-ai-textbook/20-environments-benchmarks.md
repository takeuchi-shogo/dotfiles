# 第20章 Agentic Environments and Benchmarks（評価層 — エージェントを測る・鍛える場）

> **一文サマリ:** Environment は、エージェントが行動し結果を観測し学習する「世界」(RL の意味での)。安全な探索・再現可能な評価・curriculum 学習を可能にし、リサーチエージェントの**収集品質をどう測るか / どこで鍛えるか**を与える。
> **PDF参照:** §20, p.375-391

会話モデルの評価は単純(prompt→応答→参照/人間で採点)。**エージェント評価は根本的に違う** — 一連のstepで世界に**行動**し結果を観測し挙動を適応させる。単一応答では捉えられず、構造化された **environment** が要る。ここでの environment は**RLの意味**(学習/評価用の世界)で、serving時のharness(Ch18)とは別。

**chatbot評価とのギャップ:** chatbot評価=単一生成の質(流暢さ・事実性・有用性)。**エージェント評価=policyの質**(多様で長いタスクで確実に目標達成できるか)。差は量でなく**別インフラ**を要する。

環境が要る3つの力: ①**Safe Exploration**(本番DB・実Webを学習中エージェントの探索に晒せない → サンドボックス。隔離は必須)②**Reproducible Evaluation**(全エージェントが同条件で同タスク → 決定的・version管理・配布可能)③**Curriculum Learning**(難度を徐々に上げると目標性能までの相互作用が激減 — 人間の学習と同じ)。

> **環境 = LLM の "Gym":** OpenAI Gym が RL アルゴリズムとタスクのインターフェースを標準化したように、agentic environment は LLM エージェントと多様なタスクのインターフェースを標準化する。中核は `reset()`(新エピソード初期化)/ `step(action)`(世界を進め観測と報酬を返す)/ `render()`(人間可読ビュー)。

---

## 20.2 環境設計の4軸

良い環境は直交する4軸を持つ: **observation space / action space / reward signal / episode structure**。4つ同時に正しくするのが環境工学の腕。最難関の **reward** を6フィールドで。

**Observation space（観測):** エージェントが各stepで**見る**もの。LLMでは大抵テキスト描画だが元素材は様々: Pure text(端末出力・ファイル・APIレスポンス)/ Structured(JSON/XML、精密だがparse要)/ Multimodal(screenshot・accessibility tree・HTML、GUI/web向け)/ Hybrid(screenshot+a11y tree、OSWorld/VisualWebArena)。**落とし穴 — Observation Leakage:** 観測にエージェントが見るべきでない情報(正解・報酬値・未来のstep)を混ぜると、ベンチスコアが水増しされ、実環境で壊滅的に失敗する。

**Action space（行動):** エージェントが**できる**こと。LLMでは大抵テキスト文字列を環境がparse・実行: tool calls / code execution(最も表現力高い)/ API interactions / GUI actions(`click(x,y)`等)/ natural language(別エージェントへ)。

### Reward 設計（環境工学の最難関）
**これは何か** — 報酬は3条件を満たす必要がある: ①**Aligned**(高報酬=真のタスク完了であり、表層proxyでない)②**Learnable**(進捗できる程度に密。長ホライズンでの純sparse報酬は shaping無しでは学習不能)③**Tamper-proof**(タスクを実際に完了せずに高報酬を得られない=reward hacking不可)。
**いつ使う / なぜ要る** — エージェントを学習・自動評価する全場面。報酬が歪むと、エージェントは「タスク達成」でなく「報酬最大化」を学ぶ(Goodhart)。
**最小実装**
```python
# 報酬型の選択(Table 20.1): 検証可能なら execution-based 一択
def reward(final_state, task) -> float:
    return 1.0 if run_verifier(final_state, task) else 0.0  # execution-based: ground truth
# 検証器が無いタスク: LLM-as-judge / rubric分解採点 / human注釈でproxyを較正
```
**リサーチエージェントでの使いどころ** — 収集タスクの報酬を「正しい情報源を見つけ忠実に引用したか」に設計。**execution-based**(既知正解の調査タスクで、必要文献を引けたか=Recall)+ **LLM-judge**(Ch16 Faithfulness で捏造引用を罰する)。これは Ch17 のメモリ write policy 報酬・Ch12 の RL 学習に直結。
**落とし穴** — ①sparse報酬(最後に0/1)は長い調査で学習困難 → 中間shaping(中間発見に部分報酬)だが shaping artifact に注意 ②LLM-judge は高コスト・不一致 ③**reward hacking**: 「それっぽい要約」で judge を騙す → execution-based で固定できる部分は固定。
**PDF参照** — §20.2.3, p.376-377

**Episode structure（エピソード):** Fixed-length(正確にT step、単純だが解決済みタスクに計算浪費)/ Early termination(完了signalか終端で終了、効率的だが信頼できる終端検出器が要る)/ Open-ended(固定horizon無し、資源予算=token/API/時間 が尽きるまで、本番に最も近いが評価最難)。近年は「horizon上のcurriculum」「truncationをRLペナルティに」「学習された停止」など、固定horizon前提を崩す研究も。

**Difficulty curriculum:** 静的ベンチは能力のスナップショット。**適応環境**は性能を監視し難度を調整して「最近接発達領域」(学べる程度に難しく、たまに成功する程度に易しい)に保つ。手法: procedural generation + Prioritized Level Replay / PAIRED(adversaryが regret最大化の環境を提案)/ HER(失敗軌跡を達成した目標で relabel)/ **中難度データ選択**(LLMが30-70%解けるタスクが最大の勾配情報)。

---

## 20.3 環境の種類

| 種類 | 代表 | 中身 |
|---|---|---|
| **Code Execution Sandbox** | Docker隔離 / E2B(Firecracker microVM, <200ms起動) / Modal | エージェントがコードを書き→サンドボックスが実行→出力を返す。最も基礎的 |
| **Web** | WebArena(812タスク, 人間78%/SoTA~45%) / VisualWebArena / Mind2Web(2000タスク, 未知サイト汎化) | ブラウザでマルチステップ操作(navigation・フォーム・情報取得) |
| **Computer Use** | OSWorld(369, 人間72%/LLM~18%) / WindowsAgentArena | デスクトップOS全体をscreenshot+a11yで操作 |
| **Software Engineering** | SWE-bench Verified(500実issue) / SWE-agent(ACI) | 実バグ修正・機能実装。テストが通れば報酬1 |
| **Scientific Research** | **PaperQA2**(引用付き文献QA) / **AI Scientist**(仮説→実験→論文) / **MLAgentBench** | 自律的な知識生成。**リサーチエージェントの直系** |
| **Game/Simulation** | NetHack(NLE) / **Voyager**(Minecraft, スキルライブラリ蓄積) / **GAIA**(466問, chained tool use) | 長ホライズン・明確な報酬・実害なし |
| **Multi-Agent** | DealOrNoDeal / Debate / AutoGen / MetaGPT | 交渉・議論・協調・競争 |

> **リサーチエージェントに直結するのは Scientific Research 系と GAIA。** **GAIA** は「Web検索+コード実行+ファイル解析」のchained tool useを推論ステップ数で3段階に分け、人間~92% vs LLM~15-30% の大きなギャップを露わにする — リサーチエージェントの評価ベンチとして最適。**PaperQA2** は引用付き文献QA、**AI Scientist** は仮説→実験→論文の end-to-end で、あなたが作るものの完成形に近い。

### Sandbox Escape（セキュリティ、最重要)
コード実行サンドボックスは主要な攻撃面。十分に有能なエージェント(or prompt-injectされたpayload)は kernel exploit / network exfiltration / resource枯渇でサンドボックス脱出を試みる。**多層防御必須**: コンテナ隔離 + seccomp + read-only root FS + network egress filtering + CPU/memory cgroups。**エージェント生成コードを host権限で絶対に実行しない。** リサーチエージェントが外部コードや収集スクリプトを動かすなら必ずここを守る(Ch18 のツール出力経由 prompt injection と同根)。

---

## 20.4 OpenEnv（環境インターフェースの標準化）

環境の乱立で API/観測形式/scaffolding が断片化した。**OpenEnv**(Hugging Face)は Gymnasium 風の型付き interface(`reset()`/`step()`/`state()`)を Docker隔離 + WebSocket で提供し、HF Spaces を registry に使う。既に 70+ 環境(OpenSpiel/Atari/BrowserGym/コードサンドボックス/金融RL等)。**再現性のbest practice:** semantic versioning(`WebArena-v1.2.0`)/ Docker image pinning(content-addressed hash)/ seed-based determinism(全確率要素をseed+ログ、軌跡を完全再生)/ leaderboard snapshot(環境versionをスコアと併記しsilent driftを防ぐ)。Meta-PyTorch/NVIDIA/Unsloth/Modal/HF の技術委員会がオープンに統治。

---

## 20.5 カスタム環境を作る

### Gymnasium-style API for LLM Agents
**これは何か** — Gymnasium(OpenAI Gym 後継)が RL 環境の事実標準。LLM 向けには2点改造: ①観測・行動が数値配列でなく**文字列**(or 文字列を含むdict)②`step` が**非同期ツール実行**を扱う。中核4メソッド: `reset()→(obs, info)` / `step(action)→StepResult(obs, reward, terminated, truncated, info)` / `render()` / `close()`。
**いつ使う / なぜ要る** — 自作エージェントを再現可能に評価・学習させたいとき。標準APIなら RL framework(TRL/TorchForge)に drop-in できる。
**最小実装（PDF Listing 20.1 を簡約: コード修復環境)**
```python
from dataclasses import dataclass, field

@dataclass
class StepResult:
    observation: str          # LLM に渡すテキスト
    reward: float             # 0.0 or 1.0
    terminated: bool          # タスク解決 or 終端
    truncated: bool           # 予算切れで打ち切り
    info: dict = field(default_factory=dict)

class FileEditEnv:
    MAX_STEPS = 20
    def reset(self, seed=None) -> tuple[str, dict]:
        self._workdir = make_tempdir()                       # 隔離した作業領域
        write(self._workdir/"solution.py", self.buggy_code)
        return self._build_obs("[Episode start]", self._run_tests()), {"step": 0}
    def step(self, action: str) -> StepResult:
        self._step += 1
        result_text = self._dispatch(action)                 # view/edit/run_tests/submit を解釈
        test_output = self._run_tests()                      # 隔離subprocess + timeout
        passed = "passed" in test_output and "failed" not in test_output
        return StepResult(self._build_obs(action, test_output),
                          reward=1.0 if passed else 0.0,
                          terminated=passed or action.startswith("submit"),
                          truncated=self._step >= self.MAX_STEPS, info={"passed": passed})
```
**リサーチエージェントでの使いどころ** — このコード修復環境の構造を**調査タスク環境**に転用: action={`search`,`fetch`,`summarize`,`submit`}、reward=「必要文献を引いて忠実に要約したか」(execution-based + Faithfulness judge)、`MAX_STEPS` で予算上限。これが Ch12 で RL 学習する際の「場」になる。
**落とし穴** — ①テストは**隔離subprocess + timeout**で(無限ループが学習ループをクラッシュさせない)②`reset` で前回の作業領域を必ず破棄(状態漏れ)③`truncated`(予算切れ)と `terminated`(解決)を区別しないと報酬信号が濁る。
**PDF参照** — §20.5.1, §20.8, p.384, 387-389

**設計判断(良い環境の例の教訓):** ①**text-only interface**(観測・行動が素の文字列=任意LLM互換)②**execution-based reward**(実テスト実行から導く=tamper-proof かつ完全に aligned、judge でない)③**isolated subprocess**(timeout付き別プロセス)④**Gymnasium-compatible**(reset/step/render/close 標準API=RL framework に drop-in)。

**状態管理・並列化(軽め):** 長ホライズンは state serialization(FS/cookie/DB を保存復元)+ mid-episode checkpoint(任意stepから再開=tree search可)+ trajectory logging(全 obs/action/reward を構造化記録、offline分析と reward model 学習に)。RL学習は数百万相互作用が要るので並列化必須: process並列 / async rollout worker(`asyncio` で LLM推論レイテンシと環境実行を重ねる)/ vectorized env / Ray・SLURM でクラスタ分散。

---

## 20.6 環境–エージェント interface パターン（軽め）

| パターン | obs / action | 備考 |
|---|---|---|
| **Text-Based** | 文字列 / 文字列(`<tool>...</tool>`を抽出) | 最も互換性高い。任意LLMが特別な構造なしに参加 |
| **Structured JSON** | JSON / JSON | 厳密validation(不正actionを実行前に弾く)・構造化ログ。要 FT or constrained decoding |
| **Multimodal** | `(screenshot, a11y_tree)` / GUI action | computer-use/web。screenshot=視覚文脈、a11y tree=要素IDで pixel座標不要 |
| **Streaming** | token stream / event stream | 部分観測を逐次受信・実行中の割り込み。人間のPC操作に近いが複雑 |

---

## 20.7 評価 harness 設計

### 評価 harness（エージェントをベンチに通す)
**これは何か** — エージェントをベンチ群で走らせ結果を集めて要約統計を出すインフラ。環境設計と同じくらい重要。①**決定的 vs 確率的**: 確率的環境(procedural生成・ネットワーク遅延)は task毎に複数runで平均と信頼区間を見る ②**held-out**: train/test split を**環境レベル**で厳密に(タスクレベルだけでは不十分)③**cross-environment汎化**: 環境Aで学習しBでzero-shot/few-shot ④**human baseline**: 全ベンチに人間性能を基準点として。
**いつ使う / なぜ要る** — エージェントの真の能力を測るとき。1回のrunや単一環境では運と過適合を見分けられない。
**最小実装**
```python
import math
# 何回runすれば十分か: N task・二値報酬で平均成功率の標準誤差は sqrt(p(1-p)/N)
# N=500, p=0.4 → 95%CI ≈ ±4.3%。確率的環境は task毎 k=3-5 run、×sqrt(k)
def success_rate_ci(successes, N, k=1):
    p = successes / N
    se = math.sqrt(p * (1 - p) / N) / math.sqrt(k)
    return p, 1.96 * se
```
**リサーチエージェントでの使いどころ** — 収集タスクのベンチ(GAIA や自作の既知正解セット)で成功率と信頼区間を出す。**human baseline**(自分が同じ調査をした結果)を上限基準に置き「エージェントは人間の何%か」で較正。確率的(Web は毎回違う)なので task毎複数run。
**落とし穴** — ①held-out を環境レベルで切らないと過適合を見逃す ②**benchmark contamination**(LLMの学習コーパスにベンチ解答が混入)③human baseline は**ドメイン専門家**から取る(SWE-bench なら crowdworker でなくエンジニア)+ 時間も測る(効率比較に)。
**PDF参照** — §20.7, p.386

---

## 20.8 主要ベンチの比較（Table 20.2）

| 環境 | 観測 | 行動 | ドメイン | タスク数 | 人間 | SoTA LLM |
|---|---|---|---|---|---|---|
| WebArena | Text+DOM | Browser API | Web操作 | 812 | 78% | ~45% |
| VisualWebArena | Screenshot+DOM | Browser API | 視覚Web | 910 | 88% | ~35% |
| Mind2Web | Screenshot+DOM | Browser API | 実サイト | 2000 | — | ~30% |
| OSWorld | Screenshot | Mouse+KB | デスクトップOS | 369 | 72% | ~18% |
| SWE-bench Verified | Text(repo) | Shell+edit | コード修復 | 500 | 100% | ~50% |
| **GAIA (L1)** | Text+files | Tool calls | 汎用QA | 165 | 92% | ~55% |
| **GAIA (L3)** | Text+files | Tool calls | 難QA | 42 | 92% | ~10% |
| Voyager (Minecraft) | Text+code | Code exec | 開放世界 | curriculum | — | 15+ tech tree |
| MLAgentBench | Text+code | Shell+edit | ML工学 | 13 | — | ~40% |

> **表の読み方:** 人間とSoTAの差は **computer use**(OSWorld 72% vs 18%)で最大、**code repair**(SWE-bench 100% vs 50%)で最小。これは action space の成熟度を反映 — LLMは大量のコードで学習されたが screenshot 操作データは少ない。リサーチエージェント領域(GAIA L3)も人間92% vs LLM~10% で**大きな伸びしろ**がある。

---

## この章のまとめ

- **環境は必須**。安全な探索・再現可能評価・curriculum は構造化環境無しに不可能。chatbot評価とのギャップは別インフラを要する。
- **4軸(observation/action/reward/episode)を丁寧に**。各軸に「ベンチ全体を無効化する」故障モードがある(特に observation leakage と reward hacking)。
- **reward が最難関**: aligned/learnable/tamper-proof。検証可能なら execution-based 一択、不可なら LLM-judge/rubric/human で。
- **自作は Gymnasium-style API**(reset/step/render/close、text-only、execution-based reward、隔離subprocess)。リサーチ調査環境にそのまま転用でき、Ch12 の RL 学習の「場」になる。
- **評価は複数run・環境レベルheld-out・human baseline・contamination注意**。
- リサーチエージェントの直系ベンチは **GAIA / PaperQA2 / AI Scientist**。人間との差が大きく伸びしろ大。
- **Open question**: 主観的タスクの報酬設計 / text↔multimodal 横断の汎化 / 学習に必要な環境忠実度 / benchmark contamination 対策。

**次章 → Ch21 MCP（ツール統合標準）。** エージェントが外部ツールを発見・呼び出す標準プロトコルに進む。
