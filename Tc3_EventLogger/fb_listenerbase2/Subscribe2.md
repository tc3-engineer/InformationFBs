# Subscribe2

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_ListenerBase2` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/10361960203.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_Subscribe2.TcPOU`](../examples/P_Demo_Subscribe2.TcPOU) |

---

## 1. 功能简述

`FB_ListenerBase2.Subscribe2()` 是 `Subscribe()` 的简化版——只接收一个过滤器参数 `ipEventFilter : I_TcEventFilterBase`，同时控制 message 与 alarm 的接收。

新工程推荐用本方法——接口更简洁，过滤器逻辑也更统一。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

一次性订阅：成功返回 `S_OK`，重复订阅返回相应错误码。`ipEventFilter` 传 0 时接收全部事件，传具体过滤器实例时仅接收匹配规则的事件。

**与 Subscribe 的区别**：Subscribe 分别配置 message 与 alarm 两个过滤器，Subscribe2 用一个统一的过滤器实例同时控制两者。新工程推荐用 Subscribe2——过滤器一次配置完毕，方便维护；老工程兼容用 Subscribe。两者不可在同一 listener 实例上混用。订阅成功后必须周期调 `Execute()` 让事件队列推进，否则事件堆积在 EventLogger 内部。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 订阅成功 | 继续周期调用 Execute |
| `其他错误` | ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- Subscribe2 一次性调用——用 latch 包裹。
- 统一过滤器机制 = 没法分开控制 message / alarm 的接收——需要分开控制用 Subscribe。（工程经验补充）
- Subscribe 与 Subscribe2 不可混用——选定一个版本就坚持用。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_Subscribe2.TcPOU`](../examples/P_Demo_Subscribe2.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

新工程 listener 订阅，配一个 FB_TcEventFilter 过滤所有 Severity ≥ Warning 的事件


新工程的标准订阅接口；过滤器统一管理便于维护


`Subscribe` 双过滤器 → 老工程兼容；新工程优先 Subscribe2


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.5.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/10361960203.html
- **相关**：`FB_ListenerBase2.Subscribe`, `FB_ListenerBase2.Unsubscribe`, `FB_TcEventFilter`
