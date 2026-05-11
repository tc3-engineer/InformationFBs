# FB_TcArguments

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5002149771.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TcArguments.xml`](../examples/P_Demo_FB_TcArguments.xml) |

---

## 1. 功能简述

`FB_TcArguments` 代表事件的**参数列表**（Arguments），实现 `I_TcArguments` 接口。

在 PLC 里实例化后通过 `AddInt` / `AddReal` / `AddBool` / `AddString` 等 20+ Add 方法依次压入参数；传给 alarm/message 的 `ipArguments` 参数；EventLogger 在事件文本里用占位符 `{0}` `{1}` `{2}` … 按压入顺序填充。

支持的类型：BOOL / SINT/INT/DINT/LINT / USINT/UINT/UDINT/ULINT / REAL/LREAL / BYTE/WORD/DWORD / STRING / Blob / 时间戳 / 事件引用 ID 等。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

FB_TcArguments 不维护状态机，只是一个有序的参数列表容器。每次 `AddXxx()` 把参数追加到末尾。

**调用流程**：1) 在 Raise/Send 之前实例化 FB_TcArguments；2) 调用 AddXxx 依次压入参数；3) 把它的接口指针传给 alarm.Raise / logger.SendMessage 的 ipArguments 参数；4) EventLogger 在事件文本里按序填充。

**参数顺序必须严格对应文本模板的占位符**——顺序错了文本会乱填。`IsEmpty()` 方法检测当前是否无参数（适合调用 Add 前的状态判断）。

## 4. 错误码 / 返回值

本方法/属性不返回数值（`VOID` 或 getter 直接返回引用）。状态通过 EventLogger 的事件日志间接反映。

## 5. 使用注意 / 常见坑

- 参数压入顺序与文本占位符 `{0}` `{1}` 严格对应——顺序错了文本乱填。
- 一次 Raise 用完后 Arguments 状态保留——下次 Raise 前要清空（重新实例化或用 Clear，若有）。（工程经验补充）
- STRING 默认长度 80 字节——长字符串先 STRING(255)+。（工程经验补充）
- AddBlob 用于二进制数据，注意 EventLogger 端不一定能显示。（工程经验补充）
- `IsEmpty()` 适合在 Add 前判断当前列表状态。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcArguments.xml`](../examples/P_Demo_FB_TcArguments.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

alarm 文本「电机 {0} 温度 {1}°C 过高」的两个占位符需要在 Raise 前 AddString + AddReal 填值


结构化参数列表 + EventLogger 自动文本填充，比手写字符串拼接更安全、支持多语言


`SetJsonAttribute` 写 JSON → 适合嵌套结构；本 FB 适合标准类型按顺序压入；手写 CONCAT 字符串 → 多语言切换困难


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5002149771.html
- **相关**：`FB_TcArguments.IsEmpty`, `FB_TcEventBase.ipArguments`
