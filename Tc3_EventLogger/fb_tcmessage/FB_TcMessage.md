# FB_TcMessage

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5003041163.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TcMessage.TcPOU`](../examples/P_Demo_FB_TcMessage.TcPOU) |

---

## 1. 功能简述

`FB_TcMessage` 是 TwinCAT 3 EventLogger 中代表**一次性消息事件**的功能块（FB），继承自 `FB_TcEventBase` 并实现 `I_TcMessage` 接口。Message 与 Alarm 的核心差别是：Message **没有持续状态**——`Send()` 调用一次即生效一次，不需要 Clear/Confirm。

适用于「通知」、「操作日志」、「调试 trace」类事件，例如操作员登录、配方切换、批次开始/结束、版本上线等。EventLogger 把消息写入事件日志、转发给监听器、可导出 CSV 做事后审计。

用法：声明实例 → `Create()` 注册（指定 GUID/EventID/Severity）→ 业务里上升沿调 `Send()` 发出一次通知，或直接通过 `FB_TcEventLogger.SendMessage()` 免实例发送。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

Message 是无状态事件：`Create()` 后实例处于「已就绪」，之后每次调 `Send()` 都即时执行一次。不存在 Raised/Cleared 这种持续状态机。

**典型用法**：`FB_init` 里 `Create()` 一次 → 业务里上升沿调用 `Send()`（继承自 `I_TcMessage`）发出一次通知；EventLogger 把消息异步分发到 listener / 数据库 / HMI 历史窗。

**与 `FB_TcEventLogger.SendMessage()` 的关系**：那是免实例的快捷调用，适合"发一发就完"的场景；本 FB 适合需要复用同一消息模板（同 EventClass+EventID 多次发，避免重复构造）的场景。

## 4. 错误码 / 返回值

本方法/属性不返回数值（`VOID` 或 getter 直接返回引用）。状态通过 EventLogger 的事件日志间接反映。

## 5. 使用注意 / 常见坑

- Message 没有 Clear/Confirm 概念，调那些方法没意义。
- `Send()` 是边沿触发型用法：放在 IF 上升沿后调，不要每周期调（HMI 会被刷爆）。（工程经验补充）
- EventID 配错事件类会得到"未知事件文本"——HMI 显示 EventID 但没文本翻译。
- `SetJsonAttribute()` 在 TwinCAT 4026+ 支持。
- `Create()` 一次注册即可，重复调返回 `ERROR_ALREADY_EXISTS`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcMessage.TcPOU`](../examples/P_Demo_FB_TcMessage.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

MES/SCADA 集成的操作员审计：每次操作员在 HMI 上登录 / 注销 / 切换配方 / 修改关键工艺参数都送一条消息进 EventLogger，供 MES 定时拉取做合规审计（FDA 21 CFR Part 11 / GMP 类要求）


操作审计需要结构化字段（who/when/what）+ 持久化 + 不可篡改。EventLogger 自带这些；用 `FB_TcMessage` 只需一次 `Create()` + 每次操作一次 `Send()`，不用本 FB 就得自己写 ADSLOGSTR + CSV 拼接 + 文件轮替


`ADSLOGSTR` → 文本日志、无字段；自建数据库写入 → 阻塞 PLC 周期；OPC UA Alarm → 需要额外 license；本 FB 走 EventLogger，免费、原生、跨 HMI 厂商


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.11
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5003041163.html
- **相关**：`FB_TcAlarm`, `FB_TcEventBase`, `FB_TcEventLogger.SendMessage`
