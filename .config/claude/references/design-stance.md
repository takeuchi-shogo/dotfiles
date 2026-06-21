# design-stance.md

User-facing surface を作る/磨くときの**基礎姿勢**。Vercel Design Engineer と Apple Human Interface Guidelines (current, 8 principles) の原典を並列転載する。

## 適用境界 (重要)

このスタンスは **task scope 内の user-facing surface** に対してのみ適用する。

- ✅ 設計対象の UI/API/CLI/error/copy 自体の品質は、Vercel/HIG の craft 要求に従う
- ✅ "Push back when craft is at risk" は surface 内で発動 (色、コピー、エラーメッセージ、状態遷移等)
- ❌ scope 外の隣接コード/コンポーネント/ファイルへの「ついでに磨く」は、CLAUDE.md `<core_principles>` の "leave neighbors untouched" / "minimum change" が勝つ
- ❌ "Maintain your craft (ongoing)" は今回の task 範囲を超えて refactor する許可ではない

衝突したら: **scope 内 = stance、scope 外 = core**。

skill ルーティング (19 個の UI/frontend 系 skill の使い分け) は `references/design-skill-routing.md`。

---

## Vercel Design Engineer (5 principles)

原典: https://vercel.com/design/engineer
最終確認: 2026-06-20 (defuddle 経由)

### 1. Obsess over usefulness

- Solve real problems for users and teammates
- Make useful things feel effortless

> 注: 判定軸は「ユーザーが感じる usefulness」。技術的に巧いかではない。

### 2. Own the whole experience

- Shape the product, design the interface, ship the code
- Do whatever the outcome needs: product, design, code, docs, support
- Care about every state, edge case, word, and interaction

> 注: state / edge case / word / interaction は LLM の盲点リスト。success path しか書かない癖を矯正する。

### 3. Understand the constraints

- Know the user, product, code, business, and tradeoffs
- Find the real constraint before choosing the solution

> 注: 解より先に本当の制約を見つける。XY 問題回避と同型。

### 4. Build for everyone

- Design across skill levels, abilities, and contexts
- Make complexity available, not required

> 注: Progressive disclosure の原文。デフォルトは易しく、上級者には深い扉を用意する。

### 5. Make it excellent

- Scope small enough to do it well
- Push back when clarity, craft, performance, or trust is at risk
- Leave every surface better than you found it

> 注: 押し返す権利が明文化されている。boy scout rule は **scope 内** に限定 (適用境界参照)。

---

## Apple Human Interface Guidelines — Design principles (current, 8 principles)

原典: https://developer.apple.com/design/human-interface-guidelines/design-principles
最終確認: 2026-06-20 (ユーザー paste 経由、harness fetch 不可)

> The most successful and enduring designs are based on a deep understanding of how people think, feel, and interact with the world. There's no one right way to apply these principles. Instead, they're tools to help you weigh competing priorities and make key decisions on the path to a great design.

### 1. Purpose — Make something meaningful

Design starts with intention. Identify what matters most to the people you're designing for. Focus on making those things great, and you'll create an experience that people truly value.

- **Create value.** The best designs reflect a constant orientation toward what makes a product genuinely useful. At every stage of development, ask what your product is for and whether the design serves that purpose.
- **Keep focused.** Prioritize your app's most important features by aligning with how people want to use it, and focus on making those features truly great. A product with a clear use is more effective at helping people meet their goals.
- **Find new ways to solve the problem.** Investigate existing solutions, and avoid re-creating them. Define what sets your product apart, and ask how your design can reflect that.

> 注: 意図 → 価値 → 集中 → 差別化。default に逃げず「最初に何を解くか」を宣言せよ。

### 2. Agency — Let people do things their own way

An interface exists to help people accomplish their goals. Give them the freedom to act, keep them informed about what's happening, and make it easy to recover from mistakes.

- **Stay out of the way.** People use your product to get things done. Often the best way to help them do this is to get them directly to the task or content at hand. The best designs are unobtrusive and present when people need them.
- **Give people the freedom to explore.** Let them move through your interface and access features without being locked into specific flows or modes. When a guided flow is necessary, make it easy to skip or escape so people can get to the main experience quickly.
- **Help people recover from mistakes.** When people know they can reverse an action or return to a previous state, they feel free to explore, and that freedom makes your interface more inviting. Build forgiveness into your design, and make it easy. Recovering from the unexpected shouldn't cost people their time or work.

> 注: 自由 + 情報 + 復帰可能性。CLI/API でも error recovery と undo を設計に組み込む。

### 3. Responsibility — Act in people's best interest

Your work has an impact on people's lives. Earn their trust by prioritizing safety and privacy, and being transparent about what your product does and why.

- **Be fully transparent about what your product does and why.** You have an opportunity to build a relationship with someone from their very first interaction. Make sure your app's intentions are clear from the start. Provide a clear rationale when asking for permission, and when gathering data, be clear about what you collect and how you use it.
- **Keep people's information safe.** People trust you to maintain the integrity of their data. Only collect what your product needs to function, and handle it with care. Anticipate ways it could be misused or cause harm, and put protections in place to prevent abuse and unintended consequences.

> 注: 透明性とプライバシーは UI 専用ではない。AI 出力の attribution、CLI の権限要求、API の data scope にも効く。

### 4. Familiarity — Build on what people know

Drawing on concepts people already understand helps them feel immediately at home. Ground your experience in established physical and digital patterns and apply them consistently throughout your design.

- **Use concepts that people know.** People bring knowledge of the real world and other software to every new experience. Draw on both to make your interface feel familiar and intuitive.
- **Keep visuals and interactions consistent.** Once you establish a behavior or appearance for an element, apply it throughout your design. Consistency helps people learn more quickly, and gives them confidence that new interactions will work the way they expect.
- **Provide clear feedback.** Give people clear signals about what's happening as they use your app. Show when controls are available, indicate when content changes, and use system patterns to display alerts and offer choices. Consistent feedback helps keep people informed and in control.

> 注: 既知パターンを borrow し、独自記号を発明しない。一貫性 + フィードバックがユーザーの予測可能性を作る。

### 5. Flexibility — Adapt to diverse contexts and needs

People use your software in ways as unique as they are. The more your design acknowledges this, the more people feel welcome to use it. Be mindful of experiences other than yours, and try to support as many devices, types of interaction, and perspectives as possible.

- **Design for everyone.** People are empowered by products designed with them in mind. Think about the diversity of people who may encounter your design, and take the range of their experiences, perspectives, and needs into account. Treat accessibility as a priority from the start. Design inclusively to reach the broadest possible audience and create a better experience for all.
- **Preserve a person's context.** Help people feel at home as your design adapts across platforms and configurations. Keep content and controls in consistent, predictable positions, and use natural animations to ease transitions.
- **Consider a variety of input methods.** People interact with their devices in different ways. Designing for as many inputs as possible — including voice, touch, keyboard, and more — means more people can use your product the way that works best for them.
- **Approach every platform with intention.** Your software should feel polished and at home wherever it runs. Give each platform you support the same level of care.

> 注: アクセシビリティは後付けではなく起点。input/context/platform の多様性を初手から想定する。

### 6. Simplicity — Be clear and direct

A well-designed experience removes the unnecessary, with every element earning its place. When your interface is logically organized and straightforward to navigate, it's easier to get things done.

- **Include just what's necessary.** Simplicity isn't minimalism. Aim for a focused, useful experience that keeps the important things close by and lets the others fall away.
- **Be concise.** When you find the simplest way to say something, it's often the most universal, and the most helpful. Choose exactly the words you need to convey a concept or label a control.
- **Establish hierarchy.** When form and function are readily apparent, people know how to reach a desired outcome. Prioritize recognizable controls and a consistent structure that helps people understand where they are and what comes next.

> 注: simplicity ≠ minimalism。「必要なものを近くに、不要なものを落とす」 = 焦点と階層。

### 7. Craft — Care about every detail

Your design is a reflection of how much you care. It shows your dedication to delivering the best possible experience for people. Take the time to do the work well.

- **Quality sets the tone.** Every element of your design shows people how much you care. Be deliberate with each decision, and strive for stunning visuals, smooth animations, precise wording, and thoughtful audio.
- **Experiment and iterate.** Prototype early, try new approaches, and be willing to discard what doesn't work. Set a high bar for every feature, refine it, and try again. Test your product in real-world settings to make sure it's durable, reliable, and high-performing.
- **Maintain your craft.** Shipping isn't the finish line. Keep your interface current with the latest platform capabilities and design patterns, and keep the quality bar high. Design is an ongoing commitment.

> 注: 各決定は意図的に。"Maintain your craft" の ongoing は scope 内に限定 (適用境界参照)。

### 8. Delight — Make it human

People remember how a product makes them feel. Think about the emotions that are right for your experience, and aim to deliver them in a way that's satisfying, enriching, and a joy to use.

- **Identify the emotion you want to inspire.** Not all software feels the same to use. A fitness app might energize; a meditation app might calm; a game might thrill. Know the feeling you want to evoke, and let it shape your design.
- **Create defining moments.** Every interaction is a chance to show what your software stands for. From a simple button press to an error message, consider whether each moment is an opportunity to add a touch of character that reflects the spirit of your design.
- **Don't mistake delight for decoration.** Keep in mind that people are trying to accomplish a task, so don't let pursuit of delight for its own sake get in the way of your product's core purpose. Think about your overall aesthetic: Some designs benefit from a carefully considered practical touch, while others might prefer some whimsy. Experiment to find the right balance.
- **Consider the whole.** Delight emerges as the sum of the consideration that you put into your product. It's the culmination of everything a person experiences as they use it: the freedom to act, the safety to explore, the comfort of familiar metaphors, and the flexibility to transition from one context to another. When you design with intent, focus, and care, the result is a product that people find naturally delightful.

> 注: 感情を設計対象に含めるが、decoration と混同しない。delight は他 7 原則の総和として現れる。

---

## 適用フロー

1. 触る surface を特定 (UI コンポーネント / API contract / CLI UX / error/empty/loading state / user-visible copy)
2. **意図を宣言** (Apple Purpose / Vercel Obsess over usefulness): 何の問題を、誰のために解くか
3. **本当の制約を見つける** (Vercel Understand the constraints): 解より先に
4. **状態を網羅** (Vercel Care about every state, edge case, word, interaction): success path だけで止めない
5. **押し返す** (Vercel "Push back when craft is at risk"): clarity/craft/performance/trust が危ういとき
6. surface 外には触らない (`<core_principles>` minimum change が優先)
