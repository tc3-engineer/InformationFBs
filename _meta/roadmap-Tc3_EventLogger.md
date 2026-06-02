# Roadmap · Tc3_EventLogger

- **Library Version**: `1.6.2`
- **Source PDF**: <https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf>
- **InfoSys**: <https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/>
- **Discover 日期**: 2026-05-11
- **总条目数**: 74（7 OO parent FB + 66 method + 1 standalone FB 计入 Functions; 实际 by-type: 7 parent + 67 FB）
- **状态**: ✅ done (74/74 verified · 单 Round 全量完成)

## 分类构成

| Category | 条目数 | 说明 |
|---|---|---|
| Asynchronous text requests | 11 | 异步文本请求 FB |
| EventEntry conversion | 4 | TcEventEntry ↔ 派生类型转换 |
| FB_ListenerBase2 | 9 | OO method 子项 |
| FB_TcAlarm | 6 | OO method 子项 |
| FB_TcArguments | 1 | OO method 子项 |
| FB_TcEventBase | 10 | OO method 子项 |
| FB_TcEventLogger | 14 | OO method 子项 |
| FB_TcMessage | 3 | OO method 子项 |
| FB_TcSourceInfo | 3 | OO method 子项 |
| Filter | 3 | 事件过滤 |
| Functions and function blocks | 8 | 含 7 个 OO parent FB + 1 个 standalone（FB_TcClearLoggedEventsSettings） |
| RemoteEventLogger | 2 | 远端 logger 接入 |

## 工具链增强（本 Round 沉淀）

1. **`verify_doc.py`** 已在 PR 流程前完成的改造（沿用至本 Round）：
   - `is_parent` parent FB 自动按 depth-3 child 截断（只保留 parent 自身 VAR）
   - METHOD 截断仅在 depth ≤ 2 时启用，避免砍掉 method 自身 VAR
   - 非 GVL entry 自动剥离正文中嵌入的 `VAR_GLOBAL [CONSTANT]`（例：FB_SetTimeZoneInformation）
2. **新增（本 Round）**：
   - `verify_doc.py`：当 TOC 中存在同名条目（如 `Create` 在 FB_TcAlarm / FB_TcMessage / FB_TcSourceInfo），按文档所在子目录名（`parent_dir`）与候选 `category` 做精确匹配后再回退。
   - `verify_doc.py`：example 链接不再硬编码 `P_Demo_<Name>.TcPOU`，改为从文档自身正则提取 `examples/P_Demo_<Name>.TcPOU`，以兼容 parent-prefix 命名。
   - `lint_plcopen.py`：FB 名匹配兼容 parent-prefix `FB_<Parent>_<Method>` ↔ 末段 `<Method>` 两种命名。
   - 生成器：OO method 同名时自动以 `P_Demo_<Parent>_<Method>.TcPOU` 落盘，避免覆盖。

## 单 Round 执行清单

| Round | Categories | 条目 | 状态 |
|---|---|---|---|
| 1 | 全 12 类（auto-gen 全量） | 74 | ✅ done |

## 验收结果

- `verify_doc.py` 全库 `PASS=74 FAIL=0`
- `lint_plcopen.py` 全 examples `PASS=74 FAIL=0`
- 全仓库整体回归：`PASS=476`（含 Tc2_Standard 32 + Tc2_Utilities 344 + Tc2_DataExchange 3 + Tc2_Math 9 + Tc2_Coupler 7 + Tc2_SUPS 7 + Tc3_EventLogger 74，仓库根 `.claude/`/`CLAUDE.md` 误命中由 find 过滤；脚本退出码 0 全部）

## 未尽事项 / Follow-up

每篇文档 `## 8. 待确认项` 已标 ⚠️：
- 错误码表（具体 nErrorId / nErrId 值与含义）需对照 PDF 第 X 节人工细化
- 时序图与状态机分支留空
- 高级用法示例（例如 alarm 状态机的 Confirm / Reset 边界）待补充
