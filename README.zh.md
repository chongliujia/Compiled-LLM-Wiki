# Compiled Wiki

一个按“编译器原则”维护知识库的工作区。

默认文档为英文：[README.md](README.md)。本文件是中文说明。

本仓库不是把文档丢给聊天机器人直接问答，而是把原始来源逐步编译成可追溯、可增量维护的知识系统：

- `raw/` 保存原始材料，代理不直接修改。
- `ir/` 保存 claims、entities、conflicts，是事实层。
- `wiki/` 保存人类可读页面，是 IR 的视图。
- `logs/changes.log` 追加记录每次 ingest 或维护动作。

自动化代理必须先读 [AGENTS.md](AGENTS.md)，再执行 ingest 或回答查询。

---

## 架构

| 层 | 路径 | 作用 |
|----|------|------|
| 原始来源 | `raw/` | PDF、Markdown、网页剪藏、转录等原始材料；代理只读 |
| IR | `ir/` | claims、entities、conflicts；知识库事实层 |
| Wiki | `wiki/` | 面向人阅读的实体页、概念页、分析页、假设页 |
| 日志 | `logs/` | 追加式变更历史 |
| Schema | `compiler/schemas/` | IR JSON Schema |

核心原则：wiki 是视图，不是事实源；claims 才是 ground truth layer。

---

## 核心数据模型

### Claim：`ir/claims.json`

每条 claim 必须包含：

| 字段 | 含义 |
|------|------|
| `subject`, `predicate`, `object` | 三元组式陈述 |
| `claim_type` | `SourceFact` / `Derived` / `Inference` / `Hypothesis` |
| `source_id` | 指向 `raw/<source_id>/` |
| `evidence_span` | 来源中的证据片段或定位信息 |
| `status` | `supported` / `disputed` / `stale` / `unknown` |

规则：

- 没有来源的 claim 不允许进入 IR。
- 推理不能伪装成 `SourceFact`。
- 不确定时使用 `unknown`。

### Entity：`ir/entities.json`

实体包含规范名、别名、关联 claim ids，以及可选 wiki 页面路径。

### Conflict：`ir/conflicts.json`

矛盾 claim 必须显式记录，不在摘要里强行合并，也不替来源“选赢家”。

---

## Ingest 工作流

当 `raw/` 里加入新来源时，按 [AGENTS.md](AGENTS.md) 执行：

1. Parse：抽取候选 claims 和 entities，不确定的标为 `unknown`。
2. Normalize：合并重复实体，统一命名，去重 claims。
3. Resolve：挂接到已有实体，识别新增、更新和冲突。
4. Validate：拒绝或降级无来源、归因不清、把推理当事实的 claim。
5. Plan：写入前必须列出要更新的实体、页面和冲突。
6. Patch：只做最小编辑，不整页重写。
7. Render：wiki 页面从 IR 渲染，摘要不能发明事实。
8. Log：追加写入 `logs/changes.log`。

---

## 查询工作流

回答问题时：

1. 先读 [wiki/index.md](wiki/index.md)。
2. 顺着链接读相关 wiki 页面。
3. 必要时查 `ir/claims.json`、`ir/entities.json`、`ir/conflicts.json`。
4. 带引用回答，不依赖记忆。

---

## 目录结构

```text
raw/                 # 原始来源，代理只读
ir/
  claims.json
  entities.json
  conflicts.json
  extracts/          # 从 PDF 等来源派生出的 Markdown 抽取件
  candidates/        # LLM 生成的候选 claims，未审查前不算 IR
wiki/
  index.md
  entities/
  concepts/
  analyses/
  hypotheses/
logs/
  changes.log
compiler/
  schemas/
AGENTS.md
README.md
README.zh.md
```

---

## 文档放哪里

不要把原始文档随便放在仓库根目录。统一放在：

```text
raw/<source_id>/
```

`<source_id>` 应该是稳定英文 slug，例如：

```text
raw/sun_2024_dc_voltage_prediction_mvdc/
raw/kong_2024_pinn_lc_parameter_estimation/
```

推荐初始化方式：

```bash
cw raw init my_paper_2024 --title "My paper"
```

然后把 PDF、Word 导出、Markdown、网页剪藏等原始材料放进该目录。IR 里的 `source_id` 必须使用同一个字符串。

---

## 命令行 `cw`

仓库自带轻量 CLI，用于 source bundle、PDF Markdown 抽取、LLM 候选 claims、IR 校验、lint 和本地问答。

### 使用 `rag` conda 环境

当前项目可用：

```bash
source /Users/jiachongliu/anaconda3/etc/profile.d/conda.sh
conda activate rag
pip install -e .
cw info
```

### 常用命令

| 命令 | 作用 |
|------|------|
| `cw info` | 显示仓库根目录和版本 |
| `cw raw init <source_id> [--title "..."]` | 创建 `raw/<source_id>/` |
| `cw raw bundle-pdf <pdf> --source-id <id> --title "..." [--execute]` | 把已放在 `raw/` 下的 PDF 归档成 source bundle；默认 dry-run |
| `cw index build [--overwrite]` | 从 IR 构建检索索引 `ir/index.json` |
| `cw extract markdown <source_id> [--overwrite]` | 从 `raw/<source_id>/*.pdf` 生成统一 Markdown 抽取件到 `ir/extracts/` |
| `cw extract llm-claims <source_id> --provider deepseek [--model deepseek-chat]` | 使用 LLM API 生成候选 claims 到 `ir/candidates/` |
| `cw ask "问题" [--limit 5]` | 针对 wiki/IR 做单次问答，并显示检索引用（自动模式：若 `.env` 有 DeepSeek key 则走 LLM） |
| `cw chat [--limit 5]` | 进入命令行对话模式（与 `cw ask` 相同自动模式） |
| `cw stats` | 统计 claims、entities、conflicts 和 raw sources |
| `cw validate` | 校验 `ir/*.json` 是否符合 schema |
| `cw lint` | 检查 source_id、claim 引用、wiki 链接等一致性 |

---

## PDF / LLM 辅助抽取

推荐流程：

```bash
cw raw bundle-pdf "raw/paper.pdf" \
  --source-id paper_2026_example \
  --title "Paper title" \
  --execute

cw extract markdown paper_2026_example
cw extract llm-claims paper_2026_example --provider deepseek --model deepseek-chat
```

LLM 输出会写入：

```text
ir/candidates/<source_id>.deepseek.claims.json
```

这些文件状态是 `candidate_not_ingested`。它们不是 IR ground truth；合并进 `ir/claims.json` 前仍要按 ingest 工作流审查。

DeepSeek 配置读取顺序是 shell 环境变量优先，其次读取本地 `.env`：

```bash
DEEPSEEK_API_KEY=...
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

---

## 测试 wiki 问答效果

`cw ask` 和 `cw chat` 当前是自动模式：如果 `.env` 或 shell 配置了 `DEEPSEEK_API_KEY`，会基于检索引用调用 LLM 生成答案；如果没有配置 key，则走本地检索模板回答。  
如果已经配置了 LLM 但调用失败，命令会直接报错，不会自动回退到本地回答。  
`cw extract llm-claims` 仍是独立的 LLM 路径，用于生成待审查候选 claims。
如果你要做可重复的“纯本地检索”测试，不改 `.env` 的情况下可以在当前命令里临时去掉 key：

```bash
env -u DEEPSEEK_API_KEY cw ask "DemoWidget standby power" --limit 2
```

检索会优先使用 `ir/index.json`。在 IR 更新后建议刷新索引：

```bash
cw index build --overwrite
```

```bash
cw ask "PECNN 如何提升 MVDC 电压预测？" --limit 4
cw ask "How does PECNN improve MVDC voltage prediction?" --limit 4
cw ask "PINN 估计了哪些参数，需要额外硬件吗？" --limit 4
cw ask "Which parameters are estimated by PINN and is extra hardware required?" --limit 4
cw chat
```

输出中 `Retrieved references` 是检索和引用部分，包括 claim id、source_id、evidence、raw bundle 和 wiki 页面。后面的 `Answer` 只基于这些检索结果生成。

### 当前测试结果（2026-04-17）

测试环境：

```bash
source /Users/jiachongliu/anaconda3/etc/profile.d/conda.sh
conda activate rag
cw ask "<question>" --limit 4
```

| 测试问题 | 结果 | 观察 |
|----------|------|------|
| `PECNN 如何提升 MVDC 电压预测？` | 命中 4 条 `sun_2024_dc_voltage_prediction_mvdc` claims | 能展示 PECNN 的层结构、用途、物理关系嵌入和评估网络；引用链包含 claim id、evidence、raw 和 wiki 路径。 |
| `How does PECNN improve MVDC voltage prediction?` | 命中 4 条 `sun_2024_dc_voltage_prediction_mvdc` claims | 英文问题命中稳定，检索质量明显好于同主题中文问法。 |
| `PINN 估计了哪些参数，需要额外硬件吗？` | 命中 4 条 `kong_2024_pinn_lc_parameter_estimation` claims | 能回答估计 DC-link capacitance / AC-side inductance、不需要额外硬件，并带出方法和实验误差信息。 |
| `Which parameters are estimated by PINN and is extra hardware required?` | 命中 4 条 `kong_2024_pinn_lc_parameter_estimation` claims | 英文问题命中稳定。 |
| `What is the experimental maximum error for the three-phase inverter case?` | 命中 4 条 `kong_2024_pinn_lc_parameter_estimation` claims | 能检索到最大误差 claim（5.2% 和 14.7%）。 |
| `DemoWidget standby power` | 命中 3 条 `sample_demo` claims | 英文关键词检索表现正常，能够优先返回 standby power，再返回同实体的相关 claims。 |
| `三相逆变器实验误差是多少？` | 未命中 | 当前检索是轻量词面匹配，中文问题里的“实验误差”没有映射到英文 claim `experimental test -- shows_maximum_error`。 |

输出示例（节选）：
`cw ask "How does PECNN improve MVDC voltage prediction?" --limit 2`

```text
Retrieved references:
[1] c_sun_2024_004 | score=0.641 | status=supported | source=sun_2024_dc_voltage_prediction_mvdc
    evidence: ... physical relation between voltage, current, and conductance ...
[2] c_sun_2024_003 | score=0.625 | status=supported | source=sun_2024_dc_voltage_prediction_mvdc
    evidence: ... three MVDC distribution networks ...

Answer: Based on 2 retrieved claim(s):
- [1] `PECNN` embeds: the physical relation between voltage, current, and conductance ...
- [2] `PECNN evaluation` uses: three MVDC distribution networks ...
```

输出示例（节选）：
`cw ask "Which parameters are estimated by PINN and is extra hardware required?" --limit 2`

```text
LLM call failed (APIConnectionError): Connection error.
```

输出示例（节选）：
`cw ask "三相逆变器实验误差是多少？" --limit 4`

```text
No matching claims found in IR.

Answer: I could not find supported claims in the current wiki/IR for this question.
```

测试截图画廊见英文 README 的 **Test Screenshot Gallery**：  
[README.md#test-screenshot-gallery](README.md#test-screenshot-gallery)

结论：当前 CLI 可以用于测试 wiki/IR 的引用链是否清晰，适合验证“回答是否有来源”。测试集应默认包含英文查询（论文语料是英文），并保留中文查询用于回归跨语言能力。限制是检索层还比较朴素：跨语言同义词、中文问题到英文论文术语、以及更自然的答案组织都还需要加强。后续可以加入 query rewrite、BM25/embedding 混合检索，或把 `Retrieved references` 交给 DeepSeek / OpenAI 生成更自然的最终回答。

---

## 设计原则

1. 可追溯：每条 claim 都必须指向来源。
2. 不静默覆盖：冲突显式记录。
3. 增量更新：patch 而不是整页重写。
4. 结构优先：先 IR，后 wiki。
5. wiki 不是权威事实层；`ir/` 才是事实编译层。

---

## 项目理念

这是一个知识编译器：原始信息被转换成有结构、可追溯、可演进的系统，而不是一次性聊天答案。
