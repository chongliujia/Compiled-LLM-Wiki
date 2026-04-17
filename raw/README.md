# `raw/` — Source of truth (immutable for agents)

Human-maintained originals: PDFs, Markdown exports, transcripts, URLs list, etc.

## Rules

- **Knowledge Compiler agents must not edit, move, or delete files under `raw/`.** (See root `AGENTS.md`.)
- Add new material here, then run the ingest workflow in `AGENTS.md` so updates land in `ir/` and `wiki/`.

## Suggested layout

Organize by source id (stable slug), for example:

```
raw/<source_id>/notes.md
raw/<source_id>/metadata.json   # optional: title, retrieved date, license
```

Use the same `source_id` in IR `source_id` fields so claims stay traceable.

## 快速开始（命令行）

在仓库根目录安装 CLI 后（见根目录 [`README.md`](../README.md) 的 **命令行 `cw`** 一节），可以：

```bash
cw raw init my_source_slug --title "可选标题"
```

然后把你的文档放进 `raw/my_source_slug/`。`cw lint` 会检查：每条 claim 的 `source_id` 是否在 `raw/<source_id>/` 有对应文件夹（缺文件夹时给 **warning**）。
