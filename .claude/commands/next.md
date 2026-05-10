---
description: 看仓库当前进度并给出下一步建议
---

# /next

读取仓库当前状态，给出全局进度仪表盘和下一步推荐动作。**只读，不改任何文件**。

## 流程

### 1. 读取状态文件
- `_meta/library-catalog.md` — 总目录与各库状态
- `_meta/progress.md` — 进度日志（最近 50 行）
- `_meta/blocked.md` — 失败/阻塞记录（如存在）
- 各库 `<library>/README.md` 的状态字段

### 2. 输出仪表盘

格式：

```
# tc3-libraries-kb 仪表盘

更新于 <UTC>

## 总览
- 已完成库（全部 verified）: A / 40
- 进行中库（部分 verified）: B
- 已发现未启动: C
- 阻塞: D

## 各 Tier 进度
| Tier | 已完成 | 总数 | 进度条 |
|---|---|---|---|
| T1 基础 | 1/5 | ████░░░░░░ 20% |
| T2 运动 | 0/5 | ░░░░░░░░░░ 0% |
...

## 最近完成（最近 7 天）
- <UTC> Tc2_Standard/timer/TON.md ✅ verified
- ...

## 阻塞 / verify-failed（待人工）
- <library>/<name>: <reason>
- ...

## 推荐下一步

[根据当前状态智能推荐 1-3 条命令]

例：
- 若 T1 还有库未 discover → /discover Tc2_System
- 若有库已 discover 但 doc-shard 未启动 → /doc-shard <lib> <category>
- 若 verify-failed 多 → 提示先处理这些再继续
- 若 T1 完成 → 推进 T2，按用户行业（伺服 → MC2，过程 → 通信）

每条推荐命令配一句理由。
```

### 3. 不修改任何文件

只输出到 chat。

## 用法

```
/next
```

可在任何时候运行。Claude Code 长 session 中阶段性查看进度推荐用。
