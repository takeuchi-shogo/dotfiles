Claude Code セットアップの自己評価クイズを実行してください。

引数: $ARGUMENTS (beginner / intermediate / advanced、デフォルト: intermediate)

以下の手順で実行:

1. `tools/claude-code-quiz/quiz.py` の `--list-categories` でカテゴリ一覧を表示
2. ユーザーにプロファイル（引数がなければ intermediate）とカテゴリ絞り込みの希望を確認
3. 対話型クイズは Bash で直接実行できないため、以下の方法で実施:

**実行方法**: 問題を読み込んでクイズを Claude Code セッション内で対話的に出題する

```bash
uv run --with pyyaml python3 -c "
import yaml, json
from pathlib import Path
qs = []
for p in sorted(Path('tools/claude-code-quiz/questions').glob('*.yaml')):
    data = yaml.safe_load(open(p))
    for q in data['questions']:
        q['category_label'] = data['label']
    qs.extend(data['questions'])
print(json.dumps(qs, ensure_ascii=False))
"
```

4. 出力された JSON から、プロファイルに応じた問題数を選択:
   - beginner: 10問 (初級6, 中級3, 上級1)
   - intermediate: 20問 (初級3, 中級10, 上級7)
   - advanced: 30問 (初級3, 中級9, 上級18)

5. 1問ずつ AskUserQuestion で出題し、回答を受け取る
6. 全問終了後、スコアとカテゴリ別結果を報告
7. 間違えた問題の解説を一覧表示

ターミナルから直接実行する場合:
```bash
uv run --with pyyaml tools/claude-code-quiz/quiz.py [beginner|intermediate|advanced]
```
