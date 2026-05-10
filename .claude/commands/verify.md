---
description: 重新对照 PDF 校验某篇已生成的文档；可用于事后抽检
argument-hint: <path/to/doc.md>
---

# /verify

对仓库内某一篇 FB/FC 文档执行独立校验。用于：
- 怀疑某篇文档质量（已合并 main 后抽检）
- `/doc-shard` 时被标记 `verify-failed` 的文档手动复查
- review PR 前快速验真

## 输入

- `$ARGUMENTS`：相对仓库根的文档路径，例如 `Tc2_System/ads/ADSREAD.md`
- 路径必须存在；不存在 → 报错并退出

## 流程

### 1. 读目标文档
- 解析头部元信息表，提取 Library、Library Version、Source PDF
- 提取 VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 的全部字段（名 + 类型 + 注释）
- 提取功能简述和行为说明中的关键事实

### 2. 抓 PDF
按文档头里的 Source PDF URL 重新 web_fetch。
失败 → 报错并退出（注明可能 PDF URL 失效或网络问题）。

### 3. 逐字段对照

按 `/doc-shard` 中"自验证"章节的同样检查表执行，但更严格：
- 不止检查 VAR 名/类型，还要检查**注释文字是否一致**
- 检查描述句中的数值（如 "15 字节"、"49.7 天"）是否与 PDF 一致
- 检查例程中引用的引脚名是否拼写正确

### 4. 输出报告

把结果**直接打到 chat**（不要写文件，因为这是临时校验），格式：

```
## Verify Report: <path>

Library: <name> v<version> (PDF 抓取于 <UTC>)
文档 Status: <doc 头部 status>

### 检查项
- VAR_INPUT 名/类型: ✅ / ❌ <具体差异>
- VAR_OUTPUT 名/类型: ✅ / ❌
- 元信息 Version: ✅ / ❌
- 描述关键事实: ✅ / ❌
- 例程引脚名: ✅ / ❌

### 总评
✅ PASS / ⚠️ MINOR / ❌ FAIL

### 建议
- (若 FAIL) 修正建议：<具体内容>
- (若 PASS) 是否要把 _meta/verify/<library>/<name>.md 同步刷新？(y/n 等用户回答)
```

### 5. 不自动修改

`/verify` 是只读校验，不写任何文件、不提 PR。如果发现问题，输出建议后**问用户**是否要修，得到肯定回答再编辑。

这点与 `/doc-shard` 不同——后者自动修复并重试，前者保守。

## 用法示例

```
/verify Tc2_Standard/timer/TON.md
/verify Tc2_System/ads/ADSREAD.md
```
