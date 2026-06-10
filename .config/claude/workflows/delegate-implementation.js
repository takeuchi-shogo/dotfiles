export const meta = {
  name: 'delegate-implementation',
  description: '主エージェント が計画したタスクを Sonnet に委譲して実装+検証し、実装結果評価とテンプレート自己評価を返す。各タスクは並行・メイン作業ツリー直書きで実行されるため、主エージェント はタスクを互いに独立したファイルに分解すること',
  phases: [
    { title: 'Implement', detail: 'Sonnet agent が各タスクを実装+verify', model: 'sonnet' },
    { title: 'EvalResults', detail: '実装結果を successCriteria に照らして評価', model: 'sonnet' },
    { title: 'EvalTemplate', detail: 'テンプレート(委譲器)自体を主エージェント(現在のメインモデル)が critique' },
  ],
}

const input = (() => {
  if (args == null) return {}
  if (typeof args === 'string') {
    try { return JSON.parse(args) } catch (e) { log(`delegate-implementation: args JSON parse 失敗 — ${e.message}`); return {} }
  }
  return args
})()

const tasks = Array.isArray(input.tasks) ? input.tasks : []
if (tasks.length === 0) {
  log('delegate-implementation: args.tasks が空。{tasks:[{id,instruction,files,successCriteria}]} を渡してください')
  return { error: 'no tasks provided', implemented: [], resultEvals: [], templateEval: null }
}

const invalidTasks = tasks.filter((t) => !t || typeof t !== 'object' || typeof t.id !== 'string' || typeof t.instruction !== 'string')
if (invalidTasks.length > 0) {
  log(`delegate-implementation: id と instruction (string) を欠くタスクが ${invalidTasks.length} 件`)
  return { error: 'invalid task: each task needs a string id and instruction', implemented: [], resultEvals: [], templateEval: null }
}

const ids = tasks.map((t) => t.id)
const dupIds = [...new Set(ids.filter((id, i) => ids.indexOf(id) !== i))]
if (dupIds.length > 0) {
  log(`delegate-implementation: task id が重複 — ${dupIds.join(', ')}`)
  return { error: `duplicate task ids: ${dupIds.join(', ')}`, implemented: [], resultEvals: [], templateEval: null }
}

const sharedContext = input.sharedContext ?? ''

const IMPL_SCHEMA = {
  type: 'object',
  required: ['id', 'summary', 'filesChanged', 'verifyResult', 'blockers', 'selfReport'],
  properties: {
    id: { type: 'string' },
    summary: { type: 'string', description: '何を実装したか' },
    filesChanged: { type: 'array', items: { type: 'string' } },
    verifyResult: {
      type: 'object',
      required: ['ran', 'passed', 'detail'],
      properties: {
        ran: { type: 'boolean', description: 'lint/test を実行したか' },
        passed: { type: 'boolean' },
        detail: { type: 'string', description: '実行コマンドと結果。未実行なら理由' },
      },
    },
    blockers: { type: 'array', items: { type: 'string' }, description: '完走を妨げた要因。空なら完走' },
    selfReport: {
      type: 'object',
      required: ['unclearInstructions', 'discretionaryFillins'],
      properties: {
        unclearInstructions: { type: 'array', items: { type: 'string' }, description: '指示が曖昧で判断に迷った点' },
        discretionaryFillins: { type: 'array', items: { type: 'string' }, description: '裁量で補完した判断' },
      },
    },
  },
}

const RESULT_EVAL_SCHEMA = {
  type: 'object',
  required: ['id', 'meetsCriteria', 'gaps', 'severity'],
  properties: {
    id: { type: 'string' },
    meetsCriteria: { type: 'boolean' },
    gaps: { type: 'array', items: { type: 'string' } },
    severity: { type: 'string', enum: ['none', 'minor', 'major', 'blocker'] },
  },
}

const TEMPLATE_EVAL_SCHEMA = {
  type: 'object',
  required: ['handoffClarity', 'infoLoss', 'sonnetStruggles', 'verifyAdequacy', 'suggestions', 'wouldReuse', 'weakPhase'],
  properties: {
    handoffClarity: { type: 'integer', minimum: 1, maximum: 5, description: '主エージェント→Sonnet の指示の明確さ。selfReport.unclearInstructions の量と質から判断' },
    infoLoss: { type: 'array', items: { type: 'string' }, description: 'handoff で失われた情報・前提' },
    sonnetStruggles: { type: 'array', items: { type: 'string' }, description: 'Sonnet が詰まった/補完した共通パターン' },
    verifyAdequacy: { type: 'integer', minimum: 1, maximum: 5, description: '検証ステップの妥当性' },
    suggestions: { type: 'array', items: { type: 'string' }, description: 'テンプレートへの最小改善提案' },
    wouldReuse: { type: 'boolean', description: 'このテンプレートをそのまま再利用してよいか' },
    weakPhase: { type: 'string', enum: ['Implement', 'Verify', 'Handoff', 'none'] },
  },
}

function implPrompt(t) {
  return [
    '実装タスクを遂行せよ。あなたは実装担当 (Sonnet)。設計と判断は計画側 (主エージェント) で完了済み — 指示に忠実に実装し、検証まで行う。創意工夫より指示の正確な実現を優先せよ。',
    sharedContext ? `## 共通背景\n${sharedContext}` : '',
    `## タスク id: ${t.id}`,
    `## 指示\n${t.instruction}`,
    Array.isArray(t.files) && t.files.length ? `## 対象ファイル\n${t.files.join('\n')}` : '',
    `## 完了条件 (successCriteria)\n${t.successCriteria ?? '(明示なし — 指示から妥当に判断)'}`,
    [
      '## 必須',
      '- 実装後、lint/test など妥当な検証を実行し verifyResult に記録せよ。検証手段が不明なら ran:false + detail に理由。',
      '- 指示が曖昧で裁量判断した点は selfReport.discretionaryFillins に、情報不足で迷った点は selfReport.unclearInstructions に正直に記録せよ (テンプレート改善の材料。取り繕うと改善が止まる)。',
      '- 完走できない場合は blockers に理由を記録し、握り潰さない。',
    ].join('\n'),
  ].filter(Boolean).join('\n\n')
}

function resultEvalPrompt(r, t) {
  return [
    '実装結果を、元の指示と完了条件に照らして厳密に評価せよ。実装者とは独立した視点で、満たしていない点を見逃すな。',
    `## タスク id: ${r.id}`,
    sharedContext ? `## 共通背景\n${sharedContext}` : '',
    `## 指示\n${t ? t.instruction : '(指示不明 — 実装結果の id が計画と一致しない)'}`,
    (t && Array.isArray(t.files) && t.files.length) ? `## 対象ファイル\n${t.files.join('\n')}` : '',
    `## 完了条件\n${(t && t.successCriteria) ?? '(明示なし — 上記の指示の意図から判断)'}`,
    `## 実装者の報告\n${JSON.stringify(r, null, 2)}`,
    [
      '## 出力',
      '- meetsCriteria: 完了条件 (なければ指示の意図) を満たすか',
      '- gaps: 不足点 (なければ空配列)',
      '- severity: none / minor / major / blocker',
    ].join('\n'),
  ].filter(Boolean).join('\n\n')
}

function templateEvalPrompt(allTasks, impl, evals) {
  return [
    'あなたは委譲テンプレート (delegate-implementation) 自体の精度を critique する評価者 (主エージェント=現在のメインモデル)。',
    '目的: テンプレートを継続改善するための定性評価。個々の実装の良し悪しではなく委譲メカニズムが機能したかを見る。implemented 配列の null 要素は agent が結果を返さなかったタスクを示す。',
    `## 渡したタスク (主エージェント の計画)\n${JSON.stringify(allTasks, null, 2)}`,
    `## 実装者の報告 (selfReport 含む)\n${JSON.stringify(impl, null, 2)}`,
    `## 結果評価\n${JSON.stringify(evals, null, 2)}`,
    [
      '## 評価観点 (empirical-prompt-tuning の two-sided evaluation)',
      '- handoffClarity(1-5): selfReport.unclearInstructions の量と質から、主エージェント→Sonnet の指示が曖昧さなく伝わったか',
      '- infoLoss: handoff で失われた情報・前提',
      '- sonnetStruggles: Sonnet が詰まった / 裁量補完した共通パターン',
      '- verifyAdequacy(1-5): 各タスクの検証は十分だったか',
      '- suggestions: テンプレート (指示の組み立て方・スキーマ・フェーズ) への最小改善提案',
      '- wouldReuse: このテンプレートをそのまま再利用してよいか',
      '- weakPhase: 最も弱かったフェーズ (Implement/Verify/Handoff/none)',
    ].join('\n'),
  ].join('\n\n')
}

phase('Implement')
const implemented = await pipeline(
  tasks,
  (t) => agent(implPrompt(t), { label: `impl:${t.id}`, phase: 'Implement', model: 'sonnet', schema: IMPL_SCHEMA }),
)

const okImplemented = implemented.filter(Boolean)
const failedIds = tasks.filter((t, i) => !implemented[i]).map((t) => t.id)
if (failedIds.length > 0) log(`Implement: 結果を返さなかったタスク — ${failedIds.join(', ')}`)
log(`Implement: ${okImplemented.length}/${tasks.length} 件が結果を返した`)

if (okImplemented.length === 0) {
  log('delegate-implementation: 全タスクが結果を返さなかったため EvalResults/EvalTemplate をスキップ')
  return { implemented, resultEvals: [], templateEval: null }
}

phase('EvalResults')
const taskById = {}
for (const t of tasks) taskById[t.id] = t
const resultEvals = (await parallel(
  okImplemented.map((r) => () => {
    if (!taskById[r.id]) log(`eval-result: 計画に無い id="${r.id}" — 指示なしで評価`)
    return agent(resultEvalPrompt(r, taskById[r.id]), {
      label: `eval-result:${r.id}`, phase: 'EvalResults', model: 'sonnet', schema: RESULT_EVAL_SCHEMA,
    })
  }),
)).filter(Boolean)

phase('EvalTemplate')
const templateEval = await agent(templateEvalPrompt(tasks, implemented, resultEvals), {
  label: 'eval-template', phase: 'EvalTemplate', schema: TEMPLATE_EVAL_SCHEMA,
})

return { implemented, resultEvals, templateEval }
