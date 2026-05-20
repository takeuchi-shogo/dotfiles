# Dashboard

> `$= dv.date("today").toFormat("yyyy-MM-dd EEEE")`

Vault 全体から live で読み出す single note。
**手動更新しない** — 更新は元ノートで行う。  
Dataview plugin が必要。詳細: `.claude/skills/obsidian-vault-setup/references/dashboard-template.md`

---

## Today

今日 (または overdue) の `task` ノート。優先度・期日順、最大 10 件。

```dataview
TABLE WITHOUT ID
  file.link as "Task",
  due as "Due",
  priority as "Priority"
FROM "01-Projects" OR "07-Daily"
WHERE type = "task"
  AND status != "complete"
  AND (due = date(today) OR due < date(today))
SORT priority DESC, due ASC
LIMIT 10
```

---

## Carryover

昨日の Daily Note の `## Review` 内「明日に持ち越し」セクションから自動拾い上げ。  
timekeeper review で記録 → 翌日 dashboard で表示。

```dataview
LIST
FROM "07-Daily"
WHERE date(file.name) = date(today) - dur(1 day)
FLATTEN file.lists AS item
WHERE meta(item.section).subpath = "明日に持ち越し"
```

---

## Open Loops

`status: open` の active project / unfinished task / open question。`02-Areas`, `01-Projects`, `00-Inbox` 横断。

```dataview
TABLE WITHOUT ID
  file.link as "Item",
  type as "Type",
  status as "Status"
FROM "00-Inbox" OR "01-Projects" OR "02-Areas"
WHERE status = "open"
SORT type ASC, file.mtime DESC
LIMIT 15
```

---

## Notes

- このダッシュボードは **Dataview** に依存している (2026 maintenance mode)
- 中長期: 公式 **Bases** プラグインへの移行を検討
- 取り扱い・スキーマ詳細は dotfiles 側 reference を参照:
  `dotfiles/.config/claude/skills/obsidian-vault-setup/references/dashboard-template.md`
