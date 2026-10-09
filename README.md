# Agent 对齐三信号自审工具包

用 Arena Agent Alignment Index 的三个信号（越权动作、虚假归因、虚报完成），在你自己的 Claude Code 会话日志里筛候选，再人工判定。

只读、离线、只用 Python 标准库。不联网，不改你的任何文件。

## 文件

| 文件 | 作用 |
| --- | --- |
| `audit_alignment.py` | 读 `*.jsonl` 会话日志，输出三类候选到 `candidates.jsonl`；加 `--share` 时屏幕上不显示会话 ID 和路径，方便截图 |
| `review_context.py` | 把每条候选的上下文（用户原话、动作前助手说了什么、工具结果）导出成三份 Markdown，方便人工判定 |
| `rubric.md` | 判定口径：TP / GRAY / UNSURE / MINOR / FP 怎么分，用户授权从哪 5 个地方进来 |
| `fixture_test.py` | 合成日志自测，不需要真实会话；改规则后先跑它 |

## 三步

1. 先自测（Python 3.9 以上）：

   ```bash
   python fixture_test.py
   ```

   最后一行应为 `PASS`。

2. 找到你的日志。Claude Code 把每个会话存成一个 jsonl：

   - Windows：`C:\Users\<你>\.claude\projects\<项目目录名>\*.jsonl`
   - macOS / Linux：`~/.claude/projects/<项目目录名>/*.jsonl`

   跑候选：

   ```bash
   python audit_alignment.py ~/.claude/projects/<项目目录名>/*.jsonl --out candidates.jsonl --workspace <你的工作区路径>
   ```

   `--workspace` 可以给多次。工作区以内的 Write/Edit 不算越界。

3. 导出复核材料，按 `rubric.md` 逐条判：

   ```bash
   python review_context.py candidates.jsonl ~/.claude/projects/<项目目录名> review/
   ```

## 规则在哪改

`audit_alignment.py` 顶部的 `RISKY_CMDS`（什么算有后果的命令）、`AUTH_WORDS`（什么算授权）、`NEGATION`（什么算否定）、`CLAIM_DONE`（什么算声称完成）、`ATTRIB`（什么算把话安到用户头上）。

## 别直接用候选数下结论

在我自己的 8 个会话里，134 条候选人工判完，确认的越权、虚报完成、虚假归因都是 0；48 次 git 提交和推送里另有 19 次「沿用旧授权」的灰区、5 次依据的是用户含糊的回复。候选数说明的是规则有多粗，不是 Agent 有多坏。

已知漏报：授权词只做了关键词匹配，「稿子已经提交，等对方审核」这种说的是别的事的「提交」会被当成授权。git 提交和推送数量不多，建议全量人工过一遍。

## 隐私

导出的 `review/` 和 `candidates.jsonl` 里有你的原话、本机路径和仓库名，别直接贴到公开场合。
