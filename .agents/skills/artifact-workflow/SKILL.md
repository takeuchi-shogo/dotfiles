---
name: artifact-workflow
description: Use when the user wants documents, PDFs, slide decks, or desktop screenshots and needs routing between doc, pdf, slides, and screenshot with the right validation expectations.
platforms: [agents, codex]
---

# Artifact Workflow

文書・成果物生成を、出力形式ごとに正しい skill へ振り分ける wrapper。

## When To Use

- `.docx` を作りたい / 編集したい
- PDF を生成したい / 読みたい / 見た目を確認したい
- `.pptx` スライドを作りたい / 修正したい
- desktop screenshot を撮りたい
- どの skill を使うべきかわからない

詳細な呼び出し例は `references/usage.md` を使う。

## Sources Of Truth

- `doc`
- `pdf`
- `slides`
- `screenshot`

## Routing

目的を次のどれかに分類する。

- `docx`
  - `.docx` 文書
- `pdf`
  - PDF 文書
- `slides`
  - `.pptx` deck
- `screenshot`
  - desktop / app / region capture
- `mixed`
  - 複数 artifact をまとめて作る

## Ask-Back Rule

以下が不足していれば、先に簡潔に聞き返す。

1. 最終成果物は何ですか。`docx`、`pdf`、`slides`、`screenshot` のどれですか。
2. 元になる内容はありますか。`text`、`existing file`、`reference deck`、`existing doc`、`running app`
3. 保存先やファイル名の希望はありますか。
4. 見た目の fidelity が重要ですか。

## Workflow

1. 出力形式を確定する。
2. `docx` の場合:
   - `doc` を使う
   - `python-docx` ベースで作る
   - render が可能なら visual check を入れる
3. `pdf` の場合:
   - `pdf` を使う
   - render to PNG で visual check を入れる
4. `slides` の場合:
   - `slides` を使う
   - editable `.pptx` と authoring source を残す
   - render / overflow check を行う
5. `screenshot` の場合:
   - browser / Electron なら tool-specific capture を優先する
   - それで足りないか、desktop capture が必要なら `screenshot` を使う
6. `mixed` の場合:
   - 最終 deliverable を先に決める
   - `slides` + `screenshot` のように必要 skill を順に使う

## Guardrails

- layout fidelity が重要なら text extraction だけで済ませない
- `slides` は editable output を前提にする
- `screenshot` は tool-specific capture がある場合はそちらを優先する
- `doc` / `pdf` / `slides` は render-based check を飛ばさない

## Output Modes

- `route`
  - どの skill を使うかだけ返す
- `plan`
  - 入力不足と作業 plan を返す
- `build`
  - 実際に artifact を作る

ユーザー指定がなければ `plan` を使う。

## Anti-Patterns

- `.docx` と PDF を同じものとして扱う
- slide deck を静的画像だけで終える
- screenshot が必要なのに browser capture と desktop capture を区別しない
- render / visual check を省略する
