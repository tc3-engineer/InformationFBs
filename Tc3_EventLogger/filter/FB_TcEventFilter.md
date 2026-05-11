# FB_TcEventFilter

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/9956773131.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TcEventFilter.xml`](../examples/P_Demo_FB_TcEventFilter.xml) |

---

## 1. 功能简述

`FB_TcEventFilter` 是 TwinCAT 3 EventLogger 的**通用事件过滤器**，支持流式链式语法配置规则，用于 listener 订阅时筛选事件、批量清除/确认操作的范围限定等。

支持：按 Severity、EventClass、SourceName 等过滤；用 `.AND_OP()` / `.OR_OP()` / `.NOT_OP()` 组合条件；用 `.FilterExpression()` 分组嵌套。最多 255 个条件——超出返回 `ADS_NOMOREHDL`。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**流式构建**：`fbFilter.Severity.GreaterThan(TcEventSeverity.Error).AND_OP().Source.Name.Like('%Main%');`—— 通过链式属性 + 方法调用一步步累加条件。条件累加完成后，把实例传给`FB_ListenerBase2.Subscribe2(ipEventFilter := fbFilter)` 等接口生效。

**编译**：filter 在第一次被 Subscribe / 用于操作时"编译"为内部规则树。之后可以重新调 Subscribe 让 EventLogger 替换过滤器规则——支持运行时动态调整。

**典型规则**："严重级别 ≥ Error 且来源包含 Main 模块"，"非调试事件类" 等。

## 4. 错误码 / 返回值

本方法/属性不返回数值（`VOID` 或 getter 直接返回引用）。状态通过 EventLogger 的事件日志间接反映。

## 5. 使用注意 / 常见坑

- 最多 255 个条件——超出返回 `ADS_NOMOREHDL`。
- 链式构建顺序影响逻辑——AND/OR/NOT 的优先级看库实现，复杂规则建议用 FilterExpression 分组。
- 规则要直到 Subscribe 才编译生效——配置过程中报错不会立即反馈。（工程经验补充）
- STRING 模式匹配（`Like`）支持通配符 `%`，但区分大小写——确认目标字符串大小写一致。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcEventFilter.xml`](../examples/P_Demo_FB_TcEventFilter.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

HMI 后端 listener 只接收 "严重级别 ≥ Warning 且来源是 Main 模块" 的事件，减少回调负担


复杂条件一行链式表达，比手写 IF 嵌套清晰得多


在 OnXxx 回调里手写 IF 过滤 → 事件已经到回调浪费 CPU；本 FB 在 EventLogger 端就过滤掉


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.3.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/9956773131.html
- **相关**：`FB_ListenerBase2.Subscribe2`, `FB_TcEventLogger.ClearAlarms`, `FB_TcEventLogger.ConfirmAlarms`
