# IsEmpty

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcArguments` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050589323.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_IsEmpty.TcPOU`](../examples/P_Demo_IsEmpty.TcPOU) |

---

## 1. 功能简述

`FB_TcArguments.IsEmpty()` 返回 BOOL，表示当前参数列表是否为空（即没有调用过任何 Add 方法）。

用于在 Add 前判断列表状态——例如确保某 alarm 的 Arguments 是"全新"的没有残留参数。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

本方法立即同步返回 BOOL：TRUE 表示列表当前没有任何参数（即从未调用过 Add 方法，或者实例刚刚被重置）；FALSE 表示已经有至少一个参数压入列表。本方法无副作用，可以放心反复调用。

**典型用法**：在调用 alarm.Raise 之前先判断 `ipArguments.IsEmpty()`——若为 FALSE 表示上次 Raise 的参数列表残留，可能影响本次事件文本中的占位符填充。是否清空残留看业务需求——通常事件每次都应该重新填参数（保证文本占位符的语义正确），所以发现残留时建议重新实例化 FB_TcArguments。

## 4. 错误码 / 返回值

本方法/函数返回 `BOOL`。

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 参数列表为空 | 可以开始调 AddXxx 填参数 |
| `FALSE` | 参数列表有内容 | 上次的参数仍在；可能需要清空或忽略 |

## 5. 使用注意 / 常见坑

- IsEmpty 不是"长度 = 0"——只是布尔，无法知道具体多少个参数。
- EventLogger 库没有公开 Clear 方法——若需要清空只能重新实例化 FB_TcArguments。（工程经验补充）
- 调用 IsEmpty 无副作用——可以放心反复调用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IsEmpty.TcPOU`](../examples/P_Demo_IsEmpty.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

Raise 前判断参数列表状态，若 FALSE 说明残留——决策日志输出 / 警告


一次 BOOL 判断替代手写计数器


自建 BOOL 标志位标记是否已 Add → 容易和实际状态脱节；本方法直接问库内部状态


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.7.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050589323.html
- **相关**：`FB_TcArguments`, `FB_TcEventBase.ipArguments`
