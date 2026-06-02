# Tc3_EventLogger

> Beckhoff TwinCAT 3 EventLogger — 事件 / 报警 / 消息分发库。

- **Library Version**: `1.6.2`
- **Source PDF**: <https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf>
- **InfoSys**: <https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/>
- **总条目**: 74（7 个 OO parent FB + 46 个 OO method + 1 个 misc FB（FB_TcEvent）+ 11 个 async-text FB + 4 个 EventEntry 转换 FC/FB + 3 个 Filter + 2 个 RemoteEventLogger = 全部 74）
- **状态**: ✅ done (74/74 verified) · Roadmap 单 Round

## 子目录索引

| 子目录 | 说明 |
|---|---|
| [`fb_listenerbase2/`](fb_listenerbase2/) | `FB_ListenerBase2` 监听器基类 + 9 个方法 |
| [`fb_tcalarm/`](fb_tcalarm/) | `FB_TcAlarm` 报警 FB + 6 个方法（Create/CreateEx/Clear/Confirm/SetJsonAttribute/ResetXxx） |
| [`fb_tcarguments/`](fb_tcarguments/) | `FB_TcArguments` 参数容器 + 1 个方法 |
| [`fb_tceventbase/`](fb_tceventbase/) | `FB_TcEventBase` 事件基类 + 10 个相等性 / 内省方法 |
| [`fb_tceventlogger/`](fb_tceventlogger/) | `FB_TcEventLogger` 全局 logger + 14 个方法 |
| [`fb_tcmessage/`](fb_tcmessage/) | `FB_TcMessage` 消息 FB + 3 个方法（与 TcAlarm 同名分支已用 parent-prefix 例程） |
| [`fb_tcsourceinfo/`](fb_tcsourceinfo/) | `FB_TcSourceInfo` 源信息 + 3 个方法 |
| [`async_text/`](async_text/) | 11 个异步文本请求 FB（按事件 ID 加载 EventClass / Display / Source Text） |
| [`eventry_conversion/`](eventry_conversion/) | 4 个 `TcEventEntry` ↔ 派生类型转换工具 |
| [`filter/`](filter/) | 3 个事件过滤辅助 FB |
| [`remote/`](remote/) | 2 个 RemoteEventLogger 接入 FB |
| [`misc/`](misc/) | 1 个散件 Function Block（FB_TcEvent，不属于上述 OO 树） |
| [`examples/`](examples/) | 74 个 `P_Demo_*.TcPOU` TcPOU 例程（OO method 同名时按 `FB_<Parent>_<Method>` 前缀消歧义） |

## 验收口径

每篇文档：
1. 元信息表 9 行齐全，`Library Version = 1.6.2`、`Source PDF` 指向官方下载链接。
2. `VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT` 逐字搬运自 PDF，`verify_doc.py` 退出码 0（PASS）。
3. 每篇配套 `examples/P_Demo_<...>.TcPOU`，`lint_tcpou.py` 退出码 0。
4. OO method 与父 FB 同章节文本内被 `parse_toc` 拆分；`verify_doc` 通过 `is_parent` + `parent_dir` 双路径定位。

## 已知细节

- **同名 OO 方法**：`Create` / `CreateEx` / `Clear` / `SetJsonAttribute` 同名同形参出现在多个 parent（FB_TcAlarm、FB_TcMessage、FB_TcSourceInfo）。文档保留 method 名做文件名，例程文件统一用 `P_Demo_<Parent>_<Method>.TcPOU` 避免覆盖；文档头部 Example 字段已对应。
- **METHOD 截断**：因为方法 entry 自身（depth ≥ 3）的章节正文含 `METHOD <name>` 头部，`verify_doc` 跳过 METHOD 截断（仅对 depth ≤ 2 的标准 FB 启用，避免砍掉 method 自己的 VAR_INPUT）。
- **行为/错误码细节**：auto-gen 阶段只确保 VAR 区与 PDF 一致；时序、状态机、错误码表等留待人工细化（每篇 `## 8. 待确认项` 已标 ⚠️）。
